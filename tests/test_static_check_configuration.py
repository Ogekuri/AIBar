"""
@file
@brief Regression test for static-check configuration reliability.
@details Verifies repository-level Pyright configuration exists and encodes
first-party source path resolution required by `req --here --static-check`.
"""

import json
from pathlib import Path


PYRIGHT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "pyrightconfig.json"


def test_pyright_config_declares_first_party_source_path() -> None:
    """
    @brief Verify Pyright configuration exists with first-party import paths.
    @details Ensures `pyrightconfig.json` is present, `src/aibar` is included in
    analysis roots, and `extraPaths` includes `src/aibar` so `aibar.*` imports in
    `src/` and `tests/` resolve during static-check execution.
    @return {None} Function return value.
    """
    assert PYRIGHT_CONFIG_PATH.exists(), "pyrightconfig.json must exist"
    payload = json.loads(PYRIGHT_CONFIG_PATH.read_text(encoding="utf-8"))

    include_entries = payload.get("include", [])
    assert isinstance(include_entries, list)
    assert "src/aibar" in include_entries
    assert "tests" in include_entries

    extra_paths = payload.get("extraPaths", [])
    assert isinstance(extra_paths, list)
    assert "src/aibar" in extra_paths
