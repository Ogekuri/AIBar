"""
@file
@brief Chrome parser extraction assertions using localized HTML fixtures.
@details Executes parser functions in Node and validates extracted metrics are
derived from structural semantics instead of localized text labels.
@satisfies TST-015
@satisfies TST-016
@satisfies TST-025
"""

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures" / "chrome_extension"
NODE_PARSER_RUNNER = PROJECT_ROOT / "tests" / "helpers" / "chrome_parser_runner.mjs"
NODE_MERGE_RUNNER = PROJECT_ROOT / "tests" / "helpers" / "chrome_merge_runner.mjs"
PARSER_MODULE_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "parsers.js"


def _run_parser(
    function_name: str, fixture_name: str, second_payload: dict | None = None
) -> dict:
    """
    @brief Execute one parser function through Node helper.
    @param function_name {str} Exported parser function name.
    @param fixture_name {str} Fixture file name under tests/fixtures/chrome_extension.
    @return {dict} Parsed JSON payload.
    """
    fixture_path = FIXTURE_DIR / fixture_name
    command = [
        "node",
        str(NODE_PARSER_RUNNER),
        function_name,
        str(fixture_path),
    ]
    if second_payload is not None:
        command.append(json.dumps(second_payload))

    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    return json.loads(completed.stdout)


