<div align="center">
  <img src="logo/logo-2-1.png" alt="KX-Publish-PyPI Logo" width="200"/>
</div>

<div align="center">
  <h1>🚀 KX-Publish-PyPI</h1>
  <p><em>The Professional CLI Tool for Python Package Publishing</em></p>
</div>

<div align="center">
  <a href="https://pypi.org/project/kx_publish_pypi/"><img src="https://badge.fury.io/py/kx_publish_pypi.svg" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/Khader-X/kx-publish-pypi/actions"><img src="https://img.shields.io/github/actions/workflow/status/Khader-X/kx-publish-pypi/ci.yml" alt="Build Status"></a>
  <a href="https://github.com/Khader-X/kx-publish-pypi/stargazers"><img src="https://img.shields.io/github/stars/Khader-X/kx-publish-pypi?style=social" alt="GitHub stars"></a>
</div>

<div align="center">
  <h3>⚡ <strong>Publish Python packages to PyPI in under 30 seconds!</strong> ⚡</h3>
  <p><strong>Version 1.0.0</strong> | <strong>Author: ABUELTAYEF Khader</strong> | <strong>Python 3.9+</strong></p>
</div>

---

## 🎯 **Why Choose KX-Publish-PyPI?**

<div align="center">

| Feature | **KX-Publish-PyPI** | Traditional Methods |
|---------|------------------|-------------------|
| **Setup Time** | ⚡ 30 seconds | ⏰ 30+ minutes |
| **Security** | 🔐 System keyring | 📝 Plain text files |
| **User Experience** | 🎨 Rich CLI + Progress bars | 📟 Basic terminal output |
| **Error Handling** | 🛡️ Smart validation | ❌ Manual debugging |
| **Version Management** | 📈 Intelligent bumping | 🔢 Manual editing |
| **Build Backend Support** | 🛠️ All modern backends | ⚙️ Limited support |

</div>

---

## 💻 **Installation**

### ⚡ Quick Install
```bash
pip install kx-publish-pypi
```

### ✅ Verify Installation
```bash
kx-publish-pypi --version
```

### 🎬 Installation Demo
<div align="center">
  <img src="screenshots/kx-publish-pypi_video_installation_version.gif" alt="Installation & Version Check Demo" width="600"/>
</div>

---

## 💻 **Account Setup & Token Generation**

<div align="center">
  <h3>🔑 Get Started with PyPI Publishing</h3>
</div>

