"""
@file
@brief Bare `aibar login` error-state targeting tests.
@details Verifies that `aibar login` without `--provider` executes login flows
exactly for login-capable providers whose cached last-attempt status is `FAIL`,
skips providers with `OK`, absent, or non-login-capable cached statuses, prints
an informational message with exit status 0 when no provider is in error state,
and exits non-zero when at least one login flow fails while remaining providers
still execute.
@satisfies REQ-172
@satisfies REQ-173
@satisfies REQ-174
@satisfies REQ-175
@satisfies TST-066
@satisfies TST-067
"""

import sys
from collections.abc import Callable
from pathlib import Path

from click.testing import CliRunner

from aibar import cli as cli_module
from aibar import config as config_module
from aibar.cli import main
from aibar.providers.base import ProviderName


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


def _seed_cache_status(status_section: dict) -> None:
    """
    @brief Persist a canonical cache document carrying the given status section.
    @details Uses the single `save_cli_cache` write path so the bare-login
    selector reads the same locked cache surface consumed by the production
    retrieval pipeline.
    @param status_section {dict[str, object]} Provider-keyed window status section.
    @return {None} Function return value.
    """
    config_module.save_cli_cache({"payload": {}, "status": status_section})


def _patch_login_registry(
    monkeypatch, flows: dict[str, Callable[[], None]]
) -> list[str]:
    """
    @brief Replace the login flow registry with deterministic recorder flows.
    @details Builds one recorder flow per login-capable provider that appends the
    provider key to the returned invocation-order list and then executes the
    behavior supplied in `flows` (missing behaviors default to a no-op).
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param flows {dict[str, Callable[[], None]]} Mapping from provider key to zero-argument behavior callable.
    @return {list[str]} Shared invocation-order recorder list.
    """
    calls: list[str] = []

    def _make_flow(name: str, behavior: Callable[[], None]) -> Callable[[], None]:
        def _flow() -> None:
            calls.append(name)
            behavior()

        return _flow

    registry_items = []
    for provider_name in (ProviderName.COPILOT, ProviderName.GEMINIAI):
        behavior = flows.get(provider_name.value, lambda: None)
        registry_items.append((provider_name, _make_flow(provider_name.value, behavior)))
    monkeypatch.setattr(cli_module, "_LOGIN_FLOW_REGISTRY", tuple(registry_items))
    return calls


def test_bare_login_executes_only_cached_fail_login_capable_providers(
    monkeypatch, tmp_path: Path
) -> None:
    """
    @brief Verify bare login targets exactly cached FAIL login-capable providers.
    @details Seeds Copilot `FAIL`, GeminiAI `OK`, and non-login-capable Codex
    `FAIL` statuses, then runs bare `aibar login`. Asserts only the Copilot flow
    executes and the command exits 0.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-172
    @satisfies REQ-173
    @satisfies TST-066
    """
    _patch_config_paths(monkeypatch, tmp_path)
    _seed_cache_status(
        {
            "copilot": {
                "30d": {
                    "result": "FAIL",
                    "error": "oauth token expired",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                }
            },
            "geminiai": {
                "30d": {
                    "result": "OK",
                    "error": "",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                }
            },
            "codex": {
                "7d": {
                    "result": "FAIL",
                    "error": "expired refresh token",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                }
            },
        }
    )
    calls = _patch_login_registry(
        monkeypatch, {"copilot": lambda: None, "geminiai": lambda: None}
    )
    result = CliRunner().invoke(main, ["login"])
    assert result.exit_code == 0
    assert calls == ["copilot"]


def test_bare_login_without_error_state_prints_message_and_exits_zero(
    monkeypatch, tmp_path: Path
) -> None:
    """
    @brief Verify bare login prints an informational message when nothing is in error.
    @details Seeds an all-`OK` Copilot status (GeminiAI absent), runs bare
    `aibar login`, and asserts no login flow executes, the output contains the
    informational message, and the exit status is 0.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-174
    @satisfies TST-067
    """
    _patch_config_paths(monkeypatch, tmp_path)
    _seed_cache_status(
        {
            "copilot": {
                "30d": {
                    "result": "OK",
                    "error": "",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                }
            }
        }
    )
    calls = _patch_login_registry(monkeypatch, {})
    result = CliRunner().invoke(main, ["login"])
    assert result.exit_code == 0
    assert calls == []
    assert "No provider in error state" in result.output


