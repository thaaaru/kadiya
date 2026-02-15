import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from nanobot.cli.commands import app, _detect_provider

runner = CliRunner()


@pytest.fixture
def mock_paths():
    """Mock config/workspace paths for test isolation."""
    with patch("nanobot.config.loader.get_config_path") as mock_cp, \
         patch("nanobot.config.loader.save_config") as mock_sc, \
         patch("nanobot.config.loader.load_config") as mock_lc, \
         patch("nanobot.utils.helpers.get_workspace_path") as mock_ws:

        base_dir = Path("./test_onboard_data")
        if base_dir.exists():
            shutil.rmtree(base_dir)
        base_dir.mkdir()

        config_file = base_dir / "config.json"
        workspace_dir = base_dir / "workspace"

        mock_cp.return_value = config_file
        mock_ws.return_value = workspace_dir
        mock_sc.side_effect = lambda config, config_path=None: config_file.write_text("{}")

        yield config_file, workspace_dir, mock_lc

        if base_dir.exists():
            shutil.rmtree(base_dir)


def _run_onboard(mock_paths, input_text="sk-test-deepseek-key\nn\n", config_exists=False, config_content="{}"):
    """Helper to run onboard with mocked connectivity."""
    config_file, workspace_dir, mock_lc = mock_paths

    if config_exists:
        config_file.write_text(config_content)

    with patch("nanobot.cli.commands._generate_kadiya_config"), \
         patch("nanobot.cli.commands.httpx", create=True):
        result = runner.invoke(app, ["onboard"], input=input_text)
    return result


# --- Provider detection tests ---

def test_detect_openai_proj_key():
    """OpenAI project keys start with sk-proj-."""
    assert _detect_provider("sk-proj-abc123xyz456abc123xyz456abc123xyz456abc123xyz456abc123xyz456abc123xyz456") == "openai"


def test_detect_openai_long_key():
    """OpenAI legacy keys start with sk- but are longer than 60 chars."""
    assert _detect_provider("sk-" + "a" * 80) == "openai"


def test_detect_anthropic_key():
    """Anthropic keys start with sk-ant-."""
    assert _detect_provider("sk-ant-api03-abc123def456ghi789") == "anthropic"


def test_detect_groq_key():
    """Groq keys start with gsk_."""
    assert _detect_provider("gsk_abc123def456ghi789jkl012") == "groq"


def test_detect_gemini_key():
    """Gemini keys start with AIza."""
    assert _detect_provider("AIzaSyB-abc123def456ghi789") == "gemini"


def test_detect_openrouter_key():
    """OpenRouter keys start with sk-or-."""
    assert _detect_provider("sk-or-v1-abc123def456") == "openrouter"


def test_detect_deepseek_key():
    """DeepSeek keys start with sk- and are short."""
    assert _detect_provider("sk-abc123def456ghi789") == "deepseek"


def test_detect_unknown_key():
    """Unknown key patterns default to deepseek."""
    assert _detect_provider("some-random-key") == "deepseek"


# --- Onboard flow tests ---

def test_onboard_fresh_install(mock_paths):
    """No existing config — should create from scratch with guided setup."""
    config_file, workspace_dir, _ = mock_paths

    result = _run_onboard(mock_paths, input_text="sk-test-deepseek-key\nn\n")

    assert result.exit_code == 0
    assert "Detected provider" in result.stdout
    assert "DeepSeek" in result.stdout
    assert "Setup complete" in result.stdout
    assert config_file.exists()
    assert (workspace_dir / "AGENTS.md").exists()
    assert (workspace_dir / "memory" / "MEMORY.md").exists()


def test_onboard_detects_openai(mock_paths):
    """OpenAI key is auto-detected from sk-proj- prefix."""
    result = _run_onboard(mock_paths, input_text="sk-proj-abc123xyz456abc123xyz456abc123xyz456abc123xyz456abc123xyz456abc123xyz\nn\n")

    assert result.exit_code == 0
    assert "OpenAI" in result.stdout
    assert "Setup complete" in result.stdout


def test_onboard_detects_anthropic(mock_paths):
    """Anthropic key is auto-detected from sk-ant- prefix."""
    result = _run_onboard(mock_paths, input_text="sk-ant-api03-test-key-12345\nn\n")

    assert result.exit_code == 0
    assert "Anthropic" in result.stdout
    assert "Setup complete" in result.stdout


def test_onboard_detects_groq(mock_paths):
    """Groq key is auto-detected from gsk_ prefix."""
    result = _run_onboard(mock_paths, input_text="gsk_test-key-12345abcdef\nn\n")

    assert result.exit_code == 0
    assert "Groq" in result.stdout
    assert "Setup complete" in result.stdout


def test_onboard_detects_gemini(mock_paths):
    """Gemini key is auto-detected from AIza prefix."""
    result = _run_onboard(mock_paths, input_text="AIzaSyB-test-key-12345\nn\n")

    assert result.exit_code == 0
    assert "Gemini" in result.stdout
    assert "Setup complete" in result.stdout


def test_onboard_detects_openrouter(mock_paths):
    """OpenRouter key is auto-detected from sk-or- prefix."""
    result = _run_onboard(mock_paths, input_text="sk-or-v1-test-key-12345\nn\n")

    assert result.exit_code == 0
    assert "OpenRouter" in result.stdout
    assert "Setup complete" in result.stdout


def test_onboard_with_telegram(mock_paths):
    """User enables Telegram with a bot token."""
    result = _run_onboard(mock_paths, input_text="sk-test-deepseek-key\ny\n123456:ABC-DEF\n")

    assert result.exit_code == 0
    assert "Telegram configured" in result.stdout


def test_onboard_existing_config_loads(mock_paths):
    """Config exists — should load it and continue with guided setup."""
    config_file, workspace_dir, _ = mock_paths

    result = _run_onboard(mock_paths, input_text="sk-test-deepseek-key\nn\n", config_exists=True)

    assert result.exit_code == 0
    assert "Config loaded" in result.stdout
    assert "Setup complete" in result.stdout


def test_onboard_existing_workspace_safe_create(mock_paths):
    """Workspace exists — should not recreate, but still add missing templates."""
    config_file, workspace_dir, _ = mock_paths
    workspace_dir.mkdir(parents=True)

    result = _run_onboard(mock_paths, input_text="sk-test-deepseek-key\nn\n")

    assert result.exit_code == 0
    assert "Created workspace" not in result.stdout
    assert "Created AGENTS.md" in result.stdout
    assert (workspace_dir / "AGENTS.md").exists()
