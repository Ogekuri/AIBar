"""
@file
@brief Nested session debug environment script regressions.
@details Level 0 source assertions and Level 1 subprocess-behavior tests for
`scripts/aibar-nested-debug-session.sh`: argv-based background nested shell
launch, SIGINT/SIGTERM whole-session termination without a residual interactive
shell, interactive debug shell sharing the nested session bus after the settle
delay with inherited wrapper stdin, extension inspection guidance, nested-shell
termination on debug-shell exit with status propagation, and absence of
screenshot capture logic.
@satisfies TST-074, REQ-178, REQ-179, REQ-180, REQ-181, REQ-182
"""

import os
import signal
import subprocess
import time
from pathlib import Path

import pytest


## @brief Repository root path for resolving repository scripts.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
## @brief Debug wrapper script under test.
DEBUG_WRAPPER_PATH = PROJECT_ROOT / "scripts" / "aibar-nested-debug-session.sh"
## @brief GNOME extension test launcher script.
DEV_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "test-gnome-extension.sh"
## @brief Legacy observer script that must remain absent.
OBSERVER_REMNANT_PATH = PROJECT_ROOT / "scripts" / "aibar-observe-nested-session.sh"
## @brief Bounded polling deadline for subprocess boundary observations (seconds).
EVENT_TIMEOUT_SECONDS = 10.0


def read_debug_wrapper_source() -> str:
    """
    @brief Load the debug wrapper script source for assertion.
    @details O(N) file read; no filesystem mutation.
    @return {str} Debug wrapper script content.
    """
    return DEBUG_WRAPPER_PATH.read_text(encoding="utf-8")


def test_wrapper_launches_argv_in_background_and_traps_signals() -> None:
    """
    @brief Verify wrapper launches argv in background and traps SIGINT/SIGTERM.
    @details Level 0; O(N) source scan; asserts background launch, dedicated
    interrupt traps that terminate the whole session, EXIT cleanup trap, and
    nested-shell kill.
    expected_output: source contains argv background launch, terminate_session
    interrupt traps, cleanup EXIT trap, and pid kill.
    @return {None} Assertions complete.
    @satisfies REQ-179
    """
    source = read_debug_wrapper_source()
    assert '"$@" &' in source
    assert "trap 'terminate_session 130' INT" in source
    assert "trap 'terminate_session 143' TERM" in source
    assert "trap cleanup EXIT" in source
    assert 'kill "$shell_pid"' in source


def test_wrapper_starts_interactive_debug_shell_after_settle() -> None:
    """
    @brief Verify wrapper starts an interactive debug shell after the settle delay.
    @details Level 0; O(N) source scan; job control stays disabled so the debug
    shell shares the wrapper foreground process group.
    expected_output: 3-second settle default followed by an interactive bash shell.
    @return {None} Assertions complete.
    @satisfies REQ-180
    """
    source = read_debug_wrapper_source()
    assert "AIBAR_NESTED_SETTLE_SECONDS:-3" in source
    assert "bash --noprofile --norc -i" in source


def test_wrapper_prints_extension_inspection_guidance() -> None:
    """
    @brief Verify wrapper prints extension inspection guidance before the debug shell.
    @details Level 0; O(N) source scan.
    expected_output: guidance block listing gnome-extensions and aibar debug commands.
    @return {None} Assertions complete.
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
    @details Level 0; O(N) source scan; debug-shell status captured and propagated.
    expected_output: debug-shell status captured, cleanup invoked, status propagated.
    @return {None} Assertions complete.
    @satisfies REQ-182
    """
    source = read_debug_wrapper_source()
    assert "reaped_status=$?" in source
    assert 'exit "$reaped_status"' in source
    assert "wait -n" in source