def test_bare_login_with_missing_cache_prints_message_and_exits_zero(
    monkeypatch, tmp_path: Path
) -> None:
    """
    @brief Verify bare login handles a missing cache document as empty selection.
    @details Runs bare `aibar login` without any persisted `cache.json` and
    asserts no login flow executes with exit status 0 and the informational
    message is printed.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-174
    @satisfies TST-067
    """
    _patch_config_paths(monkeypatch, tmp_path)
    calls = _patch_login_registry(monkeypatch, {})
    result = CliRunner().invoke(main, ["login"])
    assert result.exit_code == 0
    assert calls == []
    assert "No provider in error state" in result.output


def test_bare_login_continues_and_exits_non_zero_when_flow_fails(
    monkeypatch, tmp_path: Path
) -> None:
    """
    @brief Verify a failed flow does not stop remaining providers and exit is non-zero.
    @details Seeds both Copilot and GeminiAI `FAIL`; the Copilot recorder flow
    terminates via `sys.exit(1)` mirroring production flow failure semantics.
    Asserts the GeminiAI flow still executes and the command exits non-zero.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-172
    @satisfies REQ-175
    @satisfies TST-067
    """
    _patch_config_paths(monkeypatch, tmp_path)
    _seed_cache_status(
        {
            "copilot": {
                "30d": {
                    "result": "FAIL",
                    "error": "oauth token expired",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                }
            },
            "geminiai": {
                "30d": {
                    "result": "FAIL",
                    "error": "oauth refresh failed",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                }
            },
        }
    )

    def _copilot_flow_failure() -> None:
        sys.exit(1)

    calls = _patch_login_registry(
        monkeypatch, {"copilot": _copilot_flow_failure, "geminiai": lambda: None}
    )
    result = CliRunner().invoke(main, ["login"])
    assert result.exit_code != 0
    assert calls == ["copilot", "geminiai"]


def test_bare_login_exits_non_zero_when_flow_raises_exception(
    monkeypatch, tmp_path: Path
) -> None:
    """
    @brief Verify bare login exits non-zero when a login flow raises an exception.
    @details Seeds a Copilot `FAIL` status whose recorder flow raises
    `RuntimeError`. Asserts non-zero exit status and no GeminiAI execution.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-175
    @satisfies TST-067
    """
    _patch_config_paths(monkeypatch, tmp_path)
    _seed_cache_status(
        {
            "copilot": {
                "30d": {
                    "result": "FAIL",
                    "error": "oauth token expired",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                }
            }
        }
    )

    def _copilot_flow_raises() -> None:
        raise RuntimeError("device flow failed")

    calls = _patch_login_registry(monkeypatch, {"copilot": _copilot_flow_raises})
    result = CliRunner().invoke(main, ["login"])
    assert result.exit_code != 0
    assert calls == ["copilot"]


def test_explicit_provider_login_dispatch_is_preserved(
    monkeypatch, tmp_path: Path
) -> None:
    """
    @brief Verify explicit `--provider` login dispatch remains unchanged.
    @details Patches the per-provider login functions with recorders and asserts
    `login --provider copilot` and `login -p geminiai` dispatch the matching
    flow with exit status 0, while unsupported provider values exit non-zero
    without executing any flow.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-172
    """
    _patch_config_paths(monkeypatch, tmp_path)
    calls: list[str] = []
    monkeypatch.setattr(cli_module, "_login_copilot", lambda: calls.append("copilot"))
    monkeypatch.setattr(cli_module, "_login_geminiai", lambda: calls.append("geminiai"))
    runner = CliRunner()
    result_copilot = runner.invoke(main, ["login", "--provider", "copilot"])
    result_geminiai = runner.invoke(main, ["login", "-p", "geminiai"])
    result_unsupported = runner.invoke(main, ["login", "--provider", "openai"])
    assert result_copilot.exit_code == 0
    assert result_geminiai.exit_code == 0
    assert result_unsupported.exit_code != 0
    assert calls == ["copilot", "geminiai"]
