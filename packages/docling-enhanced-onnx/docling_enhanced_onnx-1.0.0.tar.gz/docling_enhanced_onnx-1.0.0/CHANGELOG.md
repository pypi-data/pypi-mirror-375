# Changelog

All notable changes to the docling-enhanced project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-09-09

### Added
- **Enhanced Layout Model**: Drop-in replacement for docling LayoutModel with ONNX auto-detection
- **Enhanced Table Structure Model**: ONNX-accelerated table structure recognition with air-gapped support
- **Enhanced Document Picture Classifier**: Figure classification with ONNX optimization
- **EnhancedModelFactory**: Factory pattern for consistent model configuration and management
- **ONNX Auto-Detection**: Automatic detection and use of ONNX models when available
- **Hardware Acceleration**: Support for CoreML (macOS), CUDA (GPU), and CPU execution providers
- **Air-Gapped Deployment**: Complete offline deployment support with local model artifacts
- **Graceful Fallback**: Seamless degradation to original docling models when ONNX unavailable
- **Provider Optimization**: Intelligent selection of optimal execution providers based on hardware
- **Configuration Utilities**: Helper functions for model info, provider detection, and pipeline setup

### Features
- **100% API Compatibility**: Drop-in replacements for existing docling models
- **Cross-Platform Support**: Windows, macOS, and Linux compatibility
- **Multiple Python Versions**: Support for Python 3.10, 3.11, and 3.12
- **Professional Packaging**: Modern Python packaging with pyproject.toml and setuptools-scm
- **Comprehensive Testing**: Unit tests, integration tests, and performance benchmarks
- **Type Safety**: Full type hints and mypy compatibility
- **Documentation**: Comprehensive README with usage examples and troubleshooting

### Technical Details
- **Dependencies**: Compatible with docling >= 2.0.0, onnxruntime >= 1.15.0
- **Package Structure**: Clean separation of models and utilities
- **Import System**: Lazy imports for optimal performance
- **Error Handling**: Robust error handling with informative messages
- **Logging**: Structured logging for debugging and monitoring

### Performance Improvements
- **TableFormer**: Up to 75% faster inference with ONNX optimization
- **Layout Detection**: Up to 65% performance improvement on CoreML
- **Memory Efficiency**: Reduced memory footprint with quantized models
- **Batch Processing**: Optimized batch inference capabilities

### Security & Deployment
- **Air-Gapped Ready**: No internet required after initial setup
- **Local Model Support**: Complete support for local model artifacts
- **Secure Environments**: Designed for deployment in restricted environments
- **No External Dependencies**: Self-contained execution without external API calls