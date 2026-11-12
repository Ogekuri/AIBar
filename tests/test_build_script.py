"""
@file
@brief Clean-build pipeline regression tests for `scripts/build.sh`.
@details Verifies the executable surface and cleanup contract of the merged
clean-build pipeline: repository-root self-resolution, `uv`/`zip`/`find`
toolchain validation, removal of every previously generated `dist/` artifact
for every version number, foreign-entry preservation, intermediate-artifact
removal, EXIT/SIGINT/SIGTERM cleanup handlers, residual-artifact verification,
retention of versioned `dist/` artifacts, and the removal of the retired
`scripts/clean.sh` entrypoint. Tests are source-level and deterministic; they
never execute the build.
@satisfies PRJ-031
@satisfies PRJ-032
@satisfies PRJ-047
@satisfies PRJ-048
@satisfies PRJ-049
@satisfies TST-099
@satisfies TST-100
@satisfies TST-101
@satisfies TST-102
"""

import stat
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "build.sh"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
RETIRED_SCRIPT_PATH = SCRIPTS_DIR / "clean.sh"


def _script_source() -> str:
    """
    @brief Read the build script source text.
    @return {str} UTF-8 decoded source of `scripts/build.sh`.
    @satisfies TST-099
    """
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_script_exists_and_is_executable() -> None:
    """
    @brief Verify the build script exists and carries the executable bit.
    @details Arrange: resolve the script path. Act: probe the file and its
    mode bits. Assert: the path is a regular file with the owner execute bit.
    @return {None} Function return value.
    @satisfies PRJ-030
    @satisfies TST-099
    """
    assert SCRIPT_PATH.is_file()
    mode = SCRIPT_PATH.stat().st_mode
    assert mode & stat.S_IXUSR


def test_script_resolves_repo_root_from_own_path() -> None:
    """
    @brief Verify the repository root is resolved from the script's own path.
    @details Arrange: load the script source. Act: search the path-resolution
    block. Assert: `readlink -f` on `BASH_SOURCE` resolves the absolute script
    path, `REPO_ROOT` derives from the script directory, and no `cd` is needed
    to locate the repository.
    @return {None} Function return value.
    @satisfies PRJ-039
    @satisfies TST-099
    """
    source = _script_source()
    assert 'readlink -f "${BASH_SOURCE[0]}"' in source
    assert 'SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"' in source
    assert 'REPO_ROOT="$(dirname "$SCRIPT_DIR")"' in source


def test_script_validates_required_tools() -> None:
    """
    @brief Verify the toolchain gate validates `uv`, `zip`, and `find`.
    @details Arrange: load the script source. Act: inspect `validate_toolchain`
    and `require_tool`. Assert: all three tools are required, resolution uses
    `command -v`, and a missing tool exits non-zero before artifact mutation.
    @return {None} Function return value.
    @satisfies PRJ-040
    @satisfies TST-099
    """
    source = _script_source()
    assert "require_tool uv" in source
    assert "require_tool zip" in source
    assert "require_tool find" in source
    assert 'command -v "$tool_name"' in source
    assert "exit 1" in source


def test_script_removes_generated_artifacts_for_every_version() -> None:
    """
    @brief Verify `dist/` deletion covers generated artifacts of every version.
    @details Arrange: load the script source. Act: inspect
    `is_generated_dist_entry` and `remove_generated_dist_artifacts`. Assert:
    matching uses the version-agnostic project sdist and wheel globs plus the
    GNOME extension zip name, removal iterates every `dist/` top-level file,
    and the pre-build stage runs the removal before the distribution build.
    @return {None} Function return value.
    @satisfies PRJ-031
    @satisfies TST-099
    """
    source = _script_source()
    assert '"${PROJECT_NAME}-"*.tar.gz) return 0 ;;' in source
    assert '"${PROJECT_NAME}-"*.whl) return 0 ;;' in source
    assert '"$EXTENSION_ZIP_NAME") return 0 ;;' in source
    assert "*) return 1 ;;" in source
    assert 'is_generated_dist_entry "$entry"' in source
    assert 'rm -f -- "$entry"' in source
    assert 'find "$DIST_DIR" -mindepth 1 -maxdepth 1 -type f -print' in source
    pre_build_index = source.index('CURRENT_STAGE="pre-build cleanup"')
    build_index = source.index('CURRENT_STAGE="python distribution build"')
    assert pre_build_index < build_index
    assert "remove_generated_dist_artifacts" in source[pre_build_index:build_index]


def test_script_preserves_foreign_dist_entries() -> None:
    """
    @brief Verify no code path bulk-deletes the `dist/` directory content.
    @details Arrange: load the script source. Act: search for recursive
    `dist/` deletions. Assert: the script never force-removes `dist/` itself,
    and `assert_dist_safe_to_clean` aborts on foreign entries.
    @return {None} Function return value.
    @satisfies PRJ-032
    @satisfies TST-099
    """
    source = _script_source()
    assert 'rm -rf -- "$DIST_DIR"' not in source
    assert "rm -rf dist" not in source
    assert "assert_dist_safe_to_clean" in source
    assert "refusing to delete it" in source


