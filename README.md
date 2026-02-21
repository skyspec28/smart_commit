# Smart Commit

AI-powered git commit message generator. Analyses your staged diff and produces a [Conventional Commits](https://www.conventionalcommits.org/) message — with or without emoji.

## Installation

```bash
pip install smart-commit
```

Requires Python 3.8+ and a free [Google AI API key](https://aistudio.google.com/app/apikey).

## Quick Start

```bash
# 1. Set your API key (once)
smart-commit config

# 2. Stage changes as normal
git add .

# 3. Let AI write the commit message
smart-commit commit
```

That's it.

## Commands

| Command | Description |
|---------|-------------|
| `smart-commit config` | Save your API key |
| `smart-commit status` | Check configuration |
| `smart-commit commit` | Generate and commit |
| `smart-commit commit --no-confirm` | Commit without confirmation prompt |
| `smart-commit commit --no-emoji` | Plain `type(scope): subject` format |

## Commit Message Format

Messages follow the Conventional Commits spec:

```
✨ feat(auth): add Google OAuth integration

Optional body explaining what changed and why.
```

Types: `feat` `fix` `docs` `style` `refactor` `perf` `test` `build` `ci` `chore` `revert`

## Getting Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Run `smart-commit config` and paste the key

## Configuration

Default settings live in the bundled `smart_commit/config.yml`. You can override the AI model or rules by editing it after installation, or by passing a custom path to `load_config()`.

## Standalone Binaries

If you prefer not to install Python, pre-built binaries are available on the [Releases page](https://github.com/skyspec28/smart_commit/releases):

```bash
# macOS (Apple Silicon)
curl -L https://github.com/skyspec28/smart_commit/releases/latest/download/smart-commit-macos -o smart-commit
chmod +x smart-commit && ./smart-commit config

# Linux
curl -L https://github.com/skyspec28/smart_commit/releases/latest/download/smart-commit-linux -o smart-commit
chmod +x smart-commit && ./smart-commit config

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://github.com/skyspec28/smart_commit/releases/latest/download/smart-commit-windows.exe" -OutFile "smart-commit.exe"
```

## Development

```bash
git clone https://github.com/skyspec28/smart_commit.git
cd smart_commit
python -m venv venv && source venv/bin/activate
pip install -e .
smart-commit --help
```

Run tests:
```bash
pip install pytest
pytest
```

## Uninstall

```bash
pip uninstall smart-commit

# Remove stored API key (optional)
rm -rf ~/.config/smart-commit   # macOS/Linux
# or %APPDATA%\smart-commit     # Windows
```

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit with smart-commit: `git add . && smart-commit commit`
4. Open a Pull Request

## License

[MIT](LICENSE) © 2025 skyspec28
