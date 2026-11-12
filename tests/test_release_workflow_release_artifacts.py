"""
@file
@brief Release artifact resolution regression tests for the release workflow.
@details Verifies that `.github/workflows/release-pypi.yml` treats the
commit-tracked `dist/` artifacts as optional: the release job probes the
required artifact patterns, reuses them when all three exist, generates them
with `scripts/build.sh` through a conditional `uv` toolchain otherwise, uploads
them as GitHub Release assets, and fails only when a required artifact is
missing after artifact resolution. Tests are source-level and deterministic;
they never execute the workflow.
@satisfies PRJ-012
@satisfies PRJ-050
@satisfies PRJ-051
@satisfies PRJ-052
@satisfies PRJ-053
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
RESOLVE_STEP_HEADER = "      - name: Resolve release artifacts"
GENERATE_STEP_HEADER = "      - name: Generate release artifacts"
VERIFY_STEP_HEADER = "      - name: Verify resolved release artifacts"
TOOLCHAIN_STEP_HEADER = "      - name: Install uv toolchain"
REQUIRED_ARTIFACT_PATTERNS = (
    "'dist/*.tar.gz' 'dist/*.whl' 'dist/aibar@aibar.panel.shell-extension.zip'"
)


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
    up to the next top-level job comment or end of file.
    @param job_header {str} Indented job header line to locate.
    @return {str} Job block text.
    @satisfies TST-103
    """
    source = _workflow_source()
    section = source.split(job_header, 1)[1]
    return section.split("\n  # ", 1)[0]


def _step_section(step_header: str) -> str:
    """
    @brief Extract one workflow step block from the release job.
    @details Returns the text from the step header up to the next step header.
    @param step_header {str} Indented step header line to locate.
    @return {str} Step block text.
    @satisfies TST-103
    """
    job = _job_section(RELEASE_JOB_HEADER)
    section = job.split(step_header, 1)[1]
    return section.split("\n      - name: ", 1)[0]


def test_release_job_resolves_and_publishes_dist_artifacts() -> None:
    """
    @brief Verify the release job resolves `dist/` artifacts before publishing.
    @details Arrange: load the workflow source. Act: inspect the
    `release-assets` job. Assert: the job checks out the tagged commit, records
    artifact presence, attests `dist/*`, and uploads `dist/**/*` as GitHub
    Release assets with `fail_on_unmatched_files` enabled.
    @return {None} Function return value.
    @satisfies PRJ-012
    @satisfies TST-103
    """
    job = _job_section(RELEASE_JOB_HEADER)
    assert "needs: check-branch" in job
    assert "if: needs.check-branch.outputs.is_release_branch == 'true'" in job
    assert "actions/checkout@v7" in job
    assert RESOLVE_STEP_HEADER in job
    assert "subject-path: dist/*" in job
    assert "files: dist/**/*" in job
    assert "fail_on_unmatched_files: true" in job
    assert REQUIRED_ARTIFACT_PATTERNS in job


def test_release_job_generates_artifacts_when_tagged_commit_has_none() -> None:
    """
    @brief Verify missing committed artifacts trigger the fallback build.
    @details Arrange: load the workflow source. Act: inspect the artifact
    resolution step and the conditional generation steps. Assert: resolution
    records `present=false` instead of failing, the `uv` toolchain step and the
    `bash scripts/build.sh` step are both gated on the missing-artifact
    condition, and the workflow never requires tracked `dist/` files.
    @return {None} Function return value.
    @satisfies PRJ-050
    @satisfies PRJ-053
    @satisfies TST-103
    """
    resolve_step = _step_section(RESOLVE_STEP_HEADER)
    assert "compgen -G \"$pattern\"" in resolve_step
    assert "present=false" in resolve_step
    assert 'echo "present=$present" >> "$GITHUB_OUTPUT"' in resolve_step
    assert "exit 1" not in resolve_step

    job = _job_section(RELEASE_JOB_HEADER)
    missing_condition = "if: steps.artifacts.outputs.present != 'true'"
    assert job.count(missing_condition) == 2

    toolchain_step = _step_section(TOOLCHAIN_STEP_HEADER)
    assert missing_condition in toolchain_step
    assert "uses: astral-sh/setup-uv@v7" in toolchain_step

    generate_step = _step_section(GENERATE_STEP_HEADER)
    assert missing_condition in generate_step
    assert "bash scripts/build.sh" in generate_step


def test_release_job_fails_only_after_artifact_resolution() -> None:
    """
    @brief Verify the artifact presence gate runs after resolution.
    @details Arrange: load the workflow source. Act: inspect the verification
    step and its position. Assert: it probes the sdist, wheel, and GNOME
    extension zip globs with `compgen -G`, reports each missing artifact on
    stderr, exits with status 1, and runs after the generation step.
    @return {None} Function return value.
    @satisfies PRJ-051
    @satisfies TST-104
    """
    verify_step = _step_section(VERIFY_STEP_HEADER)
    assert "set -euo pipefail" in verify_step
    assert "compgen -G \"$pattern\"" in verify_step
    assert REQUIRED_ARTIFACT_PATTERNS in verify_step
    assert "missing release artifact after artifact resolution" in verify_step
    assert "exit 1" in verify_step

    job = _job_section(RELEASE_JOB_HEADER)
    assert job.index(GENERATE_STEP_HEADER) < job.index(VERIFY_STEP_HEADER)
    assert job.index(VERIFY_STEP_HEADER) < job.index("      - name: Attest build provenance")


def test_workflow_runs_no_test_suite_or_local_pipeline_script() -> None:
    """
    @brief Verify the workflow never runs the pre-release pipeline or pytest.
    @details Arrange: load the workflow source. Act: search for test-pipeline
    invocations. Assert: `scripts/pre-release-check.sh`, `python -m build`,
    `uv sync`, `uv run pytest`, `pytest tests/`, and extension `zip` packaging
    are absent, because artifact generation is delegated to `scripts/build.sh`.
    @return {None} Function return value.
    @satisfies PRJ-052
    @satisfies TST-105
    """
    source = _workflow_source()
    assert "scripts/pre-release-check.sh" not in source
    assert "python -m build" not in source
    assert "uv sync" not in source
    assert "uv run pytest" not in source
    assert "pytest tests/" not in source
    assert "zip -r" not in source
    assert source.count("bash scripts/build.sh") == 1


def test_workflow_declares_conditional_toolchain_and_no_unit_test_job() -> None:
    """
    @brief Verify the toolchain step is conditional and no test job exists.
    @details Arrange: load the workflow source. Act: search for toolchain setup
    actions and the removed unit-test job. Assert: `astral-sh/setup-uv` appears
    exactly once inside the release job, `actions/setup-python` is absent, and
    no `unit-tests:` job exists.
    @return {None} Function return value.
    @satisfies PRJ-052
    @satisfies TST-106
    """
    source = _workflow_source()
    assert source.count("astral-sh/setup-uv@v7") == 1
    assert "actions/setup-python" not in source
    assert "  unit-tests:" not in source
    assert "needs: [check-branch, unit-tests]" not in source


def test_publish_job_consumes_resolved_distribution_artifacts() -> None:
    """
    @brief Verify PyPI publication reuses the resolved distributions.
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
