"""
@file
@brief GNOME extension dev launcher regressions.
@details Ensures nested-shell start flow forces the fixed 1024x800 dummy mode
and verifies install-gnome-extension.sh invocation before start/enable/reload.
@satisfies TST-004, REQ-031
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
    mutter_idx = source.index("MUTTER_DEBUG_DUMMY_MODE_SPECS")
    update_idx = source.index("update_extension", start_idx)
    assert update_idx < mutter_idx, "update_extension must be called before nested shell launch"


def test_enable_invokes_install_before_execution() -> None:
    """
    @brief Verify enable command calls update_extension before gnome-extensions enable.
    @satisfies REQ-031
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    enable_idx = source.index("enable)")
    gnome_enable_idx = source.index("gnome-extensions enable", enable_idx)
    update_idx = source.index("update_extension", enable_idx)
    assert update_idx < gnome_enable_idx, "update_extension must be called before gnome-extensions enable"


def test_reload_invokes_install_before_execution() -> None:
    """
    @brief Verify reload command calls update_extension before gnome-extensions disable/enable cycle.
    @satisfies REQ-031
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    reload_idx = source.index("reload)")
    gnome_disable_idx = source.index("gnome-extensions disable", reload_idx)
    update_idx = source.index("update_extension", reload_idx)
    assert update_idx < gnome_disable_idx, "update_extension must be called before reload cycle"


def test_update_extension_calls_install_script() -> None:
    """
    @brief Verify update_extension function references install-gnome-extension.sh.
    @satisfies REQ-031
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "install-gnome-extension.sh" in source
