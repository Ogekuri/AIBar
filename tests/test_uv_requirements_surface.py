"""
@file
@brief Repository uv/requirements surface regression tests.
@details Verifies uv lockfile tracking, requirements.txt removal, and README
documentation of uv requirement plus optional requirements export command.
@satisfies REQ-087
@satisfies TST-040
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"
README_PATH = PROJECT_ROOT / "README.md"
REQUIREMENTS_PATH = PROJECT_ROOT / "requirements.txt"


def test_gitignore_allowlist_tracks_uv_lock_and_not_requirements_txt() -> None:
    """
    @brief Verify root allowlist includes `uv.lock` and excludes `requirements.txt`.
    @return {None} Function return value.
    @satisfies REQ-087
    @satisfies TST-040
    """
    source = GITIGNORE_PATH.read_text(encoding="utf-8")
    assert "!uv.lock" in source
    assert "!requirements.txt" not in source


def test_repository_does_not_include_requirements_txt() -> None:
    """
    @brief Verify repository root no longer contains tracked `requirements.txt`.
    @return {None} Function return value.
    @satisfies REQ-087
    @satisfies TST-040
    """
    assert not REQUIREMENTS_PATH.exists()


def test_readme_includes_uv_requirement_and_optional_requirements_export() -> None:
    """
    @brief Verify README documents uv prerequisite and optional export command.
    @return {None} Function return value.
    @satisfies PRJ-007
    @satisfies REQ-087
    @satisfies TST-040
    """
    source = README_PATH.read_text(encoding="utf-8")
    assert "## Requirements (uv)" in source
    assert "Astral uv" in source
    assert "uv export --format requirements-txt > requirements.txt" in source
