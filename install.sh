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
    echo ""
    echo "📋 How to install Python:"
    echo ""
    echo "🐍 **macOS (using Homebrew):**"
    echo "   brew install python3"
    echo ""
    echo "🐧 **Linux (Ubuntu/Debian):**"
    echo "   sudo apt update && sudo apt install python3 python3-pip"
    echo ""
    echo "🐧 **Linux (CentOS/RHEL/Fedora):**"
    echo "   sudo yum install python3 python3-pip"
    echo "   # or for newer versions:"
    echo "   sudo dnf install python3 python3-pip"
    echo ""
    echo "🪟 **Windows:**"
    echo "   1. Download from https://www.python.org/downloads/"
    echo "   2. Run the installer and check 'Add Python to PATH'"
    echo "   3. Restart your terminal"
    echo ""
    echo "🌐 **Alternative (all platforms):**"
    echo "   Download from https://www.python.org/downloads/"
    echo ""
    echo "After installing Python, run this script again:"
    echo "   ./install.sh"
    echo ""
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
    echo ""
    echo "📋 How to install pip3:"
    echo ""
    echo "🐍 **macOS:**"
    echo "   python3 -m ensurepip --upgrade"
    echo "   # or: brew install python3 (includes pip)"
    echo ""
    echo "🐧 **Linux:**"
    echo "   sudo apt install python3-pip  # Ubuntu/Debian"
    echo "   sudo yum install python3-pip  # CentOS/RHEL"
    echo "   sudo dnf install python3-pip  # Fedora"
    echo ""
    echo "🪟 **Windows:**"
    echo "   pip3 should be included with Python installer"
    echo "   # If not: python -m ensurepip --upgrade"
    echo ""
    echo "After installing pip3, run this script again:"
    echo "   ./install.sh"
    echo ""
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
    echo "💡 Pro tip: Create aliases for faster usage:"
    echo "  echo 'alias sc=\"smart-commit\"' >> ~/.zshrc"
    echo "  echo 'alias gitadd=\"git add\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"
    echo "  # Then use: sc commit or gitadd ."
else
    echo "❌ Configuration setup failed."
    echo "You can run 'smart-commit config' manually to set up your API key."
fi
