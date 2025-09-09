# Changelog

All notable changes to the timestrader-preprocessing package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- TestPyPI staging environment for safer releases
- Package usage analytics and monitoring
- Automated security scanning for dependencies
- Enhanced Jupyter notebook integration

## [1.0.6] - 2025-09-09

### Changed
- **BREAKING**: Updated NumPy dependency to support NumPy 2.x (`numpy>=1.21.0,<3.0.0`)
- Improved compatibility with latest Google Colab environments
- Enhanced dependency management for future-proof installations

### Fixed
- Resolved `cannot import name '_center' from 'numpy._core.umath'` error with NumPy 2.x
- Fixed package compatibility issues in Google Colab with latest NumPy versions

### Technical Details
- Updated dependency specification to support both NumPy 1.x and 2.x
- Tested compatibility with Google Colab's latest NumPy installations
- Maintained backward compatibility with existing NumPy 1.x environments

## [1.0.3] - 2025-09-03

### Fixed
- **Google Colab Compatibility**: Resolved import errors in Google Colab environment
- **API Simplification**: Streamlined API to use `HistoricalProcessor` as main entry point
- **Method Alignment**: Fixed method signatures to match actual implementation
- **Import Structure**: Corrected package imports to prevent ModuleNotFoundError

### Changed
- **Simplified API**: Consolidated data processing through `HistoricalProcessor` class
- **Method Names**: Standardized method naming for better consistency
- **Error Handling**: Improved error messages for missing dependencies
- **Documentation**: Updated API documentation to reflect actual implementation

### Technical Details
- Fixed TimesNet training notebook compatibility issues
- Resolved `UnifiedDataProcessor` import errors (class didn't exist in package)
- Corrected method calls: `validate_data()`, `calculate_indicators()`, `normalize_data()`, `generate_training_sequences()`
- Streamlined workflow: Raw Data → Indicators → Normalization → Training Sequences

## [1.0.2] - 2025-09-03

### Fixed
- **Colab Dependencies**: Resolved numpy version compatibility issues
- **Import Performance**: Optimized package loading time in Colab environment

## [1.0.1] - 2025-09-02

### Fixed
- **Package Structure**: Corrected package directory structure for PyPI distribution
- **Dependencies**: Fixed version constraints for Google Colab compatibility

## [1.0.0] - 2025-09-02

### Added
- Initial release of timestrader-preprocessing package
- Historical data processing pipeline for Google Colab
- Technical indicators calculation (VWAP, RSI, ATR, EMA9, EMA21, Stochastic)
- Z-score normalization with rolling window support
- Data validation and quality scoring system
- Parameter export functionality for production consistency
- Google Colab environment detection and optimization
- CPU-only dependencies for Colab compatibility
- Real-time processing components for production integration
- Comprehensive test suite with multiple test categories
- Package size optimization (< 50MB target)
- Fast import performance (< 10 seconds)
- Memory-efficient design (< 100MB overhead)

### Package Structure
- `timestrader_preprocessing.historical`: Historical data processing
- `timestrader_preprocessing.realtime`: Real-time processing components
- `timestrader_preprocessing.common`: Shared models and utilities
- `timestrader_preprocessing.config`: Configuration management

### Dependencies
- Core: pandas>=1.5.0, numpy>=1.21.0, pydantic>=1.10.0, pyyaml>=6.0
- Colab extras: matplotlib>=3.5.0, jupyter>=1.0.0, ipywidgets>=8.0.0
- Production extras: redis>=4.5.0, psutil>=5.9.0, fastapi>=0.100.0

### Documentation
- Comprehensive README with usage examples
- API documentation for all public functions
- Google Colab integration guide
- Performance benchmarks and targets
- Development setup instructions

### Testing
- Unit tests for core functionality
- Integration tests for data processing workflows  
- Colab-specific compatibility tests
- Package installation and import validation
- Performance benchmark tests

### Security
- No embedded secrets or sensitive information
- Dependency security validation
- Package integrity with checksums
- Secure PyPI token management setup

---

## Version History

- **1.0.0**: Initial release with core functionality
- Future versions will follow semantic versioning:
  - **MAJOR**: Incompatible API changes
  - **MINOR**: Backward-compatible functionality additions
  - **PATCH**: Backward-compatible bug fixes

## Migration Guide

### From TimeStrader Main Package

If migrating from using TimeStrader main package modules directly:

```python
# Old (direct module usage)
from src.timestrader.data.historical_processor import HistoricalProcessor

# New (pip package)
from timestrader_preprocessing import HistoricalProcessor
```

### Dependency Changes

The package uses more conservative dependency version ranges for better compatibility:

- pandas: `>=1.5.0,<3.0.0` (was `^2.0.0`)
- numpy: `>=1.21.0,<2.0.0` (was `^1.24.0`)
- pydantic: `>=1.10.0,<3.0.0` (was `^2.0.0`)

## Support

For questions about specific versions or upgrade paths:
- Check the [README](README.md) for current usage patterns
- Open an issue at https://github.com/timestrader/timestrader-v05/issues
- Review test files for examples of new functionality