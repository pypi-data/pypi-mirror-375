"""
Enhanced Model Utilities for ONNX Integration

This module provides utilities for enhanced model loading with ONNX auto-detection
and fallback functionality, making it easy to integrate the enhanced models into
the existing docling pipeline.

Key Features:
- Auto-detection of docling-onnx-models availability
- Factory functions for enhanced model creation
- Configuration helpers for seamless integration
- Drop-in replacement utilities
"""

import logging
from pathlib import Path
from typing import Optional, Type, Union

from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.pipeline_options import LayoutOptions, TableStructureOptions
from docling.models.base_model import BasePageModel, BaseItemAndImageEnrichmentModel
from docling_enhanced.models.enhanced_document_picture_classifier import (
    EnhancedDocumentPictureClassifier, 
    EnhancedDocumentPictureClassifierOptions
)

_log = logging.getLogger(__name__)


def is_onnx_models_available() -> bool:
    """
    Check if docling-onnx-models package is available.
    
    Returns:
        bool: True if docling-onnx-models is installed and importable
    """
    try:
        import docling_onnx_models
        return True
    except ImportError:
        return False


def get_onnx_providers() -> list:
    """
    Get available ONNX execution providers.
    
    Returns:
        list: List of available ONNX execution providers
    """
    if not is_onnx_models_available():
        return []
        
    try:
        from docling_onnx_models.common import get_optimal_providers
        return get_optimal_providers('auto')
    except Exception as e:
        _log.warning(f"Failed to get ONNX providers: {e}")
        return []


def create_enhanced_layout_model(
    artifacts_path: Optional[Path],
    accelerator_options: AcceleratorOptions,
    options: LayoutOptions,
    force_original: bool = False
) -> BasePageModel:
    """
    Create an enhanced layout model with ONNX auto-detection.
    
    Args:
        artifacts_path: Path to model artifacts
        accelerator_options: Accelerator configuration
        options: Layout model options
        force_original: If True, force use of original models even if ONNX is available
        
    Returns:
        BasePageModel: Enhanced layout model instance
    """
    if force_original or not is_onnx_models_available():
        # Import here to avoid circular imports
        from docling.models.layout_model import LayoutModel
        _log.info("Using original LayoutModel")
        return LayoutModel(artifacts_path, accelerator_options, options)
    else:
        # Import here to avoid circular imports
        from docling_enhanced.models.enhanced_layout_model import EnhancedLayoutModel
        _log.info("Using EnhancedLayoutModel with ONNX auto-detection")
        return EnhancedLayoutModel(artifacts_path, accelerator_options, options)


def create_enhanced_table_model(
    enabled: bool,
    artifacts_path: Optional[Path],
    options: TableStructureOptions,
    accelerator_options: AcceleratorOptions,
    force_original: bool = False
) -> BasePageModel:
    """
    Create an enhanced table structure model with ONNX auto-detection.
    
    Args:
        enabled: Whether the model is enabled
        artifacts_path: Path to model artifacts
        options: Table structure options
        accelerator_options: Accelerator configuration
        force_original: If True, force use of original models even if ONNX is available
        
    Returns:
        BasePageModel: Enhanced table structure model instance
    """
    if force_original or not is_onnx_models_available():
        # Import here to avoid circular imports
        from docling.models.table_structure_model import TableStructureModel
        _log.info("Using original TableStructureModel")
        return TableStructureModel(enabled, artifacts_path, options, accelerator_options)
    else:
        # Import here to avoid circular imports
        from docling_enhanced.models.enhanced_table_structure_model import EnhancedTableStructureModel
        _log.info("Using EnhancedTableStructureModel with ONNX auto-detection")
        return EnhancedTableStructureModel(enabled, artifacts_path, options, accelerator_options)


def create_enhanced_picture_classifier(
    enabled: bool,
    artifacts_path: Optional[Path],
    accelerator_options: AcceleratorOptions,
    force_original: bool = False
) -> BaseItemAndImageEnrichmentModel:
    """
    Create an enhanced document picture classifier with ONNX auto-detection.
    
    Args:
        enabled: Whether the classifier is enabled
        artifacts_path: Path to model artifacts
        accelerator_options: Accelerator configuration
        force_original: If True, force use of original models even if ONNX is available
        
    Returns:
        BaseItemAndImageEnrichmentModel: Enhanced document picture classifier instance
    """
    if force_original or not is_onnx_models_available():
        # Import here to avoid circular imports
        from docling.models.document_picture_classifier import (
            DocumentPictureClassifier, 
            DocumentPictureClassifierOptions
        )
        options = DocumentPictureClassifierOptions()
        _log.info("Using original DocumentPictureClassifier")
        return DocumentPictureClassifier(enabled, artifacts_path, options, accelerator_options)
    else:
        options = EnhancedDocumentPictureClassifierOptions()
        _log.info("Using EnhancedDocumentPictureClassifier with ONNX auto-detection")
        return EnhancedDocumentPictureClassifier(enabled, artifacts_path, options, accelerator_options)


