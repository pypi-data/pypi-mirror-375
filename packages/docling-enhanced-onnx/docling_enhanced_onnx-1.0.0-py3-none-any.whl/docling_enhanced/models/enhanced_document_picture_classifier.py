"""
Enhanced Document Picture Classifier with ONNX Auto-Detection and Fallback

This module provides an enhanced document picture classifier that automatically
detects and uses ONNX variants when available, with graceful fallback to the
original IBM models.

Approach 1 + 2 Integration:
- Auto-detects docling-onnx-models package availability
- Switches between ONNX and original models seamlessly
- Maintains identical API for drop-in replacement
- Provides intelligent execution provider selection
"""

import logging
from collections.abc import Iterable
from pathlib import Path
from typing import List, Literal, Optional, Union

import numpy as np
from docling_core.types.doc import (
    DoclingDocument,
    NodeItem,
    PictureClassificationClass,
    PictureClassificationData,
    PictureItem,
)
from PIL import Image
from pydantic import BaseModel

from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import ItemAndImageEnrichmentElement
from docling.models.base_model import BaseItemAndImageEnrichmentModel
from docling.models.utils.hf_model_download import download_hf_model
from docling.utils.accelerator_utils import decide_device

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


class EnhancedDocumentPictureClassifierOptions(BaseModel):
    """
    Options for configuring the Enhanced DocumentPictureClassifier.

    Attributes
    ----------
    kind : Literal["enhanced_document_picture_classifier"]
        Identifier for the type of classifier.
    """

    kind: Literal["enhanced_document_picture_classifier"] = "enhanced_document_picture_classifier"


class EnhancedDocumentPictureClassifier(BaseItemAndImageEnrichmentModel):
    """
    Enhanced Document Picture Classifier with ONNX auto-detection and fallback.

    This class automatically detects if docling-onnx-models is available
    and uses ONNX models when beneficial, falling back to original models
    when necessary.

    Attributes
    ----------
    enabled : bool
        Whether the classifier is enabled for use.
    options : EnhancedDocumentPictureClassifierOptions
        Configuration options for the classifier.
    document_picture_classifier : Union[DocumentFigureClassifierPredictor, DocumentFigureClassifierPredictor]
        The underlying prediction model, loaded if the classifier is enabled.
    """

    _model_repo_folder = "ds4sd--DocumentFigureClassifier"
    images_scale = 2

    def __init__(
        self,
        enabled: bool,
        artifacts_path: Optional[Path],
        options: EnhancedDocumentPictureClassifierOptions,
        accelerator_options: AcceleratorOptions,
    ):
        """
        Initializes the Enhanced DocumentPictureClassifier.

        Parameters
        ----------
        enabled : bool
            Indicates whether the classifier is enabled.
        artifacts_path : Optional[Path]
            Path to the directory containing model artifacts.
        options : EnhancedDocumentPictureClassifierOptions
            Configuration options for the classifier.
        accelerator_options : AcceleratorOptions
            Options for configuring the device and parallelism.
        """
        self.enabled = enabled
        self.options = options
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
        """Initialize ONNX-based document figure classifier."""
        try:
            from docling_onnx_models.document_figure_classifier import DocumentFigureClassifier
            from docling_onnx_models.document_figure_classifier.figure_config import FigureConfig
            from docling_onnx_models.common import get_optimal_providers

            # Create ONNX configuration
            providers = get_optimal_providers('auto')
            config = FigureConfig(
                providers=providers,
                num_threads=accelerator_options.num_threads
            )

            self.document_picture_classifier = DocumentFigureClassifier(config)
            self.predictor_type = "onnx"
            _log.info(f"Using ONNX document figure classifier with providers: {providers}")

        except Exception as e:
            _log.warning(f"Failed to initialize ONNX predictor: {e}, falling back to original")
            self.use_onnx = False
            self._init_original_predictor(artifacts_path, accelerator_options)

    def _init_original_predictor(
        self,
        artifacts_path: Optional[Path],
        accelerator_options: AcceleratorOptions
    ):
        """Initialize original IBM models document figure classifier."""
        device = decide_device(accelerator_options.device)
        from docling_ibm_models.document_figure_classifier_model.document_figure_classifier_predictor import (
            DocumentFigureClassifierPredictor,
        )

        if artifacts_path is None:
            artifacts_path = self.download_models()
        else:
            artifacts_path = artifacts_path / self._model_repo_folder

        self.document_picture_classifier = DocumentFigureClassifierPredictor(
            artifacts_path=str(artifacts_path),
            device=device,
            num_threads=accelerator_options.num_threads,
        )
        self.predictor_type = "original"
        _log.info("Using original IBM models document figure classifier")

    @staticmethod
    def download_models(
        local_dir: Optional[Path] = None, force: bool = False, progress: bool = False
    ) -> Path:
        return download_hf_model(
            repo_id="ds4sd/DocumentFigureClassifier",
            revision="v1.0.1",
            local_dir=local_dir,
            force=force,
            progress=progress,
        )

    def is_processable(self, doc: DoclingDocument, element: NodeItem) -> bool:
        """
        Determines if the given element can be processed by the classifier.

        Parameters
        ----------
        doc : DoclingDocument
            The document containing the element.
        element : NodeItem
            The element to be checked.

        Returns
        -------
        bool
            True if the element is a PictureItem and processing is enabled; False otherwise.
        """
        return self.enabled and isinstance(element, PictureItem)

    def __call__(
        self,
        doc: DoclingDocument,
        element_batch: Iterable[ItemAndImageEnrichmentElement],
    ) -> Iterable[NodeItem]:
        """
        Processes a batch of elements and enriches them with classification predictions.

        Parameters
        ----------
        doc : DoclingDocument
            The document containing the elements to be processed.
        element_batch : Iterable[ItemAndImageEnrichmentElement]
            A batch of pictures to classify.

        Returns
        -------
        Iterable[NodeItem]
            An iterable of NodeItem objects after processing. The field
            'data.classification' is added containing the classification for each picture.
        """
        if not self.enabled:
            for element in element_batch:
                yield element.item
            return

        images: List[Union[Image.Image, np.ndarray]] = []
        elements: List[PictureItem] = []
        for el in element_batch:
            assert isinstance(el.item, PictureItem)
            elements.append(el.item)
            images.append(el.image)

        # Use appropriate prediction method based on type
        if self.predictor_type == "onnx":
            outputs = self.document_picture_classifier.predict_batch(images)
        else:
            outputs = self.document_picture_classifier.predict(images)

        for item, output in zip(elements, outputs):
            item.annotations.append(
                PictureClassificationData(
                    provenance=f"Enhanced{self.predictor_type.title()}DocumentPictureClassifier",
                    predicted_classes=[
                        PictureClassificationClass(
                            class_name=pred[0],
                            confidence=pred[1],
                        )
                        for pred in output
                    ],
                )
            )

            yield item