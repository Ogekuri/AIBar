"""
@file
@brief CLI provider panel width-alignment regression tests.
@details Verifies `aibar show` text-mode panel rows keep identical visible width
when body lines contain ANSI-colored progress bars.
@satisfies REQ-067
"""

import re

from aibar.cli import _print_result
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod


_ANSI_ESCAPE_SEQUENCE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi_sequences(value: str) -> str:
    """
    @brief Remove ANSI SGR color escapes from one captured output line.
    @details Produces visible-text content for deterministic length assertions.
    @param value {str} Captured output line that may include ANSI SGR escapes.
    @return {str} ANSI-free line content.
    """
    return _ANSI_ESCAPE_SEQUENCE_PATTERN.sub("", value)


def test_print_result_keeps_panel_rows_aligned_with_colored_progress_bar(capsys) -> None:
    """
    @brief Verify ANSI-colored progress bar rows preserve panel border alignment.
    @details Renders the Claude 5h partial-window error path and asserts every
    non-empty panel row has identical visible width after ANSI stripping.
    @param capsys {pytest.CaptureFixture} Pytest stdout/stderr capture fixture.
    @return {None} Function return value.
    @satisfies REQ-036
    @satisfies REQ-067
    """
    metrics = UsageMetrics(usage_percent=100.0, remaining=0.0, limit=100.0)
    result = ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod.HOUR_5,
        is_error=True,
        error="Rate limited. Try again later.",
        metrics=metrics,
        raw={"status_code": 429},
    )

    _print_result(ProviderName.CLAUDE, result, label="5h")
    panel_rows = [
        _strip_ansi_sequences(line)
        for line in capsys.readouterr().out.splitlines()
        if line.strip()
    ]

    assert panel_rows
    row_length = len(panel_rows[0])
    assert all(len(line) == row_length for line in panel_rows)
