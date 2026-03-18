"""
@file
@brief Startup update-check and lifecycle-option regression tests.
@details Verifies startup preflight ordering, idle-time gating and persistence,
HTTP 429 retry-after handling, lifecycle uv command execution, and version
option behavior for `--version` and `--ver`.
@satisfies TST-031
@satisfies TST-032
@satisfies TST-033
@satisfies TST-034
@satisfies TST-035
@satisfies TST-041
@satisfies TST-036
"""

import json
from pathlib import Path
import subprocess
import time

import click
from click.testing import CliRunner
import pytest

from aibar import __version__
import aibar.cli as cli_module
from aibar.cli import main


_REAL_STARTUP_PREFLIGHT = cli_module._run_startup_update_preflight


def test_preflight_runs_before_invalid_argument_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    @brief Verify startup preflight executes before invalid option diagnostics.
    @details Replaces preflight with probe output and invokes CLI with invalid
    top-level option. Asserts probe message appears before Click error output.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies TST-031
    """
    marker_text = "PRECHECK-MARKER"

    def _probe_preflight() -> None:
        """
        @brief Emit deterministic marker text from preflight probe.
        @return {None} Function return value.
        """
        click.echo(marker_text)

    monkeypatch.setattr(cli_module, "_run_startup_update_preflight", _probe_preflight)
    runner = CliRunner()
    result = runner.invoke(main, ["--invalid-option"])

    assert result.exit_code != 0
    assert result.output.startswith(f"{marker_text}\n")
    assert "No such option" in result.output


def test_startup_idle_gating_skips_http_until_expired(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify startup idle-time gate suppresses HTTP checks until expiry.
    @details Persists future idle_until state, runs preflight and asserts zero
    fetch calls; then persists expired idle_until and asserts one fetch call.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary filesystem root for HOME isolation.
    @return {None} Function return value.
    @satisfies TST-032
    """
    fetch_calls: list[str] = []
    now_epoch = int(time.time())

    def _fake_fetch() -> cli_module.StartupReleaseCheckResponse:
        """
        @brief Record startup fetch invocation and return success payload.
        @return {StartupReleaseCheckResponse} Mock success response.
        """
        fetch_calls.append("called")
        return cli_module.StartupReleaseCheckResponse(
            latest_version=__version__,
            status_code=200,
            error_message=None,
            retry_after_seconds=0,
        )

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(cli_module, "_fetch_startup_latest_release", _fake_fetch)

    cli_module._save_startup_idle_state(
        last_success_epoch=now_epoch - 10,
        idle_until_epoch=now_epoch + 120,
    )
    _REAL_STARTUP_PREFLIGHT()
    assert fetch_calls == []

    cli_module._save_startup_idle_state(
        last_success_epoch=now_epoch - 10,
        idle_until_epoch=now_epoch - 1,
    )
    _REAL_STARTUP_PREFLIGHT()
    assert fetch_calls == ["called"]


