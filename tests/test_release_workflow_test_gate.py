"""
@file
@brief GitHub release workflow test-gate regression tests.
@details Verifies that `.github/workflows/release-pypi.yml` runs a dedicated
`unit-tests` job (locked dependency sync + pytest suite) and gates the
`build-release` job on it, so release artifacts and the transitive PyPI
publication are never created for versions whose tests fail.
Tests are source-level and deterministic; they never execute the workflow.
@satisfies PRJ-026
@satisfies PRJ-027
@satisfies TST-086
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "release-pypi.yml"


def _workflow_source() -> str:
    """
    @brief Read the release workflow YAML source text.
    @return {str} UTF-8 decoded source of `.github/workflows/release-pypi.yml`.
    """
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def test_workflow_declares_unit_tests_job_running_locked_sync_and_pytest() -> None:
    """
    @brief Verify the workflow declares a unit-tests job running the suite.
    @details The `unit-tests` job must synchronize dependencies locked to
    `uv.lock` and execute `uv run pytest tests/` per PRJ-026.
    @return {None} Function return value.
    @satisfies PRJ-026
    @satisfies TST-086
    """
    source = _workflow_source()
    assert "  unit-tests:" in source
    assert "uv sync --locked" in source
    assert "uv run pytest tests/" in source


def test_build_release_is_gated_on_unit_tests() -> None:
    """
    @brief Verify build-release depends on both the branch gate and the tests.
    @details The `build-release` job must declare
    `needs: [check-branch, unit-tests]` so release artifact creation stops
    when the pytest suite fails per PRJ-027.
    @return {None} Function return value.
    @satisfies PRJ-027
    @satisfies TST-086
    """
    source = _workflow_source()
    assert "needs: [check-branch, unit-tests]" in source


def test_publish_pypi_remains_gated_on_gated_build_release() -> None:
    """
    @brief Verify PyPI publication stays transitively gated by the tests.
    @details The `publish-pypi` job must keep `needs: build-release`, so a
    test failure suppresses artifact creation and, transitively, PyPI
    publication per PRJ-027 and PRJ-013.
    @return {None} Function return value.
    @satisfies PRJ-027
    @satisfies TST-086
    """
    source = _workflow_source()
    publish_section = source.split("publish-pypi:", 1)[1]
    assert "needs: build-release" in publish_section
