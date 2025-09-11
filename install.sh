#!/bin/bash

# Smart Commit Installation Script
# This script installs Smart Commit globally and sets up the configuration

set -e

echo "🚀 Smart Commit Installation Script"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 detected"
echo ""

# Install Smart Commit
echo "📦 Installing Smart Commit..."
pip3 install -e .

if [ $? -eq 0 ]; then
    echo "✅ Smart Commit installed successfully!"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "🔧 Setting up configuration..."

# Run the config command
smart-commit config

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Installation complete!"
    echo ""
    echo "You can now use Smart Commit from any directory:"
    echo "  • smart-commit commit    - Generate and make a commit"
    echo "  • smart-commit status    - Check configuration"
    echo "  • smart-commit --help    - Show all commands"
    echo ""
    echo "💡 Pro tip: Create an alias for faster usage:"
    echo "  echo 'alias sc=\"smart-commit\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"
    echo "  # Then use: sc commit"
else
    echo "❌ Configuration setup failed."
    echo "You can run 'smart-commit config' manually to set up your API key."
fi
