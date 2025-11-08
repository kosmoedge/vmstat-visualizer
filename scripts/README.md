# Release Scripts

Helper scripts for version management and package publishing.

## Scripts

### `setup-pypi.sh`
Interactive script to configure PyPI credentials.

```bash
./scripts/setup-pypi.sh
```

Run this once to set up your PyPI and TestPyPI tokens.

### `bump-version.sh`
Bump the package version.

```bash
./scripts/bump-version.sh patch   # 0.1.0 -> 0.1.1
./scripts/bump-version.sh minor   # 0.1.0 -> 0.2.0
./scripts/bump-version.sh major   # 0.1.0 -> 1.0.0
```

### `release.sh`
Create a git release (commit, tag, and push).

```bash
./scripts/release.sh
```

Prompts for confirmation before pushing to remote.

### `publish.sh`
Build and publish the package to PyPI.

```bash
./scripts/publish.sh
```

Choose between TestPyPI (testing) and PyPI (production).

## Typical Workflow

```bash
# 1. Make your changes
git add .
git commit -m "feat: add new feature"

# 2. Bump version
./scripts/bump-version.sh minor

# 3. Update CHANGELOG.md with release notes

# 4. Create release
./scripts/release.sh

# 5. Publish to PyPI
./scripts/publish.sh
```

## First Time Setup

```bash
# Configure PyPI credentials
./scripts/setup-pypi.sh
```

## GitHub Actions

For automated releases, add your PyPI token to GitHub Secrets:
1. Go to repository Settings → Secrets and variables → Actions
2. Add new secret named `PYPI_TOKEN`
3. Paste your PyPI token

Then push a version tag:
```bash
git tag v0.2.0
git push origin v0.2.0
```

GitHub Actions will automatically build and publish the package.

