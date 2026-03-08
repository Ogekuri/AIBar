"""
@file
@brief CLI reset countdown formatting regression tests.
@details Verifies `show` text-mode output uses UI-style reset text with day token when remaining duration exceeds 24 hours.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = PROJECT_ROOT / "src" / "aibar" / "aibar" / "cli.py"


def test_show_reset_output_uses_ui_style_day_token() -> None:
    """
    @brief Verify CLI source renders reset text with day token format for multi-day durations.
    """
    source = CLI_PATH.read_text(encoding="utf-8")
    assert "reset_value = _format_reset_duration(delta.total_seconds())" in source
    assert 'lines.append(f"Resets in: {reset_value}")' in source
    assert 'return f"{days}d {hours}h {minutes}m"' in source
    assert 'return f"{hours}h {minutes}m"' in source


def test_show_output_prints_remaining_credits_for_quota_providers() -> None:
    """
    @brief Verify CLI source renders remaining-credits line for quota providers.
    """
    source = CLI_PATH.read_text(encoding="utf-8")
    assert "ProviderName.CLAUDE" in source
    assert "ProviderName.CODEX" in source
    assert "ProviderName.COPILOT" in source
    assert "ProviderName.GEMINIAI" in source
    assert 'lines.append(f"Remaining credits: {m.remaining:.1f} / {m.limit:.1f}")' in source
