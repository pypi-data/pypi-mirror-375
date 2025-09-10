#!/bin/bash
# Publish script for cmsketch package

set -e  # Exit on any error

echo "🚀 Publishing cmsketch to PyPI"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Run this from the project root."
    exit 1
fi

# Check if build tools are installed
if ! uv run python -c "import build, twine" &> /dev/null; then
    echo "📦 Installing build tools..."
    uv add --group dev build twine
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/

# Build the package
echo "🔨 Building package..."
uv run python -m build

# Check what was built
echo "📋 Built files:"
ls -la dist/

# Ask user which repository to upload to
echo ""
echo "Choose upload destination:"
echo "1) Test PyPI (recommended first)"
echo "2) Production PyPI"
echo "3) Both (test first, then production)"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "📤 Uploading to Test PyPI..."
        uv run python -m twine upload --repository testpypi dist/*
        echo "✅ Uploaded to Test PyPI!"
        echo "🧪 Test with: uv add --index-url https://test.pypi.org/simple/ cmsketch"
        ;;
    2)
        echo "📤 Uploading to Production PyPI..."
        uv run python -m twine upload dist/*
        echo "✅ Uploaded to PyPI!"
        echo "🎉 Install with: uv add cmsketch"
        ;;
    3)
        echo "📤 Uploading to Test PyPI first..."
        uv run python -m twine upload --repository testpypi dist/*
        echo "✅ Uploaded to Test PyPI!"
        
        read -p "Test successful? Upload to production PyPI? (y/N): " confirm
        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            echo "📤 Uploading to Production PyPI..."
            uv run python -m twine upload dist/*
            echo "✅ Uploaded to PyPI!"
            echo "🎉 Install with: uv add cmsketch"
        else
            echo "⏸️  Skipped production upload."
        fi
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎯 Publishing complete!"
