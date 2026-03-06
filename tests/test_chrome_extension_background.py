"""
@file
@brief Chrome background scheduler contract assertions.
@details Verifies refresh interval default, fixed provider order, and failure
fallback logic required by AIBar Chrome extension runtime.
@satisfies TST-014
@satisfies TST-017
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKGROUND_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "background.js"


def test_background_declares_default_180_second_interval() -> None:
    """
    @brief Verify background module declares default 180-second interval constant.
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
    copilot_premium_idx = source.index("https://github.com/settings/billing/premium_requests_usage")
    assert claude_idx < codex_idx < copilot_features_idx < copilot_premium_idx


def test_background_failure_path_keeps_previous_windows_data() -> None:
    """
    @brief Verify provider failure update preserves prior windows payload.
    @satisfies REQ-045
    @satisfies TST-017
    """
    source = BACKGROUND_PATH.read_text(encoding="utf-8")
    apply_failure_idx = source.index("function _applyProviderFailure")
    spread_idx = source.index("...runtimeState.providers[provider]", apply_failure_idx)
    error_idx = source.index("error: String(error?.message ?? error)", apply_failure_idx)
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
    assert "_assertProviderPayloadUsable(\"claude\", claudePayload);" in source
    assert "_assertProviderPayloadUsable(\"codex\", codexPayload);" in source
