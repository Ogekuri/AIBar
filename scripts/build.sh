#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# @file
# @brief Canonical clean build pipeline for the aibar repository.
# @details Resolves the repository root from its own path, validates the
# required toolchain and layout, resolves the distribution name and version
# from `pyproject.toml`, removes every previously generated `dist/` artifact
# matching the project sdist, wheel, or GNOME extension zip pattern
# regardless of version number, verifies that no generated release artifact
# survived that removal, removes intermediate build artifacts, executes
# the canonical `python -m build` invocation used by
# `.github/workflows/release-pypi.yml`, creates the GNOME Shell extension zip
# byte-reproducibly (fixed member order, fixed member timestamps, fixed member
# permissions, stripped extra fields), validates every produced artifact
# (non-empty size, archive integrity,
# required member entries), removes every intermediate artifact created by the
# build, verifies that no intermediate artifact remains outside `dist/`, and
# retains all versioned artifacts in `dist/` while printing a summary.
# Non-generated content inside `dist/` is never deleted; a failed build never
# reports success and never leaves intermediate artifacts behind.
# Time complexity O(A + T) over produced artifacts A and removed trees T;
# space O(A + T).
# @pre `uv`, `zip`, and `find` are available in `PATH`.
# @pre `pyproject.toml` declares `project.name` and `project.version`.
# @post `dist/` contains one sdist, one wheel, and one GNOME extension zip.
# @post No `build/`, `.pytest_cache/`, `*.egg-info`, or `__pycache__` artifact
# remains outside `dist/`.
# @return Exit status of the build.
# @retval 0 Every artifact was generated and verified, and the intermediate
# artifact cleanup plus the residual-artifact verification succeeded.
# @retval 1 Toolchain, build, artifact verification, cleanup, or residual
# artifact verification failed.
# @retval 2 Unexpected arguments.
# @satisfies PRJ-030
# @satisfies PRJ-031
# @satisfies PRJ-032
# @satisfies PRJ-033
# @satisfies PRJ-034
# @satisfies PRJ-056
# @satisfies PRJ-039
# @satisfies PRJ-040
# @satisfies PRJ-041
# @satisfies PRJ-047
# @satisfies PRJ-048
# @satisfies PRJ-049

set -Eeuo pipefail

# var SCRIPT_PATH {string} Absolute path of this script after symlink resolution.
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
# var SCRIPT_DIR {string} Absolute directory containing this script.
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
# var REPO_ROOT {string} Absolute repository root derived from the script path.
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
# var DIST_DIR {string} Canonical release-artifact destination directory.
DIST_DIR="$REPO_ROOT/dist"
# var BUILD_DIR {string} Python distribution build directory created by `python -m build`.
BUILD_DIR="$REPO_ROOT/build"
# var EXTENSION_STAGING_DIR {string} Intermediate staging directory used to archive extension members deterministically.
EXTENSION_STAGING_DIR="$BUILD_DIR/extension-archive-staging"
# var EXTENSION_MEMBER_TIMESTAMP {string} Fixed modification time applied to every staged extension member.
EXTENSION_MEMBER_TIMESTAMP="2000-01-01T00:00:00Z"
# var PYTEST_CACHE_DIR {string} Pytest cache directory created by build-side tooling.
PYTEST_CACHE_DIR="$REPO_ROOT/.pytest_cache"
# var SRC_DIR {string} Source tree scanned for intermediate artifacts.
SRC_DIR="$REPO_ROOT/src"
# var TESTS_DIR {string} Test tree scanned for intermediate artifacts.
TESTS_DIR="$REPO_ROOT/tests"
# var EXTENSION_SOURCE_DIR {string} GNOME extension source directory packaged as a release archive.
EXTENSION_SOURCE_DIR="$REPO_ROOT/src/aibar/aibar/gnome-extension/aibar@aibar.panel"
# var EXTENSION_ZIP_NAME {string} Release archive file name of the GNOME extension.
EXTENSION_ZIP_NAME="aibar@aibar.panel.shell-extension.zip"
# var BUILD_COMMAND_DISPLAY {string} Canonical build command mirrored from the release workflow.
BUILD_COMMAND_DISPLAY="uv run --with build --with setuptools --with wheel python -m build"
# var PROJECT_NAME {string} Distribution name resolved from `pyproject.toml`.
PROJECT_NAME=""
# var PROJECT_VERSION {string} Distribution version resolved from `pyproject.toml`.
PROJECT_VERSION=""
# var CURRENT_STAGE {string} Active build phase used by failure diagnostics.
CURRENT_STAGE="initialization"
# var REMOVED_PATHS {string[]} Absolute paths removed by this execution, in removal order.
REMOVED_PATHS=()

