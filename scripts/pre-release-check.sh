#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# @file
# @brief Pre-release verification pipeline for the aibar repository.
# @details Executes the checks required before an official release, in
# order: (1) clean git working-tree gate (skippable with `--allow-dirty`),
# (2) locked dependency synchronization via `uv sync --locked`,
# (3) full pytest suite via `uv run pytest`, (4) sdist+wheel build into
# `dist/` mirroring `.github/workflows/release-pypi.yml`, and (5) built
# artifact verification. An unconditional EXIT trap removes the pipeline
# artifacts (`dist/`, `.pytest_cache/`, `__pycache__` trees under `src/`
# and `tests/`) so the repository is left clean whether the pipeline
# succeeds or fails. Every stage prints one labeled progress header
# and the pipeline aborts at the first failing stage with a non-zero
# exit status.
# @satisfies PRJ-020
# @satisfies PRJ-021
# @satisfies PRJ-022
# @satisfies PRJ-023
# @satisfies PRJ-024
# @satisfies PRJ-025

set -euo pipefail

# var ALLOW_DIRTY {bool} When true, skip the clean working-tree gate (PRJ-021 opt-out).
ALLOW_DIRTY=false

# var STAGE_INDEX {int} Zero-based-then-incremented counter of executed pipeline stages.
STAGE_INDEX=0

# var STAGE_TOTAL {int} Total number of pipeline stages executed by this script.
STAGE_TOTAL=5

## @fn usage
# @brief Print the script usage text to stdout.
# @return {void} No return value.
usage() {
  cat <<'EOF'
Usage: scripts/pre-release-check.sh [--allow-dirty]

Runs the pre-release verification pipeline:
  1. clean git working-tree gate (skipped only with --allow-dirty)
  2. dependency sync locked to uv.lock
  3. full pytest unit-test suite
  4. sdist and wheel build into dist/
  5. built-artifact verification

Aborts at the first failing stage with a non-zero exit status.
EOF
}

## @fn check_clean_working_tree
# @brief Abort when the git working tree contains uncommitted changes.
# @details Runs `git status --porcelain`; any output means uncommitted or
# untracked content, so the script prints a diagnostic and exits non-zero
# before executing any build or test stage. The check is skipped only
# when the `--allow-dirty` flag was passed.
# @return {void} Returns on a clean tree; exits 1 on a dirty tree.
# @satisfies PRJ-021
check_clean_working_tree() {
  if [ "$ALLOW_DIRTY" = "true" ]; then
    printf '  skipped: --allow-dirty flag active\n'
    return 0
  fi
  local status_output
  status_output="$(git status --porcelain)"
  if [ -n "$status_output" ]; then
    printf 'ERROR: git working tree is not clean; commit or stash before a release.\n' >&2
    printf '%s\n' "$status_output" >&2
    exit 1
  fi
  printf '  git working tree is clean\n'
}

## @fn build_distribution
# @brief Build sdist and wheel into `dist/` mirroring the release workflow.
# @details Removes stale `dist/` content first so artifact verification
# cannot observe leftovers from previous builds, then executes the same
# build command used by `.github/workflows/release-pypi.yml`:
# `uv run --with build --with setuptools --with wheel python -m build`.
# @return {void} Returns on successful build; aborts via `set -e` otherwise.
# @satisfies PRJ-024
build_distribution() {
  rm -rf dist
  uv run --with build --with setuptools --with wheel python -m build
}

## @fn require_dist_artifacts
# @brief Verify that one sdist and one wheel exist under `dist/`.
# @details Scans `dist/` for `*.tar.gz` and `*.whl` entries and prints
# every discovered artifact. Missing sdist or wheel triggers an explicit
# error and a non-zero exit.
# @return {void} Returns when both artifact kinds are present; exits 1 otherwise.
# @satisfies PRJ-024
require_dist_artifacts() {
  local found_sdist=false
  local found_wheel=false
  local artifact
  for artifact in dist/*.tar.gz; do
    if [ -f "$artifact" ]; then
      found_sdist=true
      printf '  artifact: %s\n' "$artifact"
    fi
  done
  for artifact in dist/*.whl; do
    if [ -f "$artifact" ]; then
      found_wheel=true
      printf '  artifact: %s\n' "$artifact"
    fi
  done
  if [ "$found_sdist" = "false" ] || [ "$found_wheel" = "false" ]; then
    printf 'ERROR: expected one sdist (*.tar.gz) and one wheel (*.whl) under dist/.\n' >&2
    exit 1
  fi
}

## @fn run_stage
# @brief Execute one labeled pipeline stage via the provided command.
# @details Increments the executed-stage counter, prints a
# `[<executed>/<total>] <label>` progress header, then executes the
# remaining arguments as one command. `set -euo pipefail` aborts the
# whole pipeline with the failing command exit status on failure.
# @param stage_label {string} Human-readable stage label for the header.
# @param ... {string[]} Command argv to execute for this stage.
# @return {void} Returns only when the stage command succeeds.
# @satisfies PRJ-022
run_stage() {
  local stage_label="$1"
  shift
  STAGE_INDEX=$((STAGE_INDEX + 1))
  printf '\n==> [%d/%d] %s\n' "$STAGE_INDEX" "$STAGE_TOTAL" "$stage_label"
  "$@"
}

## @fn cleanup_pipeline_artifacts
# @brief Remove build and test artifacts created by the pipeline on exit.
# @details Registered as an EXIT trap so cleanup runs when the script
# exits, whether the pipeline succeeded, failed, or exited early (help,
# unknown arguments, dirty-tree gate). Removes `dist/`, `.pytest_cache/`,
# and every `__pycache__` tree under `src/` and `tests/`. Failures inside
# the cleanup never alter the pipeline exit status. Time complexity O(T)
# over removed trees T.
# @return {void} No return value.
# @satisfies PRJ-025
cleanup_pipeline_artifacts() {
  set +e
  rm -rf -- dist .pytest_cache
  find src tests -type d -name __pycache__ -prune -exec rm -rf -- '{}' + 2>/dev/null
  printf '  removed pipeline artifacts (dist/, .pytest_cache/, __pycache__ trees)\n'
  set -e
}

trap cleanup_pipeline_artifacts EXIT

# Argument parsing: only the documented flags are accepted.
for arg in "$@"; do
  case "$arg" in
    --allow-dirty) ALLOW_DIRTY=true ;;
    -h | --help) usage ; exit 0 ;;
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
