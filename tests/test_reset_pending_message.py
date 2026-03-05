"""
@file
@brief Reproducer tests for missing reset fallback message when usage is zero.
@details Verifies CLI and GNOME extension surfaces render a deterministic reset
fallback text when timer is not started (`usage_percent == 0` and `reset_at is None`).
@satisfies REQ-002
@satisfies REQ-017
"""

from pathlib import Path

from aibar.cli import _print_result
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_PATH = PROJECT_ROOT / "src" / "aibar" / "extension" / "aibar@aibar.panel" / "extension.js"
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
    assert "bar.resetLabel.text = `Reset in: ${RESET_PENDING_MESSAGE}`;" in source
    assert "else if (pct <= 0)" in source
