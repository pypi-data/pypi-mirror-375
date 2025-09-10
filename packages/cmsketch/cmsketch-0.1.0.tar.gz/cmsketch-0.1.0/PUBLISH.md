# Publishing to PyPI Guide

This guide shows how to publish the `cmsketch` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [Test PyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **Install Publishing Tools**:
   ```bash
   uv add --group dev build twine
   # Or globally: uv tool install build twine
   ```

## Step-by-Step Publishing Process

### 1. Prepare Your Package

**Check your README.md exists and is informative**:
```bash
ls README.md  # Should exist with good documentation
```

**Ensure your package builds correctly**:
```bash
# Test the C++ build
uv run python -m build
```

### 2. Create API Tokens

**For Test PyPI**:
1. Go to https://test.pypi.org/manage/account/token/
2. Create a new API token with scope "Entire account"
3. Save the token (starts with `pypi-`)

**For Production PyPI**:
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token with scope "Entire account" 
3. Save the token

### 3. Configure Authentication

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PRODUCTION_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

### 4. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/

# Build source distribution and wheel
uv run python -m build

# Check what was created
ls dist/
# Should see: cmsketch-0.1.0.tar.gz and cmsketch-0.1.0-*.whl
```

### 5. Test Upload to Test PyPI

```bash
# Upload to Test PyPI first
uv run python -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
uv add --index-url https://test.pypi.org/simple/ cmsketch
```

### 6. Upload to Production PyPI

**Only after testing works!**

```bash
# Upload to production PyPI
uv run python -m twine upload dist/*
```

## Version Management

### Updating Versions

Edit `pyproject.toml`:
```toml
version = "0.1.1"  # Increment version
```

### Version Naming Convention
- `0.1.0` - Initial release
- `0.1.1` - Bug fixes
- `0.2.0` - New features
- `1.0.0` - Stable API

## Common Issues & Solutions

### 1. Build Failures
```bash
# Install missing build dependencies
uv add --group dev scikit-build-core pybind11

# Check CMake is available
cmake --version
```

### 2. C++ Compilation Issues
```bash
# Make sure you have a C++ compiler
# On macOS: xcode-select --install
# On Ubuntu: sudo apt install build-essential
```

### 3. Upload Errors

**"File already exists"**: You can't upload the same version twice
```bash
# Increment version in pyproject.toml, then rebuild
uv run python -m build
uv run python -m twine upload dist/*
```

**Authentication errors**: Check your API tokens in `~/.pypirc`

### 4. Installation Test
```bash
# Create fresh environment to test
uv venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows
uv pip install cmsketch

# Test it works
uv run python -c "from cmsketch import CountMinSketchStr; print('Success!')"
```

## Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add your PyPI API token as a GitHub secret named `PYPI_API_TOKEN`.

## Quick Reference Commands

```bash
# Full publish workflow
rm -rf dist/ build/
uv run python -m build
uv run python -m twine upload --repository testpypi dist/*  # Test first
uv run python -m twine upload dist/*                        # Then production

# Test installation
uv add cmsketch
uv run python -c "from cmsketch import CountMinSketchStr; sketch = CountMinSketchStr(1000, 5); print('Works!')"
```

## Package URL After Publishing

Your package will be available at:
- **PyPI**: https://pypi.org/project/cmsketch/
- **Installation**: `pip install cmsketch`
