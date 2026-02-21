"""
Comprehensive tests for smart_commit package.

Covers: safe_echo, configure_utf8_output, initialize, get_git_diff,
        get_staged_files, commit_with_message, config/status/commit CLI
        commands, Pydantic models, and load_config.
"""
import os
import sys
import subprocess
import pytest
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner
from pydantic import ValidationError

from smart_commit.main import (
    safe_echo,
    configure_utf8_output,
    initialize,
    get_git_diff,
    get_staged_files,
    commit_with_message,
    cli,
)
from smart_commit.config_loader import (
    AIConfig,
    CommitConfig,
    GitConfig,
    Config,
    load_config,
)


# ─────────────────────────────────────────────
# 1. safe_echo
# ─────────────────────────────────────────────

class TestSafeEcho:
    def test_normal_message_printed(self):
        with patch("smart_commit.main.click.echo") as mock_echo:
            safe_echo("hello world")
        mock_echo.assert_called_once_with("hello world")

    def test_emoji_message_on_supported_system(self):
        with patch("smart_commit.main.click.echo") as mock_echo:
            safe_echo("✅ success")
        mock_echo.assert_called_once_with("✅ success")

    def test_unicode_encode_error_triggers_fallback(self):
        """On UnicodeEncodeError, non-ASCII is stripped and retried."""
        first_call = True

        def raise_once(msg, **kwargs):
            nonlocal first_call
            if first_call:
                first_call = False
                raise UnicodeEncodeError("ascii", msg, 0, 1, "ordinal out of range")

        with patch("smart_commit.main.click.echo", side_effect=raise_once) as mock_echo:
            safe_echo("✅ done")

        assert mock_echo.call_count == 2
        fallback_msg = mock_echo.call_args_list[1][0][0]
        assert all(ord(c) < 128 for c in fallback_msg)

    def test_err_kwarg_forwarded(self):
        with patch("smart_commit.main.click.echo") as mock_echo:
            safe_echo("oops", err=True)
        mock_echo.assert_called_once_with("oops", err=True)


# ─────────────────────────────────────────────
# 2. configure_utf8_output
# ─────────────────────────────────────────────

class TestConfigureUtf8Output:
    def test_non_windows_does_not_call_reconfigure(self):
        with patch("smart_commit.main.sys") as mock_sys:
            mock_sys.platform = "darwin"
            mock_sys.stdout = MagicMock()
            configure_utf8_output()
            mock_sys.stdout.reconfigure.assert_not_called()

    def test_windows_calls_reconfigure_utf8(self):
        with patch("smart_commit.main.sys") as mock_sys:
            mock_sys.platform = "win32"
            mock_sys.stdout = MagicMock(spec=["reconfigure"])
            mock_sys.stderr = MagicMock(spec=["reconfigure"])
            configure_utf8_output()
            mock_sys.stdout.reconfigure.assert_called_once_with(encoding="utf-8")
            mock_sys.stderr.reconfigure.assert_called_once_with(encoding="utf-8")

    def test_windows_attribute_error_swallowed(self):
        with patch("smart_commit.main.sys") as mock_sys:
            mock_sys.platform = "win32"
            mock_sys.stdout = MagicMock()
            mock_sys.stdout.reconfigure.side_effect = AttributeError("no reconfigure")
            mock_sys.stderr = MagicMock()
            configure_utf8_output()  # must not raise

    def test_windows_oserror_swallowed(self):
        with patch("smart_commit.main.sys") as mock_sys:
            mock_sys.platform = "win32"
            mock_sys.stdout = MagicMock()
            mock_sys.stdout.reconfigure.side_effect = OSError("io error")
            mock_sys.stderr = MagicMock()
            configure_utf8_output()  # must not raise


# ─────────────────────────────────────────────
# 3. initialize
# ─────────────────────────────────────────────

