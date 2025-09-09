"""
Enhanced Table Structure Model with ONNX Auto-Detection and Fallback

This module provides an enhanced table structure model that automatically detects
and uses ONNX variants when available, with graceful fallback to the
original IBM models.

Approach 1 + 2 Integration:
- Auto-detects docling-onnx-models package availability  
- Switches between ONNX and original models seamlessly
- Maintains identical API for drop-in replacement
- Provides intelligent execution provider selection
"""

import copy
import logging
import warnings
from collections.abc import Iterable
from pathlib import Path
from typing import Optional

import numpy
from docling_core.types.doc import BoundingBox, DocItemLabel, TableCell
from docling_core.types.doc.page import (
    BoundingRectangle,
    TextCellUnit,
)
from PIL import ImageDraw

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import Page, Table, TableStructurePrediction
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import (
    TableFormerMode,
    TableStructureOptions,
)
from docling.datamodel.settings import settings
from docling.models.base_model import BasePageModel
from docling.models.utils.hf_model_download import download_hf_model
from docling.utils.accelerator_utils import decide_device
from docling.utils.profiling import TimeRecorder

_log = logging.getLogger(__name__)


def _is_onnx_available() -> bool:
    """Check if docling-onnx-models is available."""
    try:
        import docling_onnx_models
        return True
    except ImportError:
        return False


def _should_use_onnx(accelerator_options: AcceleratorOptions) -> bool:
    """
    Determine if ONNX should be used based on availability and device.
    
    Args:
        accelerator_options: Accelerator configuration
        
    Returns:
        bool: True if ONNX should be used
    """
    if not _is_onnx_available():
        _log.info("docling-onnx-models not available, using original models")
        return False
        
    device = decide_device(accelerator_options.device)
    
    try:
        from docling_onnx_models.common import get_optimal_providers
        providers = get_optimal_providers('auto')
        _log.info(f"ONNX providers available: {providers}")
        return len(providers) > 0
    except Exception as e:
        _log.warning(f"Failed to detect ONNX providers: {e}")
        return False


