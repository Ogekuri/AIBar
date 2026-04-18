"""
@file
@brief Setup runtime-config prompt and persistence tests.
@details Verifies setup prompt order for idle-delay, API-call delay milliseconds,
API-call timeout milliseconds, default Retry-After seconds, gnome-refresh-interval,
billing dataset, provider activation flags, Copilot extra premium-request unit
cost, and per-provider currency symbol fields, then final logging mode fields;
persists selected values to `~/.config/aibar/config.json`.
@satisfies REQ-005
@satisfies REQ-049
@satisfies REQ-123
@satisfies TST-013
@satisfies TST-055
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
    monkeypatch.setattr(
        config_module, "RUNTIME_CONFIG_PATH", config_dir / "config.json"
    )
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


def test_setup_prompts_runtime_config_before_credentials(
    monkeypatch, tmp_path: Path
) -> None:
    """
    @brief Verify setup prompt order and runtime-config persistence.
    @details Ensures setup asks `idle-delay` first, `api-call delay` second,
    `api-call timeout` third, `default-retry-after` fourth,
    `gnome-refresh-interval` fifth, `billing_data` sixth, provider activation
    toggles seventh through twelfth in order `claude`, `openrouter`,
    `copilot`, `codex`, `openai`, `geminiai`, Copilot extra premium-request
    unit cost thirteenth, then per-provider currency symbols, then GeminiAI
    OAuth source prompt, provider credential prompts, final logging prompts,
    then writes all selected values to runtime config JSON.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-005
    @satisfies REQ-049
    @satisfies REQ-123
    @satisfies TST-013
    @satisfies TST-055
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    prompts: list[str] = []
    # 6 runtime values + 6 provider toggles + Copilot overage + 6 currency
    # symbols + OAuth source + empty credentials + 2 logging modes
    responses = iter(
        [
            450,
            2500,
            5200,
            3600,
            90,
            "billing_data",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            0.04,
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "skip",
            "",
            "",
            "",
            "enable",
            "disable",
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
    assert prompts[1] == "  api-call delay milliseconds"
    assert prompts[2] == "  api-call timeout milliseconds"
    assert prompts[3] == "  default-retry-after seconds"
    assert prompts[4] == "  gnome-refresh-interval seconds"
    assert prompts[5] == "  billing_data"
    assert prompts[6] == "  claude statistics mode"
    assert prompts[7] == "  openrouter statistics mode"
    assert prompts[8] == "  copilot statistics mode"
    assert prompts[9] == "  codex statistics mode"
    assert prompts[10] == "  openai statistics mode"
    assert prompts[11] == "  geminiai statistics mode"
    assert prompts[12] == "  copilot extra premium request cost (USD/request)"
    assert prompts[13] == "  claude currency symbol"
    assert prompts[14] == "  openai currency symbol"
    assert prompts[15] == "  openrouter currency symbol"
    assert prompts[16] == "  copilot currency symbol"
    assert prompts[17] == "  codex currency symbol"
    assert prompts[18] == "  geminiai currency symbol"
    assert prompts[19] == "  geminiai oauth source"
    assert prompts[20] == "  OPENROUTER_API_KEY"
    assert prompts[21] == "  OPENAI_ADMIN_KEY"
    assert prompts[22] == "  GITHUB_TOKEN"
    assert prompts[23] == "  execution log mode"
    assert prompts[24] == "  debug api log mode"

    runtime_config = json.loads(
        (config_dir / "config.json").read_text(encoding="utf-8")
    )
    assert runtime_config["idle_delay_seconds"] == 450
    assert runtime_config["api_call_delay_milliseconds"] == 2500
    assert runtime_config["api_call_timeout_milliseconds"] == 5200
    assert runtime_config["default_retry_after_seconds"] == 3600
    assert runtime_config["gnome_refresh_interval_seconds"] == 90
    assert runtime_config["billing_data"] == "billing_data"
    assert runtime_config["enabled_providers"] == {
        "claude": True,
        "openrouter": True,
        "copilot": True,
        "codex": True,
        "openai": True,
        "geminiai": True,
    }
    assert runtime_config["copilot_extra_premium_request_cost"] == 0.04
    assert runtime_config["currency_symbols"] == {
        "claude": "$",
        "openai": "$",
        "openrouter": "$",
        "copilot": "$",
        "codex": "$",
        "geminiai": "$",
    }
    assert runtime_config["geminiai_project_id"] is None
    assert runtime_config["log_enabled"] is True
    assert runtime_config["debug_enabled"] is False
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
            1000,
            5000,
            3600,
            60,
            "billing_data",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            0.04,
            "$",
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
            "enable",
            "enable",
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
    assert (
        client_doc["installed"]["client_id"]
        == "example-client.apps.googleusercontent.com"
    )
    assert client_doc["installed"]["project_id"] == "gen-lang-client-0834428245"
    assert not token_path.exists()

    runtime_doc = json.loads((config_dir / "config.json").read_text(encoding="utf-8"))
    assert runtime_doc["geminiai_project_id"] == "gen-lang-client-0834428245"
    assert runtime_doc["billing_data"] == "billing_data"
    assert runtime_doc["enabled_providers"] == {
        "claude": True,
        "openrouter": True,
        "copilot": True,
        "codex": True,
        "openai": True,
        "geminiai": True,
    }
    assert runtime_doc["log_enabled"] is True
    assert runtime_doc["debug_enabled"] is True
    assert "geminiai_billing_account" not in runtime_doc


def test_setup_geminiai_oauth_login_source_reauthorizes_with_current_scopes(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify setup `login` OAuth source re-runs GeminiAI authorization.
    @details Creates persisted GeminiAI OAuth client config, selects setup source
    `login`, and asserts `authorize_interactively` is called once with
    `GEMINIAI_OAUTH_SCOPES`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-055
    @satisfies REQ-056
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    from aibar.providers import geminiai as geminiai_module

    client_path = config_dir / "geminiai_oauth_client.json"
    token_path = config_dir / "geminiai_oauth_token.json"
    monkeypatch.setattr(geminiai_module, "GEMINIAI_OAUTH_CLIENT_PATH", client_path)
    monkeypatch.setattr(geminiai_module, "GEMINIAI_OAUTH_TOKEN_PATH", token_path)

    client_path.parent.mkdir(parents=True, exist_ok=True)
    client_path.write_text(
        json.dumps(
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
        ),
        encoding="utf-8",
    )

    recorded_scopes: list[tuple[str, ...]] = []

    def _fake_authorize(self: object, scopes: tuple[str, ...] = ()) -> object:
        """
        @brief Capture scopes used by setup login-triggered OAuth authorization.
        @param self {object} Credential store instance.
        @param scopes {tuple[str, ...]} OAuth scopes passed by setup flow.
        @return {object} Placeholder credentials object.
        """
        del self
        recorded_scopes.append(tuple(scopes))
        return object()

    monkeypatch.setattr(
        geminiai_module.GeminiAICredentialStore,
        "authorize_interactively",
        _fake_authorize,
    )

    responses = iter(
        [
            300,
            1000,
            5000,
            3600,
            60,
            "billing_data",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            0.04,
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "login",
            "",
            "",
            "",
            "",
            "disable",
            "enable",
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
        @brief Return deterministic prompt responses for setup login-source flow.
        @param text {str} Prompt label.
        @param default {object | None} Prompt default value.
        @param show_default {bool} Prompt default visibility flag.
        @param type {object | None} Optional click type.
        @return {object} Predetermined prompt response.
        """
        del text, default, show_default, type, kwargs
        return next(responses)

    monkeypatch.setattr("aibar.cli.click.prompt", _fake_prompt)

    runner = CliRunner()
    result = runner.invoke(main, ["setup"])
    assert result.exit_code == 0, result.output
    assert recorded_scopes == [geminiai_module.GEMINIAI_OAUTH_SCOPES]
    runtime_doc = json.loads((config_dir / "config.json").read_text(encoding="utf-8"))
    assert runtime_doc["enabled_providers"] == {
        "claude": True,
        "openrouter": True,
        "copilot": True,
        "codex": True,
        "openai": True,
        "geminiai": True,
    }
    assert runtime_doc["log_enabled"] is False
    assert runtime_doc["debug_enabled"] is True
