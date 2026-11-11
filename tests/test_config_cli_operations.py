"""
@file
@brief Behavior tests for the configuration CLI command surface.
@details Verifies bootstrap, strict loading, JSON `--get` output, typed `--set`,
`--unset` reset semantics, stdout/stderr routing and exit codes, byte-preserving
`--print-raw`, atomic-write failure rollback, and executability of every command
example published by `--info`.
@satisfies TST-093
@satisfies TST-094
@satisfies TST-095
@satisfies TST-096
"""

import json
import shlex
import stat
from pathlib import Path

import pytest
from click.testing import CliRunner, Result

from aibar import config as config_module
from aibar.cli import main


def _patch_config_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """
    @brief Redirect AIBar configuration paths into one temporary directory.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {Path} Effective configuration directory replacement.
    """
    config_dir = tmp_path / ".config" / "aibar"
    cache_dir = tmp_path / ".cache" / "aibar"
    monkeypatch.setattr(config_module, "APP_CONFIG_DIR", config_dir)
    monkeypatch.setattr(config_module, "APP_CACHE_DIR", cache_dir)
    monkeypatch.setattr(config_module, "ENV_FILE_PATH", config_dir / "env")
    monkeypatch.setattr(
        config_module, "RUNTIME_CONFIG_PATH", config_dir / "config.json"
    )
    monkeypatch.setattr(config_module, "CACHE_FILE_PATH", cache_dir / "cache.json")
    monkeypatch.setattr(config_module, "IDLE_TIME_PATH", cache_dir / "idle-time.json")
    return config_dir


def _invoke(arguments: list[str]) -> Result:
    """
    @brief Invoke the CLI with one argument vector.
    @param arguments {list[str]} CLI argument tokens.
    @return {Result} Click invocation result object.
    """
    return CliRunner().invoke(main, arguments)


def _write_document(config_dir: Path, document: dict) -> Path:
    """
    @brief Write one raw configuration document for a test scenario.
    @param config_dir {Path} Temporary configuration directory.
    @param document {dict} JSON document to persist.
    @return {Path} Written configuration file path.
    """
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"
    config_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return config_path


def _read_document(config_dir: Path) -> dict:
    """
    @brief Read the current configuration document.
    @param config_dir {Path} Temporary configuration directory.
    @return {dict} Decoded configuration document.
    """
    return json.loads((config_dir / "config.json").read_text(encoding="utf-8"))


def test_print_bootstraps_schema_defaults_when_file_is_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify bootstrap writes schema defaults with a private mode.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-095
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    result = _invoke(["--print"])
    assert result.exit_code == 0, result.output
    config_path = config_dir / "config.json"
    assert config_path.exists()
    assert _read_document(config_dir)["idle_delay_seconds"] == 300
    assert stat.S_IMODE(config_path.stat().st_mode) == 0o600
    assert result.stdout.startswith(
        "Application_Configuration - Current configuration\n"
    )


def test_print_preserves_existing_valid_file_bytes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify read commands never rewrite an existing valid file.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-095
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    config_path = _write_document(config_dir, {"idle_delay_seconds": 900})
    original_bytes = config_path.read_bytes()
    result = _invoke(["--print", "idle_delay_seconds"])
    assert result.exit_code == 0, result.output
    assert result.stdout == "idle_delay_seconds = 900 (custom | default: 300)\n"
    assert config_path.read_bytes() == original_bytes