## @fn on_error
# @brief Report the failing phase and command of an unexpected failure.
# @details Registered as the ERR trap so `set -Eeuo pipefail` failures name the
# active phase and the exact failing command before the process exits. The ERR
# trap exits through the registered EXIT trap, so the intermediate-artifact
# cleanup still runs on this path.
# @return {void} Returns only when invoked with a zero exit status.
# @satisfies PRJ-033
# @satisfies PRJ-048
on_error() {
  local exit_code=$?
  if [ "$exit_code" -ne 0 ]; then
    printf 'ERROR: command failed (exit %d) during "%s": %s\n' \
      "$exit_code" "$CURRENT_STAGE" "$BASH_COMMAND" >&2
  fi
  exit "$exit_code"
}

## @fn cleanup_on_exit
# @brief Remove intermediate build artifacts on every process termination path.
# @details Registered as the EXIT trap so success, failure, help, argument
# errors, SIGINT, and SIGTERM all leave the repository free of intermediate
# artifacts while keeping the versioned `dist/` artifacts in place. The
# captured exit status is preserved; a cleanup failure or a residual-artifact
# finding turns a successful run into a failing run.
# @return {void} The function never returns.
# @satisfies PRJ-047
# @satisfies PRJ-048
# @satisfies PRJ-049
cleanup_on_exit() {
  local status=$?
  trap - ERR EXIT INT TERM
  set +e
  printf '\n==> [cleanup] removing intermediate build artifacts\n'
  if ! remove_intermediate_artifacts; then
    printf 'ERROR: intermediate build artifact cleanup failed.\n' >&2
    if [ "$status" -eq 0 ]; then
      status=1
    fi
  fi
  if ! verify_no_intermediate_artifacts; then
    if [ "$status" -eq 0 ]; then
      status=1
    fi
  fi
  exit "$status"
}

trap on_error ERR
trap cleanup_on_exit EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

## @fn usage
# @brief Print the script usage text to stdout.
# @return {void} No return value.
usage() {
  cat <<'EOF'
Usage: scripts/build.sh

Runs a clean build of every aibar release artifact into dist/:
  1. validates the required toolchain (uv, zip, find)
  2. removes every previously generated dist/ artifact for every version
  3. verifies that no generated release artifact survived that removal
  4. removes intermediate build artifacts (build/, .pytest_cache/,
     *.egg-info, __pycache__)
  5. builds the sdist and wheel (python -m build)
  6. packages the GNOME Shell extension zip reproducibly
  7. verifies artifact size, archive integrity, and required members
  8. removes the intermediate artifacts created by the build and verifies
     that none remains outside dist/

The versioned artifacts stay in dist/. Non-generated dist/ content is never
deleted. Intermediate artifacts are removed on success, failure, and signal
termination.
EOF
}

## @fn fail
# @brief Abort the build with one diagnostic message.
# @param message {string} Diagnostic text describing the failed requirement.
# @return {void} The function never returns.
# @satisfies PRJ-033
fail() {
  local message="$1"
  printf 'ERROR: %s\n' "$message" >&2
  exit 1
}

## @fn require_tool
# @brief Abort when one required executable is unavailable.
# @details Resolves the executable through `command -v`; a missing executable
# terminates the build before any artifact mutation.
# @param tool_name {string} Executable name validated in `PATH`.
# @return {void} Returns when the executable resolves.
# @satisfies PRJ-040
require_tool() {
  local tool_name="$1"
  if ! command -v "$tool_name" >/dev/null 2>&1; then
    fail "required executable not found in PATH: $tool_name"
  fi
  printf '  tool available: %s\n' "$tool_name"
}

## @fn validate_toolchain
# @brief Validate every executable required to produce release artifacts.
# @return {void} Returns when the toolchain is complete.
# @satisfies PRJ-040
validate_toolchain() {
  require_tool uv
  require_tool zip
  require_tool find
}

