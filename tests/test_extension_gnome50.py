"""
@file
@brief GNOME 50 metadata and lifecycle contract regressions.
@details HDT Generator. Level 0 validates metadata/API declarations; Level 1
executes real extension methods with isolated Node GI and Shell substitutes.
No live GNOME session or provider network request is started.
@satisfies TST-075, REQ-183, REQ-184, REQ-187
"""

import json
from pathlib import Path
import subprocess


## @brief Repository root for immutable test input resolution.
ROOT = Path(__file__).resolve().parents[1]
## @brief Packaged GNOME extension directory.
EXTENSION = ROOT / "src/aibar/aibar/gnome-extension/aibar@aibar.panel"


def test_metadata_declares_gnome50_major() -> None:
    """
    @brief Verify GNOME major-version matching for all 50.x maintenance releases.
    @details Level 0; parses package metadata without user state; O(N) bytes.
    @return {None} Assertions complete.
    @satisfies REQ-184, TST-075
    """
    metadata = json.loads((EXTENSION / "metadata.json").read_text())
    assert metadata["shell-version"] == ["50"]
    assert metadata["uuid"] == "aibar@aibar.panel"


def test_ui_uses_gnome50_orientation_and_child_contracts() -> None:
    """
    @brief Verify widget declarations use supported GNOME 50 APIs.
    @details Level 0; O(N) source scan; no runtime state mutation.
    @return {None} Assertions complete.
    @satisfies REQ-187, TST-075
    """
    source = (EXTENSION / "extension.js").read_text()
    assert "vertical:" not in source
    assert ".add_actor(" not in source
    assert "orientation: Clutter.Orientation.VERTICAL" in source
    assert "orientation: Clutter.Orientation.HORIZONTAL" in source


def test_gnome50_lifecycle_contract() -> None:
    """
    @brief Execute initialization, provider cards, refresh and teardown contracts.
    @details Level 1; Node substitutes GI/Shell, scheduling and CLI boundaries;
    O(N) fixture execution; requires Node and performs no network or desktop I/O.
    @return {None} Assertions complete.
    @satisfies REQ-183, REQ-187, TST-075
    """
    result = subprocess.run(
        ["node", str(ROOT / "tests/fixtures/gnome50-runtime.cjs"),
         str(EXTENSION / "extension.js")],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "disable PASS" in result.stdout
