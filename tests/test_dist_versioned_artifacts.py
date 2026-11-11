"""
@file
@brief Versioned release-artifact `.gitignore` contract tests.
@details Verifies that `.gitignore` re-includes the `dist/` directory and its
files inside the `Include specific files and directories` section and that git
reports the release artifacts as not ignored. Tests are read-only and
deterministic; they never modify the repository, the working tree, or the
user home directory.
@satisfies PRJ-038
@satisfies PRJ-041
@satisfies TST-097
"""

import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"
INCLUDE_HEADER = "Include specific files and directories"
EXCLUDE_HEADER = "Exlucde specific files and directories"
DIST_ARTIFACT_PATHS = (
    "dist/aibar-0.4.0.tar.gz",
    "dist/aibar-0.4.0-py3-none-any.whl",
    "dist/aibar@aibar.panel.shell-extension.zip",
)


def _include_section_rules() -> list[str]:
    """
    @brief Extract the stripped rule lines of the include section.
    @details Selects lines located between the include-section header and the
    exclude-section header, dropping blank lines and comment lines.
    @return {list[str]} Stripped include-section rule lines in file order.
    @satisfies TST-097
    """
    source = GITIGNORE_PATH.read_text(encoding="utf-8")
    section = source.split(INCLUDE_HEADER, 1)[1].split(EXCLUDE_HEADER, 1)[0]
    return [
        line.strip()
        for line in section.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def test_include_section_reincludes_dist_directory_and_files() -> None:
    """
    @brief Verify the include section re-includes `dist/` and `dist/**/*`.
    @details Arrange: load the include-section rules. Act: membership check for
    the two canonical re-include rules. Assert: both rules are present.
    @return {None} Function return value.
    @satisfies PRJ-038
    @satisfies PRJ-041
    @satisfies TST-097
    """
    rules = _include_section_rules()
    assert "!dist/" in rules
    assert "!dist/**/*" in rules


def test_git_reports_dist_release_artifacts_as_not_ignored() -> None:
    """
    @brief Verify git does not ignore the canonical `dist/` release artifacts.
    @details Arrange: the artifact paths need not exist on disk because
    `git check-ignore --no-index` evaluates rules only. Act: run read-only
    `git check-ignore` per path. Assert: exit status `1` (not ignored) for each.
    @return {None} Function return value.
    @satisfies PRJ-041
    @satisfies TST-097
    """
    for artifact_path in DIST_ARTIFACT_PATHS:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--quiet", "--", artifact_path],
            cwd=PROJECT_ROOT,
            check=False,
        )
        assert result.returncode == 1, artifact_path