## @fn validate_project_layout
# @brief Validate the repository layout expected by the build.
# @details Requires `pyproject.toml`, the `aibar` package tree, and a GNOME
# extension source directory carrying `metadata.json`.
# @return {void} Returns when the layout is complete.
# @satisfies PRJ-030
validate_project_layout() {
  local required_path
  for required_path in \
    "$REPO_ROOT/pyproject.toml" \
    "$REPO_ROOT/src/aibar/aibar" \
    "$EXTENSION_SOURCE_DIR" \
    "$EXTENSION_SOURCE_DIR/metadata.json" \
    "$EXTENSION_SOURCE_DIR/extension.js"; do
    if [ ! -e "$required_path" ]; then
      fail "missing required build input: $required_path"
    fi
  done
  printf '  project layout: OK\n'
}

## @fn load_project_metadata
# @brief Resolve distribution name and version from `pyproject.toml`.
# @details Reads the PEP 621 metadata through the project environment so no
# duplicated version literal exists outside `pyproject.toml`. The resolved name
# scopes the generated sdist and wheel cleanup patterns.
# @return {void} Returns after populating `PROJECT_NAME` and `PROJECT_VERSION`.
# @satisfies PRJ-030
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
  printf '  project: %s %s\n' "$PROJECT_NAME" "$PROJECT_VERSION"
}

## @fn is_generated_dist_entry
# @brief Report whether one `dist/` entry is a build-generated artifact.
# @details Generated entries are the project sdist archive, project wheel
# archives, and the GNOME extension zip; every other entry is foreign. The
# sdist and wheel patterns carry no version literal, so entries produced by
# every previous build version match them.
# @param entry_path {string} Absolute or repository-relative `dist/` entry path.
# @return {int} 0 when the entry matches a generated artifact pattern.
# @satisfies PRJ-031
is_generated_dist_entry() {
  local entry_path="$1"
  local entry_name
  entry_name="$(basename "$entry_path")"
  case "$entry_name" in
    "${PROJECT_NAME}-"*.tar.gz) return 0 ;;
    "${PROJECT_NAME}-"*.whl) return 0 ;;
    "$EXTENSION_ZIP_NAME") return 0 ;;
    *) return 1 ;;
  esac
}

## @fn assert_dist_safe_to_clean
# @brief Abort when `dist/` holds content this script must not delete.
# @details Refuses to proceed when `dist/` contains entries outside the
# generated artifact patterns, so non-generated content is never destroyed.
# Tracked generated artifacts are permitted because the build replaces them.
# @return {void} Returns when `dist/` is absent or contains only generated artifacts.
# @satisfies PRJ-032
assert_dist_safe_to_clean() {
  if [ ! -d "$DIST_DIR" ]; then
    return 0
  fi
  local entry
  while IFS= read -r entry; do
    if [ -n "$entry" ] && ! is_generated_dist_entry "$entry"; then
      printf 'ERROR: dist/ contains a non-generated entry; refusing to delete it: %s\n' \
        "$entry" >&2
      exit 1
    fi
  done < <(find "$DIST_DIR" -mindepth 1 -maxdepth 1 -print)
  printf '  dist/ safety check: OK\n'
}

## @fn remove_generated_dist_artifacts
# @brief Remove every previously generated release artifact from `dist/`.
# @details Iterates `dist/` top-level regular files and deletes every entry
# accepted by `is_generated_dist_entry`, which matches the project sdist
# pattern, the project wheel pattern, and the GNOME extension zip name for any
# version number. Repeated builds therefore never accumulate obsolete outputs
# and never touch foreign files.
# @return {void} Returns after targeted removal.
# @satisfies PRJ-031
remove_generated_dist_artifacts() {
  if [ ! -d "$DIST_DIR" ]; then
    printf '  no previous dist/ directory to clean\n'
    return 0
  fi
  local entry
  while IFS= read -r entry; do
    if [ -n "$entry" ] && is_generated_dist_entry "$entry"; then
      rm -f -- "$entry"
      REMOVED_PATHS+=("$entry")
      printf '  removed previous artifact: %s\n' "$entry"
    fi
  done < <(find "$DIST_DIR" -mindepth 1 -maxdepth 1 -type f -print)
}

