"""
@file
@brief Pre-release verification pipeline script regression tests.
@details Verifies the executable surface and stage composition of
`scripts/pre-release-check.sh`: dirty-tree gate with `--allow-dirty`
opt-out, locked dependency synchronization, pytest execution, sdist+wheel
build into a pipeline-created temporary artifact directory, built-artifact
verification, `dist/` independence, and stage ordering.
Tests are source-level and deterministic; they never execute the pipeline.
@satisfies PRJ-020
@satisfies PRJ-021
@satisfies PRJ-022
@satisfies PRJ-023
@satisfies PRJ-024
@satisfies PRJ-054
@satisfies PRJ-056
@satisfies TST-084
@satisfies TST-107
"""

import stat
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "pre-release-check.sh"


def _script_source() -> str:
    """
    @brief Read the pre-release-check script source text.
    @return {str} UTF-8 decoded source of `scripts/pre-release-check.sh`.
    """
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_script_exists_and_is_executable() -> None:
    """
    @brief Verify the script file exists and carries the executable bit.
    @return {None} Function return value.
    @satisfies PRJ-020
    @satisfies TST-084
    """
    assert SCRIPT_PATH.is_file()
    mode = SCRIPT_PATH.stat().st_mode
    assert mode & stat.S_IXUSR


def test_script_gates_on_dirty_tree_with_allow_dirty_opt_out() -> None:
    """
    @brief Verify the clean working-tree gate and its `--allow-dirty` opt-out.
    @details The gate must inspect `git status --porcelain`, expose the
    `--allow-dirty` flag through an explicit opt-out variable, and abort
    with an explicit non-zero exit when the tree is dirty.
    @return {None} Function return value.
    @satisfies PRJ-021
    @satisfies TST-084
    """
    source = _script_source()
    assert "git status --porcelain" in source
    assert "--allow-dirty" in source
    assert "ALLOW_DIRTY" in source
    assert "exit 1" in source


def test_script_runs_locked_dependency_sync_and_pytest() -> None:
    """
    @brief Verify the pipeline executes locked sync and the pytest suite.
    @details Dependency synchronization must run `uv sync --locked` and the
    unit-test stage must invoke `uv run pytest tests/` per PRJ-023.
    @return {None} Function return value.
    @satisfies PRJ-023
    @satisfies TST-084
    """
    source = _script_source()
    assert "uv sync --locked" in source
    assert "uv run pytest tests/" in source


def test_script_builds_sdist_and_wheel_into_temporary_directory() -> None:
    """
    @brief Verify the build stage delegates artifact generation to build.sh.
    @details The build stage must delegate to `scripts/build.sh` with a
    `--dist-dir` destination located inside a `mktemp -d` temporary root, and
    must never remove the repository artifact directory.
    @return {None} Function return value.
    @satisfies PRJ-024
    @satisfies PRJ-056
    @satisfies TST-084
    """
    source = _script_source()
    assert "scripts/build.sh" in source
    assert '--dist-dir "$TEST_BUILD_ARTIFACT_DIR"' in source
    assert "mktemp -d" in source
    assert "rm -rf dist" not in source
    assert "python -m build" in source


def test_script_has_no_dist_directory_dependency() -> None:
    """
    @brief Verify the pipeline never reads, cleans, or verifies `dist/`.
    @details Arrange: load the script source. Act: search every construct that
    could address the repository `dist/` directory. Assert: no artifact
    destination assignment, no `dist/` safety probe, no `dist/`-scoped git
    pathspec, and no `dist/` artifact glob remains in the script.
    @return {None} Function return value.
    @satisfies PRJ-036
    @satisfies PRJ-056
    @satisfies TST-107
    """
    source = _script_source()
    assert "REPO_ROOT/dist" not in source
    assert "assert_dist_safe_to_clean" not in source
    assert ":(exclude)dist" not in source
    assert "rm -rf -- dist" not in source
    assert "dist/*.tar.gz" not in source
    assert "dist/*.whl" not in source


def test_script_cleans_pipeline_artifacts_on_exit() -> None:
    """
    @brief Verify the EXIT trap removes pipeline artifacts after execution.
    @details The script must register `cleanup_pipeline_artifacts` as an
    EXIT trap so `.pytest_cache/`, `__pycache__` trees under `src/` and
    `tests/`, and the pipeline-created temporary artifact directory are removed
    whether the pipeline succeeds or fails.
    @return {None} Function return value.
    @satisfies PRJ-025
    @satisfies TST-085
    """
    source = _script_source()
    assert "trap cleanup_pipeline_artifacts EXIT" in source
    assert "rm -rf -- .pytest_cache" in source
    assert "rm -rf -- dist" not in source
    assert 'rm -rf -- "$TEST_BUILD_ROOT"' in source
    assert "-name __pycache__" in source


def test_script_verifies_temporary_artifacts_and_labeled_stages() -> None:
    """
    @brief Verify artifact checks, labeled stage headers, and stage ordering.
    @details Artifact verification must check both `*.tar.gz` and `*.whl`
    inside the temporary artifact destination directory; every stage must print
    a `[<index>/<total>]` labeled header; and the main pipeline must execute
    stages in canonical order (tree gate, sync, tests, build, artifacts).
    @return {None} Function return value.
    @satisfies PRJ-022
    @satisfies PRJ-054
    @satisfies TST-084
    """
    source = _script_source()
    assert '"$TEST_BUILD_ARTIFACT_DIR"/*.tar.gz' in source
    assert '"$TEST_BUILD_ARTIFACT_DIR"/*.whl' in source
    assert '[%d/%d]' in source
    main_section = source.split("# Main pipeline:", 1)[1]
    stage_lines = [
        line.strip()
        for line in main_section.splitlines()
        if line.strip().startswith("run_stage")
    ]
    assert stage_lines == [
        "run_stage 'clean working tree' check_clean_working_tree",
        "run_stage 'sync dependencies (uv.lock)' uv sync --locked",
        "run_stage 'unit tests' uv run pytest tests/",
        "run_stage 'build sdist and wheel' build_distribution",
        "run_stage 'verify test-build artifacts' require_test_build_artifacts",
    ]