class TestInitialize:
    def test_app_env_loaded_with_override_when_exists(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GOOGLE_API_KEY=validkey1234567890abcdef\n")

        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)), \
             patch("smart_commit.main.load_dotenv") as mock_dotenv, \
             patch("smart_commit.main.os.getenv", return_value="validkey1234567890abcdef"), \
             patch("smart_commit.main.genai.configure"), \
             patch("smart_commit.main.genai.GenerativeModel"):
            initialize()

        mock_dotenv.assert_called_once_with(str(env_file), override=True)

    def test_falls_back_to_plain_load_dotenv_when_no_app_env(self, tmp_path):
        # tmp_path exists but has no .env file
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)), \
             patch("smart_commit.main.load_dotenv") as mock_dotenv, \
             patch("smart_commit.main.os.getenv", return_value="fallbackkey1234567890"), \
             patch("smart_commit.main.genai.configure"), \
             patch("smart_commit.main.genai.GenerativeModel"):
            initialize()

        mock_dotenv.assert_called_once_with()

    def test_missing_api_key_raises_value_error(self, tmp_path):
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)), \
             patch("smart_commit.main.load_dotenv"), \
             patch("smart_commit.main.os.getenv", return_value=None):
            with pytest.raises(ValueError, match="GOOGLE_API_KEY not found"):
                initialize()

    def test_custom_model_name_forwarded(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GOOGLE_API_KEY=somekey1234567890abcdef\n")

        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)), \
             patch("smart_commit.main.load_dotenv"), \
             patch("smart_commit.main.os.getenv", return_value="somekey1234567890abcdef"), \
             patch("smart_commit.main.genai.configure"), \
             patch("smart_commit.main.genai.GenerativeModel") as mock_model:
            initialize(model_name="gemini-2.0-flash")

        mock_model.assert_called_once_with(model_name="gemini-2.0-flash")

    def test_default_model_is_gemini_25_flash(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GOOGLE_API_KEY=somekey1234567890abcdef\n")

        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)), \
             patch("smart_commit.main.load_dotenv"), \
             patch("smart_commit.main.os.getenv", return_value="somekey1234567890abcdef"), \
             patch("smart_commit.main.genai.configure"), \
             patch("smart_commit.main.genai.GenerativeModel") as mock_model:
            initialize()

        mock_model.assert_called_once_with(model_name="gemini-2.5-flash")


# ─────────────────────────────────────────────
# 4. get_git_diff
# ─────────────────────────────────────────────

class TestGetGitDiff:
    def test_returns_stripped_diff(self):
        with patch("smart_commit.main.subprocess.check_output",
                   return_value="  diff content  \n"):
            result = get_git_diff()
        assert result == "diff content"

    def test_returns_empty_string_when_no_changes(self):
        with patch("smart_commit.main.subprocess.check_output", return_value=""):
            result = get_git_diff()
        assert result == ""

    def test_called_process_error_returns_empty_and_prints_stderr(self):
        with patch("smart_commit.main.subprocess.check_output",
                   side_effect=subprocess.CalledProcessError(1, "git")), \
             patch("smart_commit.main.safe_echo") as mock_echo:
            result = get_git_diff()
        assert result == ""
        mock_echo.assert_called_once()
        assert mock_echo.call_args[1].get("err") is True


# ─────────────────────────────────────────────
# 5. get_staged_files
# ─────────────────────────────────────────────

class TestGetStagedFiles:
    def test_multiple_staged_files(self):
        with patch("smart_commit.main.subprocess.check_output",
                   return_value="file1.py\nfile2.py\nfile3.py"):
            result = get_staged_files()
        assert result == ["file1.py", "file2.py", "file3.py"]

    def test_single_staged_file(self):
        with patch("smart_commit.main.subprocess.check_output",
                   return_value="main.py"):
            result = get_staged_files()
        assert result == ["main.py"]

    def test_no_staged_files_returns_empty_list(self):
        with patch("smart_commit.main.subprocess.check_output", return_value=""):
            result = get_staged_files()
        assert result == []

    def test_called_process_error_returns_empty_and_prints_stderr(self):
        with patch("smart_commit.main.subprocess.check_output",
                   side_effect=subprocess.CalledProcessError(1, "git")), \
             patch("smart_commit.main.safe_echo") as mock_echo:
            result = get_staged_files()
        assert result == []
        mock_echo.assert_called_once()
        assert mock_echo.call_args[1].get("err") is True


# ─────────────────────────────────────────────
# 6. commit_with_message
# ─────────────────────────────────────────────

