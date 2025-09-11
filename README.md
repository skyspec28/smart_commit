# Smart Commit 🤖

Got tired of thinking about commit messages and following pattern , so setup scripts for it and use gemni api


## Features 

- 🎯 Conventional commit format with emojis
- 🎨 Automatic emoji selection based on commit type
- 👀 Preview changes before committing
- 📦 **Standalone binary - No language installation required!**
- 🔧 One-time setup with Gemini API key

## Quick Start 🚀

### Option 1: Standalone Binary (Recommended) 

**No Python installation required!** Download a single executable file:

#### Quick Download Commands

```bash
# macOS (Apple Silicon) - Available Now ✅
curl -L https://github.com/skyspec28/smart_commit/releases/latest/download/smart-commit-macos -o smart-commit
chmod +x smart-commit

# Linux - Coming Soon 🚧
# curl -L https://github.com/skyspec28/smart_commit/releases/latest/download/smart-commit-linux -o smart-commit
# chmod +x smart-commit

# Windows - Coming Soon 🚧
# Invoke-WebRequest -Uri "https://github.com/skyspec28/smart_commit/releases/latest/download/smart-commit-windows.exe" -OutFile "smart-commit.exe"
```

#### Alternative: Download from GitHub Releases

Visit the [Releases page](https://github.com/skyspec28/smart_commit/releases) and download the binary for your platform:

- **macOS**: `smart-commit-macos` ✅ **Available**
- **Windows**: `smart-commit-windows.exe` 🚧 **Coming Soon**
- **Linux**: `smart-commit-linux` 🚧 **Coming Soon**

**Note**: Currently only macOS binaries are available. Windows and Linux binaries will be available in the next release.

#### Use Immediately

**For macOS (with standalone binary):**
```bash
# Configure once (enter your Google AI API key)
./smart-commit config

# Stage your changes
git add .

# Generate and commit with AI
./smart-commit commit
```

**For Windows/Linux (use Python installation until binaries are ready):**
```bash
# Configure once (enter your Google AI API key)
smart-commit config

# Stage your changes
git add .

# Generate and commit with AI
smart-commit commit
```

That's it! 🎉 No Python, no pip, no dependencies needed (when using standalone binary).

### Option 2: Python Installation (For Developers) 

If you prefer to install from source or contribute to the project:

#### Prerequisites
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Google AI API Key** - Free from [Google AI Studio](https://makersuite.google.com/app/apikey)

#### Install Smart Commit

**For macOS/Linux:**
```bash
# Clone and install with one command
git clone https://github.com/skyspec28/smart_commit.git
cd smart_commit
./install.sh
```

**For Windows:**
```bash
# Clone the repository
git clone https://github.com/skyspec28/smart_commit.git
cd smart_commit

# Install dependencies
pip install -r requirements.txt

# Install globally
pip install -e .

# Configure your API key
smart-commit config
```

The installation will:
- ✅ Check system requirements
- 📦 Install Smart Commit globally
- 🔧 Guide you through API key setup

## Usage 💡

### Available Commands

**For Standalone Binary:**
```bash
# Configure your API key (first-time setup)
./smart-commit config

# Check configuration status
./smart-commit status

# Generate and make a commit
./smart-commit commit

# Skip confirmation prompt
./smart-commit commit --no-confirm

# Show help
./smart-commit --help
```

**For Python Installation:**
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

## Getting Your API Key 🔑

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key
5. Run `./smart-commit config` (standalone binary) or `smart-commit config` (Python install) and paste your key

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request. 

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`./smart-commit commit`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Development Setup 🛠️

For developers who want to contribute:

```bash
# Clone the repository
git clone https://github.com/skyspec28/smart_commit.git
cd smart_commit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Build standalone binary
./build_binary.sh
```

## Uninstall 🗑️

### Standalone Binary

Simply delete the binary file:

```bash
# Remove the binary file
rm smart-commit

# Or if you renamed it
rm smart-commit-macos
rm smart-commit-linux
rm smart-commit.exe
```

### Python Installation

If you installed via pip:

```bash
# Uninstall the package
pip uninstall smart-commit

# Remove configuration files (optional)
rm -rf ~/.config/smart-commit
```

### Remove Aliases (if created)

If you added aliases to your shell config:

```bash
# Edit your shell config file
nano ~/.zshrc  # or ~/.bashrc

# Remove these lines:
# alias sc="./smart-commit"
# alias gitadd="git add"

# Reload your shell
source ~/.zshrc
```

## License 📄

This project is licensed under the MIT License.
