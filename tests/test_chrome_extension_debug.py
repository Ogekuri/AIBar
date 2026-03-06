"""
@file
@brief Chrome debug instrumentation wiring assertions.
@details Verifies persisted debug logs, popup export controls, and clear-log path
for field diagnostics.
@satisfies TST-017
@satisfies REQ-044
@satisfies REQ-053
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEBUG_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "debug.js"
POPUP_HTML_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "popup.html"
POPUP_SCRIPT_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "popup.js"


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


def test_popup_exposes_export_clear_and_debug_toggle_controls() -> None:
    """
    @brief Verify popup exposes debug controls and runtime debug-toggle wiring.
    @satisfies REQ-044
    @satisfies REQ-053
    """
    html_source = POPUP_HTML_PATH.read_text(encoding="utf-8")
    script_source = POPUP_SCRIPT_PATH.read_text(encoding="utf-8")
    assert 'id="exportButton"' in html_source
    assert 'id="clearLogsButton"' in html_source
    assert 'id="debugEnableCheckbox"' in html_source
    assert 'id="debugStatusLabel"' in html_source
    assert 'type: "config.debug_api.get"' in script_source
    assert 'type: "config.debug_api.set"' in script_source
    assert 'type: "debug.export_bundle"' in script_source
    assert 'type: "debug.clear_logs"' in script_source


def test_debug_logger_binds_console_methods_before_invocation() -> None:
    """
    @brief Verify logger binds console methods to prevent illegal invocation errors.
    @satisfies REQ-050
    @satisfies TST-022
    """
    source = DEBUG_PATH.read_text(encoding="utf-8")
    assert "console[level].bind(console)" in source
    assert "console.log.bind(console)" in source