def _run_copilot_merge(features_fixture: str, premium_fixture: str) -> dict:
    """
    @brief Execute Copilot merge path through Node helper.
    @param features_fixture {str} Features fixture file name.
    @param premium_fixture {str} Premium fixture file name.
    @return {dict} Merged Copilot payload.
    """
    completed = subprocess.run(
        [
            "node",
            str(NODE_MERGE_RUNNER),
            str(FIXTURE_DIR / features_fixture),
            str(FIXTURE_DIR / premium_fixture),
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    return json.loads(completed.stdout)


def test_claude_parser_extracts_dual_window_metrics_from_localized_fixture() -> None:
    """
    @brief Verify Claude parser returns deterministic 5h/7d metrics.
    @satisfies TST-015
    @satisfies REQ-040
    """
    payload = _run_parser("parseClaudeUsageHtml", "claude_usage_localized.html")
    assert payload["provider"] == "claude"
    assert payload["windows"]["5h"]["usage_percent"] == 42
    assert payload["windows"]["7d"]["usage_percent"] == 84
    assert payload["windows"]["5h"]["limit"] == 100
    assert payload["windows"]["7d"]["limit"] == 100


def test_codex_parser_extracts_dual_window_metrics_from_localized_fixture() -> None:
    """
    @brief Verify Codex parser returns deterministic 5h/7d metrics.
    @satisfies TST-015
    @satisfies REQ-041
    """
    payload = _run_parser("parseCodexUsageHtml", "codex_usage_localized.html")
    assert payload["provider"] == "codex"
    assert payload["windows"]["5h"]["usage_percent"] == 33
    assert payload["windows"]["7d"]["usage_percent"] == 71


def test_claude_parser_extracts_metrics_from_bootstrap_script_fixture() -> None:
    """
    @brief Verify Claude parser extracts quotas from bootstrap script JSON.
    @satisfies TST-015
    @satisfies REQ-040
    """
    payload = _run_parser("parseClaudeUsageHtml", "claude_usage_bootstrap_script.html")
    assert payload["provider"] == "claude"
    assert payload["windows"]["5h"]["usage_percent"] == 42
    assert payload["windows"]["5h"]["limit"] == 50
    assert payload["windows"]["5h"]["remaining"] == 29
    assert payload["windows"]["7d"]["usage_percent"] == 16
    assert payload["windows"]["7d"]["limit"] == 500
    assert payload["windows"]["7d"]["remaining"] == 420


def test_codex_parser_ignores_reset_only_json_candidates() -> None:
    """
    @brief Verify Codex parser does not treat reset-only JSON as usable metrics.
    @satisfies TST-015
    @satisfies REQ-041
    """
    payload = _run_parser("parseCodexUsageHtml", "codex_usage_reset_only_json.html")
    assert payload["provider"] == "codex"
    assert payload["windows"]["5h"]["usage_percent"] is None
    assert payload["windows"]["5h"]["remaining"] is None
    assert payload["windows"]["5h"]["limit"] is None
    assert payload["windows"]["5h"]["reset_at"] is None
    assert payload["windows"]["7d"]["usage_percent"] is None
    assert payload["windows"]["7d"]["remaining"] is None
    assert payload["windows"]["7d"]["limit"] is None
    assert payload["windows"]["7d"]["reset_at"] is None


def test_codex_parser_extracts_metrics_from_escaped_script_fixture() -> None:
    """
    @brief Verify Codex parser extracts quotas from escaped script key/value payload.
    @satisfies TST-015
    @satisfies REQ-041
    """
    payload = _run_parser("parseCodexUsageHtml", "codex_usage_escaped_script.html")
    assert payload["provider"] == "codex"
    assert payload["windows"]["5h"]["usage_percent"] == 45
    assert payload["windows"]["5h"]["limit"] == 40
    assert payload["windows"]["5h"]["remaining"] == 22
    assert payload["windows"]["7d"]["usage_percent"] == 35
    assert payload["windows"]["7d"]["limit"] == 400
    assert payload["windows"]["7d"]["remaining"] == 260


def test_codex_parser_rejects_noise_only_fraction_artifacts() -> None:
    """
    @brief Verify Codex parser rejects non-quota fractions from challenge/noise payloads.
    @satisfies REQ-041
    @satisfies TST-025
    """
    payload = _run_parser("parseCodexUsageHtml", "codex_usage_noise_fractions.html")
    assert payload["provider"] == "codex"
    assert payload["windows"]["5h"]["usage_percent"] is None
    assert payload["windows"]["5h"]["remaining"] is None
    assert payload["windows"]["5h"]["limit"] is None
    assert payload["windows"]["7d"]["usage_percent"] is None
    assert payload["windows"]["7d"]["remaining"] is None
    assert payload["windows"]["7d"]["limit"] is None


def test_signal_diagnostics_reports_metric_key_matches_for_escaped_script() -> None:
    """
    @brief Verify signal diagnostics include matched metric-key evidence.
    @satisfies TST-021
    @satisfies REQ-048
    """
    diagnostics = _run_parser(
        "extractSignalDiagnostics", "codex_usage_escaped_script.html"
    )
    assert diagnostics["signal_counts"]["metric_key_matches"] >= 2
    assert diagnostics["signal_samples"]["metric_key_matches"]


def test_window_assignment_diagnostics_exposes_ranked_trace_payload() -> None:
    """
    @brief Verify window diagnostics returns candidate rankings and derived window values.
    @satisfies REQ-048
    @satisfies TST-021
    """
    diagnostics = _run_parser(
        "extractWindowAssignmentDiagnostics",
        "codex_usage_escaped_script.html",
        {"provider": "codex"},
    )
    assert diagnostics["provider"] == "codex"
    assert diagnostics["window_keys"] == ["5h", "7d", "code_review"]
    assert diagnostics["window_trace"]["5h"]["ranked_candidates"]["json"]
    assert "derived_window" in diagnostics["window_trace"]["7d"]


def test_copilot_merge_combines_features_and_premium_sources() -> None:
    """
    @brief Verify Copilot merge output consolidates both source pages.
    @satisfies TST-016
    @satisfies REQ-042
    """
    payload = _run_copilot_merge(
        "copilot_features_localized.html",
        "copilot_premium_localized.html",
    )
    assert payload["provider"] == "copilot"
    assert payload["windows"]["30d"]["remaining"] == 820
    assert payload["windows"]["30d"]["limit"] == 1000
    assert payload["windows"]["30d"]["reset_at"] == "2026-03-31T00:00:00.000Z"


def test_claude_parser_matches_current_usage_page_statistics_fixture() -> None:
    """
    @brief Verify Claude parser maps current session/weekly usage percentages.
    @satisfies REQ-040
    @satisfies TST-025
    """
    payload = _run_parser("parseClaudeUsageHtml", "claude_usage_current_signals.html")
    assert payload["provider"] == "claude"
    assert payload["windows"]["5h"]["usage_percent"] == 0
    assert payload["windows"]["7d"]["usage_percent"] == 11
    assert payload["windows"]["7d"]["reset_at"] == "2026-03-06T11:59:00.000Z"


def test_codex_parser_converts_remaining_percentages_from_current_fixture() -> None:
    """
    @brief Verify Codex parser converts remaining percentages to usage percentages.
    @satisfies REQ-041
    @satisfies TST-025
    """
    payload = _run_parser("parseCodexUsageHtml", "codex_usage_current_signals.html")
    assert payload["provider"] == "codex"
    assert payload["windows"]["5h"]["usage_percent"] == 0
    assert payload["windows"]["7d"]["usage_percent"] == 32
    assert payload["windows"]["code_review"]["usage_percent"] == 0
    assert payload["windows"]["5h"]["reset_at"] == "2026-03-07T18:30:00.000Z"
    assert payload["windows"]["7d"]["reset_at"] == "2026-03-10T12:16:00.000Z"
    assert payload["windows"]["code_review"]["reset_at"] is None


def test_copilot_merge_matches_current_features_and_premium_fixture() -> None:
    """
    @brief Verify Copilot merge keeps features percentage and premium quota/reset fields.
    @satisfies REQ-042
    @satisfies TST-025
    """
    payload = _run_copilot_merge(
        "copilot_features_current_signals.html",
        "copilot_premium_current_signals.html",
    )
    assert payload["provider"] == "copilot"
    assert payload["windows"]["30d"]["usage_percent"] == 24.4
    assert payload["windows"]["30d"]["remaining"] == 1179
    assert payload["windows"]["30d"]["limit"] == 1500
    assert payload["windows"]["30d"]["reset_at"] == "2026-04-01T00:00:00.000Z"


def test_parser_module_uses_semantic_markers_instead_of_language_labels() -> None:
    """
    @brief Verify parser module relies on structural markers for extraction.
    @satisfies CTN-010
    @satisfies TST-015
    """
    source = PARSER_MODULE_PATH.read_text(encoding="utf-8")
    assert "role\\s*=\\s*(?:\"progressbar\"|'progressbar')" in source
    assert "datetime\\s*=\\s*(?:\"([^\"]+)\"|'([^']+)')" in source
    assert "_extractEmbeddedJsonObjects" in source
    assert "_extractEscapedScriptMetricCandidates" in source
    assert "Usage:" not in source
