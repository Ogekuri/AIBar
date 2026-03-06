"""
@file
@brief Chrome parser extraction assertions using localized HTML fixtures.
@details Executes parser functions in Node and validates extracted metrics are
derived from structural semantics instead of localized text labels.
@satisfies TST-015
@satisfies TST-016
"""

import json
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures" / "chrome_extension"
NODE_PARSER_RUNNER = PROJECT_ROOT / "tests" / "helpers" / "chrome_parser_runner.mjs"
NODE_MERGE_RUNNER = PROJECT_ROOT / "tests" / "helpers" / "chrome_merge_runner.mjs"
PARSER_MODULE_PATH = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "parsers.mjs"


def _run_parser(function_name: str, fixture_name: str) -> dict:
    """
    @brief Execute one parser function through Node helper.
    @param function_name {str} Exported parser function name.
    @param fixture_name {str} Fixture file name under tests/fixtures/chrome_extension.
    @return {dict} Parsed JSON payload.
    """
    fixture_path = FIXTURE_DIR / fixture_name
    completed = subprocess.run(
        [
            "node",
            str(NODE_PARSER_RUNNER),
            function_name,
            str(fixture_path),
        ],
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


def test_parser_module_uses_semantic_markers_instead_of_language_labels() -> None:
    """
    @brief Verify parser module relies on structural markers for extraction.
    @satisfies CTN-010
    @satisfies TST-015
    """
    source = PARSER_MODULE_PATH.read_text(encoding="utf-8")
    assert "role\\s*=\\s*(?:\"progressbar\"|\'progressbar\')" in source
    assert "datetime\\s*=\\s*(?:\"([^\"]+)\"|'([^']+)')" in source
    assert "_extractEmbeddedJsonObjects" in source
    assert "Usage:" not in source
