# Technical: How Versioning Works

## Short Answer

**Poetry does NOT read from `__version__.py`**

- Version is **only** in `pyproject.toml`
- Poetry reads/writes version there only
- `__version__.py` is for runtime use in your application

## The Flow

```
┌─────────────────┐
│ pyproject.toml  │ ← Single source of truth
│ version="0.1.0" │ ← Poetry reads/writes here
└────────┬────────┘
         │
         │ poetry build
         │
         ▼
┌─────────────────┐
│ Package         │
│ Metadata        │ ← Built into wheel/tarball
└────────┬────────┘
         │
         │ pip install
         │
         ▼
┌─────────────────┐
│ __version__.py  │ ← Reads from installed metadata
│ at runtime      │
└─────────────────┘
```

## Your Fixed Setup

### 1. `pyproject.toml` (Source of Truth)
```toml
[tool.poetry]
version = "0.1.0"  # ← Poetry uses this

[build-system]
requires = ["poetry-core>=1.0.0"]  # ← Only Poetry, no setuptools
build-backend = "poetry.core.masonry.api"
```

### 2. `__version__.py` (Runtime Version)
```python
# Reads from package metadata automatically
try:
    from importlib.metadata import version
    __version__ = version("vmstat_visualizer")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"  # Development fallback
```

### 3. CLI (Shows Version to Users)
```python
@click.version_option(version=__version__)
def cli():
    pass
```

## How It Works

### During Development
```bash
# Bump version (updates pyproject.toml)
poetry version patch

# Install in editable mode
poetry install

# __version__.py reads from package metadata
# Shows: 0.1.1
```

### During Build
```bash
# Build package
poetry build

# Creates:
# - dist/vmstat_visualizer-0.1.1-py3-none-any.whl
# - dist/vmstat_visualizer-0.1.1.tar.gz

# Version embedded in package metadata
```

### After Installation
```bash
# User installs
pip install vmstat-visualizer

# Check version
vmstat-visualizer --version
# Output: vmstat-visualizer, version 0.1.1

# In Python
python -c "from vmstat_visualizer.cli.__version__ import __version__; print(__version__)"
# Output: 0.1.1
```

## Key Points

✅ **One Source**: Version only in `pyproject.toml`
✅ **No Manual Sync**: `__version__.py` reads from metadata automatically
✅ **Poetry Commands**: Use `poetry version` to bump
✅ **CLI Flag**: Users can check with `--version`

❌ **Don't Use**: `setuptools_scm` with Poetry (removed)
❌ **Don't Hardcode**: Version in `__version__.py` (dynamic instead)
❌ **Don't Mix**: Poetry + setuptools build systems

## Commands Reference

```bash
# Check current version
poetry version                    # Shows: vmstat-visualizer 0.1.0
vmstat-visualizer --version       # Shows: vmstat-visualizer, version 0.1.0

# Bump version (updates pyproject.toml)
poetry version patch              # 0.1.0 -> 0.1.1
poetry version minor              # 0.1.0 -> 0.2.0
poetry version major              # 0.1.0 -> 1.0.0

# Build with new version
poetry build                      # Creates dist/ with version in filename

# Check version in Python
python -c "from vmstat_visualizer.cli.__version__ import __version__; print(__version__)"
```

## Why This Approach?

**Before (broken):**
- Version in `pyproject.toml`: `0.1.0`
- `setuptools_scm` configured but doesn't work with Poetry
- `__version__.py` empty or outdated
- No single source of truth

**After (fixed):**
- Version in `pyproject.toml`: `0.1.0` ← Only place
- `__version__.py` reads from package metadata ← Always correct
- `poetry version` updates `pyproject.toml` ← One command
- CLI shows version ← `--version` flag works

## Alternatives

If you really want git-tag-based versioning:

```bash
# Install plugin
poetry self add "poetry-dynamic-versioning[plugin]"
```

```toml
# pyproject.toml
[tool.poetry-dynamic-versioning]
enable = true
```

Then version comes from git tags automatically. But for simplicity, the current approach (manual version in pyproject.toml) is better.

