#!/bin/bash
# Build and publish script for sqs-worker package

set -e

echo "🔧 Building sqs-worker package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/
rm -rf *.egg-info/

# Build the package
echo "📦 Building package with uv..."
uv build

# Check the distribution
echo "🔍 Checking built distribution..."
ls -la dist/

echo "✅ Package built successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Test the package locally:"
echo "   uv pip install dist/*.whl"
echo ""
echo "2. Upload to Test PyPI (optional):"
echo "   uv publish --publish-url https://test.pypi.org/legacy/"
echo ""
echo "3. Upload to PyPI:"
echo "   uv publish"
echo ""
echo "Note: Make sure you have PyPI credentials configured:"
echo "- Set PYPI_TOKEN environment variable, or"
echo "- Configure credentials with: uv publish --help"
