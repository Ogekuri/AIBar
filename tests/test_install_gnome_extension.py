"""
@file
@brief Unit tests for scripts/install-gnome-extension.sh.
@details Validates executable permissions, bash syntax, git root resolution,
source directory validation, and non-zero exit on missing source.
@satisfies TST-009, REQ-025, REQ-027, REQ-030
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "install-gnome-extension.sh"
EXT_SRC_DIR = PROJECT_ROOT / "src" / "aibar" / "extension" / "aibar@aibar.panel"


class TestInstallGnomeExtensionAtomic:
    """
    @brief Level 0 atomic tests for install-gnome-extension.sh.
    @details Validates script file properties and static analysis without
    executing the script against real filesystem targets.
    """

    def test_script_exists(self) -> None:
        """
        @brief Verify script file exists at expected path.
        """
        assert SCRIPT_PATH.is_file(), f"Script not found: {SCRIPT_PATH}"

    def test_script_is_executable(self) -> None:
        """
        @brief Verify script has executable permission bit set.
        """
        assert os.access(SCRIPT_PATH, os.X_OK), "Script is not executable"

    def test_bash_syntax_check(self) -> None:
        """
        @brief Verify script passes bash -n syntax validation.
        """
        result = subprocess.run(
            ["bash", "-n", str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_script_contains_git_rev_parse(self) -> None:
        """
        @brief Verify script uses git rev-parse --show-toplevel for project root.
        @satisfies REQ-025
        """
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        assert "git rev-parse --show-toplevel" in source

    def test_script_contains_metadata_check(self) -> None:
        """
        @brief Verify script validates metadata.json presence.
        @satisfies REQ-027
        """
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        assert "metadata.json" in source

    def test_script_contains_mkdir_p(self) -> None:
        """
        @brief Verify script creates target directory with mkdir -p.
        @satisfies REQ-026
        """
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        assert "mkdir -p" in source

    def test_script_contains_cp_a(self) -> None:
        """
        @brief Verify script copies files preserving attributes with cp -a.
        @satisfies REQ-029
        """
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        assert "cp -a" in source

    def test_script_contains_gnome_extensions_enable(self) -> None:
        """
        @brief Verify script invokes gnome-extensions enable for the extension UUID.
        @satisfies REQ-032
        """
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        assert "gnome-extensions enable" in source
        assert "aibar@aibar.panel" in source

    def test_script_contains_ansi_colors(self) -> None:
        """
        @brief Verify script defines ANSI escape sequences for colored output.
        @satisfies REQ-028
        """
        source = SCRIPT_PATH.read_text(encoding="utf-8")
        assert "\\033[" in source


class TestInstallGnomeExtensionComposed:
    """
    @brief Level 1 composed tests for install-gnome-extension.sh.
    @details Executes the script in controlled environments to validate
    runtime behavior for error paths.
    """

    def test_exit_nonzero_outside_git_repo(self) -> None:
        """
        @brief Verify script exits non-zero when run outside a git repository.
        @satisfies REQ-030
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["bash", str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=tmpdir,
                env={**os.environ, "HOME": tmpdir},
            )
            assert result.returncode != 0, "Expected non-zero exit outside git repo"

    def test_exit_nonzero_missing_source_dir(self) -> None:
        """
        @brief Verify script exits non-zero when extension source directory is missing.
        @details Creates a minimal git repo without the extension source to trigger
        the source directory validation failure.
        @satisfies REQ-027, REQ-030
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                ["git", "init"],
                capture_output=True,
                cwd=tmpdir,
                timeout=10,
            )
            subprocess.run(
                ["git", "commit", "--allow-empty", "-m", "init"],
                capture_output=True,
                cwd=tmpdir,
                timeout=10,
            )
            result = subprocess.run(
                ["bash", str(SCRIPT_PATH)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=tmpdir,
                env={**os.environ, "HOME": tmpdir},
            )
            assert result.returncode != 0, "Expected non-zero exit with missing source"
            assert "FAIL" in result.stderr, "Expected FAIL marker in error output"
