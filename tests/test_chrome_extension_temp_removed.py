"""
@file
@brief Chrome extension temp-fixture directory removal assertion.
@details Ensures implementation output no longer contains the temporary analysis
folder under src/aibar/chrome-extension/temp.
@satisfies TST-018
@satisfies DES-010
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMP_DIR = PROJECT_ROOT / "src" / "aibar" / "chrome-extension" / "temp"


def test_chrome_extension_temp_directory_is_absent() -> None:
    """
    @brief Verify chrome-extension temp directory is not present.
    @satisfies TST-018
    """
    assert not TEMP_DIR.exists()
