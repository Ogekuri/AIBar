"""
@file
@brief Setup runtime-config prompt and persistence tests.
@details Verifies setup prompt order for provider activation flags first, then
idle-delay, API-call delay milliseconds, API-call timeout milliseconds, default
Retry-After seconds, gnome-refresh-interval, billing dataset, Copilot extra
premium-request unit cost, and per-provider currency symbol fields, then final
logging mode fields; persists selected values to
`~/.config/aibar/config.json`.
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
    @details Ensures setup asks provider activation toggles first through eighth
    in order `agy`, `openrouter`, `copilot`, `codex`, `openai`,
    `geminiai`, `zai`, `deepseek`, then asks `idle-delay` ninth,
    `api-call delay` tenth, `api-call timeout` eleventh,
    `default-retry-after` twelfth, `gnome-refresh-interval` thirteenth,
    `billing_data` fourteenth, Copilot extra premium-request unit cost
    fifteenth, then per-provider currency symbols,
    then GeminiAI service-account source prompt, provider credential prompts, final
    logging prompts, then writes all selected values to runtime config JSON.
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
    # 8 provider toggles + 6 runtime values + Copilot overage
    # + 7 currency symbols (agy excluded) + service-account source + empty credentials + 2 logging modes
    responses = iter(
        [
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            450,
            2500,
            5200,
            3600,
            90,
            "billing_data",
            0.04,
            "$",
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
    assert prompts[0] == "  agy statistics mode"
    assert prompts[1] == "  openrouter statistics mode"
    assert prompts[2] == "  copilot statistics mode"
    assert prompts[3] == "  codex statistics mode"
    assert prompts[4] == "  openai statistics mode"
    assert prompts[5] == "  geminiai statistics mode"
    assert prompts[6] == "  zai statistics mode"
    assert prompts[7] == "  deepseek statistics mode"
    assert prompts[8] == "  idle-delay seconds"
    assert prompts[9] == "  api-call delay milliseconds"
    assert prompts[10] == "  api-call timeout milliseconds"
    assert prompts[11] == "  default-retry-after seconds"
    assert prompts[12] == "  gnome-refresh-interval seconds"
    assert prompts[13] == "  billing_data"
    assert prompts[14] == "  copilot extra premium request cost (USD/request)"
    assert prompts[15] == "  openai currency symbol"
    assert prompts[16] == "  openrouter currency symbol"
    assert prompts[17] == "  copilot currency symbol"
    assert prompts[18] == "  codex currency symbol"
    assert prompts[19] == "  geminiai currency symbol"
    assert prompts[20] == "  zai currency symbol"
    assert prompts[21] == "  deepseek currency symbol"
    assert prompts[22] == "  geminiai service-account source"
    assert prompts[23] == "  OPENROUTER_API_KEY"
    assert prompts[24] == "  OPENAI_ADMIN_KEY"
    assert prompts[25] == "  GITHUB_TOKEN"
    assert prompts[26] == "  ZAI_API_KEY"
    assert prompts[27] == "  DEEPSEEK_API_KEY"
    assert prompts[28] == "  execution log mode"
    assert prompts[29] == "  debug api log mode"

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
        "agy": True,
        "openrouter": True,
        "copilot": True,
        "codex": True,
        "openai": True,
        "geminiai": True,
        "zai": True,
        "deepseek": True,
    }
    assert runtime_config["copilot_extra_premium_request_cost"] == 0.04
    assert runtime_config["currency_symbols"] == {
        "openai": "$",
        "openrouter": "$",
        "copilot": "$",
        "codex": "$",
        "geminiai": "$",
        "zai": "$",
        "deepseek": "$",
    }
    assert runtime_config["geminiai_project_id"] is None
    assert runtime_config["log_enabled"] is True
    assert runtime_config["debug_enabled"] is False
    assert "geminiai_billing_account" not in runtime_config


def _build_synthetic_service_account_payload() -> dict[str, object]:
    """
    @brief Build a synthetic Google Cloud service-account key document.
    @details Mirrors the standard Google Cloud console key-download field set
    (`type`, `project_id`, `private_key_id`, `private_key`, `client_email`,
    `client_id`, `auth_uri`, `token_uri`, `auth_provider_x509_cert_url`,
    `client_x509_cert_url`, `universe_domain`) using synthetic placeholder values;
    no real credential material is embedded.
    @return {dict[str, object]} Synthetic service-account key payload.
    """
    return {
        "type": "service_account",
        "project_id": "gen-lang-client-0834428245",
        "private_key_id": "synthetic-key-id",
        "private_key": (
            "-----BEGIN PRIVATE KEY-----\nMIIEsynthetic\n-----END PRIVATE KEY-----\n"
        ),
        "client_email": "synthetic@gen-lang-client-0834428245.iam.gserviceaccount.com",
        "client_id": "100000000000000000000",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": (
            "https://www.googleapis.com/robot/v1/metadata/x509/synthetic%40gen-lang-client-0834428245.iam.gserviceaccount.com"
        ),
        "universe_domain": "googleapis.com",
    }


def test_setup_accepts_geminiai_service_account_json_paste_and_persists_runtime_fields(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify setup persists pasted GeminiAI service-account key JSON verbatim.
    @details Simulates paste-mode service-account key input shaped like a Google
    Cloud console key download using synthetic values, answers the project-id
    prompt with its default, and asserts the persisted key document equals the
    input payload plus the `geminiai_project_id` runtime field derived from the
    key `project_id`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-055
    @satisfies REQ-056
    @satisfies REQ-257
    @satisfies TST-024
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    from aibar.providers import geminiai as geminiai_module

    service_account_path = config_dir / "geminiai_service_account.json"
    monkeypatch.setattr(
        geminiai_module, "GEMINIAI_SERVICE_ACCOUNT_PATH", service_account_path
    )

    service_account_payload = _build_synthetic_service_account_payload()

    responses = iter(
        [
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            300,
            1000,
            5000,
            3600,
            60,
            "billing_data",
            0.04,
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "paste",
            json.dumps(service_account_payload),
            ...,  # project-id prompt: accept the derived default
            "",
            "",
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
        @brief Return deterministic prompt responses for the GeminiAI paste flow.
        @details The Ellipsis response marker resolves to the prompt default so the
        derived project-id default supplied by setup is accepted verbatim.
        @param text {str} Prompt label.
        @param default {object | None} Prompt default value.
        @param show_default {bool} Flag indicating default rendering behavior.
        @param type {object | None} Optional click type.
        @return {object} Predetermined prompt response value.
        """
        del text, show_default, type, kwargs
        response = next(responses)
        if response is ...:
            return default
        return response

    monkeypatch.setattr("aibar.cli.click.prompt", _fake_prompt)

    runner = CliRunner()
    result = runner.invoke(main, ["setup"])
    assert result.exit_code == 0, result.output

    assert service_account_path.exists()
    key_doc = json.loads(service_account_path.read_text(encoding="utf-8"))
    assert key_doc == service_account_payload

    runtime_doc = json.loads((config_dir / "config.json").read_text(encoding="utf-8"))
    assert runtime_doc["geminiai_project_id"] == "gen-lang-client-0834428245"
    assert runtime_doc["billing_data"] == "billing_data"
    assert runtime_doc["enabled_providers"] == {
        "agy": True,
        "openrouter": True,
        "copilot": True,
        "codex": True,
        "openai": True,
        "geminiai": True,
        "zai": True,
        "deepseek": True,
    }
    assert runtime_doc["log_enabled"] is True
    assert runtime_doc["debug_enabled"] is True
    assert "geminiai_billing_account" not in runtime_doc


