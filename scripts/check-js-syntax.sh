#!/usr/bin/env bash
##
# @file check-js-syntax.sh
# @brief Syntax-only JavaScript checker for GJS (GNOME JavaScript) source files.
# @details Preprocesses GNOME Shell extension JS files before syntax validation with Node.js.
#   Replaces gi:// and resource:// import statements (GJS-only URL schemes) with equivalent
#   const stub declarations so that Node.js syntax checking succeeds without requiring the
#   GNOME Shell runtime. The original file is never modified.
# @param $1 Path to the .js file to syntax-check.
# @retval 0 Syntax is valid.
# @retval 1 File argument missing, sed preprocessing failed, or syntax error detected.
# @note GJS supports gi:// (GObject introspection) and resource:// (GNOME Shell UI modules)
#   as native import schemes. Node.js ESM loader rejects these with ERR_UNSUPPORTED_ESM_URL_SCHEME.
#   This script normalises them to const stubs before invoking `node --check`.
##

set -euo pipefail

if [ -z "${1:-}" ]; then
    printf '%s\n' "Usage: $0 <file.js>" >&2
    exit 1
fi

FILE="$1"
TMP=$(mktemp /tmp/check-js-syntax-XXXXXX.js)
trap 'rm -f "$TMP"' EXIT

sed \
    -e 's|^import \* as \([A-Za-z][A-Za-z0-9_]*\) from '"'"'gi://[^'"'"']*'"'"';|const \1 = {};|' \
    -e 's|^import \* as \([A-Za-z][A-Za-z0-9_]*\) from '"'"'resource://[^'"'"']*'"'"';|const \1 = {};|' \
    -e 's|^import { \([^}]*\) } from '"'"'gi://[^'"'"']*'"'"';|const \1 = undefined;|' \
    -e 's|^import { \([^}]*\) } from '"'"'resource://[^'"'"']*'"'"';|const \1 = undefined;|' \
    -e 's|^import \([A-Za-z][A-Za-z0-9_]*\) from '"'"'gi://[^'"'"']*'"'"';|const \1 = undefined;|' \
    -e 's|^import \([A-Za-z][A-Za-z0-9_]*\) from '"'"'resource://[^'"'"']*'"'"';|const \1 = undefined;|' \
    "$FILE" > "$TMP"

node --check "$TMP"
