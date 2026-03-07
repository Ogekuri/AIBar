"""
@file
@brief Chrome debug API command-interface assertions.
@details Verifies runtime debug API describe/execute routes, supported command
catalog, primary API snapshot schema, debug-access gating, parser command
dispatch, and structured command lifecycle logging.
@satisfies TST-019
@satisfies TST-020
@satisfies TST-021
@satisfies TST-022
@satisfies TST-023
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKGROUND_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "background.js"


def test_primary_and_debug_api_routes_are_exposed_in_message_handler() -> None:
    """
    @brief Verify message handler exposes primary, debug, and config API routes.
    @satisfies TST-019
    @satisfies REQ-046
    @satisfies REQ-052
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert 'message.type === "api.main.snapshot"' in source
    assert 'message.type === "debug.api.describe"' in source
    assert 'message.type === "debug.api.execute"' in source
    assert 'message.type === "config.debug_api.get"' in source
    assert 'message.type === "config.debug_api.set"' in source


def test_primary_snapshot_contract_contains_tab_and_progress_window_schema() -> None:
    """
    @brief Verify primary snapshot route returns tab/progress schema for popup rendering.
    @satisfies TST-019
    @satisfies REQ-046
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert "function _buildMainApiSnapshot()" in source
    assert 'endpoint: "api.main.snapshot"' in source
    assert "tab_order:" in source
    assert "tab_windows:" in source
    assert "MAIN_API_PROVIDER_WINDOWS" in source
    assert "providers," in source
    assert "function _toFiniteMetricNumber(token)" in source
    assert "token === null || token === undefined || token === \"\"" in source


def test_primary_snapshot_route_remains_available_without_debug_enablement() -> None:
    """
    @brief Verify api.main.snapshot route executes before debug.* guard.
    @details Ensures primary API remains callable while debug API is disabled.
    @satisfies TST-019
    @satisfies REQ-046
    @satisfies REQ-051
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    snapshot_idx = source.index('message.type === "api.main.snapshot"')
    debug_guard_idx = source.index('message.type.startsWith("debug.")')
    assert snapshot_idx < debug_guard_idx


def test_debug_api_command_catalog_includes_http_parser_and_standard_commands() -> None:
    """
    @brief Verify debug command list includes required command set.
    @satisfies TST-019
    @satisfies TST-022
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert "const DEBUG_API_SUPPORTED_COMMANDS = [" in source
    assert '"http.get"' in source
    assert '"parser.run"' in source
    assert '"provider.diagnose"' in source
    assert '"providers.diagnose"' in source
    assert '"providers.pages.get"' in source
    assert '"state.get"' in source
    assert '"refresh.run"' in source
    assert '"logs.get"' in source
    assert '"logs.clear"' in source
    assert '"interval.get"' in source
    assert '"interval.set"' in source


def test_debug_api_calls_are_rejected_when_runtime_debug_access_is_disabled() -> None:
    """
    @brief Verify debug message routes fail with deterministic error when flag is off.
    @satisfies TST-023
    @satisfies REQ-051
    @satisfies CTN-014
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert "let debugApiEnabled = false;" in source
    assert "function _ensureDebugAccessEnabled()" in source
    assert 'if (typeof message.type === "string" && message.type.startsWith("debug.")) {' in source
    assert 'code: "DEBUG_API_DISABLED"' in source
    assert "Debug API disabled: enable it in popup configuration for this runtime session." in source


