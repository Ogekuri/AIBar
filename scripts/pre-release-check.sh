#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# @file
# @brief Authoritative pre-release readiness pipeline for the aibar repository.
# @details Executes, in order: (1) the repository preflight group (clean
# working-tree gate skippable with `--allow-dirty`, pre-run baseline capture,
# project-structure validation, toolchain validation, shell syntax validation
# of every `scripts/*.sh` file, Python syntax validation, `pyright` type
# checking, `.gitignore` contract validation, and `dist/` cleanup safety),
# (2) locked dependency synchronization, (3) the full pytest suite, (4)
# release-artifact generation delegated to `scripts/build.sh`, and (5)
# artifact verification. Cleanup runs through EXIT, SIGINT, and SIGTERM traps,
# preserves the original exit status, and is followed by a repository-integrity
# verification that compares the post-run state with the pre-run baseline.
# The script exits 0 only when every mandatory check and the final cleanup
# succeed.
# Time complexity O(S + T + A) over scripts S, tests T, and artifacts A;
# space O(1) beyond tool output.
# @pre Invoked from any directory inside a git checkout of this repository.
# @pre `uv`, `git`, `bash`, `find`, and `zip` are available in `PATH`.
# @post `build/`, `.pytest_cache/`, `__pycache__` trees, and a
# script-created `.venv` are removed; versioned `dist/` artifacts are retained.
# @return Exit status of the pre-release pipeline.
# @retval 0 Every mandatory check passed and the repository is unchanged.
# @retval 1 A mandatory check, the cleanup, or the integrity check failed.
# @retval 2 Unexpected arguments.
# @retval 130 Pipeline interrupted by SIGINT.
# @retval 143 Pipeline interrupted by SIGTERM.
# @satisfies PRJ-020
# @satisfies PRJ-021
# @satisfies PRJ-022
# @satisfies PRJ-023
# @satisfies PRJ-024
# @satisfies PRJ-025
# @satisfies PRJ-028
# @satisfies PRJ-029
# @satisfies PRJ-035
# @satisfies PRJ-036
# @satisfies PRJ-037
# @satisfies PRJ-039

set -Eeuo pipefail

# var SCRIPT_PATH {string} Absolute path of this script after symlink resolution.
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
# var SCRIPT_DIR {string} Absolute directory containing this script.
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
# var REPO_ROOT {string} Absolute repository root derived from the script path.
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
# var DIST_DIR {string} Release-artifact directory created and removed by this pipeline.
DIST_DIR="$REPO_ROOT/dist"
# var BUILD_DIR {string} Intermediate packaging directory removed when created by this pipeline.
BUILD_DIR="$REPO_ROOT/build"
# var PYTEST_CACHE_DIR {string} Pytest cache directory created by the test stage.
PYTEST_CACHE_DIR="$REPO_ROOT/.pytest_cache"
# var VENV_DIR {string} Project virtual environment created on demand by `uv`.
VENV_DIR="$REPO_ROOT/.venv"
# var EXTENSION_ZIP_NAME {string} Release archive file name of the GNOME extension.
EXTENSION_ZIP_NAME="aibar@aibar.panel.shell-extension.zip"
# var BUILD_COMMAND_DISPLAY {string} Canonical build command implemented by `scripts/build.sh`.
BUILD_COMMAND_DISPLAY="uv run --with build --with setuptools --with wheel python -m build"
# var ALLOW_DIRTY {bool} When true, skip the clean working-tree gate (PRJ-021 opt-out).
ALLOW_DIRTY=false
# var STAGE_INDEX {int} Counter of executed top-level pipeline stages.
STAGE_INDEX=0
# var STAGE_TOTAL {int} Number of top-level pipeline stages executed by this script.
STAGE_TOTAL=5
# var CURRENT_STAGE {string} Active stage label used by failure diagnostics.
CURRENT_STAGE="initialization"
# var PIPELINE_ACTIVE {bool} True once the pipeline reached its first stage.
PIPELINE_ACTIVE=false
# var BASELINE_STATUS {string} Pre-run `git status --porcelain` content.
BASELINE_STATUS=""
# var VENV_PREEXISTING {bool} True when `.venv` existed before the pipeline ran.
VENV_PREEXISTING=false
# var BUILD_DIR_PREEXISTING {bool} True when `build/` existed before the pipeline ran.
BUILD_DIR_PREEXISTING=false
# var DIST_PREEXISTING {bool} True when `dist/` existed before the pipeline ran.
DIST_PREEXISTING=false
# var PROJECT_NAME {string} Distribution name resolved from `pyproject.toml`.
PROJECT_NAME=""
# var PROJECT_VERSION {string} Distribution version resolved from `pyproject.toml`.
PROJECT_VERSION=""

