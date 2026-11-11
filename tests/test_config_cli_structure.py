"""
@file
@brief Structural validators for generated configuration CLI trees and tables.
@details Independently parses real `--print` and `--info` output to assert that
every structural marker matches the schema topology, sibling order terminates
with `└── `, every detail line uses its owner continuation prefix, no detail
line carries a tree marker, and every table is rectangular with aligned
separators anchored to the owning parameter.
@satisfies TST-091
@satisfies TST-092
"""

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner, Result

from aibar import config as config_module
from aibar.cli import main
from aibar.config_cli import display_width

TREE_BRANCH = "├── "
TREE_LAST = "└── "
TREE_INDENT = "    "
TREE_CONTINUE = "│   "
TABLE_BORDER_CHARACTERS = frozenset("┌┬┐├┼┤└┴┘│")


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


def _split_segments(line: str) -> tuple[list[str], str]:
    """
    @brief Split one physical line into leading four-character segments.
    @param line {str} Physical output line.
    @return {tuple[list[str], str]} Leading segments and remaining content.
    """
    segments: list[str] = []
    remainder = line
    while remainder.startswith(TREE_CONTINUE) or remainder.startswith(TREE_INDENT):
        segments.append(remainder[:4])
        remainder = remainder[4:]
    return segments, remainder


def _is_structural(content: str) -> bool:
    """
    @brief Detect one structural node line after prefix removal.
    @param content {str} Line content after prefix removal.
    @return {bool} True when the content starts with a tree marker.
    """
    return content.startswith(TREE_BRANCH) or content.startswith(TREE_LAST)


def _validate_tree_structure(lines: list[str]) -> None:
    """
    @brief Validate every tree invariant over one generated output.
    @details Collects structural nodes, verifies depth continuity, verifies that
    `└── ` is the final real sibling at its depth, verifies each node prefix
    against the real ancestors, verifies every detail prefix against its owner,
    and rejects detail lines carrying structural markers.
    @param lines {list[str]} Physical output lines.
    @return {None} Function return value.
    @throws {AssertionError} When any structural invariant is violated.
    @satisfies TST-091
    """
    assert lines, "Output MUST NOT be empty."
    assert not _is_structural(lines[0]), "Display root MUST NOT carry a marker."
    assert _split_segments(lines[0])[0] == [], "Root MUST NOT carry a prefix."

    nodes: list[dict[str, Any]] = []
    details: list[tuple[int, list[str], str]] = []
    for position, line in enumerate(lines):
        assert "\t" not in line, "Output lines MUST NOT contain tabs."
        if position == 0:
            continue
        segments, content = _split_segments(line)
        if _is_structural(content):
            marker = content[:4]
            heading = content[4:]
            nodes.append(
                {
                    "depth": len(segments),
                    "marker": marker,
                    "heading": heading,
                    "segments": segments,
                }
            )
            continue
        details.append((len(nodes) - 1, segments, content))

    depths = [int(node["depth"]) for node in nodes]
    for index, depth in enumerate(depths):
        if index == 0:
            assert depth == 0, "First real node MUST live at depth 0."
        else:
            assert depth <= depths[index - 1] + 1, "Tree depth MUST NOT skip."

    def _has_later_sibling(index: int) -> bool:
        depth = depths[index]
        for later in range(index + 1, len(nodes)):
            if depths[later] < depth:
                return False
            if depths[later] == depth:
                return True
        return False

    for index, node in enumerate(nodes):
        expected_marker = TREE_LAST if not _has_later_sibling(index) else (TREE_BRANCH)
        assert node["marker"] == expected_marker, (
            f"Node '{node['heading']}' marker MUST be {expected_marker!r}."
        )
        expected_segments: list[str] = []
        for ancestor_depth in range(depths[index]):
            ancestor_index = max(
                candidate
                for candidate in range(index)
                if depths[candidate] == ancestor_depth
            )
            expected_segments.append(
                TREE_CONTINUE if _has_later_sibling(ancestor_index) else TREE_INDENT
            )
        assert node["segments"] == expected_segments, (
            f"Node '{node['heading']}' prefix MUST be {expected_segments!r}."
        )
        heading = str(node["heading"])
        if "[Path: " in heading:
            token, _, badge = heading.partition(" - [Path: ")
            assert badge.endswith("]"), "Section badge MUST be closed."
            assert token == badge[:-1], "Section badge MUST match its token."

    for owner_index, segments, content in details:
        assert not _is_structural(content), (
            "Detail lines MUST NOT carry structural markers."
        )
        assert not content.startswith(TREE_BRANCH), "No orphan branch markers."
        assert not content.startswith(TREE_LAST), "No orphan last markers."
        if owner_index < 0:
            expected_prefix = [TREE_INDENT]
        else:
            owner_segments = [str(item) for item in nodes[owner_index]["segments"]]
            expected_prefix = [
                *owner_segments,
                TREE_CONTINUE if _has_later_sibling(owner_index) else TREE_INDENT,
            ]
        assert segments == expected_prefix, (
            f"Detail '{content}' MUST use owner prefix {expected_prefix!r}."
        )


