#!/bin/bash
# Script to set up PyPI credentials for Poetry

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}PyPI Setup Guide${NC}"
echo ""
echo "This script will help you configure Poetry to publish to PyPI."
echo ""

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed"
    echo "Install it: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Production PyPI
echo -e "${YELLOW}1. Production PyPI Setup${NC}"
echo ""
echo "Steps:"
echo "  a. Go to https://pypi.org/account/register/ (if you don't have an account)"
echo "  b. Go to https://pypi.org/manage/account/token/"
echo "  c. Create a new API token with scope 'Entire account' or 'Project: vmstat-visualizer'"
echo "  d. Copy the token (it starts with 'pypi-')"
echo ""
read -p "Do you have a PyPI token? [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Paste your PyPI token:"
    read -s PYPI_TOKEN
    poetry config pypi-token.pypi "$PYPI_TOKEN"
    echo -e "${GREEN}✓ PyPI token configured${NC}"
else
    echo "Skipped PyPI setup"
fi

echo ""

# TestPyPI
echo -e "${YELLOW}2. TestPyPI Setup (Optional but Recommended)${NC}"
echo ""
echo "TestPyPI is for testing your package before publishing to production."
echo ""
echo "Steps:"
echo "  a. Go to https://test.pypi.org/account/register/"
echo "  b. Go to https://test.pypi.org/manage/account/token/"
echo "  c. Create a new API token"
echo "  d. Copy the token"
echo ""
read -p "Do you want to configure TestPyPI? [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    poetry config repositories.testpypi https://test.pypi.org/legacy/
    echo "Paste your TestPyPI token:"
    read -s TEST_TOKEN
    poetry config pypi-token.testpypi "$TEST_TOKEN"
    echo -e "${GREEN}✓ TestPyPI configured${NC}"
else
    echo "Skipped TestPyPI setup"
fi

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To verify your configuration:"
echo "  poetry config --list | grep pypi"
echo ""
echo "To publish:"
echo "  ./scripts/publish.sh"

