import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
from smart_commit.config_loader import load_config
import click

# Configure stdout to use UTF-8 encoding for emoji support
# This fixes issues on Windows terminals with cp1252 encoding
def configure_utf8_output():
    """Configure stdout and stderr to use UTF-8 encoding"""
    if sys.platform == 'win32':
        try:
            # Try to reconfigure stdout to use UTF-8
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
        except (AttributeError, OSError):
            # If reconfigure fails, we'll fall back to ASCII-safe output
            pass

# Call this at module import
configure_utf8_output()

def safe_echo(message, **kwargs):
    """Safely print messages with fallback for systems that don't support Unicode"""
    try:
        click.echo(message, **kwargs)
    except UnicodeEncodeError:
        # Strip emojis and special characters if encoding fails
        import re
        ascii_message = re.sub(r'[^\x00-\x7F]+', '', message)
        click.echo(ascii_message, **kwargs)

def initialize(model_name: str = "gemini-2.5-flash"):
    # Load app config .env first with override=True so it always takes priority
    config_dir = click.get_app_dir("smart-commit")
    env_path = os.path.join(config_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
    else:
        load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found. Run 'smart-commit config' to set it up.")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name=model_name)

def get_git_diff():
    try:
        diff = subprocess.check_output(["git", "diff", "--cached"], text=True)
        return diff.strip()
    except subprocess.CalledProcessError as e:
        safe_echo(f"Error getting diff: {e}", err=True)
        return ""

def commit_with_message(message):
    try:
        subprocess.run(["git", "commit", "-m", message], check=True)
        safe_echo("Successfully committed!")
    except subprocess.CalledProcessError as e:
        safe_echo(f"Git commit failed: {e}", err=True)

def get_staged_files():
    try:
        files = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
        return files
    except subprocess.CalledProcessError as e:
        safe_echo(f"Error getting staged files: {e}", err=True)
        return []

@click.group()
def cli():
    """Smart Commit: AI-powered commit message generator"""
    pass

@cli.command()
@click.option('--api-key', 'api_key_opt', default=None, help="Set API key directly without interactive prompt")
def config(api_key_opt):
    """Configure Smart Commit settings with your Gemini API key"""
    config_dir = click.get_app_dir("smart-commit")
    os.makedirs(config_dir, exist_ok=True)
    env_path = os.path.join(config_dir, '.env')

    safe_echo("🚀 Welcome to Smart Commit Setup!")
    safe_echo("")
    safe_echo("To use Smart Commit, you'll need a Google AI API key (Gemini).")
    safe_echo("")
    safe_echo("📋 How to get your API key:")
    safe_echo("1. Go to https://makersuite.google.com/app/apikey")
    safe_echo("2. Sign in with your Google account")
    safe_echo("3. Click 'Create API Key'")
    safe_echo("4. Copy the generated API key")
    safe_echo("")

    if api_key_opt:
        api_key = api_key_opt
    else:
        api_key = click.prompt("🔑 Please enter your Google AI API key", type=str, hide_input=False)
    
    # Validate the API key format (basic check)
    if not api_key or len(api_key) < 20:
        safe_echo("❌ Invalid API key format. Please check your key and try again.", err=True)
        sys.exit(1)

    with open(env_path, 'w') as f:
        f.write(f"GOOGLE_API_KEY={api_key}\n")

    safe_echo("")
    safe_echo("✅ Configuration saved successfully!")
    safe_echo("")
    safe_echo("🎉 You're all set! You can now use Smart Commit:")
    safe_echo("   • Stage your changes: git add .")
    safe_echo("   • Generate commit message: smart-commit commit")
    safe_echo("   • Or run: smart-commit commit --no-confirm (to skip confirmation)")
    safe_echo("")
    safe_echo("💡 Pro tip: You can also run 'smart-commit --help' to see all available commands.")

@cli.command()
def status():
    """Check Smart Commit configuration status"""
    config_dir = click.get_app_dir("smart-commit")
    env_path = os.path.join(config_dir, '.env')
    
    safe_echo("🔍 Smart Commit Configuration Status")
    safe_echo("=" * 40)
    
    # Check if config directory exists
    if os.path.exists(config_dir):
        safe_echo("✅ Config directory: Found")
    else:
        safe_echo("❌ Config directory: Not found")
        safe_echo("   Run 'smart-commit config' to set up your API key")
        return
    
    # Check if .env file exists
    if os.path.exists(env_path):
        safe_echo("✅ Configuration file: Found")
        
        # Try to load and validate the API key
        try:
            load_dotenv(env_path)
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key and len(api_key) >= 20:
                safe_echo("✅ API key: Configured and valid")
                safe_echo("🎉 Smart Commit is ready to use!")
            else:
                safe_echo("❌ API key: Invalid or missing")
                safe_echo("   Run 'smart-commit config' to set up your API key")
        except Exception as e:
            safe_echo(f"❌ Error reading configuration: {e}")
    else:
        safe_echo("❌ Configuration file: Not found")
        safe_echo("   Run 'smart-commit config' to set up your API key")

def _build_prompt(diff, staged_files, rules, use_emoji):
    """Build the AI prompt with or without emoji instructions."""
    if use_emoji:
        format_line = "<emoji> type(scope): subject"
        types_section = """\
**2. Commit Types & Emojis**
Use exactly one of the following types, with its corresponding emoji:
- ✨ `feat`: A new feature for the user.
- 🐛 `fix`: A bug fix for the user.
- 📚 `docs`: Documentation changes only.
- 🎨 `style`: Code style changes (formatting, whitespace, etc; no logic change).
- ♻️ `refactor`: A code change that neither fixes a bug nor adds a feature.
- ⚡ `perf`: A code change that improves performance.
- 🧪 `test`: Adding missing tests or correcting existing tests.
- 🏗️ `build`: Changes that affect the build system or external dependencies.
- 👷 `ci`: Changes to our CI configuration files and scripts.
- 🔧 `chore`: Other changes that don't modify src or test files (routine maintenance).
- ⏪ `revert`: Reverts a previous commit."""
        examples = """\
[EXAMPLE 1: Simple fix]
- ✨ feat(auth): add Google OAuth integration

[EXAMPLE 2: Complex refactor with a body]
- ♻️ refactor(api): restructure user authentication flow

  Extract OAuth logic into a separate service and add proper error
  handling for expired tokens. This improves modularity and testability.

[EXAMPLE 3: Feature with a breaking change]
- ✨ feat(api): implement v2 user management system

  Complete rewrite of user handling with a new database schema.

  BREAKING CHANGE: The `/api/user` endpoint now returns a different
  response format and requires an API key for authentication."""
    else:
        format_line = "type(scope): subject"
        types_section = """\
**2. Commit Types**
Use exactly one of the following types (no emoji):
- `feat`: A new feature for the user.
- `fix`: A bug fix for the user.
- `docs`: Documentation changes only.
- `style`: Code style changes (formatting, whitespace, etc; no logic change).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `perf`: A code change that improves performance.
- `test`: Adding missing tests or correcting existing tests.
- `build`: Changes that affect the build system or external dependencies.
- `ci`: Changes to our CI configuration files and scripts.
- `chore`: Other changes that don't modify src or test files (routine maintenance).
- `revert`: Reverts a previous commit."""
        examples = """\
[EXAMPLE 1: Simple fix]
- feat(auth): add Google OAuth integration

[EXAMPLE 2: Complex refactor with a body]
- refactor(api): restructure user authentication flow

  Extract OAuth logic into a separate service and add proper error
  handling for expired tokens. This improves modularity and testability.

[EXAMPLE 3: Feature with a breaking change]
- feat(api): implement v2 user management system

  Complete rewrite of user handling with a new database schema.

  BREAKING CHANGE: The `/api/user` endpoint now returns a different
  response format and requires an API key for authentication."""

    return f"""\
You are an expert at generating Git commit messages that follow the Conventional Commits specification.

**1. Format**
Your output must be only the commit message, in this exact format:
{format_line}

[optional body: explains the "what" and "why" of the change]

[optional footer: e.g., "BREAKING CHANGE: description"]

{types_section}

**3. Guidelines**
- Subject line must be under 72 characters and use present tense (e.g., "add," not "added").
- The `scope` should be a noun identifying the part of the codebase affected (e.g., `api`, `auth`, `ui`).
- **A body is required if:** the change is complex, affects multiple areas, or introduces a breaking change. Use bullet points in the body to explain key changes.
- **A `BREAKING CHANGE:` footer is required if** the change is not backward-compatible.

**4. Examples**
{examples}

**5. Your Task**
Analyze the following files and diff, then generate the complete commit message.
{rules}
- **Files Changed:** {", ".join(staged_files)}
- **Diff:**
```diff
{diff}

Files changed: {", ".join(staged_files)}
"""


@cli.command()
@click.option('--no-confirm', is_flag=True, help="Skip confirmation prompt")
@click.option('--no-emoji', 'no_emoji', is_flag=True, help="Generate commit message without emoji prefix")
def commit(no_confirm, no_emoji):
    """Generate and make a commit"""
    try:
        config = load_config()
        model = initialize(model_name=config.ai.model)

        diff = get_git_diff()
        if not diff:
            safe_echo("No staged changes found. Stage your files with 'git add' first.")
            sys.exit(1)

        staged_files = get_staged_files()
        rules = "\n".join(config.ai.rules)

        use_emoji = config.commit.auto_emoji and not no_emoji
        prompt = _build_prompt(diff, staged_files, rules, use_emoji)
        commit_message = model.generate_content(prompt).text.strip()
        safe_echo(f"\nGenerated commit message:\n{commit_message}\n")

        if no_confirm or click.confirm("Do you want to commit with this message?"):
            commit_with_message(commit_message)
        else:
            safe_echo("Commit aborted.")

    except Exception as e:
        safe_echo(f"Error: {e}", err=True)
        sys.exit(1)

def main():
    cli()

if __name__ == "__main__":
    main()
