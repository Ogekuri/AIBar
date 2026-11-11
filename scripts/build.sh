#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# @file
# @brief Canonical release-artifact generator for the aibar repository.
# @details Resolves the repository root from its own path, validates the
# required toolchain, removes only previously generated artifacts from
# `dist/`, executes the canonical `python -m build` invocation used by
# `.github/workflows/release-pypi.yml`, creates the GNOME Shell extension
# zip, validates every produced artifact (non-empty size, archive integrity,
# required member entries), and retains all artifacts in `dist/` while
# printing a summary. Non-generated and tracked content inside `dist/` is
# never deleted; a failed build never reports success.
# Time complexity O(A) over produced artifacts A; space O(1) beyond artifact bytes.
# @pre `uv`, `zip`, and `find` are available in `PATH`.
# @pre `pyproject.toml` declares `project.name` and `project.version`.
# @post `dist/` contains one sdist, one wheel, and one GNOME extension zip.
# @return Exit status of the build.
# @retval 0 Every artifact was generated and verified.
# @retval 1 Toolchain, build, or artifact verification failed.
# @retval 2 Unexpected arguments.
# @satisfies PRJ-030
# @satisfies PRJ-031
# @satisfies PRJ-032
# @satisfies PRJ-033
# @satisfies PRJ-034
# @satisfies PRJ-039
# @satisfies PRJ-040

set -Eeuo pipefail

# var SCRIPT_PATH {string} Absolute path of this script after symlink resolution.
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
# var SCRIPT_DIR {string} Absolute directory containing this script.
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
# var REPO_ROOT {string} Absolute repository root derived from the script path.
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
# var DIST_DIR {string} Canonical release-artifact destination directory.
DIST_DIR="$REPO_ROOT/dist"
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

## @fn on_error
# @brief Report the failing phase and command of an unexpected failure.
# @details Registered as the ERR trap so `set -Eeuo pipefail` failures name the
# active phase and the exact failing command before the process exits.
# @return {void} Returns only when invoked with a zero exit status.
# @satisfies PRJ-033
on_error() {
  local exit_code=$?
  if [ "$exit_code" -ne 0 ]; then
    printf 'ERROR: command failed (exit %d) during "%s": %s\n' \
      "$exit_code" "$CURRENT_STAGE" "$BASH_COMMAND" >&2
  fi
  exit "$exit_code"
}

trap on_error ERR

## @fn usage
# @brief Print the script usage text to stdout.
# @return {void} No return value.
usage() {
  cat <<'EOF'
Usage: scripts/build.sh

Builds every aibar release artifact into dist/:
  1. validates the required toolchain (uv, zip, find)
  2. removes previously generated artifacts from dist/
  3. builds the sdist and wheel (python -m build)
  4. packages the GNOME Shell extension zip
  5. verifies artifact size, archive integrity, and required members

The generated artifacts stay in dist/ after a successful build.
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
# duplicated version literal exists outside `pyproject.toml`.
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
# archives, and the GNOME extension zip; every other entry is foreign.
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
# @details Refuses to proceed when `dist/` contains tracked files or untracked
# entries outside the generated artifact patterns, so user and versioned
# content is never destroyed.
# @return {void} Returns when `dist/` is absent or contains only generated artifacts.
# @satisfies PRJ-032
assert_dist_safe_to_clean() {
  if [ ! -d "$DIST_DIR" ]; then
    return 0
  fi
  local tracked_entries
  tracked_entries="$(git -C "$REPO_ROOT" ls-files -- dist)"
  if [ -n "$tracked_entries" ]; then
    printf 'ERROR: dist/ contains tracked files; refusing to delete them.\n' >&2
    printf '%s\n' "$tracked_entries" >&2
    exit 1
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

## @fn remove_stale_generated_artifacts
# @brief Remove previously generated release artifacts from `dist/`.
# @details Deletes only files matching the project sdist pattern, the project
# wheel pattern, or the GNOME extension zip name, so repeated builds never
# accumulate obsolete outputs and never touch foreign files.
# @return {void} Returns after targeted removal.
# @satisfies PRJ-031
remove_stale_generated_artifacts() {
  if [ ! -d "$DIST_DIR" ]; then
    printf '  no previous dist/ directory to clean\n'
    return 0
  fi
  find "$DIST_DIR" -mindepth 1 -maxdepth 1 -type f \
    \( -name "${PROJECT_NAME}-*.tar.gz" -o -name "${PROJECT_NAME}-*.whl" \
    -o -name "$EXTENSION_ZIP_NAME" \) -delete
  printf '  removed previous generated artifacts from dist/\n'
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
# @brief Package the GNOME Shell extension into `dist/`.
# @details Archives the extension source directory content excluding markdown
# notes, using the same exclusion policy as the release workflow.
# @return {void} Returns on archive success.
# @satisfies PRJ-030
build_extension_archive() {
  mkdir -p "$DIST_DIR"
  (
    cd "$EXTENSION_SOURCE_DIR"
    zip -r -q "$DIST_DIR/$EXTENSION_ZIP_NAME" . -x "*.md"
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
# @brief Print the produced artifact inventory retained in `dist/`.
# @details Emits one deterministic line per artifact with its byte size so the
# operator can verify the release payload without listing the directory.
# @return {void} No return value.
# @satisfies PRJ-034
print_artifact_summary() {
  printf '\n==> build succeeded: %s %s\n' "$PROJECT_NAME" "$PROJECT_VERSION"
  printf 'artifacts retained in %s:\n' "$DIST_DIR"
  find "$DIST_DIR" -mindepth 1 -maxdepth 1 -type f -printf '  %f (%s bytes)\n' | sort
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

CURRENT_STAGE="dist directory preparation"
assert_dist_safe_to_clean
remove_stale_generated_artifacts

CURRENT_STAGE="python distribution build"
build_python_distributions

CURRENT_STAGE="gnome extension archive"
build_extension_archive

CURRENT_STAGE="artifact verification"
verify_artifacts

CURRENT_STAGE="artifact summary"
print_artifact_summary

CURRENT_STAGE="completed"
