# PyPI Publishing Workflow

This document describes the complete automated PyPI package build and publish workflow for `huoshui-fetch`.

## Overview

The workflow consists of 4 main phases:

1. **Pre-Publishing Validation** - Validate project structure and dependencies
2. **Configuration & Setup** - Install build dependencies and run quality checks
3. **Build Automation** - Build packages and run local tests
4. **Publishing & Validation** - Upload to PyPI repositories and validate

## Quick Start

### Automated Full Workflow

```bash
# Run complete workflow with TestPyPI only (recommended first run)
uv run python scripts/publish.py

# Include production PyPI upload (requires confirmation)
uv run python scripts/publish.py --include-pypi

# Bump version and publish
uv run python scripts/publish.py --version-bump patch --include-pypi
```

### Individual Scripts

```bash
# Version management
uv run python scripts/version_manager.py --check
uv run python scripts/version_manager.py --bump patch

# Build package
uv run python scripts/build.py

# Run tests
uv run python scripts/test.py

# Upload to PyPI
uv run python scripts/upload.py
```

## Workflow Details

### Phase 1: Pre-Publishing Validation

**Automatic checks:**

- ✅ Version consistency across `pyproject.toml`, `__init__.py`, and `manifest.json`
- ✅ Project structure validation (required files present)
- ✅ Dependencies availability check
- ✅ Python version compatibility

**Fixes applied:**

- Version synchronization across all files
- Missing `__version__` attribute in `__init__.py`
- Package metadata validation

### Phase 2: Configuration & Setup

**Build system:**

- ✅ Hatchling build backend (modern, PEP 517 compliant)
- ✅ Console script: `huoshui-fetch = "huoshui_fetch:main"`
- ✅ Development dependencies separated with uv

**Quality checks:**

- ✅ Ruff linting (with auto-fix)
- ✅ MyPy type checking
- ✅ Package structure validation

### Phase 3: Build Automation

**Build process:**

- ✅ Clean previous artifacts
- ✅ Install build dependencies via `uv sync`
- ✅ Generate wheel and source distributions
- ✅ Package size reporting and contents validation

**Local testing:**

- ✅ Package import validation
- ✅ Console script execution test
- ✅ MCP tools functionality test
- ✅ Build artifacts integrity check

### Phase 4: Publishing & Validation

**TestPyPI workflow:**

1. Upload to TestPyPI for validation
2. Test installation from TestPyPI
3. Validate basic functionality

**PyPI workflow:**

1. Confirm TestPyPI success
2. Interactive confirmation for production upload
3. Upload to production PyPI
4. Post-publishing validation

## Commands Reference

### Version Management

```bash
# Check version consistency
uv run python scripts/version_manager.py --check

# Bump version
uv run python scripts/version_manager.py --bump [major|minor|patch]

# Set specific version
uv run python scripts/version_manager.py --set "0.2.0"
```

### Building

```bash
# Full build with validation
uv run python scripts/build.py

# Clean artifacts only
uv run python scripts/build.py --clean-only

# Skip quality checks
uv run python scripts/build.py --skip-quality-checks
```

### Testing

```bash
# Run all tests
uv run python scripts/test.py

# Run with build
uv run python scripts/test.py --with-build

# Run specific test
uv run python scripts/test.py --test [dependencies|import|console|unit|mcp|build]
```

### Publishing

```bash
# Interactive upload (TestPyPI first)
uv run python scripts/upload.py

# Skip TestPyPI, go directly to PyPI
uv run python scripts/upload.py --no-test

# TestPyPI only
uv run python scripts/upload.py --testpypi-only
```

### Master Workflow

```bash
# Full workflow options
uv run python scripts/publish.py [OPTIONS]

# Version bump options
--version-bump [major|minor|patch]

# Quality control
--skip-quality-checks

# Publishing stages
--skip-testpypi          # Skip TestPyPI upload
--include-pypi           # Include PyPI upload
--no-test-install        # Skip installation testing

# Individual phases
--phase [validate|setup|build|publish]

# Testing only
--test-only             # Run comprehensive tests only
```

## Error Handling & Recovery

### Common Issues

**Build Failures:**

- Check dependencies: `uv sync`
- Validate metadata: `uv run python scripts/build.py`
- Fix linting errors: `uv run ruff check --fix .`

**Version Conflicts:**

- Check consistency: `uv run python scripts/version_manager.py --check`
- Synchronize versions: `uv run python scripts/version_manager.py --set "X.Y.Z"`

**Upload Failures:**

- Verify credentials are configured
- Check package name conflicts
- Validate package metadata with `twine check dist/*`

**Installation Issues:**

- Test locally: `uv run python scripts/test.py --test import`
- Check console script: `uv run python scripts/test.py --test console`
- Validate dependencies: `uv run python scripts/test.py --test dependencies`

### Recovery Steps

1. **Clean slate rebuild:**

   ```bash
   uv run python scripts/build.py --clean-only
   uv run python scripts/publish.py --phase build
   ```

2. **Version synchronization:**

   ```bash
   uv run python scripts/version_manager.py --check
   uv run python scripts/version_manager.py --set "$(python -c "import huoshui_fetch; print(huoshui_fetch.__version__)")"
   ```

3. **Full validation:**
   ```bash
   uv run python scripts/publish.py --test-only
   ```

## Prerequisites

### Required Tools

- Python 3.11+
- uv (package manager)
- twine (for PyPI upload)

### Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install twine
pip install twine

# Setup project
uv sync
```

### PyPI Credentials

Configure PyPI credentials for upload:

```bash
# Create ~/.pypirc or set environment variables
# TWINE_USERNAME and TWINE_PASSWORD
```

## Best Practices

1. **Always test on TestPyPI first:**

   ```bash
   uv run python scripts/publish.py  # TestPyPI only
   ```

2. **Version bump systematically:**

   - patch: Bug fixes (0.1.0 → 0.1.1)
   - minor: New features (0.1.1 → 0.2.0)
   - major: Breaking changes (0.2.0 → 1.0.0)

3. **Validate before publishing:**

   ```bash
   uv run python scripts/publish.py --test-only
   ```

4. **Use automation for consistency:**
   ```bash
   uv run python scripts/publish.py --version-bump patch --include-pypi
   ```

## Package Information

- **Name:** huoshui-fetch
- **Current Version:** 0.1.2
- **Build System:** Hatchling (PEP 517)
- **Python Support:** >=3.11
- **Console Script:** `huoshui-fetch`
- **Package Type:** MCP (Model Context Protocol) Server

## Links

- **TestPyPI:** https://test.pypi.org/project/huoshui-fetch/
- **PyPI:** https://pypi.org/project/huoshui-fetch/ (when published)
- **Repository:** Local development repository
