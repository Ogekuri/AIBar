"""
@file
@brief GNOME 50 windowed launcher behavior tests.
@details HDT Refactorer; Level 1 subprocess orchestration. Dependencies: Bash,
PATH executables and filesystem predicates replaced with temporary substitutes.
No desktop, network, installed extension or user configuration is modified.
@satisfies TST-076, REQ-031, REQ-033, REQ-178, REQ-185, REQ-186
"""

import os
from pathlib import Path
import subprocess

import pytest


## @brief Repository launcher under test; immutable source path.
SCRIPT = Path(__file__).resolve().parents[1] / "scripts/test-gnome-extension.sh"


@pytest.fixture
def launcher(tmp_path: Path) -> tuple[Path, dict[str, str], Path]:
    """
    @brief Create isolated launcher dependency substitutes.
    @details Copies the entrypoint; replaces install, bus and command boundaries.
    BASH_ENV substitutes only the Devkit executable predicate, preserving all
    other Bash predicates. Time O(N); space O(N) for copied source bytes.
    @param tmp_path {Path} Pytest-owned temporary directory.
    @return {tuple} Script path, synthetic environment and event log path.
    """
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    executable = scripts / SCRIPT.name
    executable.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    events = tmp_path / "events"
    env = {
        **os.environ,
        "PATH": f"{tmp_path}:/usr/bin:/bin",
        "WAYLAND_DISPLAY": "test-wayland",
        "DISPLAY": "",
        "EVENTS": str(events),
        "DEVKIT_AVAILABLE": "1",
        "CAPABILITY": "--devkit",
        "INSTALL_STATUS": "0",
        "LAUNCH_STATUS": "0",
    }
    shim = tmp_path / "bash-env"
    shim.write_text(
        '[() {\n'
        '  if builtin [ "$#" -eq 4 ] && '
        'builtin [ "$3" = /usr/libexec/mutter-devkit ]; then\n'
        '    builtin [ "$DEVKIT_AVAILABLE" != 1 ]; return\n'
        '  fi\n'
        '  builtin [ "$@"\n'
        '}\n',
        encoding="utf-8",
    )
    env["BASH_ENV"] = str(shim)
    commands = {
        scripts / "aibar.sh":
            'printf "install:%s\\n" "$*" >> "$EVENTS"\n'
            'exit "$INSTALL_STATUS"\n',
        tmp_path / "gnome-shell":
            'printf "%s\\n" "$CAPABILITY"\n',
        tmp_path / "dbus-run-session":
            'printf "bus:%s\\n" "$*" >> "$EVENTS"\n'
            'printf "mode:%s\\n" "$MUTTER_DEBUG_DUMMY_MODE_SPECS" '
            '>> "$EVENTS"\n'
            'exit "$LAUNCH_STATUS"\n',
    }
    for path, body in commands.items():
        path.write_text("#!/bin/bash\n" + body, encoding="utf-8")
        path.chmod(0o755)
    return executable, env, events


def test_launch_installs_before_windowed_shared_bus(launcher) -> None:
    """
    @brief Verify install ordering and GNOME 50 windowed launch contract.
    @details Level 1; observes subprocess boundary events, not source spelling.
    Time O(N); space O(N) for captured output; no host-session effects.
    @param launcher {tuple} Isolated script, environment and event log.
    @return {None} Assertions complete.
    @satisfies TST-076, REQ-031, REQ-178, REQ-185
    """
    script, env, events = launcher
    result = subprocess.run(
        ["/bin/bash", str(script)], env=env, capture_output=True,
        text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert events.read_text().splitlines() == [
        "install:gnome-install",
        "bus:-- scripts/aibar-nested-debug-session.sh "
        "gnome-shell --devkit --wayland",
        "mode:1280x720",
    ]


@pytest.mark.parametrize(
    ("overrides", "arguments", "diagnostic"),
    [
        ({"WAYLAND_DISPLAY": "", "DISPLAY": ""}, [], "graphical desktop"),
        ({"DEVKIT_AVAILABLE": "0"}, [], "mutter-dev-bin"),
        ({"CAPABILITY": "--headless --virtual-monitor"}, [], "--devkit"),
        ({}, ["unexpected"], "without arguments"),
    ],
)
def test_prerequisite_failure_precedes_install(
    launcher, overrides, arguments, diagnostic,
) -> None:
    """
    @brief Verify failed preconditions prevent installation and session launch.
    @details Level 1; parameterized failure boundaries; O(N) captured output.
    @param launcher {tuple} Isolated script, environment and event log.
    @param overrides {dict[str, str]} Synthetic environment overrides.
    @param arguments {list[str]} Invocation arguments.
    @param diagnostic {str} Required stderr fragment.
    @return {None} Assertions complete.
    @satisfies REQ-033, REQ-186, TST-076
    """
    script, env, events = launcher
    result = subprocess.run(
        ["/bin/bash", str(script), *arguments], env={**env, **overrides},
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode != 0
    assert diagnostic in result.stderr
    assert not events.exists()


@pytest.mark.parametrize("boundary", ["INSTALL_STATUS", "LAUNCH_STATUS"])
def test_subprocess_failure_is_propagated(launcher, boundary: str) -> None:
    """
    @brief Verify installer and debug-session exit statuses reach the caller.
    @details Level 1; deterministic status 7; O(N) event capture.
    @param launcher {tuple} Isolated script, environment and event log.
    @param boundary {str} Dependency configured to fail.
    @return {None} Assertions complete.
    @satisfies REQ-031, REQ-185, TST-076
    """
    script, env, events = launcher
    result = subprocess.run(
        ["/bin/bash", str(script)], env={**env, boundary: "7"},
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 7
    if boundary == "INSTALL_STATUS":
        assert events.read_text().splitlines() == ["install:gnome-install"]
