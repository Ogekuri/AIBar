"""
@file
@brief Clean-up script regression tests for `scripts/clean.sh`.
@details Verifies the executable surface and cleanup contract of
`scripts/clean.sh`: repository-root self-resolution, `uv`/`find` toolchain
validation, generated-pattern-only `dist/` deletion with foreign-entry
preservation, `build/` directory removal, empty-`dist/` removal, removal
summary emission, and the usage/exit-code surface. Tests are source-level
and deterministic; they never execute the script.
@satisfies PRJ-042
@satisfies PRJ-043
@satisfies PRJ-044
@satisfies PRJ-045
@satisfies PRJ-046
@satisfies TST-098
"""

import stat
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "clean.sh"


def _script_source() -> str:
    """
    @brief Read the clean script source text.
    @return {str} UTF-8 decoded source of `scripts/clean.sh`.
    """
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_script_exists_and_is_executable() -> None:
    """
    @brief Verify the script file exists and carries the executable bit.
    @return {None} Function return value.
    @satisfies PRJ-042
    @satisfies TST-098
    """
    assert SCRIPT_PATH.is_file()
    mode = SCRIPT_PATH.stat().st_mode
    assert mode & stat.S_IXUSR


def test_script_resolves_repo_root_from_own_path() -> None:
    """
    @brief Verify the repository root is resolved from the script's own path.
    @details The script must resolve its absolute path via `readlink -f` on
    `BASH_SOURCE` and derive `REPO_ROOT` from the script directory so it works
    from any invocation directory, including paths with spaces.
    @return {None} Function return value.
    @satisfies PRJ-043
    @satisfies TST-098
    """
    source = _script_source()
    assert 'readlink -f "${BASH_SOURCE[0]}"' in source
    assert 'SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"' in source
    assert 'REPO_ROOT="$(dirname "$SCRIPT_DIR")"' in source
    assert 'cd ' not in source


def test_script_validates_required_tools() -> None:
    """
    @brief Verify the toolchain gate validates `uv` and `find`.
    @details Each required executable must be resolved through `command -v`
    inside `require_tool`, and a missing tool must abort with a non-zero exit
    before any artifact mutation.
    @return {None} Function return value.
    @satisfies PRJ-045
    @satisfies TST-098
    """
    source = _script_source()
    assert "require_tool uv" in source
    assert "require_tool find" in source
    assert 'command -v "$tool_name"' in source
    assert "exit 1" in source


def test_script_removes_only_generated_dist_artifacts() -> None:
    """
    @brief Verify `dist/` deletion is gated on generated artifact patterns.
    @details The deletion loop must match only the project sdist pattern, the
    project wheel pattern, and the GNOME extension zip name through
    `is_generated_dist_entry`, with the fallback case preserving the entry.
    @return {None} Function return value.
    @satisfies PRJ-042
    @satisfies PRJ-044
    @satisfies TST-098
    """
    source = _script_source()
    assert '"${PROJECT_NAME}-"*.tar.gz) return 0 ;;' in source
    assert '"${PROJECT_NAME}-"*.whl) return 0 ;;' in source
    assert '"$EXTENSION_ZIP_NAME") return 0 ;;' in source
    assert "*) return 1 ;;" in source
    assert 'is_generated_dist_entry "$entry"' in source
    assert 'rm -f -- "$entry"' in source


def test_script_preserves_foreign_dist_entries() -> None:
    """
    @brief Verify no code path bulk-deletes the `dist/` directory content.
    @details The script must never recursively force-remove `dist/` or its
    whole content; only pattern-matched generated files are deleted, so
    foreign entries survive cleanup.
    @return {None} Function return value.
    @satisfies PRJ-044
    @satisfies TST-098
    """
    source = _script_source()
    assert 'rm -rf -- "$DIST_DIR"' not in source
    assert "rm -rf dist" not in source
    assert 'find "$DIST_DIR" -mindepth 1 -maxdepth 1 -type f -print' in source


def test_script_removes_build_directory_and_empty_dist() -> None:
    """
    @brief Verify removal of `build/` and of an emptied `dist/` directory.
    @details The script must force-remove the `build/` byproduct tree and must
    remove `dist/` through `rmdir` only when no entries remain after artifact
    cleanup, so preserved foreign entries keep `dist/` in place.
    @return {None} Function return value.
    @satisfies PRJ-042
    @satisfies PRJ-046
    @satisfies TST-098
    """
    source = _script_source()
    assert 'BUILD_DIR="$REPO_ROOT/build"' in source
    assert 'rm -rf -- "$BUILD_DIR"' in source
    assert 'rmdir -- "$DIST_DIR"' in source


def test_script_prints_removal_summary_and_handles_arguments() -> None:
    """
    @brief Verify the removal summary and the usage/exit-code surface.
    @details The summary must list every removed path recorded in
    `REMOVED_PATHS`; `-h`/`--help` must print usage and exit 0, and unknown
    arguments must exit with code 2.
    @return {None} Function return value.
    @satisfies PRJ-042
    @satisfies PRJ-046
    @satisfies TST-098
    """
    source = _script_source()
    assert "print_clean_summary" in source
    assert "REMOVED_PATHS" in source
    assert "removed %d path(s):" in source
    assert "-h | --help)" in source
    assert "exit 0" in source
    assert "exit 2" in source