# All relative paths below resolve against the repository root so the script
# behaves identically from any invocation directory (PRJ-039).
cd "$REPO_ROOT"

## @fn on_error
# @brief Report the failing stage and command of an unexpected failure.
# @details Registered as the ERR trap so `set -Eeuo pipefail` failures always
# name the active stage and the exact failing command.
# @return {void} Returns only when invoked with a zero exit status.
# @satisfies PRJ-022
on_error() {
  local exit_code=$?
  if [ "$exit_code" -ne 0 ]; then
    printf 'ERROR: command failed (exit %d) during stage "%s": %s\n' \
      "$exit_code" "$CURRENT_STAGE" "$BASH_COMMAND" >&2
  fi
  exit "$exit_code"
}

## @fn handle_interrupt
# @brief Terminate the pipeline on SIGINT or SIGTERM while keeping cleanup active.
# @details Exits with the conventional signal status; the EXIT trap performs
# artifact cleanup and integrity verification on this path as well.
# @param signal_status {int} Exit status associated with the received signal.
# @return {void} The function never returns.
# @satisfies PRJ-035
handle_interrupt() {
  local signal_status="$1"
  printf '\nERROR: pipeline interrupted by signal during stage "%s".\n' \
    "$CURRENT_STAGE" >&2
  exit "$signal_status"
}

## @fn cleanup_pipeline_artifacts
# @brief Remove pipeline artifacts and verify repository integrity on exit.
# @details Registered as the EXIT trap so it runs on success, failure, help,
# argument errors, and signal termination. Removes `.pytest_cache/`,
# `__pycache__` trees under `src/` and `tests/`, plus `build/` and `.venv` when
# this run created them. After removal, when the pipeline reached its first
# stage, `verify_repository_integrity` compares the repository against the
# pre-run baseline. The captured exit status is preserved; a cleanup or
# integrity failure only turns a successful run into a failing one.
# Time complexity O(T) over removed trees T.
# @return {void} The function never returns.
# @satisfies PRJ-025
# @satisfies PRJ-035
# @satisfies PRJ-037
cleanup_pipeline_artifacts() {
  local status=$?
  local cleanup_status=0
  local integrity_status=0
  trap - ERR EXIT INT TERM
  set +e
  printf '\n==> [cleanup] removing pipeline artifacts\n'
  if ! rm -rf -- .pytest_cache; then
    printf 'ERROR: failed to remove .pytest_cache/.\n' >&2
    cleanup_status=1
  fi
  if ! find src tests -type d -name __pycache__ -prune -exec rm -rf -- '{}' +; then
    printf 'ERROR: failed to remove __pycache__ trees under src/ and tests/.\n' >&2
    cleanup_status=1
  fi
  if [ "$BUILD_DIR_PREEXISTING" = "false" ] && [ -e "$BUILD_DIR" ]; then
    if ! rm -rf -- build; then
      printf 'ERROR: failed to remove the build/ directory created by this run.\n' >&2
      cleanup_status=1
    fi
  fi
  if [ "$VENV_PREEXISTING" = "false" ] && [ -e "$VENV_DIR" ]; then
    if ! rm -rf -- .venv; then
      printf 'ERROR: failed to remove the .venv directory created by this run.\n' >&2
      cleanup_status=1
    fi
  fi
  if [ "$cleanup_status" -eq 0 ]; then
    printf '  removed pipeline artifacts (build/, .pytest_cache/, __pycache__ trees, script-created .venv)\n'
  fi
  if [ "$PIPELINE_ACTIVE" = "true" ]; then
    printf '\n==> [integrity] verifying repository state\n'
    if ! verify_repository_integrity; then
      integrity_status=1
    fi
  fi
  if [ "$cleanup_status" -ne 0 ] || [ "$integrity_status" -ne 0 ]; then
    if [ "$status" -eq 0 ]; then
      printf 'ERROR: pipeline checks passed but cleanup or integrity verification failed.\n' >&2
      status=1
    else
      printf 'ERROR: original pipeline failure (exit %d) preserved despite cleanup or integrity failure.\n' \
        "$status" >&2
    fi
  fi
  exit "$status"
}

