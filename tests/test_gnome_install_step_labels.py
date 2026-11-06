"""
@file
@brief Step-total consistency regressions for `aibar gnome-install` output.
@details Source-level Level 0 assertions verifying the installer step labels
use one consistent five-step total, so colored status output cannot mix a
legacy `[1/4]` label with the `[2/5]`-`[5/5]` sequence.
@satisfies REQ-028
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI_SOURCE_PATH = PROJECT_ROOT / "src" / "aibar" / "aibar" / "cli.py"


def test_gnome_install_has_no_legacy_four_step_label() -> None:
    """
    @brief Verify gnome_install emits no legacy `[1/4]` step label.
    @details Source-level assertion; the five-step installer flow must render
    every step with the same `/5` total so status output stays coherent.
    expected_output: source contains no `[1/4]` literal.
    @satisfies REQ-028
    """
    source = CLI_SOURCE_PATH.read_text(encoding="utf-8")
    assert "[1/4]" not in source


def test_gnome_install_first_step_uses_five_step_total() -> None:
    """
    @brief Verify gnome_install first step renders `[1/5]`.
    @details Source-level assertion pairing with the `[2/5]`-`[5/5]` labels.
    expected_output: source contains the `[1/5]` literal.
    @satisfies REQ-028
    """
    source = CLI_SOURCE_PATH.read_text(encoding="utf-8")
    assert "[1/5]" in source
