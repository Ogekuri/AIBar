"""
@file
@brief GeminiAI cross-surface integration source assertions.
@details Verifies GeminiAI registration across CLI, setup/config, GNOME extension,
and dependency manifests.
@satisfies REQ-054
@satisfies REQ-059
@satisfies REQ-060
@satisfies REQ-061
@satisfies REQ-062
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = PROJECT_ROOT / "src" / "aibar" / "aibar" / "cli.py"
CONFIG_PATH = PROJECT_ROOT / "src" / "aibar" / "aibar" / "config.py"
EXTENSION_PATH = (
    PROJECT_ROOT
    / "src"
    / "aibar"
    / "gnome-extension"
    / "aibar@aibar.panel"
    / "extension.js"
)
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
REQUIREMENTS_PATH = PROJECT_ROOT / "requirements.txt"


def test_cli_registers_geminiai_provider_and_login_paths() -> None:
    """
    @brief Verify CLI source registers GeminiAI provider for show/setup/login.
    """
    source = CLI_PATH.read_text(encoding="utf-8")
    assert "ProviderName.GEMINIAI: GeminiAIProvider()," in source
    assert "geminiai oauth source" in source
    assert "billing_data" in source
    assert 'click.Choice(["skip", "file", "paste", "login"])' in source
    assert "_currency_provider_names = [p.value for p in ProviderName]" in source
    assert 'help="Provider to query (claude, openai, openrouter, copilot, codex, geminiai, all)"' in source
    assert 'help="Provider to login to (claude, copilot, geminiai)"' in source
    assert "_login_geminiai()" in source


def test_config_includes_geminiai_runtime_surfaces() -> None:
    """
    @brief Verify config/runtime source includes GeminiAI surfaces.
    """
    config_source = CONFIG_PATH.read_text(encoding="utf-8")

    assert 'ProviderName.GEMINIAI: "GEMINIAI_OAUTH_ACCESS_TOKEN"' in config_source
    assert '"name": "GeminiAI"' in config_source
    assert "geminiai_project_id: str | None = Field(default=None)" in config_source
    assert "billing_data: str = Field(default=DEFAULT_BILLING_DATASET, min_length=1)" in config_source


def test_extension_and_dependencies_include_geminiai_support() -> None:
    """
    @brief Verify GNOME extension and Python dependencies include GeminiAI support.
    """
    extension_source = EXTENSION_PATH.read_text(encoding="utf-8")
    pyproject_source = PYPROJECT_PATH.read_text(encoding="utf-8")
    requirements_source = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    assert "this._providerOrder = ['claude', 'openrouter', 'copilot', 'codex', 'geminiai'];" in extension_source
    assert "geminiai: 'GEMINIAI'" in extension_source
    assert "google-api-python-client" in pyproject_source
    assert "google-cloud-bigquery" in pyproject_source
    assert "google-auth-oauthlib" in pyproject_source
    assert "google-auth-httplib2" in pyproject_source
    assert "google-api-python-client" in requirements_source
    assert "google-cloud-bigquery" in requirements_source
    assert "google-auth-oauthlib" in requirements_source
    assert "google-auth-httplib2" in requirements_source