trap on_error ERR
trap cleanup_pipeline_artifacts EXIT
trap 'handle_interrupt 130' INT
trap 'handle_interrupt 143' TERM

## @fn usage
# @brief Print the script usage text to stdout.
# @return {void} No return value.
usage() {
  cat <<'EOF'
Usage: scripts/pre-release-check.sh [--allow-dirty]

Runs the authoritative pre-release verification pipeline:
  1. preflight: clean working-tree gate (skippable with --allow-dirty),
     baseline capture, project structure, toolchain, shell syntax,
     Python syntax, pyright type checking, .gitignore contract, dist/ safety
  2. dependency sync locked to uv.lock
  3. full pytest unit-test suite
  4. release artifacts generated by scripts/build.sh in dist/
  5. artifact verification (sdist, wheel, GNOME extension zip)

Cleanup always removes the generated artifacts; the script exits non-zero on
the first failing check, on cleanup failure, or when the repository differs
from its pre-run state.
EOF
}

## @fn fail
# @brief Abort the pipeline with one diagnostic message.
# @param message {string} Diagnostic text describing the failed requirement.
# @return {void} The function never returns.
fail() {
  local message="$1"
  printf 'ERROR: %s\n' "$message" >&2
  exit 1
}

## @fn report_check
# @brief Print one completed preflight check line.
# @param message {string} Check summary text.
# @return {void} No return value.
report_check() {
  local message="$1"
  printf '  %s\n' "$message"
}

## @fn require_tool
# @brief Abort when one required executable is unavailable.
# @param tool_name {string} Executable name validated in `PATH`.
# @return {void} Returns when the executable resolves.
# @satisfies PRJ-028
require_tool() {
  local tool_name="$1"
  if ! command -v "$tool_name" >/dev/null 2>&1; then
    fail "required executable not found in PATH: $tool_name"
  fi
  report_check "tool available: $tool_name"
}

## @fn run_stage
# @brief Execute one labeled pipeline stage.
# @details Increments the stage counter, prints the
# `[<executed>/<total>] <label>` header, then executes the remaining
# arguments as one command; `set -Eeuo pipefail` aborts at the first failure.
# @param stage_label {string} Human-readable stage label for the header.
# @param ... {string[]} Command argv executed for this stage.
# @return {void} Returns only when the stage command succeeds.
# @satisfies PRJ-022
run_stage() {
  local stage_label="$1"
  shift
  STAGE_INDEX=$((STAGE_INDEX + 1))
  CURRENT_STAGE="$stage_label"
  printf '\n==> [%d/%d] %s\n' "$STAGE_INDEX" "$STAGE_TOTAL" "$stage_label"
  "$@"
}

## @fn assert_git_repository
# @brief Abort when the current directory is not a git working tree.
# @return {void} Returns inside a git working tree.
# @satisfies PRJ-021
assert_git_repository() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    fail "$REPO_ROOT is not a git working tree."
  fi
}

