#!/bin/bash

# Load environment variables
source .env

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep -E '^version = ' pyproject.toml | cut -d'"' -f2)
echo "Current version: $CURRENT_VERSION"

# Ask for new version
read -p "Enter new version (or press Enter to keep $CURRENT_VERSION): " NEW_VERSION

# Update version if provided
if [ ! -z "$NEW_VERSION" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    else
        # Linux
        sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    fi
    echo "Updated version to: $NEW_VERSION"
else
    NEW_VERSION=$CURRENT_VERSION
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/

# Build the package
echo "Building package with version $NEW_VERSION..."
uv build

# Publish to PyPI
echo "Publishing to PyPI..."
uv publish --token $PYPI_TOKEN

echo "Done! You can now install with: uv tool install finter-agent"