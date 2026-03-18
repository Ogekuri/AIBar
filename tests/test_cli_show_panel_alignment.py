"""
@file
@brief CLI provider panel width-alignment regression tests.
@details Verifies `aibar show` text-mode panel rows keep identical visible width
when body lines contain ANSI-colored progress bars.
@satisfies REQ-067
"""

import re
from datetime import datetime, timezone
from unittest.mock import MagicMock

from click.testing import CliRunner

from aibar.cli import RetrievalPipelineOutput, main
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
    non-empty panel row has identical visible width after ANSI stripping and no
    reset line contains the `⚠️` suffix glyph.
    @param capsys {pytest.CaptureFixture} Pytest stdout/stderr capture fixture.
    @return {None} Function return value.
    @satisfies REQ-036
    @satisfies REQ-067
    """
    metrics = UsageMetrics(remaining=0.0, limit=100.0)
    result = ProviderResult(
        provider=ProviderName.CLAUDE,
        window=WindowPeriod.HOUR_5,
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
    assert all("⚠️" not in line for line in panel_rows)
    row_length = len(panel_rows[0])
    assert all(len(line) == row_length for line in panel_rows)


def test_show_uses_one_shared_panel_width_for_all_rendered_providers(monkeypatch) -> None:
    """
    @brief Verify one `show` execution renders all provider panels at one shared width.
    @details Mocks two providers with different body lengths and asserts visible border
    width is identical for every rendered panel in command output.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-067
    @satisfies TST-030
    """
    openrouter_result = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=9.8765, remaining=90.0, limit=100.0),
        raw={"status_code": 200, "data": {"byok_usage_weekly": 4.2}},
    )
    openai_result = ProviderResult(
        provider=ProviderName.OPENAI,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=0.0, currency_symbol="€"),
        raw={"status_code": 200},
    )

    provider = MagicMock()
    provider.is_configured.return_value = True
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.OPENROUTER: provider, ProviderName.OPENAI: provider},
    )
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **_: RetrievalPipelineOutput(
            payload={},
            results={
                ProviderName.OPENROUTER.value: openrouter_result,
                ProviderName.OPENAI.value: openai_result,
            },
            idle_time_by_provider={},
            idle_active=False,
            cache_available=True,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show"])
    assert result.exit_code == 0

    visible_lines = [
        _strip_ansi_sequences(line)
        for line in result.output.splitlines()
        if line.strip()
    ]
    top_borders = [line for line in visible_lines if line.startswith("┌") and line.endswith("┐")]
    assert len(top_borders) == 2
    assert len({len(line) for line in top_borders}) == 1


def test_show_default_window_groups_dual_windows_into_one_panel_per_provider(
    monkeypatch,
) -> None:
    """
    @brief Verify default-window `show` groups Claude/Codex dual windows in single provider panels.
    @details Mocks Claude and Codex parser paths so each provider emits one grouped panel
    containing blank-line-separated `5h` and `7d` sections with shared `Updated/Next`
    metadata rendered once per provider panel.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-002
    @satisfies TST-030
    """
    shared_updated_at = datetime(2026, 3, 18, 9, 0, tzinfo=timezone.utc)

    def _build_dual_parser(provider_name: ProviderName):
        def _parse(_raw: dict, window: WindowPeriod) -> ProviderResult:
            usage_by_window = {
                WindowPeriod.HOUR_5: 35.0,
                WindowPeriod.DAY_7: 55.0,
            }
            return ProviderResult(
                provider=provider_name,
                window=window,
                metrics=UsageMetrics(
                    usage_percent=usage_by_window[window],
                    remaining=65.0,
                    limit=100.0,
                ),
                updated_at=shared_updated_at,
                raw={"status_code": 200},
            )

        return _parse

    claude_provider = MagicMock()
    claude_provider.is_configured.return_value = True
    claude_provider._parse_response = _build_dual_parser(ProviderName.CLAUDE)

    codex_provider = MagicMock()
    codex_provider.is_configured.return_value = True
    codex_provider._parse_response = _build_dual_parser(ProviderName.CODEX)

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {
            ProviderName.CLAUDE: claude_provider,
            ProviderName.CODEX: codex_provider,
        },
    )
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **_: RetrievalPipelineOutput(
            payload={},
            results={
                ProviderName.CLAUDE.value: ProviderResult(
                    provider=ProviderName.CLAUDE,
                    window=WindowPeriod.DAY_7,
                    metrics=UsageMetrics(remaining=65.0, limit=100.0),
                    updated_at=shared_updated_at,
                    raw={"status_code": 200},
                ),
                ProviderName.CODEX.value: ProviderResult(
                    provider=ProviderName.CODEX,
                    window=WindowPeriod.DAY_7,
                    metrics=UsageMetrics(remaining=65.0, limit=100.0),
                    updated_at=shared_updated_at,
                    raw={"status_code": 200},
                ),
            },
            idle_time_by_provider={},
            idle_active=False,
            cache_available=True,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show"])
    assert result.exit_code == 0

    visible_lines = [
        _strip_ansi_sequences(line)
        for line in result.output.splitlines()
        if line.strip()
    ]
    top_borders = [line for line in visible_lines if line.startswith("┌") and line.endswith("┐")]
    assert len(top_borders) == 2
    assert len({len(line) for line in top_borders}) == 1
    assert "CLAUDE (5h)" not in result.output
    assert "CLAUDE (7d)" not in result.output
    assert "CODEX (5h)" not in result.output
    assert "CODEX (7d)" not in result.output
    assert result.output.count("5h:") == 2
    assert result.output.count("7d:") == 2
    assert result.output.count("Updated:") == 2