class TestCommitWithMessage:
    def test_successful_commit_runs_git_and_prints(self):
        with patch("smart_commit.main.subprocess.run") as mock_run, \
             patch("smart_commit.main.safe_echo") as mock_echo:
            commit_with_message("feat(scope): add thing")
        mock_run.assert_called_once_with(
            ["git", "commit", "-m", "feat(scope): add thing"], check=True
        )
        mock_echo.assert_called_once_with("Successfully committed!")

    def test_failed_commit_prints_error_does_not_raise(self):
        with patch("smart_commit.main.subprocess.run",
                   side_effect=subprocess.CalledProcessError(1, "git")), \
             patch("smart_commit.main.safe_echo") as mock_echo:
            commit_with_message("any message")  # must not raise
        mock_echo.assert_called_once()
        assert mock_echo.call_args[1].get("err") is True


# ─────────────────────────────────────────────
# 7. Pydantic models
# ─────────────────────────────────────────────

class TestAIConfig:
    def test_defaults(self):
        cfg = AIConfig()
        assert cfg.model == "gemini-2.5-flash"
        assert cfg.temperature == 0.7
        assert cfg.max_tokens == 100
        assert cfg.rules == []

    def test_temperature_zero_valid(self):
        AIConfig(temperature=0.0)

    def test_temperature_one_valid(self):
        AIConfig(temperature=1.0)

    def test_temperature_below_zero_raises(self):
        with pytest.raises(ValidationError):
            AIConfig(temperature=-0.1)

    def test_temperature_above_one_raises(self):
        with pytest.raises(ValidationError):
            AIConfig(temperature=1.1)

    def test_max_tokens_one_valid(self):
        AIConfig(max_tokens=1)

    def test_max_tokens_zero_raises(self):
        with pytest.raises(ValidationError):
            AIConfig(max_tokens=0)

    def test_max_tokens_negative_raises(self):
        with pytest.raises(ValidationError):
            AIConfig(max_tokens=-1)

    def test_custom_model(self):
        cfg = AIConfig(model="gemini-1.5-pro")
        assert cfg.model == "gemini-1.5-pro"

    def test_rules_list(self):
        cfg = AIConfig(rules=["rule one", "rule two"])
        assert cfg.rules == ["rule one", "rule two"]


class TestCommitConfig:
    def test_defaults(self):
        cfg = CommitConfig()
        assert cfg.auto_emoji is True
        assert cfg.validate_conventional is True
        assert cfg.preview_diff is True
        assert cfg.interactive_mode is True
        assert "feat" in cfg.allowed_types

    def test_flags_toggled_false(self):
        cfg = CommitConfig(auto_emoji=False, validate_conventional=False)
        assert cfg.auto_emoji is False
        assert cfg.validate_conventional is False

    def test_custom_allowed_types(self):
        cfg = CommitConfig(allowed_types=["feat", "fix"])
        assert cfg.allowed_types == ["feat", "fix"]


class TestGitConfig:
    def test_defaults(self):
        cfg = GitConfig()
        assert cfg.branch_reference is True
        assert cfg.similar_commits == 3

    def test_similar_commits_zero_valid(self):
        GitConfig(similar_commits=0)

    def test_similar_commits_negative_raises(self):
        with pytest.raises(ValidationError):
            GitConfig(similar_commits=-1)

    def test_branch_reference_false(self):
        cfg = GitConfig(branch_reference=False)
        assert cfg.branch_reference is False


class TestConfigModel:
    def test_full_construction(self):
        cfg = Config(ai=AIConfig(), commit=CommitConfig(), git=GitConfig())
        assert isinstance(cfg.ai, AIConfig)
        assert isinstance(cfg.commit, CommitConfig)
        assert isinstance(cfg.git, GitConfig)


# ─────────────────────────────────────────────
# 8. load_config
# ─────────────────────────────────────────────

VALID_CONFIG_YAML = """
ai:
  model: "gemini-2.5-flash"
  temperature: 0.5
  max_tokens: 50
  rules: []
commit:
  auto_emoji: true
  validate_conventional: true
  preview_diff: true
  interactive_mode: true
  allowed_types: [feat, fix]
git:
  branch_reference: true
  similar_commits: 2
"""

