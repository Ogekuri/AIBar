"""
@file
@brief Launcher regression tests for uv-only execution path.
@details Verifies `scripts/aibar.sh` delegates runtime execution to `uv run`
without creating or activating local/system virtual environments.
@satisfies REQ-086
@satisfies TST-039
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = PROJECT_ROOT / "scripts" / "aibar.sh"


def test_launcher_executes_aibar_cli_via_uv_run() -> None:
    """
    @brief Verify launcher executes CLI through `uv run`.
    @return {None} Function return value.
    @satisfies REQ-086
    @satisfies TST-039
    """
    source = LAUNCHER_PATH.read_text(encoding="utf-8")
    assert 'exec uv run --project "$project_root" python -m aibar.cli "$@"' in source


def test_launcher_has_no_virtualenv_bootstrap_or_requirements_install() -> None:
    """
    @brief Verify launcher source excludes legacy virtualenv bootstrap commands.
    @return {None} Function return value.
    @satisfies REQ-086
    @satisfies TST-039
    """
    source = LAUNCHER_PATH.read_text(encoding="utf-8")
    assert "virtualenv" not in source
    assert ".venv" not in source
    assert "pip install -r" not in source
    assert "requirements.txt" not in source
    assert "source " not in source
