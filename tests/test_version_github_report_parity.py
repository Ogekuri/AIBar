"""
@file
@brief Unit tests for `--version` GitHub report parity with `--upgrade --develop`.
@details Verifies that the `--version` GitHub line performs exactly one fresh
`releases/latest` fetch per invocation (never idle-gated) against the
program-name-composed endpoint, and that the reported version is identical to
the release pinned by the `--upgrade --develop`/`--dev` lifecycle argv: both
derive from the same `StartupReleaseCheckResponse`, with the report rendering
the raw tag minus its leading `v` prefix. Also verifies the aligned three-line
report surface: exactly three stdout lines with left-justified labels padded to
one shared 18-character field so all colons align, and the GitHub failure value
`unknown (<reason>)` on releases/latest failure. Network interaction is
replaced by deterministic module-level substitutes; assertions are
behavior-focused per HDT principles.
@satisfies TST-083
@satisfies TST-089
@satisfies REQ-192
@satisfies REQ-193
@satisfies REQ-195
@satisfies REQ-199
"""

from unittest.mock import patch

from aibar import PROGRAM_NAME, __version__
from aibar import cli


def _github_response() -> cli.StartupReleaseCheckResponse:
    """
    @brief Build one deterministic successful GitHub release-check response.
    @details Encodes a published release whose raw tag `v1.2.3` carries the
    leading `v` prefix so the report/argv parity invariant is exercised.
    @return {StartupReleaseCheckResponse} Fixed response used as test fixture.
    """
    return cli.StartupReleaseCheckResponse(
        latest_version="1.2.3",
        status_code=200,
        error_message=None,
        retry_after_seconds=0,
        raw_tag="v1.2.3",
    )


def _github_failure_response() -> cli.StartupReleaseCheckResponse:
    """
    @brief Build one deterministic failed GitHub release-check response.
    @details Encodes an HTTP 404 releases/latest failure carrying the normalized
    fetch failure message so the GitHub report failure-value rendering is
    exercised.
    @return {StartupReleaseCheckResponse} Fixed failure response used as fixture.
    """
    return cli.StartupReleaseCheckResponse(
        latest_version=None,
        status_code=404,
        error_message="GitHub release check failed: HTTP 404 Not Found.",
        retry_after_seconds=0,
        raw_tag=None,
    )


def _pypi_response() -> cli.StartupReleaseCheckResponse:
    """
    @brief Build one deterministic successful PyPI release-check response.
    @details Encodes a PyPI check without `raw_tag` so the fixture can never be
    confused with the GitHub branch of the report pipeline.
    @return {StartupReleaseCheckResponse} Fixed response used as test fixture.
    """
    return cli.StartupReleaseCheckResponse(
        latest_version="1.0.0",
        status_code=200,
        error_message=None,
        retry_after_seconds=0,
        raw_tag=None,
    )


