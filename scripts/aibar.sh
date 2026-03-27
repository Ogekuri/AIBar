#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# VERSION: 0.21.0
# AUTHORS: Ogekuri
#
# @file
# @brief Repository launcher for AIBar CLI using Astral uv runtime orchestration.
# @details Resolves repository root from script path and executes
# `uv run --project <root> python -m aibar.cli` while forwarding all CLI arguments.
# MUST NOT bootstrap or mutate any virtual environment.
# @satisfies REQ-086

set -euo pipefail

full_path="$(readlink -f "$0")"
script_dir="$(dirname "$full_path")"
project_root="$(dirname "$script_dir")"

cd "$project_root"

exec uv run --project "$project_root" python -m aibar.cli "$@"