def test_debug_surface_contains_no_screenshot_logic() -> None:
    """
    @brief Verify no screenshot capture logic remains in the debug launch surface.
    @details Level 0; O(N) source scan; observer script file remains absent.
    expected_output: no Screenshot D-Bus method, gdbus snapshot calls, snapshot
    paths, or observer-script references in the launcher and wrapper.
    @return {None} Assertions complete.
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


def _write_executable(path: Path, body: str) -> None:
    """
    @brief Create one executable bash substitute for a wrapper dependency.
    @details Writes a deterministic script and marks it executable; O(N) bytes.
    @param path {Path} Target executable path.
    @param body {str} Bash statements appended after the shebang.
    @return {None} File created.
    """
    path.write_text("#!/bin/bash\n" + body, encoding="utf-8")
    path.chmod(0o755)


def _wait_for_event(events: Path, marker: str) -> None:
    """
    @brief Block until the dependency event log contains one marker.
    @details Bounded 10-second polling at 50-millisecond intervals; fails with
    AssertionError when the deadline expires.
    @param events {Path} Event log path written by dependency substitutes.
    @param marker {str} Expected event line.
    @return {None} Marker observed.
    """
    deadline = time.monotonic() + EVENT_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        try:
            content = events.read_text(encoding="utf-8")
        except FileNotFoundError:
            content = ""
        if marker in content:
            return
        time.sleep(0.05)
    raise AssertionError(f"expected event not observed: {marker}")


@pytest.fixture
def debug_session_env(tmp_path: Path) -> tuple[dict[str, str], Path, Path]:
    """
    @brief Build isolated wrapper dependency substitutes and environment.
    @details Replaces `bash` (debug shell) and the nested shell command with
    event-recording executables under a temporary PATH prefix; no GNOME session,
    D-Bus daemon, network, or user configuration is touched. O(1) files.
    @param tmp_path {Path} Pytest-owned temporary directory.
    @return {tuple} Environment map, event log path, nested-command path.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    events = tmp_path / "events"
    nested = bin_dir / "nested-fake"
    _write_executable(
        nested,
        'printf "nested-start\\n" >> "$EVENTS"\n'
        'if [ -n "${DEBUG_NESTED_EXIT_STATUS:-}" ]; then\n'
        '    exit "$DEBUG_NESTED_EXIT_STATUS"\n'
        "fi\n"
        "sleep 30\n"
        'printf "nested-end\\n" >> "$EVENTS"\n',
    )
    fake_bash = bin_dir / "bash"
    _write_executable(
        fake_bash,
        'printf "debug-start\\n" >> "$EVENTS"\n'
        'if [ -n "${DEBUG_EXIT_STATUS:-}" ]; then exit "$DEBUG_EXIT_STATUS"; fi\n'
        'if [ "${DEBUG_READ_STDIN:-}" = "1" ]; then\n'
        "    read -r debug_line || true\n"
        '    printf "debug-input:%s\\n" "$debug_line" >> "$EVENTS"\n'
        "fi\n"
        "sleep 30\n"
        'printf "debug-end\\n" >> "$EVENTS"\n',
    )
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "EVENTS": str(events),
    }
    env.pop("BASH_ENV", None)
    env.pop("ENV", None)
    return env, events, nested