class TestVersionGithubReportParity:
    """
    @brief Validates `--version`/`--upgrade --develop` GitHub release parity.
    @details Level 0 assertions prove the report value and the upgrade-pinned
    tag describe one identical release; Level 1 assertions prove the GitHub
    fetch executes fresh exactly once per report invocation.
    """

    def test_report_value_equals_pinned_upgrade_tag_without_v_prefix(
        self,
    ) -> None:
        """
        @brief Verify report value and upgrade pin describe one identical release.
        @details Arranges a single release-check response, renders the report
        value, resolves the `--develop` upgrade argv from the same response,
        and asserts the argv pins the raw tag whose normalized form equals the
        reported version, so `--version` reports exactly the release
        `--upgrade --develop` downloads.
        @return {None} Function return value.
        @satisfies TST-083
        @satisfies REQ-193
        """
        arrange_response = _github_response()
        arrange_argv = [
            "uv",
            "tool",
            "install",
            "--force",
            f"git+https://github.com/Ogekuri/{PROGRAM_NAME}@{arrange_response.raw_tag}",
        ]
        expected_output: str = "1.2.3"
        report_value = cli._format_release_report_value(arrange_response)
        assert report_value == expected_output
        assert cli._normalize_github_release_tag(arrange_response.raw_tag) == report_value
        with patch.object(
            cli, "_fetch_github_latest_release", return_value=arrange_response
        ):
            assert cli._resolve_github_upgrade_lifecycle_command() == arrange_argv

    def test_version_report_performs_one_fresh_github_fetch_per_invocation(
        self, capsys
    ) -> None:
        """
        @brief Verify one fresh GitHub releases/latest fetch per report invocation.
        @details Arranges deterministic PyPI and GitHub fetch substitutes,
        invokes `_emit_version_option_release_report`, and asserts the GitHub
        fetch executed exactly once (never served from idle state), and the
        stdout report contains the labeled GitHub line carrying the version
        identical to the pinned upgrade tag.
        @param capsys pytest stdio capture fixture.
        @return {None} Function return value.
        @satisfies TST-083
        @satisfies REQ-192
        @satisfies REQ-193
        """
        arrange_github = _github_response()
        arrange_pypi = _pypi_response()
        expected_github_line: str = "Latest @ GitHub   : 1.2.3"
        with patch.object(cli, "_LAST_PYPI_RELEASE_CHECK", None):
            with patch.object(
                cli, "_fetch_startup_latest_release", return_value=arrange_pypi
            ):
                with patch.object(
                    cli, "_fetch_github_latest_release", return_value=arrange_github
                ) as github_fetch:
                    cli._emit_version_option_release_report()
        assert github_fetch.call_count == 1
        captured = capsys.readouterr()
        assert expected_github_line in captured.out
        assert "Latest @ PyPI     : 1.0.0" in captured.out

    def test_version_report_lines_align_labels_and_colons(self, capsys) -> None:
        """
        @brief Verify the version report emits exactly three aligned stdout lines.
        @details Arranges deterministic PyPI and GitHub fetch substitutes, invokes
        `_emit_version_option_release_report`, and asserts the stdout output is
        exactly the three aligned lines `Current Installed`, `Latest @ PyPI`,
        and `Latest @ GitHub` with the colon separator at the same shared
        label-field column and nothing emitted on stderr.
        expected_output: `[Current Installed : <__version__>, 'Latest @ PyPI     : 1.0.0',
        'Latest @ GitHub   : 1.2.3']` with colon column 18 on every line and
        empty stderr.
        @param capsys pytest stdio capture fixture.
        @return {None} Function return value.
        @satisfies TST-089
        @satisfies REQ-199
        """
        arrange_github = _github_response()
        arrange_pypi = _pypi_response()
        expected_lines = [
            f"Current Installed : {__version__}",
            "Latest @ PyPI     : 1.0.0",
            "Latest @ GitHub   : 1.2.3",
        ]
        with patch.object(cli, "_LAST_PYPI_RELEASE_CHECK", None):
            with patch.object(
                cli, "_fetch_startup_latest_release", return_value=arrange_pypi
            ):
                with patch.object(
                    cli, "_fetch_github_latest_release", return_value=arrange_github
                ):
                    cli._emit_version_option_release_report()
        captured = capsys.readouterr()
        observed_lines = captured.out.splitlines()
        assert observed_lines == expected_lines
        assert {line.index(":") for line in observed_lines} == {18}
        assert captured.err == ""

    def test_version_report_github_failure_renders_unknown_value(self, capsys) -> None:
        """
        @brief Verify the GitHub report line renders the failure value on 404.
        @details Arranges a failed releases/latest response and a successful PyPI
        response, invokes `_emit_version_option_release_report`, and asserts the
        aligned GitHub line carries the failure value `unknown (<reason>)` while
        the PyPI line keeps its success value, preserving the three-line output.
        expected_output: third stdout line equals
        `Latest @ GitHub   : unknown (GitHub release check failed: HTTP 404 Not Found.)`.
        @param capsys pytest stdio capture fixture.
        @return {None} Function return value.
        @satisfies TST-089
        @satisfies REQ-195
        """
        arrange_github = _github_failure_response()
        arrange_pypi = _pypi_response()
        expected_github_line: str = (
            "Latest @ GitHub   : unknown"
            " (GitHub release check failed: HTTP 404 Not Found.)"
        )
        with patch.object(cli, "_LAST_PYPI_RELEASE_CHECK", None):
            with patch.object(
                cli, "_fetch_startup_latest_release", return_value=arrange_pypi
            ):
                with patch.object(
                    cli, "_fetch_github_latest_release", return_value=arrange_github
                ):
                    cli._emit_version_option_release_report()
        captured = capsys.readouterr()
        observed_lines = captured.out.splitlines()
        assert len(observed_lines) == 3
        assert expected_github_line in observed_lines
        assert "Latest @ PyPI     : 1.0.0" in observed_lines
