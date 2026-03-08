"""
@file test_claude_token_refresh_script.py
@brief Source-level regression tests for claude_token_refresh.sh log-lifecycle behavior.
@details Verifies that do_refresh() truncates LOG_FILE before writing any log entries,
ensuring each 'once' invocation and each daemon refresh cycle produces a standalone log.
@satisfies TST-022, REQ-048
"""

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "claude_token_refresh.sh"


def _extract_do_refresh_body(source: str) -> str:
    """
    @brief Extract the body of the do_refresh() function from the script source.
    @param source Full text content of claude_token_refresh.sh.
    @return String containing the lines inside do_refresh() up to the closing brace.
    @details Locates 'do_refresh() {' and collects lines until the matching '}' at
    column 0 (the function end delimiter). Returns only the inner body lines.
    """
    lines = source.splitlines()
    in_func = False
    body_lines: list[str] = []
    for line in lines:
        if re.match(r"^do_refresh\(\)\s*\{", line):
            in_func = True
            continue
        if in_func:
            if line == "}":
                break
            body_lines.append(line)
    return "\n".join(body_lines)


def test_do_refresh_truncates_log_file_before_first_log_call() -> None:
    """
    @brief Verify do_refresh() truncates LOG_FILE before writing any log entries.
    @details Asserts that the truncation statement '> "$LOG_FILE"' appears in the body
    of do_refresh() before any 'log ' invocation, satisfying REQ-048 which mandates
    each once invocation and daemon cycle to produce a standalone log.
    @satisfies TST-022, REQ-048
    """
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    body = _extract_do_refresh_body(source)
    assert body, "do_refresh() body not found in script"

    lines = body.splitlines()
    truncation_index: int | None = None
    first_log_index: int | None = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if truncation_index is None and re.match(r'^>\s+"\$LOG_FILE"', stripped):
            truncation_index = i
        if first_log_index is None and stripped.startswith("log "):
            first_log_index = i

    assert truncation_index is not None, (
        'do_refresh() does not contain log truncation: > "$LOG_FILE"'
    )
    assert first_log_index is not None, "do_refresh() does not contain any log() call"
    assert truncation_index < first_log_index, (
        f"Log truncation (line {truncation_index}) must appear before first log() "
        f"call (line {first_log_index}) in do_refresh()"
    )


def test_script_log_file_variable_is_defined() -> None:
    """
    @brief Verify script defines LOG_FILE variable pointing to the expected log path.
    @satisfies REQ-048
    """
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert 'LOG_FILE="$CONFIG_DIR/claude_token_refresh.log"' in source
