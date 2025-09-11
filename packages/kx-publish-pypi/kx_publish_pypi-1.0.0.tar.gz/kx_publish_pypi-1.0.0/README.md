# 🚀 KX-Publish-PyPI

[![PyPI version](https://badge.fury.io/py/kx_publish_pypi.svg)](https://pypi.org/project/kx_publish_pypi/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/Khader-X/kx-publish-pypi/ci.yml)](https://github.com/Khader-X/kx-publish-pypi/actions)
[![Code Coverage](https://img.shields.io/codecov/c/github/Khader-X/kx-publish-pypi)](https://codecov.io/gh/Khader-X/kx-publish-pypi)
[![Website](https://img.shields.io/badge/Website-KhaderX.com-blue.svg)](https://KhaderX.com/)

> ✨ **A beautiful, intelligent CLI tool to streamline Python package publishing to PyPI and TestPyPI**

KX-Publish-PyPI is an interactive command-line interface that simplifies the entire process of preparing, building, and publishing Python packages. With **enhanced version detection** supporting all modern build backends, rich visual feedback, intelligent error handling, and secure token management, it makes package publishing as smooth as a breeze.

🎯 **Enhanced Version Detection System** - Works with **ANY** modern Python package configuration including setuptools, scikit-build-core, setuptools-scm, flit, hatchling, and more!

## 🌟 Features

- 🎨 **Beautiful Interface**: Rich, colorful output with progress bars and interactive prompts
- 🔍 **Smart Pre-checks**: Validates your package structure, version, and configuration before publishing
- 🔧 **Enhanced Version Detection**: Comprehensive support for all modern Python packaging approaches
  - ✅ **Static versions** in pyproject.toml
  - ✅ **Dynamic versions** with setuptools, scikit-build-core, setuptools-scm, flit, hatchling
  - ✅ **Intelligent fallback system** with 5-stage detection process
  - ✅ **Rich diagnostics** showing detection method, source, and confidence scoring
- 🔐 **Secure Token Management**: Uses your system's keyring for safe API token storage
- 📦 **Dual Publishing**: Supports both TestPyPI and PyPI with intelligent workflows
- 🚀 **Interactive Workflow**: Guided experience from check to publish
- 📈 **Version Management**: Smart version bumping (patch, minor, major)
- 🛠️ **Build Integration**: Works with modern build backends (setuptools, flit, hatchling, etc.)
- 🎯 **CI/CD Ready**: Perfect for automation and continuous delivery pipelines

## 🆕 What's New in Version 1.0.0

### 🎊 **Major Release - Complete KX Rebranding**
- **✅ New Package Name**: `kx_publish_pypi` (upgraded from legacy naming)
- **✅ New CLI Command**: `kx-publish-pypi` 
- **✅ Enhanced Repository**: Now at [github.com/Khader-X/kx-publish-pypi](https://github.com/Khader-X/kx-publish-pypi)
- **✅ Website Integration**: Visit [KhaderX.com](https://KhaderX.com/) for more tools and resources

### 🚀 **Enhanced Version Detection System**
- **✅ Universal compatibility** with all modern Python build backends
- **✅ Intelligent 5-stage fallback** detection process- **✅ Rich diagnostics** showing detection method, source, and confidence
- **✅ Programmatic API** for advanced integration
- **✅ Comprehensive support** for dynamic versioning configurations

### 📊 **Enhanced Output Example**
```
🔢 Version .......................... ✅ (v1.0.0 (setuptools_dynamic_attr) dynamic backend:setuptools)
```
This shows you:
- **Version**: 1.0.0
- **Detection Method**: setuptools_dynamic_attr  
- **Type**: dynamic versioning
- **Build Backend**: setuptools

## 🛠️ Installation

### From PyPI (Recommended)
```bash
pip install kx-publish-pypi
```

### Verify Installation
```bash
kx-publish-pypi --version
```

### From GitHub (Latest Development)
```bash
# Install from latest release
pip install git+https://github.com/Khader-X/kx-publish-pypi.git@main

# Install from specific version
pip install git+https://github.com/Khader-X/kx-publish-pypi.git@v1.0.0
```

### From Source (Development)
```bash
git clone https://github.com/Khader-X/kx-publish-pypi.git
cd kx-publish-pypi
pip install -e .
```

### Requirements
- Python 3.9+
- `twine` for uploads
- `build` for package building
- `keyring` for secure token storage

## 🚀 Quick Start

1. **Install the package**
   ```bash
   pip install kx-publish-pypi
   ```

2. **Set up your API tokens**
   ```bash
   kx-publish-pypi setup-tokens
   ```

3. **Publish your package**
   ```bash
   kx-publish-pypi run
   ```

That's it! The guided workflow will handle everything else.

## 📖 Usage

### Interactive Publishing (Recommended)
```bash
kx-publish-pypi run
```

This command provides a complete guided experience:
- ✅ Runs pre-publish checks with enhanced version detection
- 🔑 Manages API token configuration
- 📈 Offers version bumping options
- 🏗️ Builds your package distributions
- 📤 Publishes to TestPyPI and/or PyPI

### Individual Commands
```bash
# Run pre-publish checks with enhanced version detection
kx-publish-pypi check

# Bump version
kx-publish-pypi bump patch

# Publish to TestPyPI only
kx-publish-pypi publish-test

# Publish to PyPI only
kx-publish-pypi publish-prod
```

### Programmatic API

KX-Publish-PyPI exposes a powerful programmatic API for version detection:

```python
from kx_publish_pypi import detect_package_version, get_package_version
from pathlib import Path

# Simple version detection (legacy interface)
version = get_package_version(Path("."))
print(f"Version: {version}")

# Enhanced detection with full diagnostics
result = detect_package_version(Path("."))
if result.version_info:
    info = result.version_info
    print(f"Version: {info.version}")
    print(f"Method: {info.method}")
    print(f"Backend: {info.build_backend}")
    print(f"Confidence: {info.confidence}%")
    print(f"Source: {info.source}")
else:
    print("Version detection failed")
    for diagnostic in result.diagnostics:
        print(f"Tried {diagnostic.method}: {diagnostic.error}")
```

## 📋 Command Reference

| Command | Description |
|---------|-------------|
| `kx-publish-pypi --version` | Show CLI version |
| `kx-publish-pypi check` | Run interactive pre-publish checks |
| `kx-publish-pypi bump [patch\|minor\|major]` | Bump package version |
| `kx-publish-pypi setup-tokens` | Configure API tokens interactively |
| `kx-publish-pypi update-tokens` | Update existing tokens |
| `kx-publish-pypi run` | Complete guided publishing workflow |
| `kx-publish-pypi publish-test` | Publish to TestPyPI |
| `kx-publish-pypi publish-prod` | Publish to PyPI |

### Command Options

#### Token Setup
```bash
# Interactive setup
kx-publish-pypi setup-tokens

# Non-interactive setup
kx-publish-pypi setup-tokens --test-token YOUR_TEST_TOKEN --prod-token YOUR_PROD_TOKEN
```

#### Version Bumping
```bash
kx-publish-pypi bump patch  # 1.0.0 → 1.0.1
kx-publish-pypi bump minor  # 1.0.1 → 1.1.0
kx-publish-pypi bump major  # 1.1.0 → 2.0.0
```

## 🔐 Token Management

KX-Publish-PyPI securely stores your PyPI API tokens using your system's keyring:

- **TestPyPI**: Stored as `kx-publish-testpypi`
- **PyPI**: Stored as `kx-publish-pypi`

Tokens are encrypted and stored safely in your system's credential manager (Windows Credential Manager, macOS Keychain, or Linux Secret Service).## 🔧 Enhanced Version Detection

KX-Publish-PyPI features a **comprehensive version detection system** that handles all modern Python packaging approaches:

### Supported Build Backends
- ✅ **setuptools** (static and dynamic versions)
- ✅ **setuptools-scm** (Git-based versioning)
- ✅ **scikit-build-core** (CMake integration)
- ✅ **flit** (simple Python packaging)
- ✅ **hatchling** (modern Python packaging)
- ✅ **pdm-backend** (PDM packaging)
- ✅ **poetry-core** (Poetry packaging)

### Detection Methods
1. **Static pyproject.toml version**
2. **Dynamic setuptools attributes**
3. **setuptools-scm Git tags**
4. **scikit-build-core dynamic versioning**
5. **Package attribute inspection**

### Usage Tips
1. Ensure your `pyproject.toml` is properly configured
2. For dynamic versioning, make sure your version module is importable
3. For Git-based versioning, ensure you have proper tags
4. Use enhanced diagnostics: `kx-publish-pypi check` shows detailed detection attempts

## 💡 Examples

### Basic Publishing Workflow
```bash
# Check your package
kx-publish-pypi check

# Bump version if needed
kx-publish-pypi bump patch

# Set up tokens (first time only)
kx-publish-pypi setup-tokens

# Test publish
kx-publish-pypi publish-test

# Publish to production
kx-publish-pypi publish-prod
```

### Development Workflow
```bash
# One-command publishing
kx-publish-pypi run

# Check with verbose output
kx-publish-pypi run --verbose
```

## 🚀 CI/CD Integration

KX-Publish-PyPI works great with CI/CD pipelines:

### GitHub Actions Example
```yaml
- name: Publish to PyPI
  run: |
    pip install kx-publish-pypi
    kx-publish-pypi setup-tokens --test-token ${{ secrets.TEST_PYPI_TOKEN }} --prod-token ${{ secrets.PYPI_TOKEN }}
    kx-publish-pypi publish-prod
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup
```bash
git clone https://github.com/Khader-X/kx-publish-pypi.git
cd kx-publish-pypi
pip install -e .
```

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
We use `black` for code formatting and `flake8` for linting.

## 📚 Documentation

- 📖 **[Enhanced Version Detection Guide](docs/ENHANCED_VERSION_DETECTION.md)**: Complete guide to the new version detection system
- 🧪 **[Test Examples](tests/test_enhanced_version_detection.py)**: Comprehensive test suite demonstrating all capabilities
- 💻 **[API Usage Examples](tests/example_api_usage.py)**: Programmatic usage examples
- 📋 **[Releasing Guide](RELEASING.md)**: How to release new versions of this package

## 🆘 Support & Community

- 🌐 **Website**: [KhaderX.com](https://KhaderX.com/) - Explore more tools and resources
- 🐛 **Issues**: [GitHub Issues](https://github.com/Khader-X/kx-publish-pypi/issues)
- 📖 **Documentation**: [GitHub Wiki](https://github.com/Khader-X/kx-publish-pypi/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Khader-X/kx-publish-pypi/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ❤️ Acknowledgments

<div align="center">
  <a href="https://github.com/Khader-X/kx-publish-pypi">⭐ Star this repo</a> •
  <a href="https://pypi.org/project/kx_publish_pypi/">📦 View on PyPI</a> •
  <a href="https://KhaderX.com/">🌐 Visit KhaderX.com</a>
</div>

---

<div align="center">
  <strong>Made with ❤️ by <a href="https://KhaderX.com/">KhaderX</a></strong>
</div>