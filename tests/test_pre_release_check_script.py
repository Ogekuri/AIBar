"""
@file
@brief Pre-release verification pipeline script regression tests.
@details Verifies the executable surface and stage composition of
`scripts/pre-release-check.sh`: dirty-tree gate with `--allow-dirty`
opt-out, locked dependency synchronization, pytest execution, sdist+wheel
build into `dist/`, built-artifact verification, and stage ordering.
Tests are source-level and deterministic; they never execute the pipeline.
@satisfies PRJ-020
@satisfies PRJ-021
@satisfies PRJ-022
@satisfies PRJ-023
@satisfies PRJ-024
@satisfies TST-084
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


def test_script_builds_sdist_and_wheel_into_dist() -> None:
    """
    @brief Verify the build stage removes stale dist and builds both artifacts.
    @details The build stage must clear `dist/` before building and mirror
    the release workflow build command ending in `python -m build`.
    @return {None} Function return value.
    @satisfies PRJ-024
    @satisfies TST-084
    """
    source = _script_source()
    assert "rm -rf dist" in source
    assert "python -m build" in source


def test_script_verifies_dist_artifacts_and_labeled_stages() -> None:
    """
    @brief Verify artifact checks, labeled stage headers, and stage ordering.
    @details Artifact verification must check both `dist/*.tar.gz` and
    `dist/*.whl`; every stage must print a `[<index>/<total>]` labeled
    header; and the main pipeline must execute stages in canonical order
    (tree gate, sync, tests, build, artifacts).
    @return {None} Function return value.
    @satisfies PRJ-022
    @satisfies PRJ-024
    @satisfies TST-084
    """
    source = _script_source()
    assert "dist/*.tar.gz" in source
    assert "dist/*.whl" in source
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
        "run_stage 'verify dist artifacts' require_dist_artifacts",
    ]