class EnhancedTableStructureModel(BasePageModel):
    """
    Enhanced Table Structure Model with ONNX auto-detection and fallback.
    
    This class automatically detects if docling-onnx-models is available
    and uses ONNX models when beneficial, falling back to original models
    when necessary.
    """
    
    _model_repo_folder = "ds4sd--docling-models"
    _model_path = "model_artifacts/tableformer"

    def __init__(
        self,
        enabled: bool,
        artifacts_path: Optional[Path],
        options: TableStructureOptions,
        accelerator_options: AcceleratorOptions,
    ):
        self.options = options
        self.do_cell_matching = self.options.do_cell_matching
        self.mode = self.options.mode
        self.enabled = enabled
        self.use_onnx = _should_use_onnx(accelerator_options)
        
        if self.enabled:
            if self.use_onnx:
                self._init_onnx_predictor(artifacts_path, accelerator_options)
            else:
                self._init_original_predictor(artifacts_path, accelerator_options)

    def _init_onnx_predictor(
        self, 
        artifacts_path: Optional[Path],
        accelerator_options: AcceleratorOptions
    ):
        """Initialize ONNX-based table structure predictor."""
        try:
            # Try to create ONNX predictor with local models
            if artifacts_path and (artifacts_path / "asmud--ds4sd-docling-models-onnx").exists():
                docling_models_path = artifacts_path / "asmud--ds4sd-docling-models-onnx"
                
                # Use the updated ONNX models from our package
                import sys
                onnx_models_path = "/Users/mac/Desktop/dtsen-repo/docling/docling-onnx-models-repo/src"
                if onnx_models_path not in sys.path:
                    sys.path.insert(0, onnx_models_path)
                
                from docling_onnx_models.tableformer import TableFormerPredictor
                from docling_onnx_models.tableformer.table_config import create_config_from_local_path
                from docling_onnx_models.common import get_optimal_providers
                
                # Create ONNX configuration for air-gapped usage
                providers = get_optimal_providers('auto')
                config = create_config_from_local_path(
                    artifacts_path=docling_models_path,
                    model_type=self.mode.value.lower() if hasattr(self.mode, 'value') else "fast",
                    providers=providers,
                    num_threads=accelerator_options.num_threads
                )
                
                self.tf_predictor = TableFormerPredictor(config)
                self.predictor_type = "onnx"
                self.scale = 2.0  # Scale up table input images to 144 dpi
                _log.info(f"Using ONNX table structure predictor with providers: {providers}")
                _log.info(f"ONNX model loaded from: {docling_models_path}")
                return
            
            # If no local models found, try general ONNX approach
            from docling_onnx_models.common import get_optimal_providers
            providers = get_optimal_providers('auto')
            _log.info(f"Local ONNX models not found at {artifacts_path}, checking general ONNX availability")
            raise ImportError("No suitable ONNX models found for air-gapped usage")
            
        except Exception as e:
            _log.warning(f"Failed to initialize ONNX predictor: {e}, falling back to original")
            self.use_onnx = False
            self._init_original_predictor(artifacts_path, accelerator_options)

    def _init_original_predictor(
        self,
        artifacts_path: Optional[Path],
        accelerator_options: AcceleratorOptions
    ):
        """Initialize original IBM models table structure predictor."""
        if artifacts_path is None:
            artifacts_path = self.download_models() / self._model_path
        else:
            # will become the default in the future
            if (artifacts_path / self._model_repo_folder).exists():
                artifacts_path = (
                    artifacts_path / self._model_repo_folder / self._model_path
                )
            elif (artifacts_path / self._model_path).exists():
                warnings.warn(
                    "The usage of artifacts_path containing directly "
                    f"{self._model_path} is deprecated. Please point "
                    "the artifacts_path to the parent containing "
                    f"the {self._model_repo_folder} folder.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                artifacts_path = artifacts_path / self._model_path

        if self.mode == TableFormerMode.ACCURATE:
            artifacts_path = artifacts_path / "accurate"
        else:
            artifacts_path = artifacts_path / "fast"

        # Third Party
        import docling_ibm_models.tableformer.common as c
        from docling_ibm_models.tableformer.data_management.tf_predictor import (
            TFPredictor,
        )

        device = decide_device(accelerator_options.device)

        # Disable MPS here, until we know why it makes things slower.
        if device == AcceleratorDevice.MPS.value:
            device = AcceleratorDevice.CPU.value

        self.tm_config = c.read_config(f"{artifacts_path}/tm_config.json")
        self.tm_config["model"]["save_dir"] = artifacts_path
        self.tm_model_type = self.tm_config["model"]["type"]

        self.tf_predictor = TFPredictor(
            self.tm_config, device, accelerator_options.num_threads
        )
        self.scale = 2.0  # Scale up table input images to 144 dpi
        self.predictor_type = "original"
        _log.info("Using original IBM models table structure predictor")

    @staticmethod
    def download_models(
        local_dir: Optional[Path] = None, force: bool = False, progress: bool = False
    ) -> Path:
        return download_hf_model(
            repo_id="ds4sd/docling-models",
            revision="v2.3.0",
            local_dir=local_dir,
            force=force,
            progress=progress,
        )

    def draw_table_and_cells(
        self,
        conv_res: ConversionResult,
        page: Page,
        tbl_list: Iterable[Table],
        show: bool = False,
    ):
        assert page._backend is not None
        assert page.size is not None

        image = (
            page._backend.get_page_image()
        )  # make new image to avoid drawing on the saved ones

        scale_x = image.width / page.size.width
        scale_y = image.height / page.size.height

        draw = ImageDraw.Draw(image)

        for table_element in tbl_list:
            x0, y0, x1, y1 = table_element.cluster.bbox.as_tuple()
            y0 *= scale_x
            y1 *= scale_y
            x0 *= scale_x
            x1 *= scale_x

            draw.rectangle([(x0, y0), (x1, y1)], outline="red")

            for cell in table_element.cluster.cells:
                x0, y0, x1, y1 = cell.rect.to_bounding_box().as_tuple()
                x0 *= scale_x
                x1 *= scale_x
                y0 *= scale_x
                y1 *= scale_y

                draw.rectangle([(x0, y0), (x1, y1)], outline="green")

            for tc in table_element.table_cells:
                if tc.bbox is not None:
                    x0, y0, x1, y1 = tc.bbox.as_tuple()
                    x0 *= scale_x
                    x1 *= scale_x
                    y0 *= scale_x
                    y1 *= scale_y

                    if tc.column_header:
                        width = 3
                    else:
                        width = 1
                    draw.rectangle([(x0, y0), (x1, y1)], outline="blue", width=width)
                    draw.text(
                        (x0 + 3, y0 + 3),
                        text=f"{tc.start_row_offset_idx}, {tc.start_col_offset_idx}",
                        fill="black",
                    )
        if show:
            image.show()
        else:
            out_path: Path = (
                Path(settings.debug.debug_output_path)
                / f"debug_{conv_res.input.file.stem}"
            )
            out_path.mkdir(parents=True, exist_ok=True)

            out_file = out_path / f"table_struct_page_{page.page_no:05}.png"
            image.save(str(out_file), format="png")

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        if not self.enabled:
            yield from page_batch
            return

        for page in page_batch:
            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
            else:
                with TimeRecorder(conv_res, "table_structure"):
                    assert page.predictions.layout is not None
                    assert page.size is not None

                    page.predictions.tablestructure = (
                        TableStructurePrediction()
                    )  # dummy

                    in_tables = [
                        (
                            cluster,
                            [
                                round(cluster.bbox.l) * self.scale,
                                round(cluster.bbox.t) * self.scale,
                                round(cluster.bbox.r) * self.scale,
                                round(cluster.bbox.b) * self.scale,
                            ],
                        )
                        for cluster in page.predictions.layout.clusters
                        if cluster.label
                        in [DocItemLabel.TABLE, DocItemLabel.DOCUMENT_INDEX]
                    ]
                    if not len(in_tables):
                        yield page
                        continue

                    page_input = {
                        "width": page.size.width * self.scale,
                        "height": page.size.height * self.scale,
                        "image": numpy.asarray(page.get_image(scale=self.scale)),
                    }

                    table_clusters, table_bboxes = zip(*in_tables)

                    if len(table_bboxes):
                        for table_cluster, tbl_box in in_tables:
                            # Check if word-level cells are available from backend:
                            sp = page._backend.get_segmented_page()
                            if sp is not None:
                                tcells = sp.get_cells_in_bbox(
                                    cell_unit=TextCellUnit.WORD,
                                    bbox=table_cluster.bbox,
                                )
                                if len(tcells) == 0:
                                    # In case word-level cells yield empty
                                    tcells = table_cluster.cells
                            else:
                                # Otherwise - we use normal (line/phrase) cells
                                tcells = table_cluster.cells
                            tokens = []
                            for c in tcells:
                                # Only allow non empty strings (spaces) into the cells of a table
                                if len(c.text.strip()) > 0:
                                    new_cell = copy.deepcopy(c)
                                    new_cell.rect = BoundingRectangle.from_bounding_box(
                                        new_cell.rect.to_bounding_box().scaled(
                                            scale=self.scale
                                        )
                                    )
                                    tokens.append(
                                        {
                                            "id": new_cell.index,
                                            "text": new_cell.text,
                                            "bbox": new_cell.rect.to_bounding_box().model_dump(),
                                        }
                                    )
                            page_input["tokens"] = tokens

                            # Use appropriate predictor method based on type
                            tf_output = self.tf_predictor.multi_table_predict(
                                page_input, [tbl_box], do_matching=self.do_cell_matching
                            )
                                
                            table_out = tf_output[0]
                            table_cells = []
                            for element in table_out["tf_responses"]:
                                if not self.do_cell_matching:
                                    the_bbox = BoundingBox.model_validate(
                                        element["bbox"]
                                    ).scaled(1 / self.scale)
                                    text_piece = page._backend.get_text_in_rect(
                                        the_bbox
                                    )
                                    element["bbox"]["token"] = text_piece

                                tc = TableCell.model_validate(element)
                                if tc.bbox is not None:
                                    tc.bbox = tc.bbox.scaled(1 / self.scale)
                                table_cells.append(tc)

                            assert "predict_details" in table_out

                            # Retrieving cols/rows, after post processing:
                            num_rows = table_out["predict_details"].get("num_rows", 0)
                            num_cols = table_out["predict_details"].get("num_cols", 0)
                            otsl_seq = (
                                table_out["predict_details"]
                                .get("prediction", {})
                                .get("rs_seq", [])
                            )

                            tbl = Table(
                                otsl_seq=otsl_seq,
                                table_cells=table_cells,
                                num_rows=num_rows,
                                num_cols=num_cols,
                                id=table_cluster.id,
                                page_no=page.page_no,
                                cluster=table_cluster,
                                label=table_cluster.label,
                            )

                            page.predictions.tablestructure.table_map[
                                table_cluster.id
                            ] = tbl

                    # For debugging purposes:
                    if settings.debug.visualize_tables:
                        self.draw_table_and_cells(
                            conv_res,
                            page,
                            page.predictions.tablestructure.table_map.values(),
                        )

                yield page