def test_successful_startup_check_writes_idle_state_schema(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify successful startup check writes required idle-state fields.
    @details Executes preflight with mocked successful release metadata and
    validates cache-directory creation plus epoch and human-readable keys
    persisted to startup idle-state JSON.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary filesystem root for HOME isolation.
    @return {None} Function return value.
    @satisfies TST-033
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(
        cli_module,
        "_fetch_startup_latest_release",
        lambda: cli_module.StartupReleaseCheckResponse(
            latest_version=__version__,
            status_code=200,
            error_message=None,
            retry_after_seconds=0,
        ),
    )

    _REAL_STARTUP_PREFLIGHT()
    state_path = cli_module._startup_idle_state_path()
    assert state_path.exists()
    assert state_path.name == "check_version_idle-time.json"
    assert state_path.parent == tmp_path / ".cache" / "aibar"
    assert state_path.parent.exists()

    payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert isinstance(payload[cli_module._STARTUP_IDLE_STATE_LAST_SUCCESS_EPOCH_KEY], int)
    assert isinstance(payload[cli_module._STARTUP_IDLE_STATE_LAST_SUCCESS_HUMAN_KEY], str)
    assert isinstance(payload[cli_module._STARTUP_IDLE_STATE_IDLE_UNTIL_EPOCH_KEY], int)
    assert isinstance(payload[cli_module._STARTUP_IDLE_STATE_IDLE_UNTIL_HUMAN_KEY], str)
    delta = (
        payload[cli_module._STARTUP_IDLE_STATE_IDLE_UNTIL_EPOCH_KEY]
        - payload[cli_module._STARTUP_IDLE_STATE_LAST_SUCCESS_EPOCH_KEY]
    )
    assert delta == cli_module._STARTUP_IDLE_DELAY_SECONDS


def test_http_429_uses_max_retry_after_and_idle_delay_floor(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify startup HTTP 429 idle-time uses max retry-after semantics.
    @details Simulates repeated 429 responses and asserts persisted idle_until
    equals max(existing_idle_until, now + max(300, retry_after)).
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary filesystem root for HOME isolation.
    @return {None} Function return value.
    @satisfies TST-034
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    current_time = {"value": 10_000.0}
    monkeypatch.setattr(cli_module.time, "time", lambda: current_time["value"])
    monkeypatch.setattr(
        cli_module,
        "_emit_startup_preflight_message",
        lambda message, color_code, err=False: None,
    )

    responses = [
        cli_module.StartupReleaseCheckResponse(
            latest_version=None,
            status_code=429,
            error_message="HTTP 429",
            retry_after_seconds=120,
        ),
        cli_module.StartupReleaseCheckResponse(
            latest_version=None,
            status_code=429,
            error_message="HTTP 429",
            retry_after_seconds=900,
        ),
    ]

    def _fake_fetch() -> cli_module.StartupReleaseCheckResponse:
        """
        @brief Return queued startup 429 response payload.
        @return {StartupReleaseCheckResponse} Next queued response.
        """
        return responses.pop(0)

    monkeypatch.setattr(cli_module, "_fetch_startup_latest_release", _fake_fetch)

    cli_module._save_startup_idle_state(last_success_epoch=9_000, idle_until_epoch=0)
    _REAL_STARTUP_PREFLIGHT()
    first_payload = json.loads(cli_module._startup_idle_state_path().read_text(encoding="utf-8"))
    assert first_payload[cli_module._STARTUP_IDLE_STATE_IDLE_UNTIL_EPOCH_KEY] == 10_300
    assert first_payload[cli_module._STARTUP_IDLE_STATE_LAST_SUCCESS_EPOCH_KEY] == 9_000

    current_time["value"] = 10_600.0
    _REAL_STARTUP_PREFLIGHT()
    second_payload = json.loads(cli_module._startup_idle_state_path().read_text(encoding="utf-8"))
    assert second_payload[cli_module._STARTUP_IDLE_STATE_IDLE_UNTIL_EPOCH_KEY] == 11_500
    assert second_payload[cli_module._STARTUP_IDLE_STATE_LAST_SUCCESS_EPOCH_KEY] == 9_000


@pytest.mark.parametrize(
    ("flag", "expected_command"),
    [
        (
            "--upgrade",
            [
                "uv",
                "tool",
                "install",
                "aibar",
                "--force",
                "--from",
                "git+https://github.com/Ogekuri/AIBar.git",
            ],
        ),
        (
            "--uninstall",
            ["uv", "tool", "uninstall", "aibar"],
        ),
    ],
)
def test_lifecycle_flags_execute_uv_commands_and_propagate_exit_code(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    flag: str,
    expected_command: list[str],
) -> None:
    """
    @brief Verify lifecycle flags execute required uv commands.
    @details Mocks subprocess execution for `--upgrade` and `--uninstall`,
    asserting exact argv and propagated subprocess exit code; verifies Linux
    `--uninstall` removes startup idle-state cache artifacts.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary filesystem root for HOME isolation.
    @param flag {str} Lifecycle flag under test.
    @param expected_command {list[str]} Expected subprocess argv.
    @return {None} Function return value.
    @satisfies TST-035
    """
    observed_commands: list[list[str]] = []

    def _fake_run(command: list[str], check: bool) -> subprocess.CompletedProcess[str]:
        """
        @brief Capture lifecycle subprocess command invocation.
        @param command {list[str]} Subprocess argv.
        @param check {bool} Subprocess check argument.
        @return {subprocess.CompletedProcess[str]} Completed process stub.
        """
        assert check is False
        observed_commands.append(command)
        return subprocess.CompletedProcess(command, returncode=7)

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(cli_module.subprocess, "run", _fake_run)
    monkeypatch.setattr(cli_module, "_is_linux_runtime", lambda: True)
    startup_state_path = cli_module._startup_idle_state_path()
    startup_state_path.parent.mkdir(parents=True, exist_ok=True)
    startup_state_path.write_text("{}", encoding="utf-8")
    startup_cache_sentinel_path = startup_state_path.parent / "cache.json"
    startup_cache_sentinel_path.write_text("{}", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, [flag])

    assert result.exit_code == 7
    assert observed_commands == [expected_command]
    if flag == "--uninstall":
        assert not startup_state_path.exists()
        assert not startup_state_path.parent.exists()
    else:
        assert startup_state_path.exists()
        assert startup_cache_sentinel_path.exists()


@pytest.mark.parametrize(
    ("flag", "expected_command", "detected_os"),
    [
        (
            "--upgrade",
            [
                "uv",
                "tool",
                "install",
                "aibar",
                "--force",
                "--from",
                "git+https://github.com/Ogekuri/AIBar.git",
            ],
            "Darwin",
        ),
        (
            "--uninstall",
            ["uv", "tool", "uninstall", "aibar"],
            "Windows",
        ),
    ],
)
def test_lifecycle_flags_on_non_linux_emit_manual_guidance_without_subprocess(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    flag: str,
    expected_command: list[str],
    detected_os: str,
) -> None:
    """
    @brief Verify lifecycle flags on non-Linux emit manual guidance only.
    @details Forces non-Linux runtime branch, asserts command subprocess is not
    executed, validates guidance includes detected OS and required command, and
    verifies startup idle-state cache artifacts remain unchanged.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary filesystem root for HOME isolation.
    @param flag {str} Lifecycle flag under test.
    @param expected_command {list[str]} Expected manual command argv text.
    @param detected_os {str} Stubbed non-Linux operating-system label.
    @return {None} Function return value.
    @satisfies TST-041
    """
    observed_commands: list[list[str]] = []

    def _fake_run(command: list[str], check: bool) -> subprocess.CompletedProcess[str]:
        """
        @brief Capture unexpected subprocess invocation in non-Linux branch.
        @param command {list[str]} Subprocess argv.
        @param check {bool} Subprocess check argument.
        @return {subprocess.CompletedProcess[str]} Completed process stub.
        """
        observed_commands.append(command)
        return subprocess.CompletedProcess(command, returncode=0)

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(cli_module.subprocess, "run", _fake_run)
    monkeypatch.setattr(cli_module, "_is_linux_runtime", lambda: False)
    monkeypatch.setattr(cli_module.platform, "system", lambda: detected_os)
    startup_state_path = cli_module._startup_idle_state_path()
    startup_state_path.parent.mkdir(parents=True, exist_ok=True)
    startup_state_path.write_text("{}", encoding="utf-8")
    startup_cache_sentinel_path = startup_state_path.parent / "cache.json"
    startup_cache_sentinel_path.write_text("{}", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, [flag])

    assert result.exit_code == 1
    assert observed_commands == []
    assert f"{flag} is supported only on Linux." in result.output
    assert f"Detected OS: {detected_os}." in result.output
    assert f"Run manually: {' '.join(expected_command)}" in result.output
    assert startup_state_path.exists()
    assert startup_cache_sentinel_path.exists()


def test_version_and_ver_print_installed_version_without_dispatch() -> None:
    """
    @brief Verify `--version` and `--ver` print installed version and exit.
    @details Invokes both version flags and asserts output is the installed
    package version text with successful exit status.
    @return {None} Function return value.
    @satisfies TST-036
    """
    runner = CliRunner()
    version_result = runner.invoke(main, ["--version"])
    short_version_result = runner.invoke(main, ["--ver"])
    bypass_result = runner.invoke(main, ["--version", "show"])

    assert version_result.exit_code == 0
    assert version_result.output.strip() == __version__
    assert short_version_result.exit_code == 0
    assert short_version_result.output.strip() == __version__
    assert bypass_result.exit_code == 0
    assert bypass_result.output.strip() == __version__
