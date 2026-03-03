"""
@file
@brief Documentation inventory regression tests.
@details Validates machine-readable references coverage and per-symbol line-range evidence.
"""

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_PATH = PROJECT_ROOT / "docs" / "REFERENCES.md"


def _source_files_with_symbols() -> list[str]:
    """
    @brief Collect source files expected in documentation inventory.
    @returns list[str] Relative POSIX file paths for Python, JavaScript, and shell source files under src/.
    """
    extensions = {".py", ".js", ".sh"}
    files: list[str] = []
    for file_path in (PROJECT_ROOT / "src").rglob("*"):
        if file_path.is_file() and file_path.suffix in extensions:
            files.append(file_path.relative_to(PROJECT_ROOT).as_posix())
    return sorted(files)


def test_references_include_all_source_files() -> None:
    """
    @brief Verify references index includes every tracked source file with symbols.
    """
    references = REFERENCES_PATH.read_text(encoding="utf-8")
    documented_paths = set(
        match.group(1)
        for match in re.finditer(r"^> Path: `([^`]+)`$", references, flags=re.MULTILINE)
    )

    expected_paths = set(_source_files_with_symbols())
    missing = sorted(expected_paths - documented_paths)
    assert not missing, f"Missing file sections in docs/REFERENCES.md: {missing}"


def test_references_symbol_rows_have_line_ranges() -> None:
    """
    @brief Verify each symbol row contains concrete line-range evidence.
    """
    references = REFERENCES_PATH.read_text(encoding="utf-8")
    symbol_rows = [line for line in references.splitlines() if line.startswith("|`")]
    assert symbol_rows, "No symbol rows found in docs/REFERENCES.md."

    invalid_rows: list[str] = []
    for row in symbol_rows:
        columns = [column.strip() for column in row.strip("|").split("|")]
        if len(columns) < 4:
            invalid_rows.append(row)
            continue
        line_span = columns[3]
        if not re.fullmatch(r"\d+(?:-\d+)?", line_span):
            invalid_rows.append(row)

    assert not invalid_rows, f"Invalid symbol line ranges in docs/REFERENCES.md: {invalid_rows}"