def _table_blocks(lines: list[str]) -> list[tuple[list[str], list[str]]]:
    """
    @brief Collect contiguous table blocks with their owner prefixes.
    @param lines {list[str]} Physical output lines.
    @return {list[tuple[list[str], list[str]]]} Prefix and content pairs.
    """
    blocks: list[tuple[list[str], list[str]]] = []
    current_prefix: list[str] | None = None
    current_content: list[str] = []
    for line in lines:
        segments, content = _split_segments(line)
        if content.startswith("┌"):
            current_prefix = segments
            current_content = [content]
            continue
        if current_prefix is not None:
            current_content.append(content)
            if content.startswith("└"):
                blocks.append((current_prefix, current_content))
                current_prefix = None
                current_content = []
                continue
    assert current_prefix is None, "Table block MUST terminate with `└`."
    return blocks


def _validate_tables(lines: list[str]) -> int:
    """
    @brief Validate rectangular table layout and owner anchoring.
    @details Asserts every block shares one owner prefix, one display width, and
    one set of border-column positions, and that the prefix equals the owner
    detail prefix derived from the surrounding tree.
    @param lines {list[str]} Physical output lines.
    @return {int} Number of validated tables.
    @throws {AssertionError} When any table invariant is violated.
    @satisfies TST-092
    """
    blocks = _table_blocks(lines)
    node_positions = [
        index
        for index, line in enumerate(lines)
        if _is_structural(_split_segments(line)[1])
    ]
    for prefix, content_lines in blocks:
        assert len(content_lines) >= 3, "Table MUST carry borders and rows."
        widths = {display_width(content) for content in content_lines}
        assert len(widths) == 1, "Every table line MUST share one display width."
        column_sets = {
            frozenset(
                offset
                for offset, character in _iter_display_offsets(content)
                if character in TABLE_BORDER_CHARACTERS
            )
            for content in content_lines
        }
        assert len(column_sets) == 1, "Table separators MUST align in columns."
        assert all(
            content.startswith(("┌", "├", "└", "│")) for content in content_lines
        ), "Table lines MUST start with a frame character."
        block_start = next(
            index
            for index, line in enumerate(lines)
            if _split_segments(line)[1] == content_lines[0]
        )
        owner_index = max(
            (index for index in node_positions if index < block_start),
            default=-1,
        )
        depths = [len(_split_segments(lines[index])[0]) for index in node_positions]
        if owner_index < 0:
            expected_prefix = [TREE_INDENT]
        else:
            owner_node_index = node_positions.index(owner_index)
            depth = depths[owner_node_index]
            node_prefix = _split_segments(lines[owner_index])[0]
            has_later_sibling = False
            for later in node_positions[owner_node_index + 1 :]:
                later_depth = len(_split_segments(lines[later])[0])
                if later_depth < depth:
                    break
                if later_depth == depth:
                    has_later_sibling = True
                    break
            expected_prefix = [
                *node_prefix,
                TREE_CONTINUE if has_later_sibling else TREE_INDENT,
            ]
        assert prefix == expected_prefix, "Table prefix MUST match owner detail."
    return len(blocks)


