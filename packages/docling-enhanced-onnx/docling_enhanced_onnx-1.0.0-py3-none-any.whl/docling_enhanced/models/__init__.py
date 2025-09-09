"""
Enhanced Docling Models

Drop-in replacements for docling models with ONNX auto-detection and air-gapped support.
"""

from .enhanced_layout_model import EnhancedLayoutModel
from .enhanced_table_structure_model import EnhancedTableStructureModel
from .enhanced_document_picture_classifier import (
    EnhancedDocumentPictureClassifier,
    EnhancedDocumentPictureClassifierOptions,
)

__all__ = [
    "EnhancedLayoutModel",
    "EnhancedTableStructureModel",
    "EnhancedDocumentPictureClassifier", 
    "EnhancedDocumentPictureClassifierOptions",
]