## @fn verify_no_generated_dist_artifacts
# @brief Verify that no generated release artifact survived the pre-build removal.
# @details Re-scans every top-level `dist/` file after
# `remove_generated_dist_artifacts` and emits one diagnostic per entry still
# accepted by `is_generated_dist_entry`. Foreign entries are ignored because
# they are preserved by contract, while any surviving generated artifact turns
# the bootstrap into a failing run instead of a clean-slate build.
# @return {int} 0 when `dist/` holds no generated release artifact.
# @satisfies PRJ-056
verify_no_generated_dist_artifacts() {
  if [ ! -d "$DIST_DIR" ]; then
    printf '  pre-existing release artifacts: none\n'
    return 0
  fi
  local entry
  local residual_found=0
  while IFS= read -r entry; do
    if [ -n "$entry" ] && is_generated_dist_entry "$entry"; then
      printf 'ERROR: pre-existing release artifact survived removal: %s\n' \
        "$entry" >&2
      residual_found=1
    fi
  done < <(find "$DIST_DIR" -mindepth 1 -maxdepth 1 -type f -print)
  if [ "$residual_found" -ne 0 ]; then
    return 1
  fi
  printf '  pre-existing release artifacts: removed\n'
  return 0
}

## @fn remove_intermediate_artifacts
# @brief Remove every intermediate artifact created by the build process.
# @details Deletes the `build/` tree, the `.pytest_cache/` tree, every
# `*.egg-info` directory under the repository root and `src/`, and every
# `__pycache__` tree under `src/` and `tests/`. Versioned `dist/` artifacts are
# never removed here. Emits one line per removed path plus a deterministic
# no-work line when nothing was present.
# @return {int} 0 when every removal succeeded.
# @satisfies PRJ-047
remove_intermediate_artifacts() {
  local start_index="${#REMOVED_PATHS[@]}"
  if [ -d "$BUILD_DIR" ]; then
    rm -rf -- "$BUILD_DIR"
    REMOVED_PATHS+=("$BUILD_DIR")
    printf '  removed: %s\n' "$BUILD_DIR"
  fi
  if [ -d "$PYTEST_CACHE_DIR" ]; then
    rm -rf -- "$PYTEST_CACHE_DIR"
    REMOVED_PATHS+=("$PYTEST_CACHE_DIR")
    printf '  removed: %s\n' "$PYTEST_CACHE_DIR"
  fi
  local -a egg_info_dirs=()
  local candidate
  while IFS= read -r candidate; do
    if [ -n "$candidate" ]; then
      egg_info_dirs+=("$candidate")
    fi
  done < <(find "$REPO_ROOT" -mindepth 1 -maxdepth 3 -type d \
    -name '*.egg-info' -not -path "$DIST_DIR/*" -print)
  local -a pycache_dirs=()
  local -a pycache_roots=()
  if [ -d "$SRC_DIR" ]; then
    pycache_roots+=("$SRC_DIR")
  fi
  if [ -d "$TESTS_DIR" ]; then
    pycache_roots+=("$TESTS_DIR")
  fi
  if [ "${#pycache_roots[@]}" -gt 0 ]; then
    while IFS= read -r candidate; do
      if [ -n "$candidate" ]; then
        pycache_dirs+=("$candidate")
      fi
    done < <(find "${pycache_roots[@]}" -type d -name '__pycache__' -prune -print)
  fi
  local -a removable_dirs=(
    "${egg_info_dirs[@]+"${egg_info_dirs[@]}"}"
    "${pycache_dirs[@]+"${pycache_dirs[@]}"}"
  )
  local removable_dir
  for removable_dir in "${removable_dirs[@]+"${removable_dirs[@]}"}"; do
    rm -rf -- "$removable_dir"
    REMOVED_PATHS+=("$removable_dir")
    printf '  removed: %s\n' "$removable_dir"
  done
  if [ "${#REMOVED_PATHS[@]}" -eq "$start_index" ]; then
    printf '  no intermediate build artifacts to remove\n'
  fi
  return 0
}

