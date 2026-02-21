"""Tests for the emoji toggle feature."""
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from smart_commit.main import _build_prompt, cli


# ─────────────────────────────────────────────
# _build_prompt
# ─────────────────────────────────────────────

class TestBuildPrompt:
    def _call(self, use_emoji):
        return _build_prompt(
            diff="diff --git a/foo.py",
            staged_files=["foo.py"],
            rules="- rule one",
            use_emoji=use_emoji,
        )

    def test_emoji_on_format_line_includes_emoji_placeholder(self):
        prompt = self._call(use_emoji=True)
        assert "<emoji> type(scope): subject" in prompt

    def test_emoji_off_format_line_has_no_emoji_placeholder(self):
        prompt = self._call(use_emoji=False)
        assert "<emoji>" not in prompt
        assert "type(scope): subject" in prompt

    def test_emoji_on_types_section_lists_emojis(self):
        prompt = self._call(use_emoji=True)
        assert "✨" in prompt
        assert "🐛" in prompt

    def test_emoji_off_types_section_has_no_emojis(self):
        prompt = self._call(use_emoji=False)
        # Commit type labels still present, but unicode emoji stripped
        assert "`feat`" in prompt
        assert "`fix`" in prompt
        assert "✨" not in prompt
        assert "🐛" not in prompt

    def test_emoji_on_examples_contain_emojis(self):
        prompt = self._call(use_emoji=True)
        assert "✨ feat(auth)" in prompt

    def test_emoji_off_examples_have_no_emojis(self):
        prompt = self._call(use_emoji=False)
        assert "feat(auth)" in prompt
        assert "✨ feat(auth)" not in prompt

    def test_diff_and_files_always_included(self):
        for flag in (True, False):
            prompt = self._call(use_emoji=flag)
            assert "foo.py" in prompt
            assert "diff --git a/foo.py" in prompt

    def test_rules_always_included(self):
        for flag in (True, False):
            prompt = self._call(use_emoji=flag)
            assert "rule one" in prompt


# ─────────────────────────────────────────────
# commit CLI --no-emoji flag
# ─────────────────────────────────────────────

def _make_config(auto_emoji=True):
    cfg = MagicMock()
    cfg.ai.model = "gemini-2.5-flash"
    cfg.ai.rules = []
    cfg.commit.auto_emoji = auto_emoji
    return cfg


def _make_model(message="feat(ui): add button"):
    model = MagicMock()
    model.generate_content.return_value.text = message
    return model


class TestCommitEmojiFlag:
    def test_no_emoji_flag_disables_emoji_in_prompt(self):
        captured = {}
        runner = CliRunner()
        mock_model = MagicMock()

        def capture_prompt(prompt):
            captured["prompt"] = prompt
            result = MagicMock()
            result.text = "feat(ui): add button"
            return result

        mock_model.generate_content.side_effect = capture_prompt

        with patch("smart_commit.main.load_config", return_value=_make_config()), \
             patch("smart_commit.main.initialize", return_value=mock_model), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["ui.py"]), \
             patch("smart_commit.main.commit_with_message"):
            runner.invoke(cli, ["commit", "--no-confirm", "--no-emoji"])

        assert "<emoji>" not in captured.get("prompt", "")

    def test_default_uses_emoji_in_prompt(self):
        captured = {}
        runner = CliRunner()
        mock_model = MagicMock()

        def capture_prompt(prompt):
            captured["prompt"] = prompt
            result = MagicMock()
            result.text = "✨ feat(ui): add button"
            return result

        mock_model.generate_content.side_effect = capture_prompt

        with patch("smart_commit.main.load_config", return_value=_make_config(auto_emoji=True)), \
             patch("smart_commit.main.initialize", return_value=mock_model), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["ui.py"]), \
             patch("smart_commit.main.commit_with_message"):
            runner.invoke(cli, ["commit", "--no-confirm"])

        assert "<emoji>" in captured.get("prompt", "")

    def test_config_auto_emoji_false_disables_emoji(self):
        captured = {}
        runner = CliRunner()
        mock_model = MagicMock()

        def capture_prompt(prompt):
            captured["prompt"] = prompt
            result = MagicMock()
            result.text = "feat(ui): add button"
            return result

        mock_model.generate_content.side_effect = capture_prompt

        with patch("smart_commit.main.load_config", return_value=_make_config(auto_emoji=False)), \
             patch("smart_commit.main.initialize", return_value=mock_model), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["ui.py"]), \
             patch("smart_commit.main.commit_with_message"):
            runner.invoke(cli, ["commit", "--no-confirm"])

        assert "<emoji>" not in captured.get("prompt", "")

    def test_no_emoji_flag_overrides_auto_emoji_true(self):
        """--no-emoji takes precedence even when config has auto_emoji=True."""
        captured = {}
        runner = CliRunner()
        mock_model = MagicMock()

        def capture_prompt(prompt):
            captured["prompt"] = prompt
            result = MagicMock()
            result.text = "feat(ui): add button"
            return result

        mock_model.generate_content.side_effect = capture_prompt

        with patch("smart_commit.main.load_config", return_value=_make_config(auto_emoji=True)), \
             patch("smart_commit.main.initialize", return_value=mock_model), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["ui.py"]), \
             patch("smart_commit.main.commit_with_message"):
            runner.invoke(cli, ["commit", "--no-confirm", "--no-emoji"])

        assert "<emoji>" not in captured.get("prompt", "")

    def test_commit_still_succeeds_with_no_emoji(self):
        runner = CliRunner()
        with patch("smart_commit.main.load_config", return_value=_make_config()), \
             patch("smart_commit.main.initialize", return_value=_make_model()), \
             patch("smart_commit.main.get_git_diff", return_value="diff content"), \
             patch("smart_commit.main.get_staged_files", return_value=["ui.py"]), \
             patch("smart_commit.main.commit_with_message") as mock_commit:
            result = runner.invoke(cli, ["commit", "--no-confirm", "--no-emoji"])
        assert result.exit_code == 0
        mock_commit.assert_called_once()
