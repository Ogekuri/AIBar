"""
@file
@brief GNOME extension test launcher regressions.
@details Ensures the test script launches a nested GNOME Shell at 1280x720,
does not invoke `aibar gnome-install`, and accepts no subcommand
parameters per REQ-033.
@satisfies TST-004, REQ-031, REQ-033
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEV_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "test-gnome-extension.sh"


def test_script_includes_1280x720_dummy_mode_spec() -> None:
    """
    @brief Verify script sets MUTTER_DEBUG_DUMMY_MODE_SPECS to 1280x720.
    @satisfies PRJ-004
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert (
        "env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- gnome-shell --nested --wayland"
        in source
    )


def test_script_does_not_invoke_aibar_gnome_install() -> None:
    """
    @brief Verify test script does not call extension update commands.
    @satisfies REQ-031
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "aibar gnome-install" not in source
    assert "update_extension" not in source


def test_script_does_not_use_case_dispatch() -> None:
    """
    @brief Verify script does not use case/esac subcommand dispatch.
    @details The script must execute directly without requiring any parameter.
    @satisfies REQ-033
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "case " not in source
    assert "esac" not in source


def test_script_does_not_require_arguments() -> None:
    """
    @brief Verify script does not reference positional parameters for dispatch.
    @satisfies REQ-033
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert '"${1:-}"' not in source
    assert "$1" not in source


def test_script_falls_back_to_headless_when_nested_option_removed() -> None:
    """
    @brief Verify launcher probes --nested support and falls back to --headless.
    @details Newer GNOME Shell releases removed the `--nested` option, so the
    launcher must probe `gnome-shell --help-all`, retain the legacy
    `--nested --wayland` launch when the option is advertised, and start
    `gnome-shell --headless` otherwise, with
    `MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720` applied in both branches.
    @satisfies REQ-031, PRJ-004
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert "gnome-shell --help-all" in source
    assert "grep -q -- --nested" in source
    assert (
        "env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- gnome-shell --headless"
        in source
    )
    assert (
        "env MUTTER_DEBUG_DUMMY_MODE_SPECS=1280x720 dbus-run-session -- gnome-shell --nested --wayland"
        in source
    )
