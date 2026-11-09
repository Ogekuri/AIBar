"""
@file
@brief Unit tests for program-name-composed GitHub upgrade source resolution.
@details Verifies that the GitHub release-report endpoint and the
`--upgrade --develop`/`--dev` lifecycle repository URL are composed from the
single `PROGRAM_NAME` constant (current program name, no duplicated repository
literals), and that the resolver pins the fetched `tag_name` verbatim with no
branch filtering. Network interaction is replaced by deterministic module-level
substitutes; assertions are behavior-focused per HDT principles.
@satisfies TST-078
@satisfies TST-079
@satisfies TST-082
@satisfies TST-088
@satisfies CTN-020
@satisfies REQ-177
@satisfies REQ-189
@satisfies REQ-190
@satisfies REQ-191
@satisfies REQ-196
@satisfies REQ-198
"""

import sys
from unittest.mock import patch

from aibar import PROGRAM_NAME
from aibar import cli


class TestGithubUpgradeProgramName:
    """
    @brief Validates program-name composition and tag-pinned upgrade argv.
    @details Level 0 assertions check constant composition from `PROGRAM_NAME`;
    Level 1 assertions check the resolver output against deterministic
    release-check substitutes.
    """

    def test_program_name_is_current_project_name(self) -> None:
        """
        @brief Verify the program-name constant equals the current project name.
        @details Asserts `PROGRAM_NAME` equals `aibar` so every composed GitHub
        URL resolves the current project instead of a duplicated literal.
        @return {None} Function return value.
        @satisfies TST-082
        @satisfies REQ-191
        """
        expected_output: str = "aibar"
        assert PROGRAM_NAME == expected_output

    def test_release_api_url_composes_program_name(self) -> None:
        """
        @brief Verify the GitHub release endpoint composes from PROGRAM_NAME.
        @details Asserts `_GITHUB_RELEASE_API_URL` equals the `<program-name>`
        releases/latest template, matching
        `https://api.github.com/repos/Ogekuri/<program-name>/releases/latest`.
        @return {None} Function return value.
        @satisfies TST-082
        @satisfies CTN-020
        @satisfies REQ-189
        """
        expected_output: str = (
            f"https://api.github.com/repos/Ogekuri/{PROGRAM_NAME}/releases/latest"
        )
        assert cli._GITHUB_RELEASE_API_URL == expected_output

    def test_upgrade_repo_url_composes_program_name(self) -> None:
        """
        @brief Verify the GitHub upgrade repository URL composes from PROGRAM_NAME.
        @details Asserts `_GITHUB_UPGRADE_REPO_URL` equals the
        `git+https://github.com/Ogekuri/<program-name>` template with no
        duplicated repository literal.
        @return {None} Function return value.
        @satisfies TST-082
        @satisfies REQ-191
        """
        expected_output: str = f"git+https://github.com/Ogekuri/{PROGRAM_NAME}"
        assert cli._GITHUB_UPGRADE_REPO_URL == expected_output

    def test_develop_upgrade_pins_fetched_tag_name(self) -> None:
        """
        @brief Verify the --develop resolver pins the fetched tag verbatim.
        @details Arranges a successful release-check substitute carrying
        `raw_tag` from an arbitrary branch, invokes
        `_resolve_github_upgrade_lifecycle_command`, and asserts the argv
        equals `uv tool install --force git+https://github.com/Ogekuri/aibar@<tag>`
        with the raw tag preserved (leading `v` intact, no branch filtering).
        @return {None} Function return value.
        @satisfies TST-078
        @satisfies TST-082
        @satisfies REQ-177
        @satisfies REQ-189
        """
        arrange_response = cli.StartupReleaseCheckResponse(
            latest_version="9.9.9",
            status_code=200,
            error_message=None,
            retry_after_seconds=0,
            raw_tag="v9.9.9",
        )
        expected_output: list[str] = [
            "uv",
            "tool",
            "install",
            "--force",
            f"git+https://github.com/Ogekuri/{PROGRAM_NAME}@v9.9.9",
        ]
        with patch.object(
            cli, "_fetch_github_latest_release", return_value=arrange_response
        ):
            assert cli._resolve_github_upgrade_lifecycle_command() == expected_output

    def test_develop_force_upgrade_pins_fetched_tag_name(self) -> None:
        """
        @brief Verify the --develop --force resolver pins the forced GitHub argv.
        @details Arranges `sys.argv` carrying `--upgrade --develop --force` and
        a successful release-check substitute with `raw_tag`, invokes
        `_resolve_upgrade_lifecycle_command`, and asserts the argv equals
        `uv tool install --force --reinstall --refresh
        git+https://github.com/Ogekuri/aibar@<tag>` with the raw tag preserved
        (leading `v` intact, no branch filtering).
        @return {None} Function return value.
        @satisfies TST-088
        @satisfies REQ-196
        @satisfies REQ-198
        """
        arrange_response = cli.StartupReleaseCheckResponse(
            latest_version="9.9.9",
            status_code=200,
            error_message=None,
            retry_after_seconds=0,
            raw_tag="v9.9.9",
        )
        arrange_argv: list[str] = ["aibar", "--upgrade", "--develop", "--force"]
        expected_output: list[str] = [
            "uv",
            "tool",
            "install",
            "--force",
            "--reinstall",
            "--refresh",
            f"git+https://github.com/Ogekuri/{PROGRAM_NAME}@v9.9.9",
        ]
        with patch.object(sys, "argv", arrange_argv), patch.object(
            cli, "_fetch_github_latest_release", return_value=arrange_response
        ):
            assert cli._resolve_upgrade_lifecycle_command() == expected_output

    def test_unresolved_tag_returns_none_without_argv(self) -> None:
        """
        @brief Verify the --develop resolver aborts without argv on failure.
        @details Arranges a failed release-check substitute without `raw_tag`,
        invokes `_resolve_github_upgrade_lifecycle_command`, and asserts the
        None return so the caller exits non-zero without executing any install
        command.
        @return {None} Function return value.
        @satisfies TST-079
        @satisfies REQ-190
        """
        arrange_response = cli.StartupReleaseCheckResponse(
            latest_version=None,
            status_code=403,
            error_message="forbidden",
            retry_after_seconds=0,
            raw_tag=None,
        )
        expected_output: None = None
        with patch.object(
            cli, "_fetch_github_latest_release", return_value=arrange_response
        ):
            assert cli._resolve_github_upgrade_lifecycle_command() == expected_output
