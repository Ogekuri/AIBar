"""
@file
@brief GNOME extension quota-label regressions.
@details Ensures quota-only provider cards use the "remaining credits" suffix.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_PATH = PROJECT_ROOT / "src" / "aibar" / "extension" / "aibar@aibar.panel" / "extension.js"


def test_quota_only_label_uses_remaining_credits_suffix() -> None:
    """
    @brief Verify quota-only card labels use "remaining credits".
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert (
        "`${metrics.remaining.toFixed(1)} / ${metrics.limit.toFixed(1)} remaining credits`"
        in source
    )
    assert (
        "`${metrics.remaining.toFixed(1)} / ${metrics.limit.toFixed(1)} credits`"
        not in source
    )
