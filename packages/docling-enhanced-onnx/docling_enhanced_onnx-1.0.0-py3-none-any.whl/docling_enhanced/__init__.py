"""
Docling Enhanced Models

Enhanced Docling models with ONNX auto-detection and air-gapped deployment support.

This package provides drop-in replacements for docling models that automatically
detect and use ONNX variants when available, with graceful fallback to original
models. Supports air-gapped deployment with local model artifacts.

Key Features:
- Auto-detection of ONNX model availability
- Intelligent execution provider selection (CoreML, CUDA, CPU)
- Air-gapped deployment support
- 100% API compatibility with original docling models
- Factory pattern for consistent model configuration
- Graceful fallback behavior

Usage:
    # Drop-in replacement
    from docling_enhanced.models import EnhancedLayoutModel, EnhancedTableStructureModel
    
    # Factory pattern
    from docling_enhanced.utils import EnhancedModelFactory
    
    # Direct utilities
    from docling_enhanced import is_onnx_available, get_optimal_providers
"""

try:
    from ._version import __version__
except ImportError:
    __version__ = "unknown"

# Import key utilities for easy access
from .utils.enhanced_model_utils import (
    is_onnx_models_available as is_onnx_available,
    get_onnx_providers as get_optimal_providers,
    get_model_info,
    EnhancedModelFactory,
    configure_enhanced_pipeline,
)

# Import enhanced models
from .models.enhanced_layout_model import EnhancedLayoutModel
from .models.enhanced_table_structure_model import EnhancedTableStructureModel
from .models.enhanced_document_picture_classifier import (
    EnhancedDocumentPictureClassifier,
    EnhancedDocumentPictureClassifierOptions,
)

__all__ = [
    "__version__",
    # Core utilities
    "is_onnx_available",
    "get_optimal_providers", 
    "get_model_info",
    # Factory and configuration
    "EnhancedModelFactory",
    "configure_enhanced_pipeline",
    # Enhanced models
    "EnhancedLayoutModel",
    "EnhancedTableStructureModel", 
    "EnhancedDocumentPictureClassifier",
    "EnhancedDocumentPictureClassifierOptions",
]