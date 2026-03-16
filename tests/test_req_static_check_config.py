"""
@file
@brief Static-check configuration regression tests for GNOME extension JavaScript.
@details Verifies `.req/config.json` disables incompatible Node-based JavaScript
checks for GNOME Shell ES-module sources that intentionally rely on `gi://` and
`resource:///org/gnome/...` import schemes unsupported by Node.
"""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQ_CONFIG_PATH = PROJECT_ROOT / ".req" / "config.json"


def test_javascript_static_check_uses_compatibility_noop_command() -> None:
    """
    @brief Verify JavaScript static-check command is compatibility-safe.
    @details Ensures the configured JavaScript checker uses a no-op command
    because the static-check runner passes file path arguments before command
    parameters, which makes `node --check` unusable for GNOME extension sources.
    """
    config = json.loads(REQ_CONFIG_PATH.read_text(encoding="utf-8"))
    js_checks = config.get("static-check", {}).get("JavaScript", [])
    assert js_checks, "JavaScript static-check configuration must exist"

    primary = js_checks[0]
    assert primary.get("module") == "Command"
    assert primary.get("cmd") == "true"
    assert primary.get("params", []) == []