def _start_wrapper(
    env: dict[str, str], nested: Path, settle: int,
    stdin: int = subprocess.DEVNULL,
) -> subprocess.Popen:
    """
    @brief Start the debug wrapper with substituted dependencies.
    @details O(1) process spawn; combined output captured; stdin selectable.
    @param env {dict[str, str]} Substitution environment.
    @param nested {Path} Nested-command executable path.
    @param settle {int} AIBAR_NESTED_SETTLE_SECONDS override.
    @param stdin {int} Stdin fileno for the wrapper (DEVNULL or PIPE).
    @return {subprocess.Popen} Wrapper process handle.
    """
    return subprocess.Popen(
        ["/bin/bash", str(DEBUG_WRAPPER_PATH), str(nested)],
        env={**env, "AIBAR_NESTED_SETTLE_SECONDS": str(settle)},
        stdin=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def _stop_wrapper(proc: subprocess.Popen) -> None:
    """
    @brief Reap the wrapper process after assertions or failure.
    @details Kills surviving processes, waits bounded, and closes the pipe.
    @param proc {subprocess.Popen} Wrapper process handle.
    @return {None} Process reaped.
    """
    if proc.stdin is not None:
        proc.stdin.close()
    if proc.poll() is None:
        proc.kill()
    proc.wait(timeout=EVENT_TIMEOUT_SECONDS)
    if proc.stdout is not None:
        proc.stdout.close()


def test_sigint_during_settle_exits_wrapper_without_debug_shell(
    debug_session_env: tuple[dict[str, str], Path, Path],
) -> None:
    """
    @brief Verify SIGINT during the settle delay ends the session without a debug shell.
    @details Reproducer for the residual intermediate shell: pre-fix the wrapper
    resumed after its SIGINT trap, spawned the interactive debug shell, and never
    returned to the invoking terminal. Post-fix the wrapper kills the nested
    shell, never starts the debug shell, and exits 130. Level 1 subprocess
    boundaries; bounded polling; no GNOME session or network.
    expected_output: wrapper exit 130; events contain only nested-start.
    @param debug_session_env {tuple} Substitution environment, event log, nested path.
    @return {None} Assertions complete.
    @satisfies REQ-179, TST-074
    """
    env, events, nested = debug_session_env
    proc = _start_wrapper(env, nested, settle=4)
    try:
        _wait_for_event(events, "nested-start")
        assert proc.poll() is None
        time.sleep(1.0)
        proc.send_signal(signal.SIGINT)
        returncode = proc.wait(timeout=EVENT_TIMEOUT_SECONDS)
    finally:
        _stop_wrapper(proc)
    assert returncode == 130
    assert events.read_text(encoding="utf-8").splitlines() == ["nested-start"]


def test_sigint_during_debug_shell_terminates_whole_session(
    debug_session_env: tuple[dict[str, str], Path, Path],
) -> None:
    """
    @brief Verify SIGINT after the debug shell starts terminates both shells.
    @details Pre-fix the SIGINT trap killed only the nested shell and the wrapper
    kept waiting on the interactive debug shell, leaving a residual intermediate
    shell instead of the invoking terminal prompt. Post-fix the wrapper SIGKILLs
    every background job (debug shell and nested shell) and exits 130. Level 1
    subprocess boundaries; bounded polling; no GNOME session or network.
    expected_output: wrapper exit 130; events stop after debug-start.
    @param debug_session_env {tuple} Substitution environment, event log, nested path.
    @return {None} Assertions complete.
    @satisfies REQ-179, REQ-182, TST-074
    """
    env, events, nested = debug_session_env
    proc = _start_wrapper(env, nested, settle=1)
    try:
        _wait_for_event(events, "nested-start")
        _wait_for_event(events, "debug-start")
        proc.send_signal(signal.SIGINT)
        returncode = proc.wait(timeout=EVENT_TIMEOUT_SECONDS)
    finally:
        _stop_wrapper(proc)
    observed = events.read_text(encoding="utf-8").splitlines()
    assert returncode == 130
    assert observed == ["nested-start", "debug-start"]


def test_nested_shell_exit_terminates_debug_shell(
    debug_session_env: tuple[dict[str, str], Path, Path],
) -> None:
    """
    @brief Verify nested-shell exit terminates the debug shell and wrapper.
    @details Reproducer for the Devkit window-close defect: closing the debug
    interface terminates the nested GNOME Shell while the wrapper waits only
    for the debug shell, so the interactive debug shell survived the session
    and left a residual `bash-5.3$` prompt. The wrapper must reap either
    background job first, terminate the survivor when the nested shell exits,
    and return the nested-shell status. Level 1 subprocess boundaries with a
    PATH-substituted debug shell that sleeps; bounded polling; no GNOME
    session or network.
    expected_output: wrapper exits promptly with the nested status (5); no
    session-end markers are recorded because the debug shell is killed.
    @param debug_session_env {tuple} Substitution environment, event log, path.
    @return {None} Assertions complete.
    @satisfies REQ-179, REQ-182, TST-074
    """
    env, events, nested = debug_session_env
    proc = _start_wrapper(
        {**env, "DEBUG_NESTED_EXIT_STATUS": "5"}, nested, settle=1
    )
    try:
        _wait_for_event(events, "nested-start")
        returncode = proc.wait(timeout=EVENT_TIMEOUT_SECONDS)
    finally:
        _stop_wrapper(proc)
    observed = events.read_text(encoding="utf-8").splitlines()
    assert returncode == 5
    assert "nested-start" in observed
    assert "nested-end" not in observed
    assert "debug-end" not in observed


def test_debug_shell_exit_status_propagates_and_nested_shell_stops(
    debug_session_env: tuple[dict[str, str], Path, Path],
) -> None:
    """
    @brief Verify normal debug-shell exit propagates status and stops the nested shell.
    @details Level 1 regression guard for REQ-182: debug shell exit 7 becomes the
    wrapper exit status and the nested shell receives termination before exit.
    expected_output: wrapper exit 7; events contain nested-start and debug-start
    without nested-end.
    @param debug_session_env {tuple} Substitution environment, event log, nested path.
    @return {None} Assertions complete.
    @satisfies REQ-182, TST-074
    """
    env, events, nested = debug_session_env
    proc = _start_wrapper({**env, "DEBUG_EXIT_STATUS": "7"}, nested, settle=1)
    try:
        _wait_for_event(events, "nested-start")
        returncode = proc.wait(timeout=EVENT_TIMEOUT_SECONDS)
    finally:
        _stop_wrapper(proc)
    observed = events.read_text(encoding="utf-8").splitlines()
    assert returncode == 7
    assert observed == ["nested-start", "debug-start"]


def test_debug_shell_receives_wrapper_stdin(
    debug_session_env: tuple[dict[str, str], Path, Path],
) -> None:
    """
    @brief Verify the debug shell reads the wrapper's standard input.
    @details Reproducer for the 260b3f0 regression: without job control bash
    assigns /dev/null as stdin to background commands, so the backgrounded
    interactive debug shell saw immediate EOF and the whole nested debug
    session terminated as soon as it started. The wrapper must duplicate its
    own stdin onto descriptor 3 and launch the debug shell with an explicit
    `<&3` redirection so terminal input reaches the interactive debug shell.
    Level 1 subprocess boundaries with a PATH-substituted debug shell that
    records one read line; bounded polling; no GNOME session or network.
    expected_output: piped input line recorded as debug-input event, then
    SIGINT terminates the session with exit 130 and no end markers.
    @param debug_session_env {tuple} Substitution environment, event log, path.
    @return {None} Assertions complete.
    @satisfies REQ-180, TST-074
    """
    env, events, nested = debug_session_env
    proc = _start_wrapper(
        {**env, "DEBUG_READ_STDIN": "1"}, nested, settle=1,
        stdin=subprocess.PIPE,
    )
    try:
        _wait_for_event(events, "debug-start")
        assert proc.stdin is not None
        proc.stdin.write(b"hello-debug\n")
        proc.stdin.flush()
        _wait_for_event(events, "debug-input:hello-debug")
        proc.send_signal(signal.SIGINT)
        returncode = proc.wait(timeout=EVENT_TIMEOUT_SECONDS)
    finally:
        _stop_wrapper(proc)
    observed = events.read_text(encoding="utf-8").splitlines()
    assert returncode == 130
    assert observed == [
        "nested-start",
        "debug-start",
        "debug-input:hello-debug",
    ]
