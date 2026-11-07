"""
@file
@brief Unit tests for `--version` GitHub report parity with `--upgrade --develop`.
@details Verifies that the `--version` GitHub line performs exactly one fresh
`releases/latest` fetch per invocation (never idle-gated) against the
program-name-composed endpoint, and that the reported version is identical to
the release pinned by the `--upgrade --develop`/`--dev` lifecycle argv: both
derive from the same `StartupReleaseCheckResponse`, with the report rendering
the raw tag minus its leading `v` prefix. Network interaction is replaced by
deterministic module-level substitutes; assertions are behavior-focused per
HDT principles.
@satisfies TST-083
@satisfies REQ-192
@satisfies REQ-193
"""

from unittest.mock import patch

from aibar import PROGRAM_NAME
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
        stderr report contains the labeled GitHub line carrying the version
        identical to the pinned upgrade tag.
        @param capsys pytest stdio capture fixture.
        @return {None} Function return value.
        @satisfies TST-083
        @satisfies REQ-192
        @satisfies REQ-193
        """
        arrange_github = _github_response()
        arrange_pypi = _pypi_response()
        expected_github_line: str = "Latest GitHub release: 1.2.3"
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
        assert expected_github_line in captured.err
        assert "Latest PyPI release: 1.0.0" in captured.err