## @fn capture_preexisting_paths
# @brief Record whether pipeline-owned paths already existed before the run.
# @details Cleanup must preserve pre-existing content and remove only what this
# run created, so `.venv`, `build/`, and `dist/` presence is recorded up front.
# @return {void} No return value.
# @satisfies PRJ-025
capture_preexisting_paths() {
  VENV_PREEXISTING=false
  BUILD_DIR_PREEXISTING=false
  DIST_PREEXISTING=false
  if [ -d "$VENV_DIR" ]; then
    VENV_PREEXISTING=true
  fi
  if [ -e "$BUILD_DIR" ]; then
    BUILD_DIR_PREEXISTING=true
  fi
  if [ -e "$DIST_DIR" ]; then
    DIST_PREEXISTING=true
  fi
  report_check "pre-existing .venv: $VENV_PREEXISTING, build/: $BUILD_DIR_PREEXISTING, dist/: $DIST_PREEXISTING"
}

## @fn load_project_metadata
# @brief Resolve distribution name and version from `pyproject.toml`.
# @details Uses the project interpreter so no duplicated version literal exists
# outside the PEP 621 metadata.
# @return {void} Returns after populating `PROJECT_NAME` and `PROJECT_VERSION`.
# @satisfies PRJ-028
load_project_metadata() {
  local metadata
  metadata="$(uv run --locked --project "$REPO_ROOT" python -c '
import pathlib
import sys
import tomllib

data = tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
print(data["project"]["name"])
print(data["project"]["version"])
' "$REPO_ROOT/pyproject.toml")"
  PROJECT_NAME="$(printf '%s\n' "$metadata" | sed -n '1p')"
  PROJECT_VERSION="$(printf '%s\n' "$metadata" | sed -n '2p')"
  if [ -z "$PROJECT_NAME" ] || [ -z "$PROJECT_VERSION" ]; then
    fail "unable to resolve project name and version from pyproject.toml"
  fi
  report_check "project: $PROJECT_NAME $PROJECT_VERSION"
}

## @fn validate_project_structure
# @brief Validate the repository structure required by the pipeline.
# @details Requires the packaging manifest, lockfile, package tree, test tree,
# executable scripts, and the GNOME extension metadata used during packaging.
# @return {void} Returns when every required path exists.
# @satisfies PRJ-028
validate_project_structure() {
  local required_path
  for required_path in \
    pyproject.toml \
    uv.lock \
    src/aibar/aibar \
    src/aibar/aibar/cli.py \
    src/aibar/aibar/gnome-extension/aibar@aibar.panel/metadata.json \
    tests \
    scripts/aibar.sh \
    scripts/build.sh; do
    if [ ! -e "$required_path" ]; then
      fail "missing required repository path: $required_path"
    fi
  done
  if [ ! -x scripts/build.sh ]; then
    fail "scripts/build.sh is not executable."
  fi
  report_check "project structure: OK"
}

## @fn validate_toolchain
# @brief Validate every executable required by the pipeline.
# @details Verifies the external commands and the project interpreter floor
# declared by `requires-python` before any artifact mutation.
# @return {void} Returns when the toolchain is complete.
# @satisfies PRJ-028
validate_toolchain() {
  require_tool uv
  require_tool git
  require_tool bash
  require_tool find
  require_tool zip
  if ! uv run --locked --project "$REPO_ROOT" python -c '
import sys

sys.exit(0 if sys.version_info >= (3, 12) else 1)
'; then
    fail "project interpreter is older than the required Python 3.12 floor."
  fi
  report_check "toolchain: OK (Python >= 3.12)"
}