def test_setup_geminiai_service_account_file_source_persists_key_verbatim(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify setup `file` source persists the service-account key document verbatim.
    @details Writes a service-account key document with the full Google Cloud
    console field set to a temporary key file, selects the setup source `file`,
    and asserts every field (including optional fields such as `universe_domain`)
    survives persistence unchanged.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-257
    @satisfies TST-024
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    from aibar.providers import geminiai as geminiai_module

    service_account_path = config_dir / "geminiai_service_account.json"
    monkeypatch.setattr(
        geminiai_module, "GEMINIAI_SERVICE_ACCOUNT_PATH", service_account_path
    )

    key_source_path = tmp_path / "downloaded-gen-lang-client-key.json"
    service_account_payload = _build_synthetic_service_account_payload()
    key_source_path.write_text(json.dumps(service_account_payload), encoding="utf-8")

    responses = iter(
        [
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            300,
            1000,
            5000,
            3600,
            60,
            "billing_data",
            0.04,
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "file",
            str(key_source_path),
            ...,  # project-id prompt: accept the derived default
            "",
            "",
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
        @brief Return deterministic prompt responses for the GeminiAI file flow.
        @details The Ellipsis response marker resolves to the prompt default so the
        derived project-id default supplied by setup is accepted verbatim.
        @param text {str} Prompt label.
        @param default {object | None} Prompt default value.
        @param show_default {bool} Flag indicating default rendering behavior.
        @param type {object | None} Optional click type.
        @return {object} Predetermined prompt response value.
        """
        del text, show_default, type, kwargs
        response = next(responses)
        if response is ...:
            return default
        return response

    monkeypatch.setattr("aibar.cli.click.prompt", _fake_prompt)

    runner = CliRunner()
    result = runner.invoke(main, ["setup"])
    assert result.exit_code == 0, result.output

    assert service_account_path.exists()
    persisted_doc = json.loads(service_account_path.read_text(encoding="utf-8"))
    assert persisted_doc == service_account_payload
    assert persisted_doc["universe_domain"] == "googleapis.com"
    assert persisted_doc["type"] == "service_account"

    runtime_doc = json.loads((config_dir / "config.json").read_text(encoding="utf-8"))
    assert runtime_doc["geminiai_project_id"] == "gen-lang-client-0834428245"


def test_setup_rejects_oauth_client_json_as_gemini_credential(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify setup refuses OAuth client-secret JSON for GeminiAI credentials.
    @details Simulates paste-mode input carrying an OAuth desktop-client document
    (`installed` section) and asserts setup reports the service-account validation
    failure, persists no service-account key file, and still completes with the
    runtime configuration saved.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-055
    @satisfies REQ-257
    @satisfies TST-117
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    from aibar.providers import geminiai as geminiai_module

    service_account_path = config_dir / "geminiai_service_account.json"
    monkeypatch.setattr(
        geminiai_module, "GEMINIAI_SERVICE_ACCOUNT_PATH", service_account_path
    )

    oauth_client_payload = json.dumps(
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
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            300,
            1000,
            5000,
            3600,
            60,
            "billing_data",
            0.04,
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "paste",
            oauth_client_payload,
            "",
            "",
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
        @brief Return deterministic prompt responses for the rejection flow.
        @param text {str} Prompt label.
        @param default {object | None} Prompt default value.
        @param show_default {bool} Flag indicating default rendering behavior.
        @param type {object | None} Optional click type.
        @return {object} Predetermined prompt response value.
        """
        del text, default, show_default, type, kwargs
        return next(responses)

    monkeypatch.setattr("aibar.cli.click.prompt", _fake_prompt)

    runner = CliRunner()
    result = runner.invoke(main, ["setup"])
    assert result.exit_code == 0, result.output
    assert "GeminiAI service-account setup failed" in result.output
    assert not service_account_path.exists()

    runtime_doc = json.loads((config_dir / "config.json").read_text(encoding="utf-8"))
    assert runtime_doc["geminiai_project_id"] is None
    assert runtime_doc["log_enabled"] is False
    assert runtime_doc["debug_enabled"] is True


def test_setup_resolves_home_references_in_service_account_key_path(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify setup expands `~` and `$HOME` references in the key file path.
    @details Patches `HOME` to the temporary directory, writes the synthetic
    service-account key under `<tmp-home>/Desktop`, and answers the path prompt
    with a `~`-prefixed path in one run and a `$HOME`-prefixed path in a second
    run; asserts both runs read the key document and persist it verbatim.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-265
    @satisfies TST-118
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    from aibar.providers import geminiai as geminiai_module

    service_account_path = config_dir / "geminiai_service_account.json"
    monkeypatch.setattr(
        geminiai_module, "GEMINIAI_SERVICE_ACCOUNT_PATH", service_account_path
    )
    monkeypatch.setenv("HOME", str(tmp_path))

    key_relative_posix = "Desktop/gen-lang-client-0834428245-21e85e6435de.json"
    key_source_path = tmp_path / key_relative_posix
    key_source_path.parent.mkdir(parents=True, exist_ok=True)
    service_account_payload = _build_synthetic_service_account_payload()
    key_source_path.write_text(json.dumps(service_account_payload), encoding="utf-8")

    for raw_path_input in (f"~/{key_relative_posix}", f"$HOME/{key_relative_posix}"):
        service_account_path.unlink(missing_ok=True)
        responses = iter(
            [
                "enable",
                "enable",
                "enable",
                "enable",
                "enable",
                "enable",
                "enable",
                "enable",
                300,
                1000,
                5000,
                3600,
                60,
                "billing_data",
                0.04,
                "$",
                "$",
                "$",
                "$",
                "$",
                "$",
                "$",
                "file",
                raw_path_input,
                ...,  # project-id prompt: accept the derived default
                "",
                "",
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
            @brief Return deterministic prompt responses for the home-path flow.
            @details The Ellipsis response marker resolves to the prompt default so the
            derived project-id default supplied by setup is accepted verbatim.
            @param text {str} Prompt label.
            @param default {object | None} Prompt default value.
            @param show_default {bool} Flag indicating default rendering behavior.
            @param type {object | None} Optional click type.
            @return {object} Predetermined prompt response value.
            """
            del text, show_default, type, kwargs
            response = next(responses)
            if response is ...:
                return default
            return response

        monkeypatch.setattr("aibar.cli.click.prompt", _fake_prompt)

        runner = CliRunner()
        result = runner.invoke(main, ["setup"])
        assert result.exit_code == 0, result.output
        assert "Service-account file error" not in result.output

        assert service_account_path.exists()
        persisted_doc = json.loads(service_account_path.read_text(encoding="utf-8"))
        assert persisted_doc == service_account_payload

        runtime_doc = json.loads(
            (config_dir / "config.json").read_text(encoding="utf-8")
        )
        assert runtime_doc["geminiai_project_id"] == "gen-lang-client-0834428245"


def test_setup_reprompts_service_account_key_path_after_read_or_decode_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify setup re-prompts the key path after read and decode failures.
    @details Answers the path prompt first with a nonexistent path (read failure),
    then with a non-JSON file (decode failure), and finally with a valid key file;
    asserts both failure diagnostics are printed, the path prompt is presented
    three times, and setup persists the key document and exits 0.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-266
    @satisfies TST-119
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    from aibar.providers import geminiai as geminiai_module

    service_account_path = config_dir / "geminiai_service_account.json"
    monkeypatch.setattr(
        geminiai_module, "GEMINIAI_SERVICE_ACCOUNT_PATH", service_account_path
    )

    invalid_json_path = tmp_path / "not-json-gen-lang-client-key.json"
    invalid_json_path.write_text("not-json{", encoding="utf-8")
    key_source_path = tmp_path / "valid-gen-lang-client-key.json"
    service_account_payload = _build_synthetic_service_account_payload()
    key_source_path.write_text(json.dumps(service_account_payload), encoding="utf-8")

    prompts: list[str] = []
    responses = iter(
        [
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            "enable",
            300,
            1000,
            5000,
            3600,
            60,
            "billing_data",
            0.04,
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "$",
            "file",
            str(tmp_path / "missing-gen-lang-client-key.json"),
            str(invalid_json_path),
            str(key_source_path),
            ...,  # project-id prompt: accept the derived default
            "",
            "",
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
        @brief Record prompt labels and return deterministic responses.
        @details The Ellipsis response marker resolves to the prompt default so the
        derived project-id default supplied by setup is accepted verbatim.
        @param text {str} Prompt label appended to the shared recorder list.
        @param default {object | None} Prompt default value.
        @param show_default {bool} Flag indicating default rendering behavior.
        @param type {object | None} Optional click type.
        @return {object} Predetermined prompt response value.
        """
        prompts.append(text)
        response = next(responses)
        if response is ...:
            return default
        return response

    monkeypatch.setattr("aibar.cli.click.prompt", _fake_prompt)

    runner = CliRunner()
    result = runner.invoke(main, ["setup"])
    assert result.exit_code == 0, result.output
    assert "Service-account file error" in result.output
    assert "Service-account JSON decode error" in result.output
    assert prompts.count("  geminiai service-account key json path") == 3

    assert service_account_path.exists()
    persisted_doc = json.loads(service_account_path.read_text(encoding="utf-8"))
    assert persisted_doc == service_account_payload
