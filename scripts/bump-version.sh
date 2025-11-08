#!/bin/bash
# Script to bump version using Poetry

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Error: Poetry is not installed${NC}"
    echo "Install it: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Get bump type
BUMP_TYPE=${1:-patch}

if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo -e "${RED}Error: Invalid bump type '${BUMP_TYPE}'${NC}"
    echo "Usage: $0 [major|minor|patch]"
    echo ""
    echo "Examples:"
    echo "  $0 patch  # 0.1.0 -> 0.1.1"
    echo "  $0 minor  # 0.1.0 -> 0.2.0"
    echo "  $0 major  # 0.1.0 -> 1.0.0"
    exit 1
fi

# Get current version
OLD_VERSION=$(poetry version -s)
echo -e "${YELLOW}Current version: ${OLD_VERSION}${NC}"

# Bump version
poetry version $BUMP_TYPE
NEW_VERSION=$(poetry version -s)

echo -e "${GREEN}✓ Version bumped to: ${NEW_VERSION}${NC}"
echo ""
echo "Next steps:"
echo "  1. Update CHANGELOG.md with release notes"
echo "  2. Run: git add pyproject.toml CHANGELOG.md"
echo "  3. Run: git commit -m 'chore: bump version to ${NEW_VERSION}'"
echo "  4. Run: git tag -a v${NEW_VERSION} -m 'Release v${NEW_VERSION}'"
echo "  5. Run: git push origin main && git push origin v${NEW_VERSION}"
echo ""
echo "Or run: ./scripts/release.sh"

