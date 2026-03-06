"""
@file
@brief Chrome debug API command-interface assertions.
@details Verifies runtime debug API describe/execute routes, supported command
catalog, HTTP safety constraints, parser command dispatch, and structured
command lifecycle logging.
@satisfies TST-019
@satisfies TST-020
@satisfies TST-021
@satisfies TST-022
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKGROUND_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "background.js"


def test_debug_api_routes_are_exposed_in_message_handler() -> None:
    """
    @brief Verify background message handler exposes debug API routes.
    @satisfies TST-019
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    assert 'message.type === "debug.api.describe"' in source
    assert 'message.type === "debug.api.execute"' in source


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
    assert '"state.get"' in source
    assert '"refresh.run"' in source
    assert '"logs.get"' in source
    assert '"logs.clear"' in source
    assert '"interval.get"' in source
    assert '"interval.set"' in source


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
    assert "body_truncated" in source
    assert "body_length" in source


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
    assert "parser_payload" in source


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
