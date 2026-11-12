"""
@file
@brief Pre-built release artifact workflow regression tests.
@details Verifies that `.github/workflows/release-pypi.yml` publishes the
release artifacts already committed under `dist/` by `scripts/build.sh`:
the release job checks out the tagged commit, verifies the required artifacts,
uploads them as GitHub Release assets, and runs no build, no Python/`uv`
toolchain setup, no pytest suite, and no local release script. Tests are
source-level and deterministic; they never execute the workflow.
@satisfies PRJ-012
@satisfies PRJ-050
@satisfies PRJ-051
@satisfies PRJ-052
@satisfies TST-103
@satisfies TST-104
@satisfies TST-105
@satisfies TST-106
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "release-pypi.yml"

RELEASE_JOB_HEADER = "  release-assets:"
PUBLISH_JOB_HEADER = "  publish-pypi:"


def _workflow_source() -> str:
    """
    @brief Read the release workflow YAML source text.
    @return {str} UTF-8 decoded source of `.github/workflows/release-pypi.yml`.
    @satisfies TST-103
    """
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _job_section(job_header: str) -> str:
    """
    @brief Extract one job block from the workflow source.
    @details Splits the workflow at the job header line and returns the block
    up to the next top-level job declaration or end of file.
    @param job_header {str} Indented job header line to locate.
    @return {str} Job block text.
    @satisfies TST-103
    """
    source = _workflow_source()
    section = source.split(job_header, 1)[1]
    return section.split("\n  # ", 1)[0]


def test_release_job_publishes_tagged_commit_dist_artifacts() -> None:
    """
    @brief Verify the release job publishes the tagged-commit `dist/` artifacts.
    @details Arrange: load the workflow source. Act: inspect the
    `release-assets` job. Assert: the job checks out the tagged commit with no
    build step, attests `dist/*`, and uploads `dist/**/*` as GitHub Release
    assets with `fail_on_unmatched_files` enabled.
    @return {None} Function return value.
    @satisfies PRJ-012
    @satisfies PRJ-050
    @satisfies TST-103
    """
    source = _workflow_source()
    job = _job_section(RELEASE_JOB_HEADER)
    assert "needs: check-branch" in job
    assert "if: needs.check-branch.outputs.is_release_branch == 'true'" in job
    assert "actions/checkout@v7" in job
    assert "subject-path: dist/*" in job
    assert "files: dist/**/*" in job
    assert "fail_on_unmatched_files: true" in job
    assert "dist/*.tar.gz" in job
    assert "dist/*.whl" in job
    assert "dist/aibar@aibar.panel.shell-extension.zip" in job
    assert "dist/" in source


def test_release_job_fails_when_a_dist_artifact_is_missing() -> None:
    """
    @brief Verify the pre-built artifact presence gate fails the release.
    @details Arrange: load the workflow source. Act: inspect the artifact
    verification step. Assert: it probes the sdist, wheel, and GNOME extension
    zip globs with `compgen -G`, reports each missing artifact on stderr, and
    exits with status 1 so no release is published without its artifacts.
    @return {None} Function return value.
    @satisfies PRJ-051
    @satisfies TST-104
    """
    job = _job_section(RELEASE_JOB_HEADER)
    assert "name: Verify pre-built dist artifacts" in job
    assert "set -euo pipefail" in job
    assert "compgen -G \"$pattern\"" in job
    assert "for pattern in 'dist/*.tar.gz' 'dist/*.whl' 'dist/aibar@aibar.panel.shell-extension.zip'" in job
    assert "missing pre-built release artifact" in job
    assert "exit 1" in job


def test_workflow_runs_no_build_or_local_release_script() -> None:
    """
    @brief Verify the workflow never builds or delegates to local scripts.
    @details Arrange: load the workflow source. Act: search for build and local
    pipeline invocations. Assert: neither `scripts/build.sh` nor
    `scripts/pre-release-check.sh` is executed, and no `python -m build`,
    `uv sync`, `uv run pytest`, or extension `zip` packaging step exists.
    @return {None} Function return value.
    @satisfies PRJ-052
    @satisfies TST-105
    """
    source = _workflow_source()
    assert "scripts/build.sh" not in source
    assert "scripts/pre-release-check.sh" not in source
    assert "python -m build" not in source
    assert "uv sync" not in source
    assert "uv run pytest" not in source
    assert "zip -r" not in source
    assert "pytest tests/" not in source


def test_workflow_declares_no_toolchain_setup_or_unit_test_job() -> None:
    """
    @brief Verify the workflow installs no Python/uv toolchain and runs no tests.
    @details Arrange: load the workflow source. Act: search for toolchain setup
    actions and the removed unit-test job. Assert: `actions/setup-python`,
    `astral-sh/setup-uv`, `unit-tests:`, and `needs: [check-branch, unit-tests]`
    are all absent because pre-built artifacts need no build toolchain.
    @return {None} Function return value.
    @satisfies PRJ-052
    @satisfies TST-106
    """
    source = _workflow_source()
    assert "actions/setup-python" not in source
    assert "astral-sh/setup-uv" not in source
    assert "  unit-tests:" not in source
    assert "needs: [check-branch, unit-tests]" not in source
    assert "uv.lock" not in source


def test_publish_job_consumes_prebuilt_distribution_artifacts() -> None:
    """
    @brief Verify PyPI publication reuses the uploaded pre-built distributions.
    @details Arrange: load the workflow source. Act: inspect the `publish-pypi`
    job. Assert: it downloads the `python-distributions` artifact into `dist/`
    and publishes it with `pypa/gh-action-pypi-publish@release/v1`.
    @return {None} Function return value.
    @satisfies PRJ-013
    @satisfies TST-103
    """
    job = _job_section(PUBLISH_JOB_HEADER)
    assert "actions/download-artifact@v8" in job
    assert "name: python-distributions" in job
    assert "path: dist/" in job
    assert "pypa/gh-action-pypi-publish@release/v1" in job
