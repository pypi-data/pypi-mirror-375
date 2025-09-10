# Changelog

All notable changes to RangeBar will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-09-09

### 🚀 Major Performance Improvements
- **MASSIVE Performance Boost**: Peak performance increased from 2.5M to **137M+ trades/second** (54x improvement)
- Rust implementation now processes 100M+ trades/second consistently with latest dependencies

### 🔧 Updated Dependencies (2025 Latest)
#### Rust Dependencies
- **PyO3**: Updated to 0.26.0 (latest Python bindings)
- **numpy**: Updated to 0.26.0 (latest numpy integration)
- **rayon**: Updated to 1.11.0 (latest parallel processing)
- **thiserror**: Updated to 2.0.0 (latest error handling)
- **Rust Edition**: Updated to 2024 (current for 2025)

#### Python Dependencies
- **Python**: Minimum requirement raised to 3.13+ (2025 standard)
- **numpy**: Updated to >=2.3.0 (latest stable)
- **pandas**: Updated to >=2.3.0 (latest stable)
- **pyarrow**: Updated to >=21.0.0 (latest columnar processing)
- **httpx**: Updated to >=0.28.0 (latest async HTTP)

### 🛠️ Breaking Changes
- **Python Version**: Minimum Python version raised from 3.12+ to 3.13+
- **Dependency Versions**: All dependencies updated to 2025 latest versions
- May require updating development environments to Python 3.13+

### ✨ Enhancements
- Fixed PyO3 0.26 API compatibility issues
- Updated deprecated `allow_threads` to `detach` method
- Added repository metadata to Cargo.toml (fixes build warnings)
- Comprehensive benchmark suite added for performance verification

### 🧪 Testing
- Full algorithm parity maintained between Python and Rust implementations
- Comprehensive benchmarks verify performance across 10K to 1M trade datasets
- All edge cases validated with latest dependency stack

### 📚 Documentation
- Updated README with latest dependency versions and performance metrics
- Added migration guide for upgrading from v0.1.x
- Updated installation requirements and development setup

## [0.1.1] - 2025-09-09

### 🐛 Bug Fixes
- Fixed Python source code inclusion in PyPI wheel
- Added proper maturin configuration for mixed Python/Rust projects

### 📦 Packaging
- Improved wheel building with `python-source = "src"` configuration
- Better MANIFEST.in for comprehensive file inclusion

## [0.1.0] - 2025-09-09

### 🎉 Initial Release
- **Core Algorithm**: Non-lookahead bias range bar construction
- **High Performance**: Rust core with Python bindings
- **Data Integration**: Direct Binance UM Futures aggTrades fetching
- **CLI Tools**: Complete command-line interface
- **Python API**: Easy-to-use Python interface
- **Fixed-Point Arithmetic**: Precise decimal calculations without floating-point errors

### 🔧 Features
- Range bars with configurable thresholds (default 0.8%)
- Breach tick inclusion in closing bars
- Deterministic, reproducible results
- Support for historical data fetching
- Parquet format support for efficient storage

### 📋 Dependencies
- Python 3.12+ support
- PyO3 0.22.x for Python-Rust bindings
- Modern Python data stack (numpy, pandas, pyarrow)

[0.2.0]: https://github.com/eonlabs/rangebar/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/eonlabs/rangebar/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/eonlabs/rangebar/releases/tag/v0.1.0