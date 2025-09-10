# Build and Publishing Scripts

This directory contains automation scripts for building and publishing the huoshui-pdf-converter package to PyPI.

## Scripts

### 🏗️ build.py

Automated build script that handles the complete build process:

- Cleans previous build artifacts
- Validates project structure and version consistency
- Installs build dependencies
- Builds wheel and source distributions
- Validates built packages
- Tests local installation
- Generates build report

**Usage:**

```bash
python scripts/build.py
```

### 📤 upload.py

Interactive PyPI upload script with safety features:

- Supports both TestPyPI and production PyPI
- Validates package metadata before upload
- Checks for credentials
- Tests installation after upload
- Generates upload report

**Usage:**

```bash
# Upload to TestPyPI first (recommended)
python scripts/upload.py --test

# Upload to TestPyPI and test installation
python scripts/upload.py --test --test-install

# Upload directly to production PyPI
python scripts/upload.py

# Skip confirmation prompts
python scripts/upload.py --yes
```

**Options:**

- `--test`: Upload to TestPyPI first
- `--test-only`: Only upload to TestPyPI
- `--test-install`: Test installation after upload
- `--skip-existing`: Skip files that already exist
- `--yes, -y`: Skip confirmation prompts
- `--force, -f`: Force upload even if validation fails

### 🔢 version_bump.py

Version management script with semantic versioning support:

- Updates version in all relevant files
- Supports major, minor, and patch bumps
- Can create and push git tags
- Interactive and CLI modes

**Usage:**

```bash
# Interactive mode
python scripts/version_bump.py

# Bump patch version (bug fixes)
python scripts/version_bump.py --bump patch

# Bump minor version (new features)
python scripts/version_bump.py --bump minor

# Bump major version (breaking changes)
python scripts/version_bump.py --bump major

# Set specific version
python scripts/version_bump.py --version 2.0.0

# Create git tag after version update
python scripts/version_bump.py --bump patch --tag

# Show current version info
python scripts/version_bump.py --show
```

## Complete Publishing Workflow

1. **Update version** (if needed):

   ```bash
   python scripts/version_bump.py --bump patch
   ```

2. **Build the package**:

   ```bash
   python scripts/build.py
   ```

3. **Upload to TestPyPI** (recommended):

   ```bash
   python scripts/upload.py --test --test-install
   ```

4. **Upload to production PyPI**:
   ```bash
   python scripts/upload.py
   ```

## Prerequisites

### Required Python packages

The scripts will automatically install required packages:

- `build`: For building packages
- `twine`: For uploading to PyPI
- `wheel`: For building wheel distributions
- `tomli_w`: For updating TOML files (version_bump.py)

### PyPI Credentials

You need to configure PyPI credentials before uploading:

**Option 1: Environment Variables**

```bash
export PYPI_TOKEN=pypi-YOUR_TOKEN_HERE
export TESTPYPI_TOKEN=pypi-YOUR_TOKEN_HERE
```

**Option 2: ~/.pypirc file**

```ini
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

## Troubleshooting

### Build failures

- Ensure all required files exist (pyproject.toml, README.md, LICENSE)
- Check version consistency across files
- Run `python scripts/build.py` to see detailed error messages

### Upload failures

- Verify credentials are configured correctly
- Check if the version already exists on PyPI
- Use `--skip-existing` to skip already uploaded files
- Try TestPyPI first with `--test` flag

### Version conflicts

- Use `version_bump.py` to ensure version consistency
- Check that version follows semantic versioning (x.y.z)

## Notes

- Always test on TestPyPI before uploading to production
- The scripts include safety checks and confirmation prompts
- Build artifacts are placed in the `dist/` directory
- Reports are generated as JSON files in the project root
