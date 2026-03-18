"""
@file
@brief GNOME extension test launcher regressions.
@details Ensures the test script launches a nested GNOME Shell at 1024x800,
does not invoke `aibar gnome-install`, and accepts no subcommand
parameters per REQ-033.
@satisfies TST-004, REQ-031, REQ-033
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEV_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "test-gnome-extension.sh"


def test_script_includes_1024x800_dummy_mode_spec() -> None:
    """
    @brief Verify script sets MUTTER_DEBUG_DUMMY_MODE_SPECS to 1024x800.
    """
    source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    assert (
        "env MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland"
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
