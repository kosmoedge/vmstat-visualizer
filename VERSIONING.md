# Versioning and Release Guide

## Version Management

This project uses [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

Current version is stored in `pyproject.toml`.

## Creating a New Release

### 1. Update Version

Use Poetry to bump the version:

```bash
# Patch release (0.1.0 -> 0.1.1)
poetry version patch

# Minor release (0.1.0 -> 0.2.0)
poetry version minor

# Major release (0.1.0 -> 1.0.0)
poetry version major

# Specific version
poetry version 1.2.3
```

Or use the helper script:

```bash
# Bump patch version
./scripts/bump-version.sh patch

# Bump minor version
./scripts/bump-version.sh minor

# Bump major version
./scripts/bump-version.sh major
```

### 2. Update CHANGELOG

Edit `CHANGELOG.md` and add release notes under the new version:

```markdown
## [0.2.0] - 2025-11-08

### Added
- New feature X
- Support for Y

### Fixed
- Bug in Z

### Changed
- Improved performance of A
```

### 3. Commit and Tag

```bash
# Commit version bump and changelog
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to $(poetry version -s)"

# Create git tag
git tag -a v$(poetry version -s) -m "Release v$(poetry version -s)"

# Push commits and tags
git push origin main
git push origin v$(poetry version -s)
```

Or use the release script:

```bash
./scripts/release.sh
```

### 4. Build and Publish

```bash
# Build the package
poetry build

# Publish to PyPI
poetry publish
```

Or use the publish script:

```bash
./scripts/publish.sh
```

## First-Time PyPI Setup

### 1. Create PyPI Account

- Register at [https://pypi.org/account/register/](https://pypi.org/account/register/)
- Verify your email

### 2. Configure Poetry with PyPI Token

```bash
# Create API token at https://pypi.org/manage/account/token/

# Configure Poetry
poetry config pypi-token.pypi YOUR_TOKEN_HERE
```

### 3. Test on TestPyPI First (Recommended)

```bash
# Configure TestPyPI
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi YOUR_TEST_TOKEN_HERE

# Publish to TestPyPI
poetry publish -r testpypi

# Test installation
pip install -i https://test.pypi.org/simple/ vmstat-visualizer
```

## Automated Releases with GitHub Actions

See `.github/workflows/release.yml` for automated releases when you push a tag.

The workflow will:
1. Run tests
2. Build the package
3. Publish to PyPI automatically

Just push a version tag and the rest happens automatically:

```bash
git tag v0.2.0
git push origin v0.2.0
```

## Version Checking

Check current version:

```bash
# From Poetry
poetry version

# From installed package
vmstat-visualizer --version

# From Python
python -c "from vmstat_visualizer.cli.__version__ import __version__; print(__version__)"
```

## Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Git commit created
- [ ] Git tag created
- [ ] Changes pushed to GitHub
- [ ] Package built successfully
- [ ] Package published to PyPI
- [ ] GitHub release created with notes

## Troubleshooting

**Version already exists on PyPI:**
- You cannot overwrite a published version
- Bump to a new version number

**Poetry publish fails:**
- Check your PyPI token is configured: `poetry config --list`
- Verify token permissions on PyPI

**Build fails:**
- Clean build artifacts: `rm -rf dist/`
- Rebuild: `poetry build`

