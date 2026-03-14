"""
@file
@brief GNOME contract-documentation location regression tests.
@details Verifies GNOME contract documentation remains canonical in `docs/`
and that deprecated source-tree plan artifact `src/aibar/plans/Gnome.plan.md`
is absent.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GNOME_PLAN_PATH = PROJECT_ROOT / "src" / "aibar" / "plans" / "Gnome.plan.md"
REQUIREMENTS_PATH = PROJECT_ROOT / "docs" / "REQUIREMENTS.md"
WORKFLOW_PATH = PROJECT_ROOT / "docs" / "WORKFLOW.md"
REFERENCES_PATH = PROJECT_ROOT / "docs" / "REFERENCES.md"


def test_gnome_contract_docs_are_canonical_and_source_plan_is_absent() -> None:
    """
    @brief Verify GNOME contract docs are canonical and source plan file is absent.
    @details Asserts `PRJ-011` is declared in requirements, validates canonical
    documentation paths under `docs/`, and enforces absence of deprecated source
    plan artifact under `src/aibar/plans/`.
    @return {None} Function return value.
    @satisfies PRJ-011
    """
    requirements_source = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    assert "PRJ-011" in requirements_source
    assert "src/aibar/plans/Gnome.plan.md" in requirements_source
    assert REQUIREMENTS_PATH.exists()
    assert WORKFLOW_PATH.exists()
    assert REFERENCES_PATH.exists()
    assert not GNOME_PLAN_PATH.exists()
