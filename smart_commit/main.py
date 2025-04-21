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
        raise ValueError("GOOGLE_API_KEY not found. Run 'smart-commit config' to set it up.")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name="models/gemini-1.5-flash")

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
    """Configure Smart Commit settings"""
    config_dir = click.get_app_dir("smart-commit")
    os.makedirs(config_dir, exist_ok=True)
    env_path = os.path.join(config_dir, '.env')

    api_key = click.prompt("Please enter your Google API key", type=str)

    with open(env_path, 'w') as f:
        f.write(f"GOOGLE_API_KEY={api_key}\n")

    click.echo("Configuration saved successfully!")

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

        prompt = f"""{rules}

Diff:
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