def test_script_removes_intermediate_artifacts() -> None:
    """
    @brief Verify intermediate build artifacts are removed by the pipeline.
    @details Arrange: load the script source. Act: inspect
    `remove_intermediate_artifacts`. Assert: the function removes the `build/`
    tree, the `.pytest_cache/` tree, `*.egg-info` directories, and
    `__pycache__` trees under `src/` and `tests/` while never touching the
    versioned `dist/` artifacts.
    @return {None} Function return value.
    @satisfies PRJ-047
    @satisfies TST-100
    """
    source = _script_source()
    assert 'BUILD_DIR="$REPO_ROOT/build"' in source
    assert 'PYTEST_CACHE_DIR="$REPO_ROOT/.pytest_cache"' in source
    assert "remove_intermediate_artifacts" in source
    assert 'rm -rf -- "$BUILD_DIR"' in source
    assert 'rm -rf -- "$PYTEST_CACHE_DIR"' in source
    assert "-name '*.egg-info'" in source
    assert "-name '__pycache__'" in source
    assert 'pycache_roots+=("$SRC_DIR")' in source
    assert 'pycache_roots+=("$TESTS_DIR")' in source
    removal_body = source.split("remove_intermediate_artifacts() {", 1)[1]
    removal_body = removal_body.split("\n}\n", 1)[0]
    assert 'rm -rf -- "$DIST_DIR"' not in removal_body


def test_script_registers_cleanup_traps() -> None:
    """
    @brief Verify EXIT, SIGINT, and SIGTERM handlers run the cleanup.
    @details Arrange: load the script source. Act: inspect the trap
    registrations and `cleanup_on_exit`. Assert: the EXIT trap calls the
    cleanup, INT and TERM map to 130 and 143, the captured status is preserved
    when cleanup succeeds, and a cleanup failure escalates a successful run to
    a non-zero exit.
    @return {None} Function return value.
    @satisfies PRJ-048
    @satisfies TST-100
    """
    source = _script_source()
    assert "trap cleanup_on_exit EXIT" in source
    assert "trap 'exit 130' INT" in source
    assert "trap 'exit 143' TERM" in source
    cleanup_body = source.split("cleanup_on_exit() {", 1)[1]
    cleanup_body = cleanup_body.split("\n}\n", 1)[0]
    assert "local status=$?" in cleanup_body
    assert "remove_intermediate_artifacts" in cleanup_body
    assert "verify_no_intermediate_artifacts" in cleanup_body
    assert 'exit "$status"' in cleanup_body
    assert "status=1" in cleanup_body


def test_script_verifies_residual_intermediate_artifacts() -> None:
    """
    @brief Verify residual intermediate artifacts fail the build.
    @details Arrange: load the script source. Act: inspect
    `verify_no_intermediate_artifacts` and the post-build stage ordering.
    Assert: the verification probes every intermediate artifact location,
    reports each residual path on stderr, returns non-zero on any residual, and
    runs after the post-build cleanup stage.
    @return {None} Function return value.
    @satisfies PRJ-049
    @satisfies TST-101
    """
    source = _script_source()
    verify_body = source.split("verify_no_intermediate_artifacts() {", 1)[1]
    verify_body = verify_body.split("\n}\n", 1)[0]
    assert "residual intermediate artifact" in verify_body
    assert "residual_found=1" in verify_body
    assert "return 1" in verify_body
    assert "-name '*.egg-info'" in verify_body
    assert "-name '__pycache__'" in verify_body
    post_cleanup_index = source.index('CURRENT_STAGE="post-build intermediate artifact cleanup"')
    verification_index = source.index('CURRENT_STAGE="intermediate artifact verification"')
    summary_index = source.index('CURRENT_STAGE="artifact summary"')
    assert post_cleanup_index < verification_index < summary_index


def test_script_prints_artifact_summary_and_handles_arguments() -> None:
    """
    @brief Verify the artifact summary and the usage/exit-code surface.
    @details Arrange: load the script source. Act: inspect the summary emitter
    and the argument parser. Assert: retained artifacts are listed with their
    byte size, `-h`/`--help` exits 0, and unknown arguments exit with code 2.
    @return {None} Function return value.
    @satisfies PRJ-034
    @satisfies TST-099
    """
    source = _script_source()
    assert "print_artifact_summary" in source
    assert "artifacts retained in" in source
    assert "(%s bytes)" in source
    assert "-h | --help)" in source
    assert "exit 0" in source
    assert "exit 2" in source


def test_script_accepts_dist_dir_override_with_default() -> None:
    """
    @brief Verify the `--dist-dir` artifact-destination override.
    @details Arrange: load the script source. Act: inspect the destination
    assignment, the argument parser, and the build invocation. Assert: the
    destination defaults to `<repository-root>/dist`, `--dist-dir <Path>`
    replaces it, and the distribution build forwards it through `--outdir`.
    @return {None} Function return value.
    @satisfies PRJ-055
    @satisfies TST-099
    """
    source = _script_source()
    assert 'DIST_DIR="$REPO_ROOT/dist"' in source
    assert "--dist-dir)" in source
    assert 'DIST_DIR="$2"' in source
    assert '--outdir "$DIST_DIR"' in source


def test_retired_clean_script_is_absent() -> None:
    """
    @brief Verify `scripts/clean.sh` was removed and is no longer referenced.
    @details Arrange: enumerate `scripts/*.sh`. Act: probe the retired path and
    scan every remaining script for a `clean.sh` reference. Assert: the retired
    script does not exist and no remaining script invokes it, because the
    cleanup now runs inside `scripts/build.sh`.
    @return {None} Function return value.
    @satisfies TST-102
    """
    assert not RETIRED_SCRIPT_PATH.exists()
    remaining_scripts = sorted(SCRIPTS_DIR.glob("*.sh"))
    assert remaining_scripts
    for script_path in remaining_scripts:
        assert "clean.sh" not in script_path.read_text(encoding="utf-8"), script_path.name
