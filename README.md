# Smart Commit 🤖

A CLI tool that uses Google's Gemini AI to generate meaningful, conventional commit messages based on your staged changes.

## Features ✨

- 🎯 Generates semantic commit messages following conventional commit format
- 🎨 Automatically adds appropriate emojis based on commit type
- 👀 Preview changes before committing
- ⚙️ Configurable rules and settings
- 🤝 Interactive mode for confirming generated messages
- 🌐 Global installation support - use from any directory
- 🔧 Easy setup with just your Gemini API key

## Quick Start 🚀

### Option 1: One-Command Installation (Easiest)

```bash
# Clone and install with one command
git clone https://github.com/yourusername/smart-commit.git
cd smart-commit
./install.sh
```

The installation script will:
- ✅ Check system requirements
- 📦 Install Smart Commit globally
- 🔧 Guide you through API key setup
- 🎉 Make it ready to use from any directory

### Option 2: Manual Installation

```bash
# Install from PyPI (when published)
pip install smart-commit

# Or install from source
git clone https://github.com/yourusername/smart-commit.git
cd smart-commit
pip install -e .

# Configure your API key
smart-commit config
```

### 3. Start Using Smart Commit

```bash
# Stage your changes
git add .

# Generate and commit with AI
smart-commit commit
```

That's it! 🎉 Smart Commit is now ready to use globally on your system.

## Installation Options 📦

### Option 1: Global Installation (Recommended)

This makes Smart Commit available system-wide from any directory:

```bash
# Install globally
pip install smart-commit

# Or install from source
git clone https://github.com/yourusername/smart-commit.git
cd smart-commit
pip install -e .

# Configure once
smart-commit config
```

### Option 2: Development Installation

For development or testing:

```bash
git clone https://github.com/yourusername/smart-commit.git
cd smart-commit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run directly
python smart_commit/main.py config
python smart_commit/main.py commit
```

## Usage 💡

### Basic Usage

1. Stage your changes as usual:
```bash
git add <files>
```

2. Generate and commit with AI:
```bash
smart-commit commit
```

3. Review the suggested commit message and confirm with 'y' to commit or 'n' to abort.

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

### Creating a Shorter Command Alias

If you find `smart-commit` too long to type, you can create a shorter alias like `sc`:

```bash
# For bash/zsh users, add to your ~/.bashrc or ~/.zshrc:
echo 'alias sc="smart-commit"' >> ~/.zshrc

# For fish shell users:
echo 'alias sc="smart-commit"' >> ~/.config/fish/config.fish

# Apply changes to current session:
source ~/.zshrc  # or source ~/.bashrc or source ~/.config/fish/config.fish
```

Now you can use the shorter command:
```bash
sc commit
```

### Using the Global `gitadd` Command

For even more convenience, you can set up a global `gitadd` command that combines `git add` and `smart-commit commit` in one step. See the [Global Installation](#global-installation-) section below for instructions.

## Configuration ⚙️

Configuration is managed through a YAML file. The tool looks for this file in the following locations (in order of preference):

1. User-specified path (if provided)
2. `smart_commit/config.yml` in the current directory
3. Package installation directory
4. Global system path: `/usr/local/etc/smart-commit/config.yml`

You can customize the following settings:

- AI model parameters
- Commit message rules
- Emoji mappings


Example configuration:
```yaml
ai:
  model: "gemini-1.5-flash"
  temperature: 0.7
  max_tokens: 100

commit:
  auto_emoji: true
  validate_conventional: true
  preview_diff: true
  interactive_mode: true
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

## Global Installation 🌐

Follow these steps to make Smart Commit truly global on your system, allowing you to use it from any directory with a convenient `gitadd` command.

### Step 1: Install Smart Commit

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-commit.git
cd smart-commit

# Install the package
pip install -e .
```

### Step 2: Make the Configuration Globally Available

```bash
# Create a global config directory
sudo mkdir -p /usr/local/etc/smart-commit

# Copy the configuration file
sudo cp smart_commit/config.yml /usr/local/etc/smart-commit/
```

### Step 3: Create a Symbolic Link to Smart Commit

```bash
# Create a symbolic link in /usr/local/bin
sudo ln -sf $(which smart-commit) /usr/local/bin/smart-commit
```

### Step 4: Create the Global gitadd Command

```bash
# Create the gitadd script
sudo bash -c 'cat > /usr/local/bin/gitadd << "EOF"
#!/bin/bash
# gitadd - A global command that combines git add and smart-commit
# Usage: gitadd file1 file2 directory/

# Add all specified files to git staging area
git add "$@"

# If the add was successful, run smart-commit
if [ $? -eq 0 ]; then
    smart-commit commit
else
    echo "Error: Failed to add files to git staging area"
    exit 1
fi
EOF'

# Make it executable
sudo chmod +x /usr/local/bin/gitadd
```

### Step 5: Create a Shorter Alias (Optional)

If you find `smart-commit` too long to type, you can create a shorter alias like `sc`:

```bash
# Method 1: Create a symbolic link (works immediately system-wide)
sudo ln -sf /usr/local/bin/smart-commit /usr/local/bin/sc

# Method 2: Add a shell alias
# For bash/zsh users:
sudo bash -c 'echo "alias sc=\"smart-commit\"" >> /etc/profile'

# Or add it to your personal shell configuration:
echo 'alias sc="smart-commit"' >> ~/.zshrc  # or ~/.bashrc

# Apply changes to current session:
source ~/.zshrc  # or source ~/.bashrc
```

### Step 6: Test the Global Commands

You can now use both commands from any Git repository on your system:

```bash
# Navigate to any Git repository
cd /path/to/any/git/repo

# Use the shorter alias for smart-commit
sc commit

# Or use gitadd instead of git add
gitadd file1.txt file2.py
```

The `gitadd` command will add the files and trigger the smart-commit process in one step.

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`smart-commit commit` or `gitadd .`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Google Gemini AI for powering the commit message generation
- Conventional Commits specification
- Gitmoji for emoji convention
