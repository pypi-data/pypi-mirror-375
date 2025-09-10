# Publishing to PyPI

This document describes how to publish the kft package to PyPI.

## Prerequisites

1. Install required tools:
   ```bash
   pip install twine
   ```

2. Set up PyPI credentials with project-scoped tokens (recommended):
   
   **Step 1: Create the project on PyPI first**
   - Use a global API token for the initial upload
   - This reserves the project name and enables scoped tokens
   
   **Step 2: Create project-scoped API token** 
   - Go to [PyPI Account Settings](https://pypi.org/manage/account/)
   - Click "Add API token"
   - Set scope to "Project: kfulltree" (available after first upload)
   - Copy the project-scoped token
   
   **Step 3: Configure credentials in `~/.pypirc`:**
   ```ini
   [distutils]
   index-servers = 
       pypi
       testpypi

   [pypi]
   username = __token__
   password = <your-project-scoped-pypi-token>

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = <your-testpypi-token>
   ```

   **Why use project-scoped tokens?**
   - More secure - token only works for this specific project
   - Limits blast radius if token is compromised
   - Can be revoked independently of other projects

## Building the Package

1. Update version number in `pyproject.toml`
2. Build the package:
   ```bash
   uv build
   ```
3. Verify the build artifacts in `dist/`:
   - `kft-<version>.tar.gz` (source distribution)
   - `kft-<version>-py3-none-any.whl` (wheel)

## Publishing

### Initial Release (First Time Only)

For the very first release to create the project and enable scoped tokens:

1. **Use global API token** for initial upload:
   ```bash
   # Build the package
   uv build
   
   # Upload with global token (configure in ~/.pypirc first)
   twine upload dist/*
   ```

2. **Create project-scoped token** (see Prerequisites section)

3. **Update ~/.pypirc** with the new project-scoped token

### Subsequent Releases

Once the project exists and you have a scoped token:

#### Test Publishing (Recommended First)

1. Upload to TestPyPI:
   ```bash
   python scripts/upload_to_pypi.py --test
   ```

2. Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ kfulltree
   ```

#### Production Publishing

1. Upload to PyPI:
   ```bash
   python scripts/upload_to_pypi.py
   ```

2. Test installation:
   ```bash
   pip install kfulltree
   ```

## Manual Publishing

If you prefer to use twine directly:

```bash
# For TestPyPI
twine upload --repository testpypi dist/*

# For PyPI  
twine upload dist/*
```

## Post-Publishing

1. Create a git tag for the release:
   ```bash
   git tag v<version>
   git push origin v<version>
   ```

2. Update the version number for the next development cycle

## Package Information

- **Package Name**: kfulltree
- **Description**: Python implementation of the k-Full Tree (kFT) algorithm for geo-referenced time-series data summarization
- **License**: MIT
- **Python Version**: >=3.13
- **Dependencies**: networkx>=3.5, numpy>=2.3.2

## Troubleshooting

### Common Issues

1. **Build fails**: Check `pyproject.toml` syntax and ensure all files are in place
2. **Upload fails**: Verify credentials and package name availability
3. **Import fails after install**: Check package structure and `__init__.py` exports

### Getting Help

- PyPI Documentation: https://packaging.python.org/
- Twine Documentation: https://twine.readthedocs.io/
- Packaging Tutorial: https://packaging.python.org/tutorials/packaging-projects/