class TestLoadConfig:
    def test_loads_from_explicit_path(self, tmp_path):
        config_file = tmp_path / "config.yml"
        config_file.write_text(VALID_CONFIG_YAML)
        cfg = load_config(str(config_file))
        assert cfg.ai.model == "gemini-2.5-flash"
        assert cfg.git.similar_commits == 2

    def test_raises_file_not_found_when_no_config(self):
        # Patch open so every path lookup raises FileNotFoundError
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                load_config("/nonexistent/path.yml")

    def test_invalid_yaml_raises(self, tmp_path):
        config_file = tmp_path / "config.yml"
        config_file.write_text("ai: [\n  unclosed bracket")
        with pytest.raises(Exception):
            load_config(str(config_file))

    def test_invalid_field_value_raises_validation_error(self, tmp_path):
        config_file = tmp_path / "config.yml"
        config_file.write_text("""
ai:
  temperature: 9.9
  max_tokens: 50
  rules: []
commit:
  auto_emoji: true
  validate_conventional: true
  preview_diff: true
  interactive_mode: true
  allowed_types: [feat]
git:
  branch_reference: true
  similar_commits: 1
""")
        with pytest.raises(Exception):
            load_config(str(config_file))

    def test_loads_project_config_yml_successfully(self):
        """The actual bundled config.yml loads without error."""
        cfg = load_config()
        assert cfg.ai.model == "gemini-2.5-flash"
        assert cfg.ai.temperature == 0.5
        assert len(cfg.ai.rules) > 0
        assert cfg.git.similar_commits >= 0


# ─────────────────────────────────────────────
# 9. config CLI command
# ─────────────────────────────────────────────

class TestConfigCommand:
    def test_api_key_flag_saves_to_env_file(self, tmp_path):
        key = "A" * 40
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)):
            result = runner.invoke(cli, ["config", "--provider", "google", "--api-key", key])
        assert result.exit_code == 0
        env_file = tmp_path / ".env"
        assert env_file.exists()
        assert f"GOOGLE_API_KEY={key}" in env_file.read_text()

    def test_env_file_has_correct_format(self, tmp_path):
        key = "B" * 40
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)):
            runner.invoke(cli, ["config", "--provider", "google", "--api-key", key])
        content = (tmp_path / ".env").read_text()
        assert content == f"GOOGLE_API_KEY={key}\n"

    def test_interactive_mode_saves_key(self, tmp_path):
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)):
            result = runner.invoke(cli, ["config"], input="\n" + ("C" * 39) + "\n")
        assert result.exit_code == 0
        assert (tmp_path / ".env").exists()

    def test_short_key_exits_1_with_error_message(self, tmp_path):
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)):
            result = runner.invoke(cli, ["config", "--api-key", "tooshort"])
        assert result.exit_code == 1

    def test_creates_config_directory_if_missing(self, tmp_path):
        new_dir = str(tmp_path / "nested" / "smart-commit")
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=new_dir):
            result = runner.invoke(cli, ["config", "--provider", "google", "--api-key", "D" * 40])
        assert result.exit_code == 0
        assert os.path.isdir(new_dir)

    def test_success_message_displayed(self, tmp_path):
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)):
            result = runner.invoke(cli, ["config", "--provider", "google", "--api-key", "E" * 40])
        assert "API key saved successfully" in result.output

    def test_overwrites_existing_env_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GOOGLE_API_KEY=oldkey\n")
        new_key = "F" * 40
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)):
            runner.invoke(cli, ["config", "--provider", "google", "--api-key", new_key])
        assert f"GOOGLE_API_KEY={new_key}" in env_file.read_text()


# ─────────────────────────────────────────────
# 10. status CLI command
# ─────────────────────────────────────────────

