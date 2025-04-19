# Smart Commit 🤖

A CLI tool that uses Google's Gemini AI to generate meaningful, conventional commit messages based on your staged changes.

## Features ✨

- 🎯 Generates semantic commit messages following conventional commit format
- 🎨 Automatically adds appropriate emojis based on commit type
- 👀 Preview changes before committing
- ⚙️ Configurable rules and settings
- 🤝 Interactive mode for confirming generated messages

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-commit.git
cd smart-commit
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp .env.example .env
```
Then edit `.env` and add your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Usage 💡

1. Stage your changes as usual:
```bash
git add <files>
```

2. Instead of `git commit`, run:
```bash
python smart_commit/main.py
```

3. Review the suggested commit message and confirm with 'y' to commit or 'n' to abort.

## Configuration ⚙️

Configuration is managed through `smart_commit/config.yml`. You can customize:

- AI model parameters
- Commit message rules
- Emoji mappings
- Git integration settings

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

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`python smart_commit/main.py`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- Google Gemini AI for powering the commit message generation
- Conventional Commits specification
- Gitmoji for emoji conventions
