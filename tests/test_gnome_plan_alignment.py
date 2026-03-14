"""
@file
@brief GNOME plan consistency regression test.
@details Validates that `src/aibar/plans/Gnome.plan.md` documents the current
JSON contract, GNOME popup actions, branding, and GeminiAI integration required
by the implemented extension behavior.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GNOME_PLAN_PATH = PROJECT_ROOT / "src" / "aibar" / "plans" / "Gnome.plan.md"


def test_gnome_plan_matches_current_extension_contract() -> None:
    """
    @brief Verify GNOME plan content matches implemented extension contract.
    @details Asserts the plan documents the canonical `show --json` envelope
    (`payload`, `status`, `extension.gnome_refresh_interval_seconds`), forced
    refresh behavior, AIBar branding, and GeminiAI provider ordering/labeling.
    @return {None} Function return value.
    @satisfies PRJ-004
    @satisfies DES-006
    @satisfies REQ-003
    @satisfies REQ-016
    @satisfies REQ-017
    @satisfies REQ-021
    @satisfies REQ-053
    @satisfies REQ-061
    @satisfies REQ-062
    """
    source = GNOME_PLAN_PATH.read_text(encoding="utf-8")

    assert "\"payload\": {" in source
    assert "\"status\": {" in source
    assert "\"extension\": {" in source
    assert "\"gnome_refresh_interval_seconds\": 60" in source
    assert "aibar show --json --force" in source
    assert "Open AIBar Report" in source
    assert "AIBar Monitor" in source
    assert "geminiai" in source
    assert "GEMINIAI" in source
    assert "['claude', 'openrouter', 'copilot', 'codex', 'geminiai']" in source

    assert "Open aibar UI" not in source
    assert "aibar Monitor" not in source