class TestStatusCommand:
    def test_missing_config_dir_shows_error_exits_early(self, tmp_path):
        missing = str(tmp_path / "nonexistent")
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=missing):
            result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "Config directory: Not found" in result.output
        assert "Configuration file" not in result.output

    def test_missing_env_file_shows_error(self, tmp_path):
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)):
            result = runner.invoke(cli, ["status"])
        assert "Config directory: Found" in result.output
        assert "Configuration file: Not found" in result.output

    def test_valid_key_shows_all_green(self, tmp_path):
        valid_key = "X" * 39
        env_file = tmp_path / ".env"
        env_file.write_text(f"GOOGLE_API_KEY={valid_key}\n")
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)), \
             patch("smart_commit.main.os.getenv", return_value=valid_key):
            result = runner.invoke(cli, ["status"])
        assert "Configured and valid" in result.output
        assert "ready to use" in result.output

    def test_short_api_key_shows_invalid(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("GOOGLE_API_KEY=short\n")
        runner = CliRunner()
        with patch("smart_commit.main.click.get_app_dir", return_value=str(tmp_path)), \
             patch("smart_commit.main.os.getenv", return_value="short"):
            result = runner.invoke(cli, ["status"])
        assert "Invalid or missing" in result.output


# ─────────────────────────────────────────────
# 11. commit CLI command
# ─────────────────────────────────────────────

def _make_config():
    """Return a fully configured mock Config."""
    cfg = MagicMock()
    cfg.ai.model = "gemini-2.5-flash"
    cfg.ai.rules = ["rule one", "rule two"]
    return cfg

def _make_model(message="✨ feat(test): add feature"):
    """Return a mock generate callable (initialize returns a callable)."""
    return MagicMock(return_value=message)


class TestCommitCommand:
    def test_no_staged_changes_exits_1(self):
        runner = CliRunner()
        with patch("smart_commit.main.load_config", return_value=_make_config()), \
             patch("smart_commit.main.initialize", return_value=_make_model()), \
             patch("smart_commit.main.get_git_diff", return_value=""):
            result = runner.invoke(cli, ["commit"])
        assert result.exit_code == 1
        assert "No staged changes" in result.output

    def test_config_missing_exits_1(self):
        runner = CliRunner()
        with patch("smart_commit.main.load_config",
                   side_effect=FileNotFoundError("no config found")):
            result = runner.invoke(cli, ["commit"])
        assert result.exit_code == 1

    def test_missing_api_key_exits_1(self):
        runner = CliRunner()
        with patch("smart_commit.main.load_config", return_value=_make_config()), \
             patch("smart_commit.main.initialize",
                   side_effect=ValueError("GOOGLE_API_KEY not found")):
            result = runner.invoke(cli, ["commit"])
        assert result.exit_code == 1

    def test_api_failure_exits_1(self):
        broken_model = MagicMock()
        broken_model.generate_content.side_effect = Exception("quota exceeded")
        runner = CliRunner()
        with patch("smart_commit.main.load_config", return_value=_make_config()), \
             patch("smart_commit.main.initialize", return_value=broken_model), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["main.py"]):
            result = runner.invoke(cli, ["commit"])
        assert result.exit_code == 1

    def test_no_confirm_flag_commits_without_prompt(self):
        runner = CliRunner()
        with patch("smart_commit.main.load_config", return_value=_make_config()), \
             patch("smart_commit.main.initialize", return_value=_make_model()), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["main.py"]), \
             patch("smart_commit.main.commit_with_message") as mock_commit:
            result = runner.invoke(cli, ["commit", "--no-confirm"])
        assert result.exit_code == 0
        mock_commit.assert_called_once()

    def test_user_confirms_triggers_commit(self):
        runner = CliRunner()
        with patch("smart_commit.main.load_config", return_value=_make_config()), \
             patch("smart_commit.main.initialize", return_value=_make_model()), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["main.py"]), \
             patch("smart_commit.main.commit_with_message") as mock_commit:
            result = runner.invoke(cli, ["commit"], input="y\n")
        assert result.exit_code == 0
        mock_commit.assert_called_once()

    def test_user_declines_aborts_commit(self):
        runner = CliRunner()
        with patch("smart_commit.main.load_config", return_value=_make_config()), \
             patch("smart_commit.main.initialize", return_value=_make_model()), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["main.py"]), \
             patch("smart_commit.main.commit_with_message") as mock_commit:
            result = runner.invoke(cli, ["commit"], input="n\n")
        assert result.exit_code == 0
        mock_commit.assert_not_called()
        assert "Commit aborted" in result.output

    def test_generated_message_shown_to_user(self):
        msg = "✨ feat(ui): add button"
        runner = CliRunner()
        with patch("smart_commit.main.load_config", return_value=_make_config()), \
             patch("smart_commit.main.initialize", return_value=_make_model(msg)), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["ui.py"]), \
             patch("smart_commit.main.commit_with_message"):
            result = runner.invoke(cli, ["commit", "--no-confirm"])
        assert "feat(ui): add button" in result.output
