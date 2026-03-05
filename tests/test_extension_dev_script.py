"""
@file
@brief GNOME extension test launcher regressions.
@details Ensures nested-shell start flow forces the fixed 1024x800 dummy mode,
verifies install-gnome-extension.sh invocation before start, and validates
that only the start subcommand is present per REQ-033.
@satisfies TST-004, REQ-031, REQ-033
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEV_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "test-gnome-extension.sh"


def test_start_forces_1024x800_dummy_mode_spec() -> None:
    """
    @brief Verify start command sets MUTTER_DEBUG_DUMMY_MODE_SPECS to 1024x800.
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert (
        "env MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland"
        in source
    )


def test_start_invokes_install_before_execution() -> None:
    """
    @brief Verify start command calls update_extension before launching nested shell.
    @satisfies REQ-031
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    start_idx = source.index("start)")
    mutter_idx = source.index("MUTTER_DEBUG_DUMMY_MODE_SPECS", start_idx)
    update_idx = source.index("update_extension", start_idx)
    assert update_idx < mutter_idx, "update_extension must be called before nested shell launch"


def test_update_extension_calls_install_script() -> None:
    """
    @brief Verify update_extension function references install-gnome-extension.sh.
    @satisfies REQ-031
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "install-gnome-extension.sh" in source


def test_script_exposes_only_start_subcommand() -> None:
    """
    @brief Verify test script exposes only the start subcommand.
    @details Ensures enable, disable, reload, and logs subcommands are not present
    in the case dispatch of the script.
    @satisfies REQ-033
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "start)" in source
    assert "enable)" not in source
    assert "disable)" not in source
    assert "reload)" not in source
    assert "logs)" not in source


def test_usage_message_shows_only_start() -> None:
    """
    @brief Verify usage message advertises only the start subcommand.
    @satisfies REQ-033
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "{start}" in source
