"""
@file
@brief Chrome extension API reference documentation assertions.
@details Verifies `guidelines/Google_Extension_API_Reference.md` exists and
documents the primary API, debug APIs, configuration routes, and disabled-debug
error semantics required by runtime behavior.
@satisfies TST-024
@satisfies REQ-054
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_REFERENCE_PATH = PROJECT_ROOT / "guidelines" / "Google_Extension_API_Reference.md"


def test_api_reference_file_exists_and_covers_required_routes() -> None:
    """
    @brief Verify API reference includes all mandatory runtime message routes.
    @satisfies TST-024
    @satisfies REQ-054
    """
    assert API_REFERENCE_PATH.is_file()
    source = API_REFERENCE_PATH.read_text(encoding="utf-8")
    assert "api.main.snapshot" in source
    assert "debug.api.describe" in source
    assert "debug.api.execute" in source
    assert "providers.pages.get" in source
    assert "config.debug_api.get" in source
    assert "config.debug_api.set" in source


def test_api_reference_documents_disabled_debug_error_semantics() -> None:
    """
    @brief Verify API reference documents deterministic disabled-debug failures.
    @satisfies TST-024
    @satisfies REQ-051
    """
    source = API_REFERENCE_PATH.read_text(encoding="utf-8")
    assert "DEBUG_API_DISABLED" in source
    assert "Debug API disabled: enable it in popup configuration for this runtime session." in source
