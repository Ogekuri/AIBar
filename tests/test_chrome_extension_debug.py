"""
@file
@brief Chrome debug instrumentation wiring assertions.
@details Verifies persisted debug logs, popup debug-toggle controls, and
absence of removed debug action buttons per REQ-053 / TST-028.
@satisfies TST-017
@satisfies TST-028
@satisfies REQ-044
@satisfies REQ-053
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEBUG_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "debug.js"
POPUP_HTML_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "popup.html"
POPUP_SCRIPT_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "popup.js"
BACKGROUND_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "background.js"


def test_debug_module_declares_storage_ring_buffer_and_bundle_export() -> None:
    """
    @brief Verify debug module stores logs in storage and supports bundle export.
    @satisfies TST-017
    @satisfies REQ-044
    """
    source = DEBUG_PATH.read_text(encoding="utf-8")
    assert 'export const DEBUG_LOG_STORAGE_KEY = "aibar.debug.logs";' in source
    assert "export async function appendDebugRecord" in source
    assert "export async function buildDebugBundle" in source


def test_popup_retains_debug_toggle_but_removes_action_buttons() -> None:
    """
    @brief Verify popup retains debug checkbox/label but no export, clear, or
    fetch-pages buttons.  Debug actions are only available via debug API.
    @satisfies REQ-053
    @satisfies TST-028
    """
    html_source = POPUP_HTML_PATH.read_text(encoding="utf-8")
    script_source = POPUP_SCRIPT_PATH.read_text(encoding="utf-8")
    # Debug toggle controls remain
    assert 'id="debugEnableCheckbox"' in html_source
    assert 'id="debugStatusLabel"' in html_source
    assert 'type: "config.debug_api.get"' in script_source
    assert 'type: "config.debug_api.set"' in script_source
    # Removed buttons must NOT appear in popup HTML or popup JS
    assert 'id="exportButton"' not in html_source
    assert 'id="clearLogsButton"' not in html_source
    assert 'id="providerPagesButton"' not in html_source
    assert 'id="debugOutput"' not in html_source
    assert 'type: "debug.export_bundle"' not in script_source
    assert 'type: "debug.clear_logs"' not in script_source
    assert 'command: "providers.pages.get"' not in script_source


def test_debug_action_handlers_remain_in_background_service_worker() -> None:
    """
    @brief Verify debug export/clear/logs handlers are still in background.js
    for API access even though popup buttons were removed.
    @satisfies REQ-044
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert '"debug.export_bundle"' in source
    assert '"debug.clear_logs"' in source
    assert '"debug.get_logs"' in source


def test_debug_logger_binds_console_methods_before_invocation() -> None:
    """
    @brief Verify logger binds console methods to prevent illegal invocation errors.
    @satisfies REQ-050
    @satisfies TST-022
    """
    source = DEBUG_PATH.read_text(encoding="utf-8")
    assert "function _resolveConsoleMethod(level)" in source
    assert "function _emitConsoleSafe(level, prefix, safeDetails)" in source
    assert "_emitConsoleSafe(level, prefix, safeDetails);" in source
    assert "await appendDebugRecord(record);" in source
    assert (
        '_emitConsoleSafe("error", "[AIBar:debug] appendDebugRecord failed"' in source
    )
