# Smart Commit 🤖

AI-powered commit message generator using Google's Gemini AI. Generate meaningful, conventional commit messages with emojis based on your staged changes.

## Features ✨

- 🎯 Conventional commit format with emojis
- 🎨 Automatic emoji selection based on commit type
- 👀 Preview changes before committing
- 🌐 Global installation - use from any directory
- 🔧 One-time setup with Gemini API key

## Prerequisites 📋

- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Git** - For version control
- **Google AI API Key** - Free from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Quick Start 🚀

### 1. Install Smart Commit

```bash
# Clone and install with one command
git clone https://github.com/skyspec28/smart_commit.git
cd smart_commit
./install.sh
```

The installation script will:
- ✅ Check system requirements
- 📦 Install Smart Commit globally
- 🔧 Guide you through API key setup

**Note:** If you don't have Python installed, the script will show you exactly how to install it for your operating system.

### 2. Start Using Smart Commit

```bash
# Option 1: Traditional way
git add .
smart-commit commit

# Option 2: With aliases (after setup)
gitadd .
sc commit
```

That's it! 🎉 Smart Commit is now ready to use globally on your system.

## Alternative: Standalone Binary 📦

**No Python installation required!** Download a single executable file:

### Download from GitHub Releases

Visit the [Releases page](https://github.com/skyspec28/smart_commit/releases) and download the binary for your platform:

- **macOS**: `smart-commit-macos`
- **Windows**: `smart-commit-windows.exe`
- **Linux**: `smart-commit-linux`

### Quick Download Commands

```bash
# macOS (Apple Silicon)
curl -L https://github.com/skyspec28/smart_commit/releases/latest/download/smart-commit-macos -o smart-commit
chmod +x smart-commit

# Linux
curl -L https://github.com/skyspec28/smart_commit/releases/latest/download/smart-commit-linux -o smart-commit
chmod +x smart-commit

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://github.com/skyspec28/smart_commit/releases/latest/download/smart-commit-windows.exe" -OutFile "smart-commit.exe"
```

### Use Immediately

```bash
# Configure once
./smart-commit config

# Use from anywhere
./smart-commit commit
```

See [STANDALONE_BINARY.md](STANDALONE_BINARY.md) for more details.

## Usage 💡

### Available Commands

```bash
# Configure your API key (first-time setup)
smart-commit config

# Check configuration status
smart-commit status

# Generate and make a commit
smart-commit commit

# Skip confirmation prompt
smart-commit commit --no-confirm

# Show help
smart-commit --help
```

### Create Aliases (Optional)

```bash
# Add to your shell config (~/.zshrc, ~/.bashrc, etc.)
echo 'alias sc="smart-commit"' >> ~/.zshrc
echo 'alias gitadd="git add"' >> ~/.zshrc
source ~/.zshrc

# Now use the shorter commands
gitadd .
sc commit
```

## Commit Message Format 📝

Messages follow the conventional commit format with emojis:

```
<emoji> type(scope): subject

Example: ✨ feat(auth): Add OAuth2 authentication
```

Common types:
- ✨ feat: New features
- 🐛 fix: Bug fixes
- 📝 docs: Documentation
- ♻️ refactor: Code refactoring
- 🎨 style: Code style/formatting
- ⚡ perf: Performance improvements
- 🔧 chore: Maintenance tasks

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`smart-commit commit`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License.

## Acknowledgments 🙏

- Google Gemini AI for powering the commit message generation
- Conventional Commits specification
- Gitmoji for emoji convention
