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


def _extract_panel_titles_and_bodies(output: str) -> list[tuple[str, list[str]]]:
    """
    @brief Parse ANSI-stripped `show` output into ordered panel title/body tuples.
    @details Scans box-drawing borders and returns one tuple per rendered panel, where
    body rows are unwrapped from border glyphs and preserve intentional blank separators.
    @param output {str} Raw CLI output including ANSI escape codes.
    @return {list[tuple[str, list[str]]]} Ordered `(title, body_lines)` panel records.
    """
    lines = [_strip_ansi_sequences(line) for line in output.splitlines()]
    panels: list[tuple[str, list[str]]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not (line.startswith("┌") and line.endswith("┐")):
            index += 1
            continue
        if index + 2 >= len(lines):
            break
        title_line = lines[index + 1]
        title = title_line[1:-1].strip()
        body: list[str] = []
        index += 3
        while index < len(lines):
            row = lines[index]
            if row.startswith("└") and row.endswith("┘"):
                break
            if row.startswith("│") and row.endswith("│"):
                body.append(row[1:-1].strip())
            index += 1
        panels.append((title, body))
        index += 1
    return panels


def _assert_status_and_freshness_layout(body_lines: list[str]) -> None:
    """
    @brief Verify panel body puts `Status` first and `Updated/Next` last with blank separators.
    @param body_lines {list[str]} Parsed panel body lines.
    @return {None} Function return value.
    """
    non_empty_indexes = [idx for idx, value in enumerate(body_lines) if value]
    assert non_empty_indexes
    first_index = non_empty_indexes[0]
    last_index = non_empty_indexes[-1]
    assert body_lines[first_index].startswith("Status:")
    assert body_lines[last_index].startswith("Updated:")
    assert first_index + 1 < len(body_lines)
    assert body_lines[first_index + 1] == ""
    assert last_index > 0
    assert body_lines[last_index - 1] == ""


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
            codex_requests = {
                WindowPeriod.HOUR_5: 12,
                WindowPeriod.DAY_7: 34,
            }
            codex_input_tokens = {
                WindowPeriod.HOUR_5: 120,
                WindowPeriod.DAY_7: 340,
            }
            codex_output_tokens = {
                WindowPeriod.HOUR_5: 45,
                WindowPeriod.DAY_7: 78,
            }
            codex_cost = {
                WindowPeriod.HOUR_5: 0.4321,
                WindowPeriod.DAY_7: 1.2345,
            }
            metrics = UsageMetrics(
                usage_percent=usage_by_window[window],
                remaining=65.0,
                limit=100.0,
            )
            if provider_name == ProviderName.CODEX:
                metrics = UsageMetrics(
                    usage_percent=usage_by_window[window],
                    remaining=65.0,
                    limit=100.0,
                    cost=codex_cost[window],
                    requests=codex_requests[window],
                    input_tokens=codex_input_tokens[window],
                    output_tokens=codex_output_tokens[window],
                )
            return ProviderResult(
                provider=provider_name,
                window=window,
                metrics=metrics,
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

    panel_data = _extract_panel_titles_and_bodies(result.output)
    assert [title for title, _body in panel_data] == ["CLAUDE", "CODEX"]
    assert "CLAUDE (5h)" not in result.output
    assert "CLAUDE (7d)" not in result.output
    assert "CODEX (5h)" not in result.output
    assert "CODEX (7d)" not in result.output
    assert result.output.count("5h:") == 2
    assert result.output.count("7d:") == 2
    assert result.output.count("Updated:") == 2
    for _title, body_lines in panel_data:
        _assert_status_and_freshness_layout(body_lines)
        assert not any(line.startswith("Window:") for line in body_lines)
        assert "5h:" in body_lines
        assert "7d:" in body_lines
        idx_5h = body_lines.index("5h:")
        idx_7d = body_lines.index("7d:")
        assert idx_7d > idx_5h
        assert body_lines[idx_7d - 1] == ""

    codex_body = panel_data[1][1]
    idx_7d = codex_body.index("7d:")
    idx_cost = next(idx for idx, line in enumerate(codex_body) if line.startswith("Cost:"))
    idx_requests = next(
        idx for idx, line in enumerate(codex_body) if line.startswith("Requests:")
    )
    idx_tokens = next(idx for idx, line in enumerate(codex_body) if line.startswith("Tokens:"))
    assert idx_cost > idx_7d
    assert codex_body[idx_cost - 1] == ""
    assert idx_7d < idx_cost < idx_requests < idx_tokens


def test_show_orders_provider_panels_status_first_and_updated_last(monkeypatch) -> None:
    """
    @brief Verify `show` panel order and per-panel status/freshness row placement.
    @details Forces explicit `7d` rendering across all providers with shuffled input maps
    and asserts output panel order `CLAUDE, OPENROUTER, COPILOT, CODEX, OPENAI, GEMINIAI`
    while each panel body starts with `Status:` and ends with `Updated: ..., Next: ...`.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-067
    @satisfies TST-030
    """
    provider_stub = MagicMock()
    provider_stub.is_configured.return_value = True
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {
            ProviderName.GEMINIAI: provider_stub,
            ProviderName.OPENAI: provider_stub,
            ProviderName.CODEX: provider_stub,
            ProviderName.COPILOT: provider_stub,
            ProviderName.OPENROUTER: provider_stub,
            ProviderName.CLAUDE: provider_stub,
        },
    )

    def _build_result(provider_name: ProviderName) -> ProviderResult:
        return ProviderResult(
            provider=provider_name,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(
                usage_percent=12.5,
                cost=0.1234,
                remaining=87.5,
                limit=100.0,
                requests=8,
                input_tokens=80,
                output_tokens=20,
            ),
            updated_at=datetime(2026, 3, 18, 9, 0, tzinfo=timezone.utc),
            raw={"status_code": 200},
        )

    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **_: RetrievalPipelineOutput(
            payload={},
            results={
                ProviderName.OPENAI.value: _build_result(ProviderName.OPENAI),
                ProviderName.COPILOT.value: _build_result(ProviderName.COPILOT),
                ProviderName.CLAUDE.value: _build_result(ProviderName.CLAUDE),
                ProviderName.GEMINIAI.value: _build_result(ProviderName.GEMINIAI),
                ProviderName.OPENROUTER.value: _build_result(ProviderName.OPENROUTER),
                ProviderName.CODEX.value: _build_result(ProviderName.CODEX),
            },
            idle_time_by_provider={},
            idle_active=False,
            cache_available=True,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--window", "7d"])
    assert result.exit_code == 0

    panel_data = _extract_panel_titles_and_bodies(result.output)
    assert [title for title, _body in panel_data] == [
        "CLAUDE",
        "OPENROUTER",
        "COPILOT",
        "CODEX",
        "OPENAI",
        "GEMINIAI",
    ]
    for _title, body_lines in panel_data:
        _assert_status_and_freshness_layout(body_lines)
