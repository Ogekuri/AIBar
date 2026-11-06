"""
@file
@brief Nested session debug environment script regressions.
@details Source-level Level 0 assertions for `scripts/aibar-nested-debug-session.sh`:
argv-based background nested shell launch with signal cleanup, interactive debug
shell sharing the nested session bus after the settle delay, extension inspection
guidance output, termination of the nested shell when the debug shell exits, and
absence of screenshot capture logic in the debug launcher surface.
@satisfies TST-074, REQ-178, REQ-179, REQ-180, REQ-181, REQ-182
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEBUG_WRAPPER_PATH = PROJECT_ROOT / "scripts" / "aibar-nested-debug-session.sh"
DEV_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "test-gnome-extension.sh"
OBSERVER_REMNANT_PATH = PROJECT_ROOT / "scripts" / "aibar-observe-nested-session.sh"


def read_debug_wrapper_source() -> str:
    """
    @brief Load the debug wrapper script source for assertion.
    @return {str} Debug wrapper script content.
    """
    return DEBUG_WRAPPER_PATH.read_text(encoding="utf-8")


def test_wrapper_launches_argv_in_background_and_traps_signals() -> None:
    """
    @brief Verify wrapper launches argv in background and traps SIGINT/SIGTERM.
    expected_output: source contains argv background launch, signal traps, and pid cleanup.
    @satisfies REQ-179
    """
    source = read_debug_wrapper_source()
    assert '"$@" &' in source
    assert "trap cleanup INT TERM EXIT" in source
    assert 'kill "$shell_pid"' in source


def test_wrapper_starts_interactive_debug_shell_after_settle() -> None:
    """
    @brief Verify wrapper starts an interactive debug shell after the settle delay.
    expected_output: 3-second settle default followed by an interactive bash shell.
    @satisfies REQ-180
    """
    source = read_debug_wrapper_source()
    assert "AIBAR_NESTED_SETTLE_SECONDS:-3" in source
    assert "bash --noprofile --norc -i" in source


def test_wrapper_prints_extension_inspection_guidance() -> None:
    """
    @brief Verify wrapper prints extension inspection guidance before the debug shell.
    expected_output: guidance block listing gnome-extensions and aibar debug commands.
    @satisfies REQ-181
    """
    source = read_debug_wrapper_source()
    assert "gnome-extensions info aibar@aibar.panel" in source
    assert "gnome-extensions list --enabled" in source
    assert "aibar show --json --force" in source
    assert "aibar doctor" in source


def test_wrapper_terminates_nested_shell_on_debug_shell_exit() -> None:
    """
    @brief Verify wrapper terminates the nested shell when the debug shell exits.
    expected_output: debug-shell status captured, cleanup invoked, status propagated.
    @satisfies REQ-182
    """
    source = read_debug_wrapper_source()
    assert "debug_status=$?" in source
    assert "exit \"$debug_status\"" in source


def test_debug_surface_contains_no_screenshot_logic() -> None:
    """
    @brief Verify no screenshot capture logic remains in the debug launch surface.
    expected_output: no Screenshot D-Bus method, gdbus snapshot calls, snapshot
    paths, or observer-script references in the launcher and wrapper; the observer
    script file is absent.
    @satisfies TST-074
    """
    dev_source = DEV_SCRIPT_PATH.read_text(encoding="utf-8")
    wrapper_source = read_debug_wrapper_source()
    for source in (dev_source, wrapper_source):
        assert "Shell.Screenshot" not in source
        assert "gdbus" not in source
        assert "nested-shell-snapshot" not in source
        assert "observe-nested-session" not in source
    assert not OBSERVER_REMNANT_PATH.exists()
