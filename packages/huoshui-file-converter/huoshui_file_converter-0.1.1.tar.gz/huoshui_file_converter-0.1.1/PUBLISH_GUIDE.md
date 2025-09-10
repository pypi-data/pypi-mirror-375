# PyPI Publishing Guide for Huoshui File Converter

This guide explains how to use the comprehensive PyPI publishing workflow that has been set up for this project.

## Quick Start

### 1. Test Workflow (Recommended First)

```bash
# Complete test workflow: validate → build → TestPyPI
uv run python scripts/workflow.py test-workflow
```

### 2. Production Workflow

```bash
# Full production workflow: validate → build → TestPyPI → PyPI
uv run python scripts/workflow.py full
```

## Workflow Stages

### Available Commands

| Command                                           | Description                    |
| ------------------------------------------------- | ------------------------------ |
| `uv run python scripts/workflow.py validate`      | Pre-publishing validation only |
| `uv run python scripts/workflow.py build`         | Build package with testing     |
| `uv run python scripts/workflow.py testpypi`      | Upload to TestPyPI             |
| `uv run python scripts/workflow.py pypi`          | Upload to production PyPI      |
| `uv run python scripts/workflow.py test-workflow` | Full test workflow             |
| `uv run python scripts/workflow.py full`          | Complete production workflow   |

### Individual Scripts

You can also run the individual scripts directly:

```bash
# Build only
uv run python scripts/build.py

# Upload to TestPyPI
uv run python scripts/upload.py --test

# Upload to production PyPI (with confirmations)
uv run python scripts/upload.py --prod
```

## Configuration

### 1. PyPI Credentials

Set up your PyPI API tokens as environment variables:

```bash
# For TestPyPI
export TESTPYPI_TOKEN="pypi-your-test-token-here"

# For production PyPI
export PYPI_TOKEN="pypi-your-production-token-here"
```

Alternatively, create a `~/.pypirc` file:

```bash
cp .pypirc.example ~/.pypirc
# Edit ~/.pypirc with your credentials
```

### 2. Build Dependencies

The scripts automatically install required dependencies, but you can install them manually:

```bash
uv pip install -r scripts/requirements.txt
```

## Phase-by-Phase Breakdown

### Phase 1: Pre-Publishing Validation

- ✅ Validates `pyproject.toml` completeness
- ✅ Checks version consistency between `pyproject.toml` and `__init__.py`
- ✅ Verifies package structure
- ✅ Validates Python version requirements
- ✅ Checks dependency declarations

### Phase 2: Configuration & Setup

- ✅ Ensures build system is configured (Hatchling)
- ✅ Validates package metadata completeness
- ✅ Runs quality checks and import tests
- ✅ Tests console script entry points

### Phase 3: Build Automation

- ✅ Cleans previous build artifacts
- ✅ Installs build dependencies
- ✅ Generates wheel and source distributions
- ✅ Reports package sizes and contents
- ✅ Tests local installation in isolated environment
- ✅ Validates package metadata with `twine check`

### Phase 4: Publishing & Validation

- ✅ Uploads to TestPyPI first (if in full workflow)
- ✅ Tests installation from TestPyPI
- ✅ Validates basic functionality
- ✅ Interactive confirmation for production uploads
- ✅ Uploads to production PyPI
- ✅ Post-publishing validation

## Version Management

### Automatic Version Bumping

```bash
# Prompt for version bump type
uv run python scripts/workflow.py test-workflow --version-bump ask

# Auto-increment patch version (0.1.1 → 0.1.2)
uv run python scripts/workflow.py test-workflow --version-bump patch

# Auto-increment minor version (0.1.1 → 0.2.0)
uv run python scripts/workflow.py test-workflow --version-bump minor

# Auto-increment major version (0.1.1 → 1.0.0)
uv run python scripts/workflow.py test-workflow --version-bump major
```

## Common Workflows

### 1. First Time Publishing

```bash
# 1. Test everything on TestPyPI first
uv run python scripts/workflow.py test-workflow

# 2. If successful, do production release
uv run python scripts/workflow.py pypi
```

### 2. Regular Updates

```bash
# Increment version and test
uv run python scripts/workflow.py test-workflow --version-bump patch

# If tests pass, release to production
uv run python scripts/workflow.py pypi
```

### 3. Major Release

```bash
# Bump major version and do full workflow
uv run python scripts/workflow.py full --version-bump major
```

## Error Handling & Recovery

### Build Failures

If build fails:

1. Check error messages in output
2. Fix issues (dependencies, metadata, file structure)
3. Run `uv run python scripts/build.py --clean-only` to clean
4. Retry build

### Upload Failures

If upload fails:

1. Check PyPI credentials
2. Verify package name availability
3. Check for version conflicts
4. Review metadata with `uv run python scripts/build.py --validation-only`

### Version Conflicts

If version already exists on PyPI:

1. Increment version: `--version-bump patch`
2. Or manually edit `pyproject.toml` and `server/__init__.py`

## Generated Reports

The workflow generates several reports:

- `build_report.json` - Build artifacts and metadata
- `upload_report_testpypi_*.json` - TestPyPI upload details
- `upload_report_pypi_*.json` - Production upload details

## Safety Features

### TestPyPI First

- All workflows upload to TestPyPI before production
- Allows testing without affecting production
- Installation testing from TestPyPI before proceeding

### Interactive Confirmations

- Production uploads require typing package name
- Must type "UPLOAD" to confirm production release
- Clear warnings about irreversible actions

### Validation Checks

- Metadata validation with `twine check`
- Local installation testing
- Import and entry point testing
- Version consistency verification

## Troubleshooting

### Common Issues

| Issue                    | Solution                                  |
| ------------------------ | ----------------------------------------- |
| "Package not found"      | Check package name spelling               |
| "Version already exists" | Use `--version-bump` or manual increment  |
| "Authentication failed"  | Check API tokens in environment variables |
| "Build failed"           | Check dependencies and metadata           |
| "Import test failed"     | Check package structure and imports       |

### Debug Mode

Add `--verbose` to any command for detailed output:

```bash
uv run python scripts/workflow.py test-workflow --verbose
```

### Dry Run Mode

Test what would happen without actually uploading:

```bash
uv run python scripts/upload.py --test --dry-run
```

## Best Practices

1. **Always test first**: Use `test-workflow` before production
2. **Version incrementally**: Use semantic versioning
3. **Check TestPyPI**: Verify installation before production
4. **Review metadata**: Check `build_report.json` before upload
5. **Keep credentials secure**: Use environment variables, not files

## Support

If you encounter issues:

1. Check the generated reports for details
2. Use `--verbose` flag for more information
3. Review error messages carefully
4. Clean and retry with: `uv run python scripts/build.py --clean-only`

The workflow is designed to be safe and recoverable - you can always clean up and start over!
