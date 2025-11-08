#!/bin/bash
# Script to create a release: commit, tag, and push

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Error: Poetry is not installed${NC}"
    exit 1
fi

# Check if there are uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    echo ""
    git status -s
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Get current version
VERSION=$(poetry version -s)
echo -e "${GREEN}Creating release for version: ${VERSION}${NC}"

# Check if CHANGELOG.md has been updated
if ! grep -q "\[${VERSION}\]" CHANGELOG.md 2>/dev/null; then
    echo -e "${YELLOW}Warning: CHANGELOG.md doesn't seem to have notes for version ${VERSION}${NC}"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please update CHANGELOG.md first."
        exit 1
    fi
fi

# Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to ${VERSION}" || echo "Nothing to commit"

# Create tag
echo -e "${YELLOW}Creating git tag v${VERSION}...${NC}"
if git tag -l | grep -q "v${VERSION}"; then
    echo -e "${RED}Error: Tag v${VERSION} already exists${NC}"
    exit 1
fi
git tag -a "v${VERSION}" -m "Release v${VERSION}"

# Push
echo -e "${YELLOW}Pushing to origin...${NC}"
read -p "Push to remote? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Skipped push. To push manually:"
    echo "  git push origin main"
    echo "  git push origin v${VERSION}"
else
    git push origin main
    git push origin "v${VERSION}"
    echo -e "${GREEN}✓ Release v${VERSION} created and pushed!${NC}"
fi

echo ""
echo "Next steps:"
echo "  1. Build: poetry build"
echo "  2. Publish: poetry publish"
echo "  Or run: ./scripts/publish.sh"