## @fn verify_no_intermediate_artifacts
# @brief Verify that no intermediate build artifact remains outside `dist/`.
# @details Probes the intermediate artifact locations (`build/`,
# `.pytest_cache/`, `*.egg-info` directories, and `__pycache__` trees under
# `src/` and `tests/`) and prints one diagnostic per residual path so a failed
# cleanup is never reported as a successful build.
# @return {int} 0 when no residual intermediate artifact exists.
# @satisfies PRJ-049
verify_no_intermediate_artifacts() {
  local residual_found=0
  if [ -e "$BUILD_DIR" ]; then
    printf 'ERROR: residual intermediate artifact: %s\n' "$BUILD_DIR" >&2
    residual_found=1
  fi
  if [ -e "$PYTEST_CACHE_DIR" ]; then
    printf 'ERROR: residual intermediate artifact: %s\n' "$PYTEST_CACHE_DIR" >&2
    residual_found=1
  fi
  local residual
  while IFS= read -r residual; do
    if [ -n "$residual" ]; then
      printf 'ERROR: residual intermediate artifact: %s\n' "$residual" >&2
      residual_found=1
    fi
  done < <(find "$REPO_ROOT" -mindepth 1 -maxdepth 3 -type d \
    -name '*.egg-info' -not -path "$DIST_DIR/*" -print)
  local -a residual_roots=()
  if [ -d "$SRC_DIR" ]; then
    residual_roots+=("$SRC_DIR")
  fi
  if [ -d "$TESTS_DIR" ]; then
    residual_roots+=("$TESTS_DIR")
  fi
  if [ "${#residual_roots[@]}" -gt 0 ]; then
    while IFS= read -r residual; do
      if [ -n "$residual" ]; then
        printf 'ERROR: residual intermediate artifact: %s\n' "$residual" >&2
        residual_found=1
      fi
    done < <(find "${residual_roots[@]}" -type d -name '__pycache__' -prune -print)
  fi
  if [ "$residual_found" -ne 0 ]; then
    return 1
  fi
  printf '  no intermediate build artifact remains outside dist/\n'
  return 0
}

## @fn build_python_distributions
# @brief Build the sdist and wheel with the canonical workload command.
# @details Mirrors `.github/workflows/release-pypi.yml` exactly while pinning
# dependency resolution to the tracked `uv.lock`.
# @return {void} Returns on build success.
# @satisfies PRJ-030
build_python_distributions() {
  printf '  build command: %s\n' "$BUILD_COMMAND_DISPLAY"
  (
    cd "$REPO_ROOT"
    uv run --locked --with build --with setuptools --with wheel python -m build
  )
}