### 1. **Create PyPI Account**
1. 🌐 Visit [pypi.org](https://pypi.org/)
2. 📝 Click "Register" in the top right
3. ✉️ Fill out the registration form
4. ✅ Verify your email address

### 2. **Create TestPyPI Account**
1. 🌐 Visit [test.pypi.org](https://test.pypi.org/)
2. 📝 Click "Register" in the top right
3. ✉️ Fill out the registration form
4. ✅ Verify your email address

### 3. **Generate API Tokens**

#### **For PyPI Production:**
1. 🔑 Log in to [pypi.org](https://pypi.org/)
2. ⚙️ Go to **Account Settings** → **API tokens**
3. ➕ Click **"Add API token"**
4. 🏷️ Give it a name (e.g., "kx-publish-pypi")
5. 💾 **Copy & Save the token** (you won't see it again!)

#### **For TestPyPI:**
1. 🔑 Log in to [test.pypi.org](https://test.pypi.org/)
2. ⚙️ Go to **Account Settings** → **API tokens**
3. ➕ Click **"Add API token"**
4. 🏷️ Give it a name (e.g., "kx-publish-pypi-test")
5. 💾 Copy & Save the token

### 4. **Store Tokens Securely**
Use the CLI to store your tokens securely:
```bash
kx-publish-pypi setup-tokens
```

This will prompt you to enter your TestPyPI and PyPI tokens, which will be stored in your system's keyring.

💡 **Pro Tip:** You can also store tokens directly during the guided workflow:
```bash
kx-publish-pypi run
```

---

## 🚀 **Quick Start**

<div align="center">
  <h3>Choose Your Publishing Journey</h3>
</div>

### 🎯 **Option 1: Complete Guided Workflow (Recommended)**
```bash
kx-publish-pypi run
```
<div align="center">
  <em>✨ <strong>One command handles everything:</strong> checks, tokens, version bump, build, and publish</em>
</div>

### 🛠️ **Option 2: Individual Commands**
```bash
# 🔍 Pre-flight check your package
kx-publish-pypi check

# 🔐 Setup API tokens securely
kx-publish-pypi setup-tokens

# 📈 Bump version (patch/minor/major)
kx-publish-pypi bump patch

# 🧪 Publish to TestPyPI first
kx-publish-pypi publish-test

# 🚀 Publish to production PyPI
kx-publish-pypi publish-prod
```

---

## ✨ **Key Features**

<div align="center">

| 🎨 **Rich Interface** | Rich, colorful output with progress bars |
|----------------------|------------------------------------------|
| 🔍 **Smart Pre-checks** | Validates package structure and configuration |
| 🔐 **Secure Token Storage** | Uses system keyring for API tokens |
| 📦 **Enhanced Version Detection** | Supports all modern Python build backends |
| 🔥 **Interactive Workflow** | Guided experience from check to publish |
| 📈 **Version Management** | Intelligent version bumping |
| 🛠️ **Build Integration** | Works with setuptools, flit, hatchling, etc. |

</div>

---

## 🏗️ **Supported Build Backends**

<div align="center">

| Backend | Status | Version Detection |
|---------|--------|-------------------|
| setuptools | ✅ Full Support | `__version__` files |
| poetry | ✅ Full Support | `pyproject.toml` |
| flit | ✅ Full Support | `pyproject.toml` |
| hatchling | ✅ Full Support | `pyproject.toml` |
| pdm | ✅ Full Support | `pyproject.toml` |
| scikit-build | ✅ Full Support | Custom detection |

</div>

---

## 🚀 **Programmatic API**

```python
from kx_publish_pypi import detect_package_version
from pathlib import Path

# Enhanced version detection
result = detect_package_version(Path("."))
if result.version_info:
    print(f"📦 Version: {result.version_info.version}")
    print(f"🔧 Method: {result.version_info.method}")
```

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### 🐛 Found a Bug?
- 🐛 [Open an Issue](https://github.com/Khader-X/kx-publish-pypi/issues)
- 💡 [Suggest a Feature](https://github.com/Khader-X/kx-publish-pypi/discussions)

---

## 📄 **License**

<div align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  </a>
</div>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

## 🌐 **Connect with Us**

**🚀 Powered by [KhaderX](https://KhaderX.com/)** |
**👨‍💻 Founder: [ABUELTAYEF Khader](https://github.com/KhaderX-com)**

<div align="center">
  <a href="https://github.com/Khader-X"><img src="https://img.shields.io/badge/GitHub-Khader--X-blue?style=for-the-badge&logo=github" alt="GitHub"></a>
  <a href="https://KhaderX.com/"><img src="https://img.shields.io/badge/Website-KhaderX.com-blue?style=for-the-badge&logo=firefox" alt="Website"></a>
  <a href="https://pypi.org/user/KhaderX/"><img src="https://img.shields.io/badge/PyPI-KhaderX-orange?style=for-the-badge&logo=pypi" alt="PyPI"></a>
</div>

<div align="center">
  <h3>⭐ If you find this tool useful, please star this repo!</h3>
  <a href="https://github.com/Khader-X/kx-publish-pypi/stargazers">
    <img src="https://img.shields.io/github/stars/Khader-X/kx-publish-pypi?style=social" alt="GitHub stars">
  </a>
</div>

</div>

<div align="center">
  <img src="logo/logo-2-1.png" alt="KX-Publish-PyPI Logo" width="150"/>
</div>