def get_model_info() -> dict:
    """
    Get information about available models and ONNX support.
    
    Returns:
        dict: Information about model availability and ONNX support
    """
    info = {
        "onnx_available": is_onnx_models_available(),
        "onnx_providers": get_onnx_providers(),
        "enhanced_models": {
            "layout": "EnhancedLayoutModel",
            "table_structure": "EnhancedTableStructureModel", 
            "picture_classifier": "EnhancedDocumentPictureClassifier"
        }
    }
    
    if info["onnx_available"]:
        try:
            import docling_onnx_models
            info["onnx_version"] = getattr(docling_onnx_models, '__version__', 'unknown')
        except:
            info["onnx_version"] = 'unknown'
    
    return info


def configure_enhanced_pipeline(
    accelerator_options: AcceleratorOptions,
    artifacts_path: Optional[Path] = None,
    layout_options: Optional[LayoutOptions] = None,
    table_options: Optional[TableStructureOptions] = None,
    enable_table_structure: bool = True,
    enable_picture_classifier: bool = True,
    force_original: bool = False
) -> dict:
    """
    Configure a complete enhanced processing pipeline with ONNX auto-detection.
    
    Args:
        accelerator_options: Accelerator configuration
        artifacts_path: Path to model artifacts
        layout_options: Layout model options
        table_options: Table structure options
        enable_table_structure: Whether to enable table structure model
        enable_picture_classifier: Whether to enable picture classifier
        force_original: If True, force use of original models
        
    Returns:
        dict: Dictionary containing configured model instances
    """
    # Set defaults
    if layout_options is None:
        layout_options = LayoutOptions()
    if table_options is None:
        table_options = TableStructureOptions()
    
    pipeline = {}
    
    # Layout model (always enabled)
    pipeline["layout"] = create_enhanced_layout_model(
        artifacts_path=artifacts_path,
        accelerator_options=accelerator_options,
        options=layout_options,
        force_original=force_original
    )
    
    # Table structure model (optional)
    pipeline["table_structure"] = create_enhanced_table_model(
        enabled=enable_table_structure,
        artifacts_path=artifacts_path,
        options=table_options,
        accelerator_options=accelerator_options,
        force_original=force_original
    )
    
    # Picture classifier (optional)
    pipeline["picture_classifier"] = create_enhanced_picture_classifier(
        enabled=enable_picture_classifier,
        artifacts_path=artifacts_path,
        accelerator_options=accelerator_options,
        force_original=force_original
    )
    
    # Add metadata
    pipeline["_metadata"] = {
        "onnx_available": is_onnx_models_available(),
        "onnx_providers": get_onnx_providers(),
        "force_original": force_original,
        "accelerator_options": accelerator_options
    }
    
    return pipeline


class EnhancedModelFactory:
    """
    Factory class for creating enhanced models with consistent configuration.
    """
    
    def __init__(
        self, 
        accelerator_options: AcceleratorOptions,
        artifacts_path: Optional[Path] = None,
        force_original: bool = False
    ):
        """
        Initialize the enhanced model factory.
        
        Args:
            accelerator_options: Accelerator configuration to use for all models
            artifacts_path: Base path for model artifacts
            force_original: If True, force use of original models
        """
        self.accelerator_options = accelerator_options
        self.artifacts_path = artifacts_path
        self.force_original = force_original
        self._onnx_available = is_onnx_models_available()
        
        if self._onnx_available and not force_original:
            _log.info("EnhancedModelFactory: ONNX models available and will be used when beneficial")
        else:
            _log.info("EnhancedModelFactory: Using original models only")
    
    def create_layout_model(self, options: Optional[LayoutOptions] = None) -> BasePageModel:
        """Create enhanced layout model."""
        if options is None:
            options = LayoutOptions()
        return create_enhanced_layout_model(
            self.artifacts_path, 
            self.accelerator_options, 
            options, 
            self.force_original
        )
    
    def create_table_model(
        self, 
        enabled: bool = True,
        options: Optional[TableStructureOptions] = None
    ) -> BasePageModel:
        """Create enhanced table structure model."""
        if options is None:
            options = TableStructureOptions()
        return create_enhanced_table_model(
            enabled,
            self.artifacts_path, 
            options, 
            self.accelerator_options,
            self.force_original
        )
    
    def create_picture_classifier(self, enabled: bool = True) -> BaseItemAndImageEnrichmentModel:
        """Create enhanced document picture classifier."""
        return create_enhanced_picture_classifier(
            enabled,
            self.artifacts_path,
            self.accelerator_options,
            self.force_original
        )
    
    def get_info(self) -> dict:
        """Get factory configuration info."""
        return {
            "onnx_available": self._onnx_available,
            "force_original": self.force_original,
            "artifacts_path": str(self.artifacts_path) if self.artifacts_path else None,
            "accelerator_options": self.accelerator_options
        }