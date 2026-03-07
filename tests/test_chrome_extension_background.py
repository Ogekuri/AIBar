"""
@file
@brief Chrome background scheduler contract assertions.
@details Verifies startup refresh ordering, fixed provider order, refresh
interval persistence, debug-session persistence, and failure fallback logic
required by AIBar Chrome extension runtime.
@satisfies TST-014
@satisfies TST-017
@satisfies TST-023
@satisfies TST-029
@satisfies TST-030
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKGROUND_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "background.js"


def test_background_declares_default_180_second_interval() -> None:
    """
    @brief Verify background module declares default 180-second interval constant.
    @details Confirms interval override storage key exists so default interval
    can be replaced by persisted user configuration.
    @satisfies TST-014
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert "export const REFRESH_INTERVAL_SECONDS = 180;" in source
    assert "const INTERVAL_OVERRIDE_STORAGE_KEY" in source


def test_background_fetch_sequence_is_fixed_and_ordered() -> None:
    """
    @brief Verify provider fetch sequence order matches requirements.
    @satisfies CTN-009
    @satisfies TST-014
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    claude_idx = source.index("https://claude.ai/settings/usage")
    codex_idx = source.index("https://chatgpt.com/codex/settings/usage")
    copilot_features_idx = source.index("https://github.com/settings/copilot/features")
    copilot_premium_idx = source.index(
        "https://github.com/settings/billing/premium_requests_usage"
    )
    assert claude_idx < codex_idx < copilot_features_idx < copilot_premium_idx


def test_background_initialization_runs_refresh_before_alarm_scheduling() -> None:
    """
    @brief Verify startup initialization refreshes provider data before alarm scheduling.
    @details Ensures extension boot triggers immediate data download and is not
    blocked by alarm registration.
    @satisfies REQ-043
    @satisfies TST-014
    @satisfies TST-030
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    init_idx = source.index("async function _initializeRuntime(trigger)")
    refresh_idx = source.index("await _refreshAllProviders(trigger);", init_idx)
    schedule_idx = source.index("await _scheduleRefreshAlarm();", init_idx)
    assert refresh_idx < schedule_idx


def test_background_initialization_is_bound_to_service_worker_boot_events() -> None:
    """
    @brief Verify provider refresh starts on extension runtime bootstrap events.
    @details Confirms initialization is called from install/startup listeners and
    immediate service-worker bootstrap path, independent from popup or debug APIs.
    @satisfies REQ-043
    @satisfies TST-030
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert 'chrome.runtime.onInstalled.addListener(() => {' in source
    assert 'chrome.runtime.onStartup.addListener(() => {' in source
    assert 'void _initializeRuntime("service_worker_bootstrap")' in source


def test_background_failure_path_keeps_previous_windows_data() -> None:
    """
    @brief Verify provider failure update preserves prior windows payload.
    @satisfies REQ-045
    @satisfies TST-017
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    apply_failure_idx = source.index("function _applyProviderFailure")
    spread_idx = source.index("...runtimeState.providers[provider]", apply_failure_idx)
    error_idx = source.index(
        "error: String(error?.message ?? error)", apply_failure_idx
    )
    assert spread_idx < error_idx


def test_background_marks_parser_empty_payload_as_refresh_failure() -> None:
    """
    @brief Verify parser-empty payloads are treated as failures, not successes.
    @satisfies REQ-045
    @satisfies TST-017
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert "function _assertProviderPayloadUsable(provider, payload)" in source
    assert "Parser produced no usable" in source
    assert '_assertProviderPayloadUsable("claude", claudePayload);' in source
    assert '_assertProviderPayloadUsable("codex", codexPayload);' in source


def test_config_refresh_interval_set_handler_exists_outside_debug_guard() -> None:
    """
    @brief Verify config.refresh_interval.set handler is defined before the
    debug.* guard so the popup interval control works without debug enabled.
    @satisfies TST-029
    @satisfies CTN-008
    @satisfies CTN-016
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    config_handler_idx = source.index('"config.refresh_interval.set"')
    debug_guard_idx = source.index('message.type.startsWith("debug.")')
    assert config_handler_idx < debug_guard_idx
    assert (
        "INTERVAL_OVERRIDE_STORAGE_KEY"
        in source[config_handler_idx : config_handler_idx + 500]
    )
    assert (
        "_scheduleRefreshAlarm" in source[config_handler_idx : config_handler_idx + 500]
    )


def test_background_persists_debug_access_in_browser_session_storage() -> None:
    """
    @brief Verify debug-access state is persisted in browser-session storage.
    @details Confirms session-key declaration plus load/save helpers and usage
    in config.debug_api handlers.
    @satisfies CTN-017
    @satisfies REQ-052
    @satisfies TST-023
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert "const DEBUG_API_ENABLED_SESSION_STORAGE_KEY" in source
    assert "function _getSessionStorageArea()" in source
    assert "async function _loadDebugAccessState()" in source
    assert "async function _persistDebugAccessState(enabled)" in source
    assert "await _loadDebugAccessState();" in source
    assert "const persisted = await _persistDebugAccessState(debugApiEnabled);" in source