## @fn validate_shell_syntax
# @brief Validate the syntax of every shell script in `scripts/`.
# @details Runs `bash -n` on every `scripts/*.sh` file and, when available,
# runs `shellcheck` at warning severity without modifying any source.
# @return {void} Returns when every script parses.
# @satisfies PRJ-028
validate_shell_syntax() {
  local script_file
  local script_count=0
  for script_file in scripts/*.sh; do
    if [ ! -f "$script_file" ]; then
      continue
    fi
    if ! bash -n "$script_file"; then
      fail "shell syntax error detected in $script_file"
    fi
    script_count=$((script_count + 1))
  done
  if [ "$script_count" -eq 0 ]; then
    fail "no shell scripts found under scripts/."
  fi
  report_check "shell syntax: OK ($script_count scripts)"
  if command -v shellcheck >/dev/null 2>&1; then
    if ! shellcheck --severity=warning --shell=bash scripts/*.sh; then
      fail "shellcheck reported findings (severity >= warning)."
    fi
    report_check "shellcheck: OK"
  else
    report_check "shellcheck: skipped (executable not installed)"
  fi
}

## @fn validate_python_syntax
# @brief Validate Python syntax across the package sources.
# @details Uses the project interpreter `compileall` pass, which exits non-zero
# on any syntax error; generated bytecode trees are removed during cleanup.
# @return {void} Returns when every module compiles.
# @satisfies PRJ-029
validate_python_syntax() {
  if ! uv run --locked --project "$REPO_ROOT" python -m compileall -q src; then
    fail "Python syntax validation failed under src/."
  fi
  report_check "python syntax: OK"
}

## @fn validate_type_checking
# @brief Run the repository type checker against the declared configuration.
# @details Executes `pyright` with `pyrightconfig.json` through the project
# environment, provisioning the checker as an ephemeral tool dependency so no
# manifest change is required.
# @return {void} Returns when type checking reports no error.
# @satisfies PRJ-029
validate_type_checking() {
  if ! uv run --locked --project "$REPO_ROOT" --with pyright \
    pyright --project "$REPO_ROOT/pyrightconfig.json"; then
    fail "pyright type checking reported errors."
  fi
  report_check "type checking: OK"
}

## @fn assert_path_visible_to_git
# @brief Abort when git unexpectedly ignores one intentionally tracked path.
# @param target_path {string} Repository-relative path that must stay visible.
# @return {void} Returns when the path is not ignored.
# @satisfies PRJ-038
assert_path_visible_to_git() {
  local target_path="$1"
  if git check-ignore --no-index --quiet -- "$target_path"; then
    fail "intentionally tracked path is ignored by .gitignore: $target_path"
  fi
}

## @fn validate_gitignore_rules
# @brief Validate the `.gitignore` artifact and source-exclusion contract.
# @details Confirms generated release artifacts, the release scripts, package
# sources, documentation, and lockfile stay visible to git for versioning.
# @return {void} Returns when the contract holds.
# @satisfies PRJ-038
# @satisfies PRJ-041
validate_gitignore_rules() {
  assert_path_visible_to_git "dist/${PROJECT_NAME}-${PROJECT_VERSION}.tar.gz"
  assert_path_visible_to_git "dist/${PROJECT_NAME}-${PROJECT_VERSION}-py3-none-any.whl"
  assert_path_visible_to_git "dist/${EXTENSION_ZIP_NAME}"
  assert_path_visible_to_git "src/aibar/aibar/cli.py"
  assert_path_visible_to_git "scripts/build.sh"
  assert_path_visible_to_git "scripts/pre-release-check.sh"
  assert_path_visible_to_git "usereq/docs/REQUIREMENTS.md"
  assert_path_visible_to_git "uv.lock"
  report_check ".gitignore contract: OK"
}

## @fn assert_dist_safe_to_clean
# @brief Abort when `dist/` holds content this pipeline must not delete.
# @details Refuses to proceed when `dist/` contains entries outside the
# generated artifact patterns, so non-generated content is never destroyed.
# Tracked generated artifacts are permitted because the build replaces them.
# @return {void} Returns when `dist/` is absent or only generated artifacts.
# @satisfies PRJ-036
assert_dist_safe_to_clean() {
  if [ ! -d "$DIST_DIR" ]; then
    report_check "dist/ safety: absent"
    return 0
  fi
  local entry
  local entry_name
  while IFS= read -r entry; do
    if [ -z "$entry" ]; then
      continue
    fi
    entry_name="$(basename "$entry")"
    case "$entry_name" in
      "${PROJECT_NAME}-"*.tar.gz | "${PROJECT_NAME}-"*.whl | "$EXTENSION_ZIP_NAME") ;;
      *)
        printf 'ERROR: dist/ contains a non-generated entry; refusing to remove it: %s\n' \
          "$entry" >&2
        exit 1
        ;;
    esac
  done < <(find "$DIST_DIR" -mindepth 1 -maxdepth 1 -print)
  report_check "dist/ safety: only generated artifacts present"
}

## @fn check_clean_working_tree
# @brief Execute the repository preflight group and the working-tree gate.
# @details Runs the clean-tree gate with the `--allow-dirty` opt-out, captures
# the pre-run baseline, then executes every read-only preflight check:
# structure, toolchain, shell syntax, Python syntax, type checking, the
# `.gitignore` contract, and the `dist/` cleanup-safety check.
# @return {void} Returns when the tree state is acceptable and every preflight check passed.
# @satisfies PRJ-021
# @satisfies PRJ-028
# @satisfies PRJ-029
# @satisfies PRJ-036
# @satisfies PRJ-038
check_clean_working_tree() {
  assert_git_repository
  local status_output
  status_output="$(git status --porcelain)"
  if [ "$ALLOW_DIRTY" = "true" ]; then
    report_check "working tree gate: skipped (--allow-dirty flag active)"
  elif [ -n "$status_output" ]; then
    printf 'ERROR: git working tree is not clean; commit or stash before a release.\n' >&2
    printf '%s\n' "$status_output" >&2
    printf '  hint: pass --allow-dirty to bypass this gate.\n' >&2
    exit 1
  else
    report_check "working tree gate: clean"
  fi
  BASELINE_STATUS="$(git status --porcelain -- . ':(exclude)dist')"
  PIPELINE_ACTIVE=true
  capture_preexisting_paths
  validate_project_structure
  load_project_metadata
  validate_toolchain
  validate_shell_syntax
  validate_python_syntax
  validate_type_checking
  validate_gitignore_rules
  assert_dist_safe_to_clean
}

## @fn build_distribution
# @brief Generate release artifacts through the canonical build script.
# @details Re-checks the `dist/` cleanup safety and delegates artifact
# generation, including removal of stale generated artifacts, to
# `scripts/build.sh` so the build logic has a single implementation. Versioned
# `dist/` content outside the generated patterns is never removed here.
# @return {void} Returns when `scripts/build.sh` succeeded.
# @satisfies PRJ-024
# @satisfies PRJ-036
# @satisfies PRJ-041
build_distribution() {
  assert_dist_safe_to_clean
  report_check "delegating artifact generation to scripts/build.sh ($BUILD_COMMAND_DISPLAY)"
  if ! "$REPO_ROOT/scripts/build.sh"; then
    fail "scripts/build.sh failed; release artifact generation aborted."
  fi
}

## @fn require_dist_artifacts
# @brief Verify the generated release artifacts and their git visibility.
# @details Requires exactly one sdist, one wheel, and the GNOME extension zip,
# validates archive integrity and required members through the project
# interpreter, and confirms every produced artifact stays visible to git.
# @return {void} Returns when every artifact is valid and git-visible.
# @satisfies PRJ-024
# @satisfies PRJ-033
require_dist_artifacts() {
  if [ ! -d "$DIST_DIR" ]; then
    fail "dist/ directory is missing after the build."
  fi
  local artifact
  local sdist_count=0
  local wheel_count=0
  for artifact in dist/*.tar.gz; do
    if [ -f "$artifact" ]; then
      sdist_count=$((sdist_count + 1))
      report_check "artifact: $artifact"
    fi
  done
  for artifact in dist/*.whl; do
    if [ -f "$artifact" ]; then
      wheel_count=$((wheel_count + 1))
      report_check "artifact: $artifact"
    fi
  done
  if [ "$sdist_count" -ne 1 ]; then
    fail "expected exactly one sdist (*.tar.gz) under dist/, found $sdist_count."
  fi
  if [ "$wheel_count" -ne 1 ]; then
    fail "expected exactly one wheel (*.whl) under dist/, found $wheel_count."
  fi
  if [ ! -f "dist/$EXTENSION_ZIP_NAME" ]; then
    fail "expected GNOME extension zip under dist/: $EXTENSION_ZIP_NAME"
  fi
  report_check "artifact: dist/$EXTENSION_ZIP_NAME"
  uv run --locked --project "$REPO_ROOT" python - \
    "$DIST_DIR" "$PROJECT_NAME" "$PROJECT_VERSION" "$EXTENSION_ZIP_NAME" <<'PY'
import pathlib
import sys
import tarfile
import zipfile

dist_dir = pathlib.Path(sys.argv[1])
project_name = sys.argv[2]
project_version = sys.argv[3]
extension_zip_name = sys.argv[4]

failures: list[str] = []
reported: list[str] = []


def report(message: str) -> None:
    reported.append(message)


def fail(message: str) -> None:
    failures.append(message)


sdist_path = dist_dir / f"{project_name}-{project_version}.tar.gz"
if not sdist_path.is_file() or sdist_path.stat().st_size == 0:
    fail(f"missing or empty sdist artifact: {sdist_path}")
else:
    try:
        with tarfile.open(sdist_path, "r:gz") as archive:
            names = archive.getnames()
    except (tarfile.TarError, OSError) as error:
        fail(f"unreadable sdist archive {sdist_path}: {error}")
    else:
        required = (
            f"{project_name}-{project_version}/pyproject.toml",
            f"{project_name}-{project_version}/src/aibar/aibar/cli.py",
            f"{project_name}-{project_version}/src/aibar/aibar/gnome-extension/aibar@aibar.panel/metadata.json",
            f"{project_name}-{project_version}/LICENSE_GnomeCodexBar",
        )
        missing = [name for name in required if name not in names]
        if missing:
            fail(f"sdist missing required members: {', '.join(missing)}")
        report(f"sdist OK: {sdist_path.name}")

wheel_paths = sorted(dist_dir.glob(f"{project_name}-{project_version}-*.whl"))
if len(wheel_paths) != 1 or wheel_paths[0].stat().st_size == 0:
    fail(f"expected one non-empty wheel matching {project_name}-{project_version}-*.whl")
else:
    wheel_path = wheel_paths[0]
    try:
        with zipfile.ZipFile(wheel_path) as archive:
            corrupted = archive.testzip()
            names = archive.namelist()
    except (zipfile.BadZipFile, OSError) as error:
        fail(f"unreadable wheel archive {wheel_path}: {error}")
    else:
        if corrupted is not None:
            fail(f"corrupted wheel member {corrupted} in {wheel_path}")
        required = (
            "aibar/cli.py",
            "aibar/gnome-extension/aibar@aibar.panel/metadata.json",
            "aibar/gnome-extension/aibar@aibar.panel/extension.js",
            f"{project_name}-{project_version}.dist-info/METADATA",
        )
        missing = [name for name in required if name not in names]
        if missing:
            fail(f"wheel missing required members: {', '.join(missing)}")
        report(f"wheel OK: {wheel_path.name}")

extension_zip_path = dist_dir / extension_zip_name
if not extension_zip_path.is_file() or extension_zip_path.stat().st_size == 0:
    fail(f"missing or empty GNOME extension zip: {extension_zip_path}")
else:
    try:
        with zipfile.ZipFile(extension_zip_path) as archive:
            corrupted = archive.testzip()
            names = archive.namelist()
    except (zipfile.BadZipFile, OSError) as error:
        fail(f"unreadable GNOME extension zip {extension_zip_path}: {error}")
    else:
        if corrupted is not None:
            fail(f"corrupted extension member {corrupted} in {extension_zip_path}")
        missing = [
            name for name in ("metadata.json", "extension.js") if name not in names
        ]
        if missing:
            fail(f"extension zip missing required members: {', '.join(missing)}")
        report(f"GNOME extension zip OK: {extension_zip_path.name}")

for message in reported:
    print(f"  {message}")
for message in failures:
    print(f"ERROR: {message}", file=sys.stderr)
sys.exit(1 if failures else 0)
PY
  for artifact in dist/*; do
    if [ -f "$artifact" ]; then
      assert_path_visible_to_git "$artifact"
    fi
  done
  report_check "artifact git visibility: OK"
}

## @fn verify_repository_integrity
# @brief Compare the post-run repository state with the pre-run baseline.
# @details Fails when tracked files outside `dist/` changed, when the `git status --porcelain` (excluding `dist/`)
# output differs from the baseline, when any pipeline artifact survived
# cleanup, or when a script-created environment directory remains. Ignored
# build output is inspected explicitly because `git status` alone cannot
# detect it.
# @return {int} 0 when the repository matches the baseline, 1 otherwise.
# @satisfies PRJ-037
verify_repository_integrity() {
  local failures=0
  local current_status=""
  if ! current_status="$(git status --porcelain -- . ':(exclude)dist')"; then
    printf 'ERROR: unable to read git status during integrity verification.\n' >&2
    return 1
  fi
  if [ "$current_status" != "$BASELINE_STATUS" ]; then
    printf 'ERROR: repository state changed during the pipeline.\n' >&2
    printf '  baseline: %s\n' "${BASELINE_STATUS:-<clean>}" >&2
    printf '  current:  %s\n' "${current_status:-<clean>}" >&2
    failures=1
  else
    printf '  working tree matches the pre-run baseline\n'
  fi
  if [ "$ALLOW_DIRTY" = "false" ] && ! git diff --quiet HEAD -- . ':(exclude)dist'; then
    printf 'ERROR: tracked files differ from HEAD after the pipeline.\n' >&2
    git diff --stat HEAD -- . ':(exclude)dist' >&2
    failures=1
  fi
  local generated_path
  for generated_path in .pytest_cache; do
    if [ -e "$generated_path" ]; then
      printf 'ERROR: %s remains after cleanup.\n' "$generated_path" >&2
      failures=1
    fi
  done
  if [ "$BUILD_DIR_PREEXISTING" = "false" ] && [ -e "$BUILD_DIR" ]; then
    printf 'ERROR: build/ created by this run remains after cleanup.\n' >&2
    failures=1
  fi
  local pycache_output=""
  pycache_output="$(find src tests -type d -name __pycache__ -print -quit)"
  if [ -n "$pycache_output" ]; then
    printf 'ERROR: __pycache__ trees remain under src/ or tests/ after cleanup: %s\n' \
      "$pycache_output" >&2
    failures=1
  fi
  if [ "$VENV_PREEXISTING" = "false" ] && [ -e "$VENV_DIR" ]; then
    printf 'ERROR: .venv created by this run remains after cleanup.\n' >&2
    failures=1
  fi
  if [ "$failures" -eq 0 ]; then
    printf '  no pipeline artifacts remain; ignored build output absent\n'
    printf '  repository integrity: OK\n'
    return 0
  fi
  return 1
}

# Argument parsing: only the documented flags are accepted.
for arg in "$@"; do
  case "$arg" in
    --allow-dirty) ALLOW_DIRTY=true ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      printf 'ERROR: unknown argument: %s\n' "$arg" >&2
      usage >&2
      exit 2
      ;;
  esac
done

# Main pipeline: ordered pre-release verification stages (PRJ-020, PRJ-022).
run_stage 'clean working tree' check_clean_working_tree
run_stage 'sync dependencies (uv.lock)' uv sync --locked
run_stage 'unit tests' uv run pytest tests/
run_stage 'build sdist and wheel' build_distribution
run_stage 'verify dist artifacts' require_dist_artifacts

printf '\n==> pre-release checks passed (%d/%d stages OK)\n' "$STAGE_TOTAL" "$STAGE_TOTAL"
