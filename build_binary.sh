#!/bin/bash

# Build Standalone Binary for Smart Commit
# This script creates a single executable file that doesn't require Python installation

set -e

echo "🔨 Building Smart Commit Standalone Binary"
echo "=========================================="
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

echo "✅ PyInstaller found"

# Create build directory
mkdir -p dist

echo "📦 Building standalone binary..."

# Build the binary
pyinstaller \
    --onefile \
    --name smart-commit \
    --add-data "smart_commit/config.yml:smart_commit" \
    --hidden-import google.generativeai \
    --hidden-import pydantic \
    --hidden-import yaml \
    --hidden-import click \
    --hidden-import dotenv \
    smart_commit/main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Binary built successfully!"
    echo ""
    echo "📁 Output location: dist/smart-commit"
    echo ""
    echo "📊 File size:"
    ls -lh dist/smart-commit
    echo ""
    echo "🧪 Testing the binary..."
    
    # Test the binary
    if [ -f "dist/smart-commit" ]; then
        echo "✅ Binary file created successfully!"
        echo ""
        echo "🎉 Your standalone binary is ready!"
        echo ""
        echo "📋 How to use:"
        echo "1. Copy dist/smart-commit to any directory"
        echo "2. Make it executable: chmod +x smart-commit"
        echo "3. Run: ./smart-commit --help"
        echo ""
        echo "💡 The binary contains everything needed - no Python installation required!"
    else
        echo "❌ Binary file not found. Check the build output above."
        exit 1
    fi
else
    echo "❌ Build failed. Check the error messages above."
    exit 1
fi