def test_config_routes_toggle_debug_access_with_session_persistence() -> None:
    """
    @brief Verify config routes mutate debug flag and persist state per browser session.
    @details Confirms config handlers use session storage read/write helpers and
    expose `persisted` response metadata.
    @satisfies TST-023
    @satisfies REQ-052
    @satisfies CTN-017
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert 'message.type === "config.debug_api.get"' in source
    assert 'message.type === "config.debug_api.set"' in source
    assert "async function _loadDebugAccessState()" in source
    assert "async function _persistDebugAccessState(enabled)" in source
    assert "DEBUG_API_ENABLED_SESSION_STORAGE_KEY" in source
    assert "debugApiEnabled = message.enabled;" in source
    assert "const persisted = _getSessionStorageArea() !== null;" in source
    assert "const persisted = await _persistDebugAccessState(debugApiEnabled);" in source


def test_debug_http_command_enforces_https_and_allowlisted_hosts() -> None:
    """
    @brief Verify HTTP debug command enforces transport and host constraints.
    @satisfies TST-020
    @satisfies CTN-012
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert 'const DEBUG_API_ALLOWED_HOSTS = new Set(["claude.ai", "chatgpt.com", "github.com"]);' in source
    assert "URL must use https protocol for debug command" in source
    assert "URL host not allowed for debug command" in source


def test_debug_http_command_returns_bounded_body_preview_metadata() -> None:
    """
    @brief Verify HTTP debug response includes preview and truncation metadata.
    @satisfies TST-020
    @satisfies CTN-013
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert "const DEBUG_API_DEFAULT_MAX_CHARS =" in source
    assert "const DEBUG_API_MAX_CHARS =" in source
    assert "body_preview" in source
    assert "body_preview_tail" in source
    assert "body_sha256" in source
    assert "body_truncated" in source
    assert "body_length" in source
    assert "html_probe" in source


def test_debug_parser_command_dispatch_maps_provider_parsers() -> None:
    """
    @brief Verify parser command dispatch maps provider keys to parser functions.
    @satisfies TST-021
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert "function _resolveDebugParser(provider)" in source
    assert "case \"claude\":" in source
    assert "case \"codex\":" in source
    assert "case \"copilot_features\":" in source
    assert "case \"copilot_premium\":" in source
    assert "provider === \"copilot_merged\"" in source
    assert "html_probe" in source
    assert "parser_signal_diagnostics" in source
    assert "window_assignment_diagnostics" in source
    assert "payload_assertion" in source
    assert "parser_payload" in source
    assert "payload_quality" in source


def test_debug_provider_diagnose_command_is_exposed_with_source_diagnostics() -> None:
    """
    @brief Verify provider.diagnose command returns fetch+parser diagnostics.
    @satisfies REQ-048
    @satisfies TST-021
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert 'case "provider.diagnose":' in source
    assert "provider.diagnose requires provider argument" in source
    assert 'command: "provider.diagnose"' in source
    assert "sources:" in source
    assert "payload_usable" in source
    assert "providers.diagnose" in source


def test_debug_providers_diagnose_command_returns_aggregate_diagnostics() -> None:
    """
    @brief Verify providers.diagnose command exposes aggregate multi-provider diagnostics.
    @satisfies REQ-048
    @satisfies TST-021
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert 'case "providers.diagnose":' in source
    assert "providers.diagnose requires at least one provider token" in source
    assert "provider_fetch_sequence" in source
    assert "DEBUG_API_DEFAULT_PROVIDER_DIAGNOSE_SET" in source


def test_debug_providers_pages_get_command_returns_page_and_related_diagnostics() -> None:
    """
    @brief Verify providers.pages.get command downloads required provider pages and related resources.
    @satisfies REQ-048
    @satisfies TST-020
    @satisfies TST-021
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert 'case "providers.pages.get":' in source
    assert "const DEBUG_API_PROVIDER_PAGES = [" in source
    assert '"https://claude.ai/settings/usage"' in source
    assert '"https://github.com/settings/copilot/features"' in source
    assert '"https://github.com/settings/billing/premium_requests_usage"' in source
    assert '"https://chatgpt.com/codex/settings/usage"' in source
    assert "related_content" in source
    assert "parser_signal_diagnostics" in source
    assert "window_assignment_diagnostics" in source
    assert "payload_analysis" in source


def test_debug_api_logs_command_lifecycle_events() -> None:
    """
    @brief Verify debug API emits start/success/failure structured logs.
    @satisfies REQ-050
    @satisfies TST-022
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert 'logger.info("debug-api-command-start"' in source
    assert 'logger.info("debug-api-command-success"' in source
    assert 'logger.error("debug-api-command-failure"' in source
    assert "duration_ms" in source
