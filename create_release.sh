#!/bin/bash

# Create a GitHub Release with binaries
# This script creates a tag and pushes it to trigger the release workflow

set -e

echo "🚀 Creating Smart Commit Release"
echo "================================"
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Check if we have uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ You have uncommitted changes. Please commit them first."
    exit 1
fi

# Get current version from setup.py
current_version=$(python -c "import re; print(re.search(r'version=\"([^\"]+)\"', open('setup.py').read()).group(1))")
echo "📦 Current version: $current_version"

# Ask for new version
read -p "Enter new version (current: $current_version): " new_version

if [ -z "$new_version" ]; then
    echo "❌ Version cannot be empty"
    exit 1
fi

# Update setup.py with new version
sed -i.bak "s/version=\"$current_version\"/version=\"$new_version\"/" setup.py
rm setup.py.bak

# Commit version update
git add setup.py
git commit -m "🔖 bump version to $new_version"

# Create and push tag
echo "🏷️  Creating tag v$new_version..."
git tag "v$new_version"
git push origin main
git push origin "v$new_version"

echo ""
echo "✅ Release v$new_version created!"
echo ""
echo "🔗 View release: https://github.com/skyspec28/smart_commit/releases/tag/v$new_version"
echo ""
echo "⏳ GitHub Actions will now build and upload binaries for all platforms."
echo "   Check the Actions tab to monitor progress."
echo ""
echo "📋 Once complete, users can download binaries from:"
echo "   https://github.com/skyspec28/smart_commit/releases/latest"
