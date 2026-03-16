"""
@file
@brief Static-check configuration regression tests for GNOME extension JavaScript.
@details Verifies `.req/config.json` configures a GJS-compatible JavaScript syntax checker
(`scripts/check-js-syntax.sh`) that preprocesses `gi://` and `resource://` import schemes
before delegating to `node --check`, enabling syntax validation of GNOME Shell ES-module
sources without requiring the GNOME Shell runtime.
"""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQ_CONFIG_PATH = PROJECT_ROOT / ".req" / "config.json"


def test_javascript_static_check_uses_gjs_compatible_script() -> None:
    """
    @brief Verify JavaScript static-check primary command is the GJS-compatible wrapper script.
    @details Ensures the first configured JavaScript checker uses `scripts/check-js-syntax.sh`,
    a preprocessing wrapper that replaces `gi://` and `resource://` imports with const stubs
    before running `node --check`, resolving Node.js `ERR_UNSUPPORTED_ESM_URL_SCHEME` errors
    for GNOME Shell extension sources.
    @return {None} Function return value.
    """
    config = json.loads(REQ_CONFIG_PATH.read_text(encoding="utf-8"))
    js_checks = config.get("static-check", {}).get("JavaScript", [])
    assert js_checks, "JavaScript static-check configuration must exist"

    primary = js_checks[0]
    assert primary.get("module") == "Command"
    assert primary.get("cmd") == "scripts/check-js-syntax.sh"
