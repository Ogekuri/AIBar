"""
@file test_claude_token_refresh_script.py
@brief Source-level regression tests for claude_token_refresh.sh log-lifecycle behavior.
@details Verifies that do_refresh() truncates LOG_FILE before writing any log entries,
ensuring each 'once' invocation and each daemon refresh cycle produces a standalone log.
@satisfies TST-022, REQ-048
"""

import os
import re
import subprocess
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


def test_once_runs_setup_token_when_usage_reports_expired_oauth(
    tmp_path: Path,
) -> None:
    """
    @brief Verify once mode executes `claude setup-token` after auth-expired usage failure.
    @details Creates deterministic fake `claude` and `aibar` binaries on PATH. The first
    `claude /usage` call returns canonical auth-expired text; `claude setup-token` creates
    a marker file and the retry path becomes successful. Asserts marker creation and log
    evidence for setup-token execution.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies REQ-100
    @satisfies TST-043
    """
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(parents=True, exist_ok=True)
    marker_path = tmp_path / "claude_token_refreshed.marker"

    claude_stub = fake_bin / "claude"
    claude_stub.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'MARKER_PATH="${MARKER_PATH:?}"',
                'if [[ "${1:-}" == "/usage" ]]; then',
                '  if [[ -f "$MARKER_PATH" ]]; then',
                '    echo "usage-ok"',
                "    exit 0",
                "  fi",
                '  echo "Invalid or expired OAuth token"',
                "  exit 1",
                "fi",
                'if [[ "${1:-}" == "setup-token" ]]; then',
                '  : >"$MARKER_PATH"',
                '  echo "setup-ok"',
                "  exit 0",
                "fi",
                'echo "unexpected-claude-args: $*"',
                "exit 2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    claude_stub.chmod(0o755)

    aibar_stub = fake_bin / "aibar"
    aibar_stub.write_text(
        "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                'if [[ "${1:-}" == "login" && "${2:-}" == "--provider" && "${3:-}" == "claude" ]]; then',
                "  exit 0",
                "fi",
                'echo "unexpected-aibar-args: $*"',
                "exit 2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    aibar_stub.chmod(0o755)

    env = {
        "HOME": str(tmp_path),
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "XDG_CONFIG_HOME": str(tmp_path / ".config"),
        "MARKER_PATH": str(marker_path),
    }
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), "once"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert marker_path.exists(), "Expected once mode to run `claude setup-token`."

    log_path = tmp_path / ".config" / "aibar" / "claude_token_refresh.log"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "Running: claude setup-token" in content
