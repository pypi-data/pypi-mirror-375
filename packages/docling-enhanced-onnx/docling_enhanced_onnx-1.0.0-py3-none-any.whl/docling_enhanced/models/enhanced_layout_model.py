"""
Enhanced Layout Model with ONNX Auto-Detection and Fallback

This module provides an enhanced layout model that automatically detects
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
from typing import List, Optional, Union

import numpy as np
from docling_core.types.doc import DocItemLabel
from PIL import Image

from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import BoundingBox, Cluster, LayoutPrediction, Page
from docling.datamodel.document import ConversionResult
from docling.datamodel.layout_model_specs import DOCLING_LAYOUT_V2, LayoutModelConfig
from docling.datamodel.pipeline_options import LayoutOptions
from docling.datamodel.settings import settings
from docling.models.base_model import BasePageModel
from docling.models.utils.hf_model_download import download_hf_model
from docling.utils.accelerator_utils import decide_device
from docling.utils.layout_postprocessor import LayoutPostprocessor
from docling.utils.profiling import TimeRecorder
from docling.utils.visualization import draw_clusters

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
        
    # For CPU-only setups, ONNX might be beneficial
    # For GPU setups, let the user choose or auto-detect optimal provider
    device = decide_device(accelerator_options.device)
    
    try:
        from docling_onnx_models.common import get_optimal_providers
        providers = get_optimal_providers('auto')
        _log.info(f"ONNX providers available: {providers}")
        return len(providers) > 0
    except Exception as e:
        _log.warning(f"Failed to detect ONNX providers: {e}")
        return False


class EnhancedLayoutModel(BasePageModel):
    """
    Enhanced Layout Model with ONNX auto-detection and fallback.
    
    This class automatically detects if docling-onnx-models is available
    and uses ONNX models when beneficial, falling back to original models
    when necessary.
    """
    
    TEXT_ELEM_LABELS = [
        DocItemLabel.TEXT,
        DocItemLabel.FOOTNOTE,
        DocItemLabel.CAPTION,
        DocItemLabel.CHECKBOX_UNSELECTED,
        DocItemLabel.CHECKBOX_SELECTED,
        DocItemLabel.SECTION_HEADER,
        DocItemLabel.PAGE_HEADER,
        DocItemLabel.PAGE_FOOTER,
        DocItemLabel.CODE,
        DocItemLabel.LIST_ITEM,
        DocItemLabel.FORMULA,
    ]
    PAGE_HEADER_LABELS = [DocItemLabel.PAGE_HEADER, DocItemLabel.PAGE_FOOTER]

    TABLE_LABELS = [DocItemLabel.TABLE, DocItemLabel.DOCUMENT_INDEX]
    FIGURE_LABEL = DocItemLabel.PICTURE
    FORMULA_LABEL = DocItemLabel.FORMULA
    CONTAINER_LABELS = [DocItemLabel.FORM, DocItemLabel.KEY_VALUE_REGION]

    def __init__(
        self,
        artifacts_path: Optional[Path],
        accelerator_options: AcceleratorOptions,
        options: LayoutOptions,
    ):
        self.options = options
        self.use_onnx = _should_use_onnx(accelerator_options)
        
        if self.use_onnx:
            self._init_onnx_predictor(artifacts_path, accelerator_options, options)
        else:
            self._init_original_predictor(artifacts_path, accelerator_options, options)
    
    def _init_onnx_predictor(
        self, 
        artifacts_path: Optional[Path],
        accelerator_options: AcceleratorOptions,
        options: LayoutOptions
    ):
        """Initialize ONNX-based layout predictor."""
        try:
            from docling_onnx_models.layoutmodel import LayoutPredictor
            from docling_onnx_models.layoutmodel.layout_config import LayoutConfig
            from docling_onnx_models.common import get_optimal_providers
            
            # Create ONNX configuration
            providers = get_optimal_providers('auto')
            config = LayoutConfig(
                providers=providers,
                num_threads=accelerator_options.num_threads
            )
            
            self.layout_predictor = LayoutPredictor(config)
            self.predictor_type = "onnx"
            _log.info(f"Using ONNX layout predictor with providers: {providers}")
            
        except Exception as e:
            _log.warning(f"Failed to initialize ONNX predictor: {e}, falling back to original")
            self.use_onnx = False
            self._init_original_predictor(artifacts_path, accelerator_options, options)
    
    def _init_original_predictor(
        self,
        artifacts_path: Optional[Path],
        accelerator_options: AcceleratorOptions,
        options: LayoutOptions
    ):
        """Initialize original IBM models layout predictor."""
        from docling_ibm_models.layoutmodel.layout_predictor import LayoutPredictor

        device = decide_device(accelerator_options.device)
        layout_model_config = options.model_spec
        model_repo_folder = layout_model_config.model_repo_folder
        model_path = layout_model_config.model_path

        if artifacts_path is None:
            artifacts_path = (
                self.download_models(layout_model_config=layout_model_config)
                / model_path
            )
        else:
            if (artifacts_path / model_repo_folder).exists():
                artifacts_path = artifacts_path / model_repo_folder / model_path
            elif (artifacts_path / model_path).exists():
                warnings.warn(
                    "The usage of artifacts_path containing directly "
                    f"{model_path} is deprecated. Please point "
                    "the artifacts_path to the parent containing "
                    f"the {model_repo_folder} folder.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                artifacts_path = artifacts_path / model_path

        self.layout_predictor = LayoutPredictor(
            artifact_path=str(artifacts_path),
            device=device,
            num_threads=accelerator_options.num_threads,
        )
        self.predictor_type = "original"
        _log.info("Using original IBM models layout predictor")

    @staticmethod
    def download_models(
        local_dir: Optional[Path] = None,
        force: bool = False,
        progress: bool = False,
        layout_model_config: LayoutModelConfig = LayoutOptions().model_spec,
    ) -> Path:
        return download_hf_model(
            repo_id=layout_model_config.repo_id,
            revision=layout_model_config.revision,
            local_dir=local_dir,
            force=force,
            progress=progress,
        )

    def draw_clusters_and_cells_side_by_side(
        self, conv_res, page, clusters, mode_prefix: str, show: bool = False
    ):
        """
        Draws a page image side by side with clusters filtered into two categories:
        - Left: Clusters excluding FORM, KEY_VALUE_REGION, and PICTURE.
        - Right: Clusters including FORM, KEY_VALUE_REGION, and PICTURE.
        """
        scale_x = page.image.width / page.size.width
        scale_y = page.image.height / page.size.height

        # Filter clusters for left and right images
        exclude_labels = {
            DocItemLabel.FORM,
            DocItemLabel.KEY_VALUE_REGION,
            DocItemLabel.PICTURE,
        }
        left_clusters = [c for c in clusters if c.label not in exclude_labels]
        right_clusters = [c for c in clusters if c.label in exclude_labels]
        
        # Create a deep copy of the original image for both sides
        left_image = page.image.copy()
        right_image = page.image.copy()

        # Draw clusters on both images
        draw_clusters(left_image, left_clusters, scale_x, scale_y)
        draw_clusters(right_image, right_clusters, scale_x, scale_y)
        
        # Combine the images side by side
        combined_width = left_image.width * 2
        combined_height = left_image.height
        combined_image = Image.new("RGB", (combined_width, combined_height))
        combined_image.paste(left_image, (0, 0))
        combined_image.paste(right_image, (left_image.width, 0))
        
        if show:
            combined_image.show()
        else:
            out_path: Path = (
                Path(settings.debug.debug_output_path)
                / f"debug_{conv_res.input.file.stem}"
            )
            out_path.mkdir(parents=True, exist_ok=True)
            out_file = out_path / f"{mode_prefix}_layout_page_{page.page_no:05}.png"
            combined_image.save(str(out_file), format="png")

    def __call__(
        self, conv_res: ConversionResult, page_batch: Iterable[Page]
    ) -> Iterable[Page]:
        # Convert to list to allow multiple iterations
        pages = list(page_batch)

        # Separate valid and invalid pages
        valid_pages = []
        valid_page_images: List[Union[Image.Image, np.ndarray]] = []

        for page in pages:
            assert page._backend is not None
            if not page._backend.is_valid():
                continue

            assert page.size is not None
            page_image = page.get_image(scale=1.0)
            assert page_image is not None

            valid_pages.append(page)
            valid_page_images.append(page_image)

        # Process all valid pages with batch prediction
        batch_predictions = []
        if valid_page_images:
            with TimeRecorder(conv_res, "layout"):
                batch_predictions = self.layout_predictor.predict_batch(
                    valid_page_images
                )

        # Process each page with its predictions
        valid_page_idx = 0
        for page in pages:
            assert page._backend is not None
            if not page._backend.is_valid():
                yield page
                continue

            page_predictions = batch_predictions[valid_page_idx]
            valid_page_idx += 1

            clusters = []
            for ix, pred_item in enumerate(page_predictions):
                label = DocItemLabel(
                    pred_item["label"].lower().replace(" ", "_").replace("-", "_")
                )
                cluster = Cluster(
                    id=ix,
                    label=label,
                    confidence=pred_item["confidence"],
                    bbox=BoundingBox.model_validate(pred_item),
                    cells=[],
                )
                clusters.append(cluster)

            if settings.debug.visualize_raw_layout:
                self.draw_clusters_and_cells_side_by_side(
                    conv_res, page, clusters, mode_prefix="raw"
                )

            # Apply postprocessing
            processed_clusters, processed_cells = LayoutPostprocessor(
                page, clusters, self.options
            ).postprocess()

            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    "Mean of empty slice|invalid value encountered in scalar divide",
                    RuntimeWarning,
                    "numpy",
                )

                conv_res.confidence.pages[page.page_no].layout_score = float(
                    np.mean([c.confidence for c in processed_clusters])
                )

                conv_res.confidence.pages[page.page_no].ocr_score = float(
                    np.mean([c.confidence for c in processed_cells if c.from_ocr])
                )

            page.predictions.layout = LayoutPrediction(clusters=processed_clusters)

            if settings.debug.visualize_layout:
                self.draw_clusters_and_cells_side_by_side(
                    conv_res, page, processed_clusters, mode_prefix="postprocessed"
                )

            yield page