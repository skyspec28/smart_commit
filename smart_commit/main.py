import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
from smart_commit.config_loader import load_config
import click

def initialize():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        config_dir = click.get_app_dir("smart-commit")
        env_path = os.path.join(config_dir, '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found.Run 'smart-commit config' to set it up.")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name="gemini-2.5-pro")

def get_git_diff():
    try:
        diff = subprocess.check_output(["git", "diff", "--cached"], text=True)
        return diff.strip()
    except subprocess.CalledProcessError as e:
        click.echo(f"Error getting diff: {e}", err=True)
        return ""

def commit_with_message(message):
    try:
        subprocess.run(["git", "commit", "-m", message], check=True)
        click.echo("Successfully committed!")
    except subprocess.CalledProcessError as e:
        click.echo(f"Git commit failed: {e}", err=True)

def get_staged_files():
    try:
        files = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
        return files
    except subprocess.CalledProcessError as e:
        click.echo(f"Error getting staged files: {e}", err=True)
        return []

@click.group()
def cli():
    """Smart Commit: AI-powered commit message generator"""
    pass

@cli.command()
def config():
    """Configure Smart Commit settings with your Gemini API key"""
    config_dir = click.get_app_dir("smart-commit")
    os.makedirs(config_dir, exist_ok=True)
    env_path = os.path.join(config_dir, '.env')

    click.echo("🚀 Welcome to Smart Commit Setup!")
    click.echo("")
    click.echo("To use Smart Commit, you'll need a Google AI API key (Gemini).")
    click.echo("")
    click.echo("📋 How to get your API key:")
    click.echo("1. Go to https://makersuite.google.com/app/apikey")
    click.echo("2. Sign in with your Google account")
    click.echo("3. Click 'Create API Key'")
    click.echo("4. Copy the generated API key")
    click.echo("")
    
    api_key = click.prompt("🔑 Please enter your Google AI API key", type=str, hide_input=True)
    
    # Validate the API key format (basic check)
    if not api_key or len(api_key) < 20:
        click.echo("❌ Invalid API key format. Please check your key and try again.", err=True)
        sys.exit(1)

    with open(env_path, 'w') as f:
        f.write(f"GOOGLE_API_KEY={api_key}\n")

    click.echo("")
    click.echo("✅ Configuration saved successfully!")
    click.echo("")
    click.echo("🎉 You're all set! You can now use Smart Commit:")
    click.echo("   • Stage your changes: git add .")
    click.echo("   • Generate commit message: smart-commit commit")
    click.echo("   • Or run: smart-commit commit --no-confirm (to skip confirmation)")
    click.echo("")
    click.echo("💡 Pro tip: You can also run 'smart-commit --help' to see all available commands.")

@cli.command()
def status():
    """Check Smart Commit configuration status"""
    config_dir = click.get_app_dir("smart-commit")
    env_path = os.path.join(config_dir, '.env')
    
    click.echo("🔍 Smart Commit Configuration Status")
    click.echo("=" * 40)
    
    # Check if config directory exists
    if os.path.exists(config_dir):
        click.echo("✅ Config directory: Found")
    else:
        click.echo("❌ Config directory: Not found")
        click.echo("   Run 'smart-commit config' to set up your API key")
        return
    
    # Check if .env file exists
    if os.path.exists(env_path):
        click.echo("✅ Configuration file: Found")
        
        # Try to load and validate the API key
        try:
            load_dotenv(env_path)
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key and len(api_key) >= 20:
                click.echo("✅ API key: Configured and valid")
                click.echo("🎉 Smart Commit is ready to use!")
            else:
                click.echo("❌ API key: Invalid or missing")
                click.echo("   Run 'smart-commit config' to set up your API key")
        except Exception as e:
            click.echo(f"❌ Error reading configuration: {e}")
    else:
        click.echo("❌ Configuration file: Not found")
        click.echo("   Run 'smart-commit config' to set up your API key")

@cli.command()
@click.option('--no-confirm', is_flag=True, help="Skip confirmation prompt")
def commit(no_confirm):
    """Generate and make a commit"""
    try:
        model = initialize()
        config = load_config()

        diff = get_git_diff()
        if not diff:
            click.echo("No staged changes found. Stage your files with 'git add' first.")
            sys.exit(1)

        staged_files = get_staged_files()
        rules = "\n".join(config.ai.rules)

        prompt = f"""
You are an expert at generating Git commit messages that follow the Conventional Commits specification.

**1. Format**
Your output must be only the commit message, in this exact format:
<emoji> type(scope): subject

[optional body: explains the "what" and "why" of the change]

[optional footer: e.g., "BREAKING CHANGE: description"]

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
- ⏪ `revert`: Reverts a previous commit.

**3. Guidelines**
- Subject line must be under 72 characters and use present tense (e.g., "add," not "added").
- The `scope` should be a noun identifying the part of the codebase affected (e.g., `api`, `auth`, `ui`).
- **A body is required if:** the change is complex, affects multiple areas, or introduces a breaking change. Use bullet points in the body to explain key changes.
- **A `BREAKING CHANGE:` footer is required if** the change is not backward-compatible.

**4. Examples**
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
  response format and requires an API key for authentication.

**5. Your Task**
Analyze the following files and diff, then generate the complete commit message.
{rules}
- **Files Changed:** {", ".join(staged_files)}
- **Diff:**
```diff
{diff}

Files changed: {", ".join(staged_files)}
"""
        commit_message = model.generate_content(prompt).text.strip()
        click.echo(f"\nGenerated commit message:\n{commit_message}\n")

        if no_confirm or click.confirm("Do you want to commit with this message?"):
            commit_with_message(commit_message)
        else:
            click.echo("Commit aborted.")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

def main():
    cli()

if __name__ == "__main__":
    main()