def _iter_display_offsets(content: str):
    """
    @brief Iterate `(display_offset, character)` pairs for one line.
    @param content {str} Line content.
    @return {object} Generator of offset/character pairs.
    """
    offset = 0
    for character in content:
        yield offset, character
        offset += display_width(character)


def _seed_document(config_dir: Path) -> None:
    """
    @brief Write one representative configuration document for validation.
    @param config_dir {Path} Temporary configuration directory.
    @return {None} Function return value.
    """
    config_dir.mkdir(parents=True, exist_ok=True)
    document = {
        "idle_delay_seconds": 600,
        "enabled_providers": {"codex": False, "openai": True},
        "currency_symbols": {"openai": "$", "openrouter": "€"},
        "geminiai_project_id": "aibar-project",
    }
    (config_dir / "config.json").write_text(
        json.dumps(document, indent=2) + "\n", encoding="utf-8"
    )


@pytest.mark.parametrize(
    "arguments,minimum_tables",
    [
        (["--print"], 2),
        (["--info"], 1),
        (["--print", "enabled_providers"], 1),
        (["--print", "currency_symbols"], 1),
        (["--print", "currency_symbols:openai"], 1),
        (["--print", "idle_delay_seconds"], 0),
        (["--info", "enabled_providers"], 0),
        (["--info", "currency_symbols"], 1),
        (["--info", "currency_symbols:openai"], 1),
        (["--info", "enabled_providers:codex"], 0),
        (["--info", "billing_data"], 0),
    ],
)
def test_generated_output_satisfies_tree_and_table_invariants(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    arguments: list[str],
    minimum_tables: int,
) -> None:
    """
    @brief Validate structure and tables for representative CLI invocations.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @param arguments {list[str]} CLI argument vector under test.
    @param minimum_tables {int} Minimum table blocks expected in the output.
    @return {None} Function return value.
    @satisfies TST-091
    @satisfies TST-092
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    _seed_document(config_dir)
    result = _invoke(arguments)
    assert result.exit_code == 0, result.output
    assert result.stderr == ""
    lines = result.stdout.splitlines()
    _validate_tree_structure(lines)
    assert _validate_tables(lines) >= minimum_tables


def test_info_detail_prefixes_follow_sibling_position(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify non-last and last leaf metadata use the correct prefixes.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-091
    """
    _patch_config_paths(monkeypatch, tmp_path)
    result = _invoke(["--info"])
    assert result.exit_code == 0, result.output
    output_lines = result.stdout.splitlines()
    assert (
        "│   Default : 300 (restored via: --unset idle_delay_seconds)" in output_lines
    )
    assert (
        "    Default : null (restored via: --unset geminiai_project_id)" in output_lines
    )
    for line in output_lines:
        assert "│   ├── " not in line
        assert "│   └── " not in line
    assert "│       Default :" not in "\n".join(output_lines)


def test_full_print_anchors_map_table_to_owner_detail_prefix(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    @brief Verify a non-last map table uses its owner continuation prefix.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param tmp_path {Path} Temporary path fixture.
    @return {None} Function return value.
    @satisfies TST-092
    """
    config_dir = _patch_config_paths(monkeypatch, tmp_path)
    _seed_document(config_dir)
    result = _invoke(["--print"])
    assert result.exit_code == 0, result.output
    output_lines = result.stdout.splitlines()
    table_lines = [line for line in output_lines if '│ "codex"' in line]
    assert len(table_lines) == 1
    assert table_lines[0].startswith("│   │ ")
    assert "│   ┌──────────┬───────┐" in output_lines
    assert "│   └──────────┴───────┘" in output_lines
