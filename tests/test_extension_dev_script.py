"""
@file
@brief GNOME extension dev launcher regressions.
@details Ensures nested-shell start flow forces the fixed 1024x800 dummy mode.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEV_SCRIPT_PATH = PROJECT_ROOT / "src" / "aibar" / "extension" / "aibar@aibar.panel" / "dev.sh"


def test_start_forces_1024x800_dummy_mode_spec() -> None:
    """
    @brief Verify start command sets MUTTER_DEBUG_DUMMY_MODE_SPECS to 1024x800.
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert (
        "env MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland"
        in source
    )
