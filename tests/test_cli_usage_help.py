"""
@file
@brief CLI usage/help output regression tests.
@details Verifies top-level and command-specific help output is human-readable,
contains command and option coverage, and excludes Doxygen tag leakage.
@satisfies REQ-068
"""

from click.testing import CliRunner

from aibar.cli import main


def test_main_invocation_without_subcommand_prints_human_usage() -> None:
    """
    @brief Verify bare `aibar` invocation prints human-readable help text.
    @return {None} Function return value.
    @satisfies REQ-068
    """
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "show --json" in result.output
    assert "show --force" in result.output
    assert "@brief" not in result.output
    assert "@details" not in result.output


def test_top_level_help_lists_commands_without_doxygen_fragments() -> None:
    """
    @brief Verify `aibar --help` lists commands and excludes Doxygen fragments.
    @return {None} Function return value.
    @satisfies REQ-068
    """
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Commands:" in result.output
    assert "doctor" in result.output
    assert "show" in result.output
    assert "setup" in result.output
    assert "@return" not in result.output


def test_show_help_lists_force_and_json_options() -> None:
    """
    @brief Verify `aibar show --help` lists refresh and output options.
    @return {None} Function return value.
    @satisfies REQ-068
    """
    runner = CliRunner()
    result = runner.invoke(main, ["show", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.output
    assert "--force" in result.output
    assert "--provider" in result.output
    assert "--window" in result.output