def test_get_emits_json_values_for_every_schema_kind(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify `--get` emits one JSON value per schema kind on stdout.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-093
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    _write_document(
        config_dir,
        {
            "idle_delay_seconds": 600,
            "billing_data": "export_ds",
            "log_enabled": True,
            "copilot_extra_premium_request_cost": 0.25,
            "geminiai_project_id": None,
            "enabled_providers": {"codex": False},
        },
    )
    expectations = {
        "idle_delay_seconds": "600\n",
        "billing_data": '"export_ds"\n',
        "log_enabled": "true\n",
        "copilot_extra_premium_request_cost": "0.25\n",
        "geminiai_project_id": "null\n",
        "enabled_providers": '{"codex": false}\n',
        "enabled_providers:codex": "false\n",
        "default_retry_after_seconds": "3600\n",
    }
    for path_text, expected_stdout in expectations.items():
        result = _invoke(["--get", path_text])
        assert result.exit_code == 0, result.output
        assert result.stdout == expected_stdout
        assert result.stderr == ""


def test_set_parses_json_types_before_persisting(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify typed `--set` parsing and silent success output.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-093
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    scenarios = [
        ("idle_delay_seconds", "600", 600),
        ("copilot_extra_premium_request_cost", "1", 1.0),
        ("log_enabled", "true", True),
        ("billing_data", '"export_ds"', "export_ds"),
        ("billing_data", "plain_dataset", "plain_dataset"),
        ("geminiai_project_id", "null", None),
        ("geminiai_project_id", '"my-project"', "my-project"),
    ]
    for path_text, raw_value, expected_value in scenarios:
        result = _invoke(["--set", path_text, raw_value])
        assert result.exit_code == 0, result.output
        assert result.stdout == ""
        assert result.stderr == ""
        assert _read_document(config_dir)[path_text] == expected_value


def test_set_map_entry_and_whole_map_operations(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify map entry creation, whole-map replacement, and key deletion.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-093
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    assert _invoke(["--set", "enabled_providers:codex", "false"]).exit_code == 0
    assert _invoke(["--set", "currency_symbols:openai", '"$"']).exit_code == 0
    document = _read_document(config_dir)
    assert document["enabled_providers"] == {"codex": False}
    assert document["currency_symbols"] == {"openai": "$"}

    result = _invoke(["--set", "enabled_providers", '{"openai": true, "zai": false}'])
    assert result.exit_code == 0, result.output
    assert _read_document(config_dir)["enabled_providers"] == {
        "openai": True,
        "zai": False,
    }

    assert _invoke(["--unset", "enabled_providers:zai"]).exit_code == 0
    assert _read_document(config_dir)["enabled_providers"] == {"openai": True}


def test_unset_field_removes_key_and_restores_default(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify `--unset` removes the field so the schema default applies.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-093
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    _write_document(config_dir, {"idle_delay_seconds": 900, "log_enabled": True})
    result = _invoke(["--unset", "idle_delay_seconds"])
    assert result.exit_code == 0, result.output
    assert result.stdout == ""
    document = _read_document(config_dir)
    assert "idle_delay_seconds" not in document
    assert document["log_enabled"] is True
    assert _invoke(["--get", "idle_delay_seconds"]).stdout == "300\n"
    assert _invoke(["--unset", "idle_delay_seconds"]).exit_code == 0


@pytest.mark.parametrize(
    "arguments,expected_error_fragment",
    [
        (["--get", "unknown_field"], "Unknown configuration field"),
        (["--get", "Application_Configuration"], "virtual root label"),
        (["--get", "enabled_providers:"], "empty token"),
        (["--get", "billing_data:extra"], "is not a dynamic map"),
        (["--get", "enabled_providers:+"], "reserved array-operation token"),
        (["--get", "enabled_providers:a:b"], "addresses too many levels"),
        (["--get", "enabled_providers:absent"], "does not exist"),
        (["--get", "IDLE_DELAY_SECONDS"], "Unknown configuration field"),
        (["--set", "idle_delay_seconds", "abc"], "MUST be valid JSON"),
        (["--set", "idle_delay_seconds", "1.5"], "MUST be a JSON integer"),
        (["--set", "idle_delay_seconds", "0"], "MUST be >= 1"),
        (["--set", "log_enabled", "1"], "MUST be a JSON boolean"),
        (["--set", "billing_data", "123"], "not a string"),
        (["--set", "billing_data", '""'], "MUST be a non-empty string"),
        (["--set", "enabled_providers", "[]"], "MUST be one JSON object"),
        (["--set", "enabled_providers:codex", '"no"'], "MUST be a JSON boolean"),
        (["--set", "currency_symbols:openai", '"¥"'], "MUST be one of"),
        (["--unset", "enabled_providers:absent"], "does not exist"),
    ],
)
def test_rejected_operations_exit_one_with_stderr_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    arguments: list[str],
    expected_error_fragment: str,
) -> None:
    """
    @brief Verify rejected paths and values fail without stdout output.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @param arguments {list[str]} CLI argument vector under test.
    @param expected_error_fragment {str} Required stderr diagnostic substring.
    @return {None} Function return value.
    @satisfies TST-093
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    config_path = _write_document(
        config_dir, {"idle_delay_seconds": 600, "enabled_providers": {"zai": True}}
    )
    original_bytes = config_path.read_bytes()
    result = _invoke(arguments)
    assert result.exit_code == 1, result.output
    assert result.stdout == ""
    assert expected_error_fragment in result.stderr
    assert config_path.read_bytes() == original_bytes


def test_malformed_configuration_file_is_rejected_without_rewrite(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify malformed JSON fails read commands and stays untouched.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-093
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"
    config_path.write_bytes(b'{"idle_delay_seconds": }')
    original_bytes = config_path.read_bytes()
    for arguments in (
        ["--get", "idle_delay_seconds"],
        ["--print"],
        ["--set", "idle_delay_seconds", "600"],
    ):
        result = _invoke(arguments)
        assert result.exit_code == 1, result.output
        assert "not valid JSON" in result.stderr
        assert config_path.read_bytes() == original_bytes


def test_unknown_document_field_is_rejected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify documents with unknown fields fail strict validation.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-093
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    _write_document(config_dir, {"idle_delay_seconds": 600, "legacy_key": 1})
    result = _invoke(["--get", "idle_delay_seconds"])
    assert result.exit_code == 1
    assert "unknown field(s): legacy_key" in result.stderr


def test_print_raw_emits_unmodified_file_bytes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify `--print-raw` preserves compact bytes without reformatting.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-093
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"
    original_bytes = b'{"idle_delay_seconds":900}'
    config_path.write_bytes(original_bytes)
    result = _invoke(["--print-raw"])
    assert result.exit_code == 0, result.output
    assert result.stdout_bytes == original_bytes
    assert config_path.read_bytes() == original_bytes


def test_print_raw_bootstraps_missing_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify `--print-raw` bootstraps defaults before byte emission.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-095
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    result = _invoke(["--print-raw"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["idle_delay_seconds"] == 300
    assert (config_dir / "config.json").exists()


def test_print_raw_emits_bytes_of_malformed_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify `--print-raw` stays byte-preserving for invalid JSON.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-093
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"
    config_path.write_bytes(b"{broken")
    result = _invoke(["--print-raw"])
    assert result.exit_code == 0, result.output
    assert result.stdout_bytes == b"{broken"


def test_write_failure_preserves_file_and_removes_temporary_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify atomic-write failure leaves the original bytes and no temp file.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-094
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    config_path = _write_document(config_dir, {"idle_delay_seconds": 600})
    original_bytes = config_path.read_bytes()

    def _fail_replace(source: object, destination: object) -> None:
        raise OSError("replacement rejected")

    monkeypatch.setattr(config_module.os, "replace", _fail_replace)
    result = _invoke(["--set", "idle_delay_seconds", "900"])
    assert result.exit_code == 1, result.output
    assert result.stdout == ""
    assert "Cannot write" in result.stderr
    assert config_path.read_bytes() == original_bytes
    assert [path.name for path in config_dir.iterdir()] == ["config.json"]


def test_set_preserves_existing_file_mode(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify an existing configuration file keeps its permission mode.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-094
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    config_path = _write_document(config_dir, {"idle_delay_seconds": 600})
    config_path.chmod(0o640)
    result = _invoke(["--set", "idle_delay_seconds", "900"])
    assert result.exit_code == 0, result.output
    assert stat.S_IMODE(config_path.stat().st_mode) == 0o640
    assert _read_document(config_dir)["idle_delay_seconds"] == 900


def test_help_lists_configuration_options(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify `--help` documents all six configuration options.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-093
    """
    _patch_config_paths(monkeypatch, tmp_path)
    result = _invoke(["--help"])
    assert result.exit_code == 0, result.output
    for option in ("--print", "--info", "--print-raw", "--get", "--set", "--unset"):
        assert option in result.stdout
    assert "aibar --set idle_delay_seconds 600" in result.stdout
    assert "aibar --get idle_delay_seconds" in result.stdout


def test_published_info_examples_are_executable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify every `--info` example is shell-parsable and succeeds.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-096
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    info_result = _invoke(["--info"])
    assert info_result.exit_code == 0, info_result.output
    command_labels = (
        "Set cmd",
        "Set key",
        "Remove key",
        "Full overwrite",
        "Reset cmd",
        "Reset map",
    )
    example_commands: list[list[str]] = []
    for line in info_result.stdout.splitlines():
        content = line.lstrip("│ ")
        for label in command_labels:
            label_prefix = f"{label} : "
            if not content.startswith(label_prefix):
                continue
            command_text = content[len(label_prefix) :]
            assert "..." not in command_text
            argument_tokens = shlex.split(command_text)
            assert argument_tokens[0] in ("--set", "--unset")
            example_commands.append(argument_tokens)
            break
    assert example_commands, "Documentation MUST publish executable examples."
    for argument_tokens in example_commands:
        result = _invoke(argument_tokens)
        assert result.exit_code == 0, (argument_tokens, result.stderr)
        assert result.stdout == ""
    assert (config_dir / "config.json").exists()
