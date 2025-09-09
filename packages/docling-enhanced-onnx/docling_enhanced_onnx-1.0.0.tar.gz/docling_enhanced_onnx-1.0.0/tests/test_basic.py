"""
Basic tests for docling-enhanced package.
"""

import pytest


def test_package_import():
    """Test that the package can be imported."""
    import docling_enhanced
    assert hasattr(docling_enhanced, '__version__')


def test_utility_imports():
    """Test that utility functions can be imported."""
    from docling_enhanced import (
        is_onnx_available,
        get_optimal_providers,
        get_model_info,
        EnhancedModelFactory,
    )
    
    # Test basic functionality
    onnx_available = is_onnx_available()
    assert isinstance(onnx_available, bool)
    
    model_info = get_model_info()
    assert isinstance(model_info, dict)
    assert 'onnx_available' in model_info


def test_model_imports():
    """Test that enhanced models can be imported."""
    from docling_enhanced.models import (
        EnhancedLayoutModel,
        EnhancedTableStructureModel,
        EnhancedDocumentPictureClassifier,
    )
    
    # Just test that classes exist
    assert EnhancedLayoutModel is not None
    assert EnhancedTableStructureModel is not None
    assert EnhancedDocumentPictureClassifier is not None


def test_factory_creation():
    """Test that the factory can be created."""
    from docling_enhanced import EnhancedModelFactory
    from docling.datamodel.accelerator_options import AcceleratorOptions
    
    accelerator_options = AcceleratorOptions()
    factory = EnhancedModelFactory(accelerator_options)
    
    info = factory.get_info()
    assert isinstance(info, dict)
    assert 'onnx_available' in info


@pytest.mark.integration
def test_model_creation_disabled():
    """Test creating models in disabled mode (no actual model loading)."""
    from docling_enhanced import EnhancedModelFactory
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from docling.datamodel.pipeline_options import TableStructureOptions
    
    accelerator_options = AcceleratorOptions()
    factory = EnhancedModelFactory(accelerator_options)
    
    # Create models in disabled mode to avoid loading actual models
    table_model = factory.create_table_model(enabled=False)
    assert table_model is not None
    
    picture_classifier = factory.create_picture_classifier(enabled=False)
    assert picture_classifier is not None