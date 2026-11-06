"""
@file
@brief Nested session observation script regressions.
@details Source-level Level 0 assertions for `scripts/aibar-observe-nested-session.sh`:
argv-based nested shell launch with signal cleanup, snapshot capture through the
`org.gnome.Shell.Screenshot.Screenshot` D-Bus method, mandated snapshot path with
printed path per capture, and settle/interval defaults.
@satisfies TST-074, REQ-179, REQ-180, REQ-181, REQ-182
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OBSERVER_PATH = PROJECT_ROOT / "scripts" / "aibar-observe-nested-session.sh"


def read_observer_source() -> str:
    """
    @brief Load the observer script source for assertion.
    @return {str} Observer script content.
    """
    return OBSERVER_PATH.read_text(encoding="utf-8")


def test_observer_launches_argv_and_traps_signals() -> None:
    """
    @brief Verify observer launches argv as the nested shell and traps signals.
    expected_output: source contains argv launch, SIGINT/SIGTERM traps, and pid cleanup.
    @satisfies REQ-179
    """
    source = read_observer_source()
    assert '"$@" &' in source
    assert "trap cleanup INT TERM EXIT" in source
    assert 'kill "$shell_pid"' in source


def test_observer_captures_screenshot_dbus_method() -> None:
    """
    @brief Verify observer captures snapshots via the Screenshot D-Bus method.
    expected_output: source targets org.gnome.Shell on the session bus with the
    Screenshot method.
    @satisfies REQ-180
    """
    source = read_observer_source()
    assert "--dest org.gnome.Shell" in source
    assert "--method org.gnome.Shell.Screenshot.Screenshot" in source
    assert "--session" in source


def test_observer_snapshot_path_and_printed_capture() -> None:
    """
    @brief Verify observer writes the mandated snapshot path and prints it.
    expected_output: snapshot file under ~/.cache/aibar/nested-shell and per-capture
    path echo.
    @satisfies REQ-181
    """
    source = read_observer_source()
    assert '"${HOME}/.cache/aibar/nested-shell"' in source
    assert "nested-shell-snapshot.png" in source
    assert "mkdir -p" in source
    assert "Observation snapshot saved" in source


def test_observer_settle_and_interval_defaults() -> None:
    """
    @brief Verify observer applies 3-second settle and 5-second interval defaults.
    expected_output: default expansions resolve to 3 and 5 seconds respectively.
    @satisfies REQ-182
    """
    source = read_observer_source()
    assert 'AIBAR_NESTED_SETTLE_SECONDS:-3' in source
    assert 'AIBAR_NESTED_SNAPSHOT_INTERVAL:-5' in source
