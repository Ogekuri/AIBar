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
from aibar.config import RuntimeConfig
from aibar.providers.base import (
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)


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
                body.append(row[2:-2])
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
    non_empty_indexes = [idx for idx, value in enumerate(body_lines) if value.strip()]
    assert non_empty_indexes
    first_index = non_empty_indexes[0]
    last_index = non_empty_indexes[-1]
    assert body_lines[first_index].startswith("Status:")
    assert body_lines[last_index].lstrip().startswith("Updated:")
    assert body_lines[last_index] == body_lines[last_index].rstrip()
    assert first_index + 1 < len(body_lines)
    assert body_lines[first_index + 1].strip() == ""
    assert last_index > 0
    assert body_lines[last_index - 1].strip() == ""


def _assert_fail_reason_layout(body_lines: list[str]) -> None:
    """
    @brief Verify failed panel body order for `Status/Reason/Updated` rows.
    @details Confirms failed-state block ordering `Status: FAIL`, blank line,
    `Reason: ...`, blank line, and trailing right-aligned `Updated:` freshness row.
    @param body_lines {list[str]} Parsed panel body lines.
    @return {None} Function return value.
    """
    normalized_lines = [line.strip() for line in body_lines]
    assert normalized_lines[0] == "Status: FAIL"
    assert normalized_lines[1] == ""
    assert normalized_lines[2].startswith("Reason: ")
    assert normalized_lines[3] == ""
    assert normalized_lines[4].startswith("Updated: ")


