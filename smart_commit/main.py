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

PROVIDER_ENV_VARS = {
    "google": "GOOGLE_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
}

PROVIDER_DEFAULT_MODELS = {
    "google": "gemini-2.5-flash",
    "anthropic": "claude-3-5-haiku-20241022",
    "openai": "gpt-4o-mini",
}

def initialize(provider: str = "google", model_name: str = "gemini-2.5-flash"):
    """Initialize the AI provider and return a generate(prompt) -> str callable."""
    config_dir = click.get_app_dir("smart-commit")
    env_path = os.path.join(config_dir, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
    else:
        load_dotenv()

    if provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found. Run 'smart-commit config' to set it up.")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name=model_name)
        return lambda prompt: model.generate_content(prompt).text.strip()

    elif provider == "anthropic":
        import anthropic as anthropic_sdk
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Run 'smart-commit config' to set it up.")
        client = anthropic_sdk.Anthropic(api_key=api_key)
        return lambda prompt: client.messages.create(
            model=model_name,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        ).content[0].text.strip()

    elif provider == "openai":
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found. Run 'smart-commit config' to set it up.")
        client = OpenAI(api_key=api_key)
        return lambda prompt: client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        ).choices[0].message.content.strip()

    else:
        raise ValueError(f"Unknown provider '{provider}'. Choose: google, anthropic, openai")
    
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
@click.option('--provider', 'provider_opt', default=None,
              type=click.Choice(["google", "anthropic", "openai"], case_sensitive=False),
              help="AI provider to configure (google, anthropic, openai)")
def config(api_key_opt, provider_opt):
    """Configure Smart Commit settings with your AI provider API key"""
    config_dir = click.get_app_dir("smart-commit")
    os.makedirs(config_dir, exist_ok=True)
    env_path = os.path.join(config_dir, '.env')

    safe_echo("🚀 Welcome to Smart Commit Setup!")
    safe_echo("")

    # Determine provider
    if provider_opt:
        provider = provider_opt
    else:
        safe_echo("Which AI provider do you want to use?")
        safe_echo("  1. google    - Gemini (gemini-2.5-flash)")
        safe_echo("  2. anthropic - Claude (claude-3-5-haiku-20241022)")
        safe_echo("  3. openai    - ChatGPT (gpt-4o-mini)")
        safe_echo("")
        provider = click.prompt("Provider", type=click.Choice(["google", "anthropic", "openai"]), default="google")

    env_var = PROVIDER_ENV_VARS[provider]

    safe_echo("")
    safe_echo(f"Provider: {provider}  |  API key variable: {env_var}")
    safe_echo("")

    if api_key_opt:
        api_key = api_key_opt
    else:
        api_key = click.prompt(f"🔑 Enter your {provider} API key", type=str, hide_input=False)

    # Validate the API key format (basic check)
    if not api_key or len(api_key) < 20:
        safe_echo("❌ Invalid API key format. Please check your key and try again.", err=True)
        sys.exit(1)

    # Read existing .env to preserve other providers' keys
    existing = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    k, v = line.split('=', 1)
                    existing[k.strip()] = v.strip()

    existing[env_var] = api_key

    with open(env_path, 'w') as f:
        for k, v in existing.items():
            f.write(f"{k}={v}\n")

    safe_echo("")
    safe_echo(f"✅ {provider} API key saved successfully!")
    safe_echo(f"   Saved to: {env_path}")
    safe_echo("")
    safe_echo(f"💡 To use {provider}, set in your config.yml:")
    safe_echo(f"   ai:")
    safe_echo(f"     provider: \"{provider}\"")
    safe_echo(f"     model: \"{PROVIDER_DEFAULT_MODELS[provider]}\"")
    safe_echo("")
    safe_echo("🎉 You're all set! Stage your changes and run: smart-commit commit")

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

        try:
            load_dotenv(env_path, override=True)

            # Detect configured provider from config.yml
            try:
                cfg = load_config()
                provider = cfg.ai.provider
                model = cfg.ai.model
            except Exception:
                provider = "google"
                model = "gemini-2.5-flash"

            env_var = PROVIDER_ENV_VARS.get(provider, "GOOGLE_API_KEY")
            api_key = os.getenv(env_var)

            safe_echo(f"✅ Provider: {provider} (model: {model})")

            if api_key and len(api_key) >= 20:
                safe_echo(f"✅ API key ({env_var}): Configured and valid")
                safe_echo("🎉 Smart Commit is ready to use!")
            else:
                safe_echo(f"❌ API key ({env_var}): Invalid or missing")
                safe_echo(f"   Run 'smart-commit config --provider {provider}' to set it up")
        except Exception as e:
            safe_echo(f"❌ Error reading configuration: {e}")
    else:
        safe_echo("❌ Configuration file: Not found")
        safe_echo("   Run 'smart-commit config' to set up your API key")

@cli.command()
@click.option('--no-confirm', is_flag=True, help="Skip confirmation prompt")
def commit(no_confirm):
    """Generate and make a commit"""
    try:
        config = load_config()
        generate = initialize(provider=config.ai.provider, model_name=config.ai.model)

        diff = get_git_diff()
        if not diff:
            safe_echo("No staged changes found. Stage your files with 'git add' first.")
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
        commit_message = generate(prompt)
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
