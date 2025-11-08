#!/bin/bash
# Script to build and publish package to PyPI

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

VERSION=$(poetry version -s)
echo -e "${GREEN}Publishing version: ${VERSION}${NC}"

# Check if PyPI token is configured
if ! poetry config pypi-token.pypi &> /dev/null; then
    echo -e "${YELLOW}Warning: PyPI token not configured${NC}"
    echo "Run: poetry config pypi-token.pypi YOUR_TOKEN_HERE"
    echo "Get token from: https://pypi.org/manage/account/token/"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Ask which repository to publish to
echo ""
echo "Publish to:"
echo "  1. TestPyPI (recommended for testing)"
echo "  2. PyPI (production)"
echo ""
read -p "Select [1-2]: " -n 1 -r
echo

REPO=""
if [[ $REPLY == "1" ]]; then
    REPO="-r testpypi"
    echo -e "${YELLOW}Publishing to TestPyPI...${NC}"
elif [[ $REPLY == "2" ]]; then
    echo -e "${RED}Publishing to production PyPI!${NC}"
    read -p "Are you sure? This cannot be undone. [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
else
    echo "Invalid selection. Aborted."
    exit 1
fi

# Clean old builds
echo -e "${YELLOW}Cleaning old builds...${NC}"
rm -rf dist/ build/ *.egg-info

# Build package
echo -e "${YELLOW}Building package...${NC}"
poetry build

# Verify build
if [[ ! -d "dist" ]]; then
    echo -e "${RED}Error: Build failed - dist/ directory not found${NC}"
    exit 1
fi

echo ""
echo "Built files:"
ls -lh dist/
echo ""

# Publish
echo -e "${YELLOW}Publishing...${NC}"
poetry publish $REPO

echo ""
echo -e "${GREEN}✓ Successfully published version ${VERSION}!${NC}"

if [[ $REPLY == "1" ]]; then
    echo ""
    echo "Test installation with:"
    echo "  pip install -i https://test.pypi.org/simple/ vmstat-visualizer"
else
    echo ""
    echo "Installation command:"
    echo "  pip install vmstat-visualizer"
    echo ""
    echo "Package URL:"
    echo "  https://pypi.org/project/vmstat-visualizer/"
fi

