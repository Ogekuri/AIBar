"""
@file
@brief Startup update-check and lifecycle-option regression tests.
@details Verifies startup preflight ordering, idle-time gating and persistence,
HTTP 429 retry-after handling, lifecycle uv command execution, and version
option behavior for `--version`.
@satisfies TST-031
@satisfies TST-032
@satisfies TST-033
@satisfies TST-034
@satisfies TST-035
@satisfies TST-041
@satisfies TST-036
@satisfies TST-070
"""

import json
from pathlib import Path
import subprocess
import time
import urllib.request

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


def test_version_prints_installed_version_without_dispatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    @brief Verify `--version` prints installed version, release report, and exits.
    @details Replaces both release fetch boundaries with deterministic responses,
    invokes `--version` standalone and before a subcommand, and asserts the first
    output line equals the installed version, labeled PyPI/GitHub release lines
    follow, exit status is zero, and subcommand dispatch is bypassed.
    expected_output: `<version>\nLatest PyPI release: 9.9.9\nLatest GitHub
    release: 9.9.9` with exit status 0 for both invocations.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies TST-036
    @satisfies REQ-078
    """
    def _fake_fetch() -> cli_module.StartupReleaseCheckResponse:
        """
        @brief Return deterministic successful release-check response.
        @return {StartupReleaseCheckResponse} Mock success response.
        """
        return cli_module.StartupReleaseCheckResponse(
            latest_version="9.9.9",
            status_code=200,
            error_message=None,
            retry_after_seconds=0,
        )

    monkeypatch.setattr(cli_module, "_fetch_startup_latest_release", _fake_fetch)
    monkeypatch.setattr(cli_module, "_fetch_github_latest_release", _fake_fetch)
    monkeypatch.setattr(cli_module, "_LAST_PYPI_RELEASE_CHECK", None)

    runner = CliRunner()
    version_result = runner.invoke(main, ["--version"])
    bypass_result = runner.invoke(main, ["--version", "show"])

    for result in (version_result, bypass_result):
        assert result.exit_code == 0
        assert result.output.splitlines()[0] == __version__
        assert "Latest PyPI release: 9.9.9" in result.output
        assert "Latest GitHub release: 9.9.9" in result.output


def test_version_flags_force_startup_online_check_bypassing_idle_gate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """
    @brief Verify the version flag forces online startup check bypassing idle gate.
    @details Persists startup idle-state with future `idle_until`, invokes
    `--version`, and asserts startup release fetch executes once despite the
    active idle gate.
    expected_output: exit status 0 with exactly one recorded startup fetch.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary filesystem root for HOME isolation.
    @return {None} Function return value.
    @satisfies TST-032
    @satisfies TST-036
    """
    fetch_calls: list[str] = []
    monkeypatch.setenv("HOME", str(tmp_path))
    now_epoch = int(time.time())

    def _fake_fetch() -> cli_module.StartupReleaseCheckResponse:
        """
        @brief Record startup fetch invocation and return deterministic success payload.
        @return {StartupReleaseCheckResponse} Mock success response.
        """
        fetch_calls.append("called")
        return cli_module.StartupReleaseCheckResponse(
            latest_version=__version__,
            status_code=200,
            error_message=None,
            retry_after_seconds=0,
        )

    monkeypatch.setattr(cli_module, "_fetch_startup_latest_release", _fake_fetch)
    monkeypatch.setattr(cli_module, "_LAST_PYPI_RELEASE_CHECK", None)

    def _fake_github_fetch() -> cli_module.StartupReleaseCheckResponse:
        """
        @brief Return deterministic GitHub release-check response.
        @return {StartupReleaseCheckResponse} Mock success response.
        """
        return cli_module.StartupReleaseCheckResponse(
            latest_version=__version__,
            status_code=200,
            error_message=None,
            retry_after_seconds=0,
        )

    monkeypatch.setattr(
        cli_module,
        "_fetch_github_latest_release",
        _fake_github_fetch,
    )
    monkeypatch.setattr(
        cli_module,
        "_run_startup_update_preflight",
        _REAL_STARTUP_PREFLIGHT,
    )

    cli_module._save_startup_idle_state(
        last_success_epoch=now_epoch,
        idle_until_epoch=now_epoch + 3600,
    )
    runner = CliRunner()
    version_result = runner.invoke(main, ["--version"])

    assert version_result.exit_code == 0
    assert fetch_calls == ["called"]


def test_startup_fetch_queries_pypi_json_and_parses_info_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    @brief Verify startup fetch targets the PyPI JSON API and parses info.version.
    @details Mocks `urllib.request.urlopen` to capture the outbound request and
    return a PyPI-shaped JSON payload; asserts the request URL equals the
    canonical PyPI JSON endpoint and the normalized latest version equals the
    `info.version` field, with no git-hosted fallback request issued.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies TST-070
    @satisfies CTN-011
    """
    observed_urls: list[str] = []

    class _FakeResponse:
        """
        @brief Minimal urlopen response stub for PyPI JSON payload.
        """

        def __enter__(self) -> "_FakeResponse":
            """
            @brief Enter the response context manager.
            @return {_FakeResponse} Self reference.
            """
            return self

        def __exit__(self, *args: object) -> None:
            """
            @brief Exit the response context manager.
            @param args {object} Context exception details (unused).
            """

        def read(self) -> bytes:
            """
            @brief Return the serialized PyPI JSON document.
            @return {bytes} UTF-8 encoded JSON payload.
            """
            return json.dumps({"info": {"version": "9.9.9"}}).encode("utf-8")

    def _fake_urlopen(
        request: urllib.request.Request, timeout: float
    ) -> _FakeResponse:
        """
        @brief Capture the outbound startup-check request.
        @param request {urllib.request.Request} urllib request carrying the target URL.
        @param timeout {float} Configured HTTP timeout (unused).
        @return {_FakeResponse} Response stub.
        """
        observed_urls.append(request.full_url)
        return _FakeResponse()

    monkeypatch.setattr(cli_module.urllib_request, "urlopen", _fake_urlopen)

    response = cli_module._fetch_startup_latest_release()

    assert observed_urls == ["https://pypi.org/pypi/aibar/json"]
    assert response.latest_version == "9.9.9"
    assert response.status_code == 200
    assert response.error_message is None