def test_print_result_keeps_panel_rows_aligned_with_colored_progress_bar(
    capsys,
) -> None:
    """
    @brief Verify ANSI-colored progress bar rows preserve panel border alignment.
    @details Renders the Claude 5h partial-window failed path and asserts every
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
    assert any("Status: FAIL" in line for line in panel_rows)
    assert any("Reason: Rate limited. Try again later." in line for line in panel_rows)
    assert any("Updated:" in line for line in panel_rows)
    row_length = len(panel_rows[0])
    assert all(len(line) == row_length for line in panel_rows)


def test_print_result_keeps_panel_rows_aligned_with_over_limit_progress_bar(
    capsys,
) -> None:
    """
    @brief Verify CLI text output renders over-limit quota inside a fixed-width bar.
    @details Renders one Copilot result above 100% usage and asserts the visible
    usage row contains provider fill (`█`), one 100%-boundary marker (`|`), and
    one neutral over-limit segment (`▓`) while preserving identical visible width
    for all non-empty panel rows after ANSI stripping.
    @param capsys {pytest.CaptureFixture} Pytest stdout/stderr capture fixture.
    @return {None} Function return value.
    @satisfies REQ-122
    @satisfies TST-054
    """
    metrics = UsageMetrics(
        usage_percent=111.1,
        remaining=-167.0,
        limit=1500.0,
        cost=6.68,
        currency_symbol="$",
    )
    result = ProviderResult(
        provider=ProviderName.COPILOT,
        window=WindowPeriod.DAY_30,
        updated_at=datetime(2026, 4, 15, 15, 19, tzinfo=timezone.utc),
        metrics=metrics,
    )

    _print_result(ProviderName.COPILOT, result)
    panel_rows = [
        _strip_ansi_sequences(line)
        for line in capsys.readouterr().out.splitlines()
        if line.strip()
    ]

    usage_row = next(line for line in panel_rows if "Usage:" in line)
    assert "█" in usage_row
    assert usage_row.count("|") == 1
    assert "▓" in usage_row
    row_length = len(panel_rows[0])
    assert all(len(line) == row_length for line in panel_rows)


def test_show_uses_one_shared_panel_width_for_all_rendered_providers(
    monkeypatch,
) -> None:
    """
    @brief Verify one `show` execution renders all provider panels at one shared width.
    @details Mocks one bar-enabled provider and one text-only usage provider, then
    asserts visible border width is identical for every rendered panel and OpenAI
    usage text omits progress-bar glyphs.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-067
    @satisfies REQ-131
    @satisfies TST-030
    @satisfies TST-054
    """
    openrouter_result = ProviderResult(
        provider=ProviderName.OPENROUTER,
        window=WindowPeriod.DAY_7,
        metrics=UsageMetrics(cost=9.8765, remaining=90.0, limit=100.0),
        raw={"status_code": 200, "data": {"byok_usage_weekly": 4.2}},
    )
    openai_result = ProviderResult(
        provider=ProviderName.OPENAI,
        window=WindowPeriod.DAY_30,
        metrics=UsageMetrics(
            remaining=57.5,
            limit=100.0,
            cost=0.0,
            currency_symbol="€",
        ),
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
    top_borders = [
        line for line in visible_lines if line.startswith("┌") and line.endswith("┐")
    ]
    assert len(top_borders) == 2
    assert len({len(line) for line in top_borders}) == 1
    openai_usage_row = next(
        line for line in visible_lines if "Usage: 30d 42.5%" in line
    )
    assert "[" not in openai_usage_row
    assert "]" not in openai_usage_row
    assert "█" not in openai_usage_row
    assert "░" not in openai_usage_row
    assert "▓" not in openai_usage_row


def test_show_default_window_groups_dual_windows_into_one_panel_per_provider(
    monkeypatch,
) -> None:
    """
    @brief Verify default-window `show` groups Claude/Codex dual windows in single provider panels.
    @details Mocks Claude and Codex parser paths so each provider emits one grouped
    panel with shared `Updated/Next` metadata rendered once per provider panel.
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
                remaining=100.0 - usage_by_window[window],
                limit=100.0,
            )
            if provider_name == ProviderName.CODEX:
                metrics = UsageMetrics(
                    remaining=100.0 - usage_by_window[window],
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
    assert result.output.count("Window 5h:") == 0
    assert result.output.count("Window 7d:") == 0
    assert result.output.count("Updated:") == 2
    for _title, body_lines in panel_data:
        _assert_status_and_freshness_layout(body_lines)
        normalized_lines = [line.strip() for line in body_lines]
        assert not any(line.startswith("Window:") for line in normalized_lines)
        assert "Window 5h:" not in normalized_lines
        assert "Window 7d:" not in normalized_lines

    codex_body = panel_data[1][1]
    normalized_codex_body = [line.strip() for line in codex_body]
    idx_cost = next(
        idx
        for idx, line in enumerate(normalized_codex_body)
        if line.startswith("Cost:")
    )
    idx_requests = next(
        idx
        for idx, line in enumerate(normalized_codex_body)
        if line.startswith("Requests:")
    )
    idx_tokens = next(
        idx
        for idx, line in enumerate(normalized_codex_body)
        if line.startswith("Tokens:")
    )
    assert normalized_codex_body[idx_cost - 1] == ""
    assert idx_cost < idx_requests < idx_tokens


def test_show_default_window_keeps_dual_section_labels_when_other_providers_are_disabled(
    monkeypatch,
) -> None:
    """
    @brief Verify disabled single-window providers do not remove Claude/Codex `5h` and `7d` section labels.
    @details Reproduces the user-reported surface where `openrouter` and `openai`
    are disabled and Claude/Codex are the only rendered providers. Both dual-window
    providers return identical `5h` and `7d` usage values so panel assembly MUST
    preserve explicit `5h`/`7d` section labels and two usage rows instead of
    collapsing one row away.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-002
    @satisfies REQ-125
    @satisfies TST-030
    @satisfies TST-056
    """
    shared_updated_at = datetime(2026, 3, 18, 9, 0, tzinfo=timezone.utc)

    def _build_equal_dual_parser(provider_name: ProviderName):
        def _parse(_raw: dict, window: WindowPeriod) -> ProviderResult:
            metrics = UsageMetrics(
                remaining=50.0,
                limit=100.0,
                reset_at=datetime(2026, 3, 25, 12, 0, tzinfo=timezone.utc),
            )
            if provider_name == ProviderName.CODEX:
                metrics = UsageMetrics(
                    remaining=50.0,
                    limit=100.0,
                    reset_at=datetime(2026, 3, 25, 12, 0, tzinfo=timezone.utc),
                    cost=1.2345,
                    requests=42,
                    input_tokens=420,
                    output_tokens=42,
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
    claude_provider._parse_response = _build_equal_dual_parser(ProviderName.CLAUDE)

    codex_provider = MagicMock()
    codex_provider.is_configured.return_value = True
    codex_provider._parse_response = _build_equal_dual_parser(ProviderName.CODEX)

    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {
            ProviderName.CLAUDE: claude_provider,
            ProviderName.CODEX: codex_provider,
        },
    )
    monkeypatch.setattr(
        "aibar.cli.load_runtime_config",
        lambda: RuntimeConfig(
            enabled_providers={
                "claude": True,
                "openrouter": False,
                "copilot": False,
                "codex": True,
                "openai": False,
                "geminiai": False,
            }
        ),
    )
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **_: RetrievalPipelineOutput(
            payload={},
            results={
                ProviderName.CLAUDE.value: ProviderResult(
                    provider=ProviderName.CLAUDE,
                    window=WindowPeriod.DAY_7,
                    metrics=UsageMetrics(remaining=50.0, limit=100.0),
                    updated_at=shared_updated_at,
                    raw={"status_code": 200},
                ),
                ProviderName.CODEX.value: ProviderResult(
                    provider=ProviderName.CODEX,
                    window=WindowPeriod.DAY_7,
                    metrics=UsageMetrics(remaining=50.0, limit=100.0),
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
    assert "OPENROUTER" not in result.output
    assert "OPENAI" not in result.output

    panel_data = _extract_panel_titles_and_bodies(result.output)
    assert [title for title, _body in panel_data] == ["CLAUDE", "CODEX"]
    codex_body = [line.strip() for title, body in panel_data if title == "CODEX" for line in body]
    claude_body = [line.strip() for title, body in panel_data if title == "CLAUDE" for line in body]

    assert codex_body.count("5h") == 1
    assert codex_body.count("7d") == 1
    assert claude_body.count("5h") == 1
    assert claude_body.count("7d") == 1
    assert sum(line.startswith("Usage:") for line in codex_body) == 2
    assert sum(line.startswith("Usage:") for line in claude_body) == 2


def test_show_fail_panel_uses_status_reason_updated_layout(monkeypatch) -> None:
    """
    @brief Verify failed CLI panel layout uses `Status`, `Reason`, and `Updated` rows.
    @details Forces one failed provider result and asserts panel body renders
    `Status: FAIL`, blank line, `Reason: ...`, blank line, and `Updated/Next`
    without window heading rows.
    @param monkeypatch {_pytest.monkeypatch.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-036
    @satisfies TST-030
    """
    provider_stub = MagicMock()
    provider_stub.is_configured.return_value = True
    monkeypatch.setattr(
        "aibar.cli.get_providers",
        lambda: {ProviderName.OPENROUTER: provider_stub},
    )
    monkeypatch.setattr(
        "aibar.cli.retrieve_results_via_cache_pipeline",
        lambda **_: RetrievalPipelineOutput(
            payload={},
            results={
                ProviderName.OPENROUTER.value: ProviderResult(
                    provider=ProviderName.OPENROUTER,
                    window=WindowPeriod.DAY_30,
                    metrics=UsageMetrics(),
                    error="Invalid or expired OAuth token",
                    updated_at=datetime(2026, 3, 18, 9, 0, tzinfo=timezone.utc),
                    raw={"status_code": 401, "retry_after_seconds": 300},
                )
            },
            idle_time_by_provider={},
            idle_active=False,
            cache_available=True,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(main, ["show", "--provider", "openrouter", "--window", "7d"])
    assert result.exit_code == 0

    panel_data = _extract_panel_titles_and_bodies(result.output)
    assert len(panel_data) == 1
    _assert_fail_reason_layout(panel_data[0][1])
    normalized_lines = [line.strip() for line in panel_data[0][1]]
    assert all(not line.startswith("Window") for line in normalized_lines)


def test_show_orders_provider_panels_status_first_and_updated_last(monkeypatch) -> None:
    """
    @brief Verify `show` panel order and per-panel status/freshness row placement.
    @details Forces explicit `7d` rendering across all providers with shuffled input maps
    and asserts output panel order `CLAUDE, OPENROUTER, COPILOT, CODEX, OPENAI, GEMINIAI`
    while each panel body starts with `Status:` and ends with `Updated: ..., Next: ...`,
    and Copilot inserts one blank line between `Remaining credits` and `Cost`.
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
                remaining=87.5,
                limit=100.0,
                cost=0.1234,
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

    copilot_body_lines = panel_data[2][1]
    normalized_copilot_lines = [line.strip() for line in copilot_body_lines]
    remaining_line_index = next(
        index
        for index, line in enumerate(normalized_copilot_lines)
        if line.startswith("Remaining credits:")
    )
    cost_line_index = next(
        index
        for index, line in enumerate(normalized_copilot_lines)
        if line.startswith("Cost:")
    )
    assert cost_line_index == remaining_line_index + 2
    assert normalized_copilot_lines[remaining_line_index + 1] == ""
