"""
@file
@brief Reproducer tests for missing reset fallback message when usage is zero.
@details Verifies CLI and GNOME extension surfaces render a deterministic reset
fallback text when timer is not started (`usage_percent == 0` and `reset_at is None`).
@satisfies REQ-002
@satisfies REQ-017
"""

from pathlib import Path

from aibar.cli import _print_result, _should_print_claude_reset_pending_hint
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_PATH = PROJECT_ROOT / "src" / "aibar" / "gnome-extension" / "aibar@aibar.panel" / "extension.js"
_RESET_PENDING_TEXT = "Starts when the first message is sent"


def test_cli_show_prints_reset_fallback_for_claude_zero_usage(capsys) -> None:
    """
    @brief Verify CLI prints reset fallback text for Claude when usage is zero.
    @details Arrange a Claude result with remaining=limit (usage_percent=0), no reset_at,
    and invoke `_print_result` for both dual-window labels. Assert each output block
    includes `Resets in:` with the fallback text, preventing silent omission of reset info.
    @param capsys {_pytest.capture.CaptureFixture[str]} Pytest capture fixture.
    @return {None} Function return value.
    @satisfies REQ-002
    """
    base_result = ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod.HOUR_5,
        metrics=UsageMetrics(
            remaining=100.0,
            limit=100.0,
            reset_at=None,
            cost=None,
            requests=None,
            input_tokens=None,
            output_tokens=None,
        ),
        raw={
            "five_hour": {"utilization": 0.0},
            "seven_day": {"utilization": 0.0},
        },
    )

    _print_result(ProviderName.CLAUDE, base_result, label="5h")
    _print_result(
        ProviderName.CLAUDE,
        base_result.model_copy(update={"window": WindowPeriod.DAY_7}),
        label="7d",
    )

    out = capsys.readouterr().out
    assert out.count(f"Resets in: {_RESET_PENDING_TEXT}") == 2


def test_extension_source_contains_reset_fallback_for_zero_usage() -> None:
    """
    @brief Verify extension source defines reset fallback text for zero-usage windows.
    @details Asserts the GNOME extension updateWindowBar path contains the fallback reset
    message and a zero-usage branch so Claude 5h bars keep reset guidance visible.
    @return {None} Function return value.
    @satisfies REQ-017
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "const RESET_PENDING_MESSAGE = 'Starts when the first message is sent';" in source
    assert "const showResetPendingHint = () => {" in source
    assert "setResetLabel(`Reset in: ${RESET_PENDING_MESSAGE}`);" in source
    assert "const shouldShowResetPending = _isDisplayedZeroPercent(pct);" in source
    assert "else if (shouldShowResetPending)" in source


def test_cli_reset_pending_hint_triggers_for_display_rounded_zero_usage() -> None:
    """
    @brief Verify CLI fallback logic triggers when usage rounds to displayed 0.0%.
    @details Uses `remaining=99.96` and `limit=100.0` so internal usage is `0.04%`.
    Even though value is not mathematically zero, the UI renders `0.0%` with one
    decimal; fallback reset text must therefore be shown to avoid silent omission.
    @return {None} Function return value.
    @satisfies REQ-002
    """
    metrics = UsageMetrics(
        remaining=99.96,
        limit=100.0,
        reset_at=None,
        cost=None,
        requests=None,
        input_tokens=None,
        output_tokens=None,
    )
    assert _should_print_claude_reset_pending_hint(ProviderName.CLAUDE, metrics)
