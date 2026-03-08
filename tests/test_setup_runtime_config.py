"""
@file
@brief Setup runtime-config prompt and persistence tests.
@details Verifies setup prompt order for idle-delay, API-call delay, gnome-refresh-interval,
and per-provider currency symbol fields; persists selected values to `~/.config/aibar/config.json`.
@satisfies REQ-005
@satisfies REQ-049
@satisfies TST-013
"""

import json
from pathlib import Path

from click.testing import CliRunner

from aibar import config as config_module
from aibar.cli import main


def _patch_config_paths(monkeypatch, tmp_path: Path) -> Path:
    """
    @brief Redirect AIBar config/cache file paths to a temporary directory.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {Path} Effective `~/.config/aibar` replacement directory.
    """
    config_dir = tmp_path / ".config" / "aibar"
    cache_dir = tmp_path / ".cache" / "aibar"
    monkeypatch.setattr(config_module, "APP_CONFIG_DIR", config_dir)
    monkeypatch.setattr(config_module, "APP_CACHE_DIR", cache_dir)
    monkeypatch.setattr(config_module, "ENV_FILE_PATH", config_dir / "env")
    monkeypatch.setattr(config_module, "RUNTIME_CONFIG_PATH", config_dir / "config.json")
    monkeypatch.setattr(config_module, "CACHE_FILE_PATH", cache_dir / "cache.json")
    monkeypatch.setattr(config_module, "IDLE_TIME_PATH", cache_dir / "idle-time.json")
    return config_dir


def test_default_cache_and_idle_time_paths_use_home_cache_directory() -> None:
    """
    @brief Verify default CLI cache and idle-time paths target `~/.cache/aibar`.
    @details Asserts module-level path constants for cache and idle-time
    persistence resolve under the user cache directory, while runtime config
    remains in `~/.config/aibar`.
    @return {None} Function return value.
    @satisfies CTN-004
    @satisfies CTN-009
    """
    expected_cache_dir = Path.home() / ".cache" / "aibar"
    assert config_module.APP_CACHE_DIR == expected_cache_dir
    assert config_module.CACHE_FILE_PATH == expected_cache_dir / "cache.json"
    assert config_module.IDLE_TIME_PATH == expected_cache_dir / "idle-time.json"


def test_setup_prompts_runtime_config_before_credentials(monkeypatch, tmp_path: Path) -> None:
    """
    @brief Verify setup prompt order and runtime-config persistence.
    @details Ensures setup asks `idle-delay` first, `api-call delay` second,
    `gnome-refresh-interval` third, then per-provider currency symbols (one prompt
    per cost-enabled provider: claude, openai, openrouter, copilot, codex),
    then GeminiAI OAuth source prompt, then writes all selected values to runtime config JSON.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-005
    @satisfies REQ-049
    @satisfies TST-013
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    prompts: list[str] = []
    # 3 timeout values + 5 currency symbols + OAuth source + empty credentials
    responses = iter([450, 25, 90, "$", "$", "$", "$", "$", "skip", "", "", ""])

    def _fake_prompt(
        text: str,
        default=None,
        show_default: bool = True,
        type=None,
        **kwargs,
    ):
        """
        @brief Return deterministic prompt responses for setup flow.
        @param text {str} Prompt label.
        @param default {object | None} Prompt default value.
        @param show_default {bool} Flag indicating default rendering behavior.
        @param type {object | None} Optional click type.
        @return {object} Predetermined prompt response value.
        """
        del default, show_default, type, kwargs
        prompts.append(text)
        return next(responses)

    monkeypatch.setattr("aibar.cli.click.prompt", _fake_prompt)
    runner = CliRunner()
    result = runner.invoke(main, ["setup"])

    assert result.exit_code == 0
    assert prompts[0] == "  idle-delay seconds"
    assert prompts[1] == "  api-call delay seconds"
    assert prompts[2] == "  gnome-refresh-interval seconds"
    assert prompts[3] == "  claude currency symbol"
    assert prompts[4] == "  openai currency symbol"
    assert prompts[5] == "  openrouter currency symbol"
    assert prompts[6] == "  copilot currency symbol"
    assert prompts[7] == "  codex currency symbol"
    assert prompts[8] == "  geminiai oauth source"

    runtime_config = json.loads((config_dir / "config.json").read_text(encoding="utf-8"))
    assert runtime_config["idle_delay_seconds"] == 450
    assert runtime_config["api_call_delay_seconds"] == 25
    assert runtime_config["gnome_refresh_interval_seconds"] == 90
    assert runtime_config["currency_symbols"] == {
        "claude": "$",
        "openai": "$",
        "openrouter": "$",
        "copilot": "$",
        "codex": "$",
    }
    assert runtime_config["geminiai_project_id"] is None
    assert "geminiai_billing_account" not in runtime_config


def test_setup_accepts_geminiai_oauth_json_paste_and_persists_runtime_fields(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify setup persists GeminiAI OAuth client JSON and runtime identifiers.
    @details Simulates paste-mode OAuth client input, skips browser authorization,
    and asserts persisted client config plus `geminiai_project_id` runtime config field.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-055
    @satisfies REQ-056
    @satisfies TST-024
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    from aibar.providers import geminiai as geminiai_module

    client_path = config_dir / "geminiai_oauth_client.json"
    token_path = config_dir / "geminiai_oauth_token.json"
    monkeypatch.setattr(geminiai_module, "GEMINIAI_OAUTH_CLIENT_PATH", client_path)
    monkeypatch.setattr(geminiai_module, "GEMINIAI_OAUTH_TOKEN_PATH", token_path)

    oauth_payload = json.dumps(
        {
            "installed": {
                "client_id": "example-client.apps.googleusercontent.com",
                "project_id": "gen-lang-client-0834428245",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "example-secret",
                "redirect_uris": ["http://localhost"],
            }
        }
    )

    responses = iter(
        [
            300,
            20,
            60,
            "$",
            "$",
            "$",
            "$",
            "$",
            "paste",
            oauth_payload,
            "gen-lang-client-0834428245",
            "",
            "",
            "",
        ]
    )

    def _fake_prompt(
        text: str,
        default=None,
        show_default: bool = True,
        type=None,
        **kwargs,
    ):
        """
        @brief Return deterministic prompt responses for GeminiAI setup flow.
        @param text {str} Prompt label.
        @param default {object | None} Prompt default value.
        @param show_default {bool} Prompt default visibility flag.
        @param type {object | None} Optional click type.
        @return {object} Predetermined prompt response.
        """
        del text, default, show_default, type, kwargs
        return next(responses)

    monkeypatch.setattr("aibar.cli.click.prompt", _fake_prompt)
    monkeypatch.setattr("aibar.cli.click.confirm", lambda *args, **kwargs: False)

    runner = CliRunner()
    result = runner.invoke(main, ["setup"])
    assert result.exit_code == 0, result.output

    assert client_path.exists()
    client_doc = json.loads(client_path.read_text(encoding="utf-8"))
    assert client_doc["installed"]["client_id"] == "example-client.apps.googleusercontent.com"
    assert client_doc["installed"]["project_id"] == "gen-lang-client-0834428245"
    assert not token_path.exists()

    runtime_doc = json.loads((config_dir / "config.json").read_text(encoding="utf-8"))
    assert runtime_doc["geminiai_project_id"] == "gen-lang-client-0834428245"
    assert "geminiai_billing_account" not in runtime_doc