## @fn build_extension_archive
# @brief Package the GNOME Shell extension into `dist/` byte-reproducibly.
# @details Copies every non-markdown extension source file into the intermediate
# staging directory `$EXTENSION_STAGING_DIR`, normalizes every staged member to
# the fixed modification time `$EXTENSION_MEMBER_TIMESTAMP` and the fixed
# permission `0644`, then adds the members to the archive in `LC_ALL=C` sorted
# order with `zip -X` under `TZ=UTC0`. Member order, member timestamps, member
# permissions, and archive extra fields are therefore independent of filesystem
# enumeration order, checkout mtimes, umask, and host timezone, so repeated
# builds from the same sources produce an identical archive. The markdown
# exclusion policy of the release workflow is preserved, and the staging
# directory lives inside `$BUILD_DIR`, so the existing intermediate-artifact
# cleanup removes it on success, failure, and signal termination.
# @pre `$EXTENSION_SOURCE_DIR` exists and carries at least one packageable file.
# @post `dist/$EXTENSION_ZIP_NAME` carries exactly the non-markdown source files
# as flat members and no directory entry.
# @return {void} Returns on archive success.
# @satisfies PRJ-030
# @satisfies PRJ-047
# @satisfies PRJ-049
build_extension_archive() {
  mkdir -p -- "$DIST_DIR"
  local archive_path="$DIST_DIR/$EXTENSION_ZIP_NAME"
  local staging_dir="$EXTENSION_STAGING_DIR"
  local -a member_names=()
  local source_path
  local relative_name
  local member_dir
  rm -rf -- "$staging_dir"
  mkdir -p -- "$staging_dir"
  while IFS= read -r source_path; do
    if [ -z "$source_path" ]; then
      continue
    fi
    relative_name="${source_path#"$EXTENSION_SOURCE_DIR"/}"
    case "$relative_name" in
      *.md) continue ;;
    esac
    if [[ "$relative_name" == */* ]]; then
      member_dir="$staging_dir/${relative_name%/*}"
    else
      member_dir="$staging_dir"
    fi
    mkdir -p -- "$member_dir"
    cp -- "$source_path" "$staging_dir/$relative_name"
    chmod 0644 -- "$staging_dir/$relative_name"
    member_names+=("$relative_name")
  done < <(find "$EXTENSION_SOURCE_DIR" -mindepth 1 -type f -print | LC_ALL=C sort)
  if [ "${#member_names[@]}" -eq 0 ]; then
    fail "GNOME extension source directory has no packageable file: $EXTENSION_SOURCE_DIR"
  fi
  find "$staging_dir" -exec touch -d "$EXTENSION_MEMBER_TIMESTAMP" -- {} +
  rm -f -- "$archive_path"
  (
    cd "$staging_dir"
    LC_ALL=C TZ=UTC0 zip -X -q "$archive_path" "${member_names[@]}"
  )
  printf '  extension archive: %s\n' "$EXTENSION_ZIP_NAME"
}

## @fn verify_artifacts
# @brief Verify presence, size, integrity, and required members of every artifact.
# @details Delegates to the project interpreter so archive validation uses the
# standard `tarfile` and `zipfile` modules without extra dependencies.
# @return {void} Returns when every artifact is valid.
# @satisfies PRJ-033
verify_artifacts() {
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
if not sdist_path.is_file():
    fail(f"missing sdist artifact: {sdist_path}")
elif sdist_path.stat().st_size == 0:
    fail(f"empty sdist artifact: {sdist_path}")
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
        report(f"sdist OK: {sdist_path.name} ({sdist_path.stat().st_size} bytes)")

wheel_paths = sorted(dist_dir.glob(f"{project_name}-{project_version}-*.whl"))
if len(wheel_paths) != 1:
    fail(
        "expected exactly one wheel artifact matching "
        f"{project_name}-{project_version}-*.whl, found {len(wheel_paths)}"
    )
else:
    wheel_path = wheel_paths[0]
    if wheel_path.stat().st_size == 0:
        fail(f"empty wheel artifact: {wheel_path}")
    else:
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
            report(f"wheel OK: {wheel_path.name} ({wheel_path.stat().st_size} bytes)")

extension_zip_path = dist_dir / extension_zip_name
if not extension_zip_path.is_file():
    fail(f"missing GNOME extension zip: {extension_zip_path}")
elif extension_zip_path.stat().st_size == 0:
    fail(f"empty GNOME extension zip: {extension_zip_path}")
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
        required = ("metadata.json", "extension.js", "stylesheet.css")
        missing = [name for name in required if name not in names]
        if missing:
            fail(f"extension zip missing required members: {', '.join(missing)}")
        report(
            f"GNOME extension zip OK: {extension_zip_path.name} "
            f"({extension_zip_path.stat().st_size} bytes)"
        )

for message in reported:
    print(f"  {message}")
for message in failures:
    print(f"ERROR: {message}", file=sys.stderr)
sys.exit(1 if failures else 0)
PY
}

## @fn print_artifact_summary
# @brief Print the absolute path and byte size of every artifact retained in `dist/`.
# @details Emits one deterministic line per artifact in sorted order. Each line
# carries the full artifact path (`DIST_DIR` joined with the file name; absolute
# because `DIST_DIR` derives from `readlink -f`) followed by its byte size, so the
# operator can verify the release payload without listing the directory.
# @return {void} No return value.
# @satisfies PRJ-034
print_artifact_summary() {
  printf '\n==> build succeeded: %s %s\n' "$PROJECT_NAME" "$PROJECT_VERSION"
  printf 'artifacts retained in %s:\n' "$DIST_DIR"
  find "$DIST_DIR" -mindepth 1 -maxdepth 1 -type f -printf '  %p (%s bytes)\n' | sort
}

# Argument parsing: this script accepts only the help flags.
for arg in "$@"; do
  case "$arg" in
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

CURRENT_STAGE="toolchain validation"
validate_toolchain

CURRENT_STAGE="project layout validation"
validate_project_layout

CURRENT_STAGE="project metadata resolution"
load_project_metadata

CURRENT_STAGE="pre-build cleanup"
assert_dist_safe_to_clean
remove_generated_dist_artifacts
verify_no_generated_dist_artifacts
remove_intermediate_artifacts

CURRENT_STAGE="python distribution build"
build_python_distributions

CURRENT_STAGE="gnome extension archive"
build_extension_archive

CURRENT_STAGE="artifact verification"
verify_artifacts

CURRENT_STAGE="post-build intermediate artifact cleanup"
remove_intermediate_artifacts

CURRENT_STAGE="intermediate artifact verification"
verify_no_intermediate_artifacts

CURRENT_STAGE="artifact summary"
print_artifact_summary

CURRENT_STAGE="completed"
