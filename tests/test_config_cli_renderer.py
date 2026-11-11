"""
@file
@brief Exact-golden unit tests for the shared configuration tree renderer.
@details Verifies complete output strings (spaces and newlines included) for
single children, sibling ordering, nested first/middle/last siblings, detail
prefix parity, marker-free requested roots, selection tables, object tables,
wide/escaped cells, and empty-map suppression of empty tables.
@satisfies TST-090
@satisfies TST-092
"""

from aibar.config_cli import (
    CONFIG_PARAM_SPECS_BY_KEY,
    ConfigNodeKind,
    ConfigTreeNode,
    format_print_parameter,
    build_print_tree,
    display_width,
    format_config_table,
    format_selection_state_table,
    render_config_tree,
)


def _param(
    token: str,
    heading: str,
    details: tuple[str, ...] = (),
    children: tuple[ConfigTreeNode, ...] = (),
) -> ConfigTreeNode:
    """
    @brief Build one synthetic parameter node for renderer isolation tests.
    @param token {str} Node schema token.
    @param heading {str} Rendered heading text.
    @param details {tuple[str, ...]} Attached detail lines.
    @param children {tuple[ConfigTreeNode, ...]} Real child nodes.
    @return {ConfigTreeNode} Synthetic parameter node.
    """
    return ConfigTreeNode(
        token=token,
        canonical_path=token,
        kind=ConfigNodeKind.PARAMETER,
        heading=heading,
        details=details,
        children=children,
    )


def _section(
    token: str,
    details: tuple[str, ...] = (),
    children: tuple[ConfigTreeNode, ...] = (),
) -> ConfigTreeNode:
    """
    @brief Build one synthetic section node for renderer isolation tests.
    @param token {str} Section token.
    @param details {tuple[str, ...]} Attached detail lines.
    @param children {tuple[ConfigTreeNode, ...]} Real child nodes.
    @return {ConfigTreeNode} Synthetic section node.
    """
    return ConfigTreeNode(
        token=token,
        canonical_path=token,
        kind=ConfigNodeKind.SECTION,
        heading=f"{token} - [Path: {token}]",
        details=details,
        children=children,
    )


def _root(*children: ConfigTreeNode) -> ConfigTreeNode:
    """
    @brief Build one synthetic marker-free display root.
    @param children {ConfigTreeNode} Real root children in sibling order.
    @return {ConfigTreeNode} Synthetic display root.
    """
    return ConfigTreeNode(
        token="Application_Configuration",
        canonical_path="",
        kind=ConfigNodeKind.SECTION,
        heading="Application_Configuration - Current configuration",
        children=children,
    )


def _render(root: ConfigTreeNode) -> str:
    """
    @brief Render one tree as a complete newline-terminated string.
    @param root {ConfigTreeNode} Display root node.
    @return {str} Full output text.
    """
    return "\n".join(render_config_tree(root)) + "\n"


def test_render_single_root_child() -> None:
    """
    @brief Verify a single root child renders with one last-sibling marker.
    @return {None} Function return value.
    @satisfies TST-090
    """
    expected_output = (
        "Application_Configuration - Current configuration\n"
        "└── idle_delay_seconds = 300 (default)\n"
    )
    assert _render(_root(_param("a", "idle_delay_seconds = 300 (default)"))) == (
        expected_output
    )


def test_render_two_root_siblings() -> None:
    """
    @brief Verify two root siblings use branch then last markers in order.
    @return {None} Function return value.
    @satisfies TST-090
    """
    expected_output = (
        "Application_Configuration - Current configuration\n"
        "├── idle_delay_seconds = 300 (default)\n"
        "└── log_enabled = false (default)\n"
    )
    root = _root(
        _param("a", "idle_delay_seconds = 300 (default)"),
        _param("b", "log_enabled = false (default)"),
    )
    assert _render(root) == expected_output


def test_render_nested_first_middle_last_siblings() -> None:
    """
    @brief Verify nested first/middle/last sibling prefixes and details.
    @return {None} Function return value.
    @satisfies TST-090
    """
    expected_output = (
        "Application_Configuration - Current configuration\n"
        "├── A - [Path: A]\n"
        "│   A note\n"
        "│   ├── a1 = 1 (default)\n"
        "│   │   d1\n"
        "│   │   d2\n"
        "│   ├── a2 = 2 (default)\n"
        "│   └── a3 = 3 (default)\n"
        "│       d3\n"
        "└── b = 4 (default)\n"
    )
    branch = _section(
        "A",
        details=("A note",),
        children=(
            _param("a1", "a1 = 1 (default)", ("d1", "d2")),
            _param("a2", "a2 = 2 (default)"),
            _param("a3", "a3 = 3 (default)", ("d3",)),
        ),
    )
    assert _render(_root(branch, _param("b", "b = 4 (default)"))) == expected_output


def test_render_non_last_parameter_with_several_details() -> None:
    """
    @brief Verify a non-last parameter prefixes details with one continuation.
    @return {None} Function return value.
    @satisfies TST-090
    """
    expected_output = (
        "Application_Configuration - Current configuration\n"
        "├── p1 = 1 (default)\n"
        "│   d1\n"
        "│   d2\n"
        "└── p2 = 2 (default)\n"
    )
    root = _root(
        _param("p1", "p1 = 1 (default)", ("d1", "d2")),
        _param("p2", "p2 = 2 (default)"),
    )
    assert _render(root) == expected_output


def test_render_last_parameter_with_several_details() -> None:
    """
    @brief Verify a last parameter prefixes details with four spaces.
    @return {None} Function return value.
    @satisfies TST-090
    """
    expected_output = (
        "Application_Configuration - Current configuration\n"
        "├── p1 = 1 (default)\n"
        "└── p2 = 2 (default)\n"
        "    d1\n"
        "    d2\n"
    )
    root = _root(
        _param("p1", "p1 = 1 (default)"),
        _param("p2", "p2 = 2 (default)", ("d1", "d2")),
    )
    assert _render(root) == expected_output


def test_render_branch_with_details_and_real_children() -> None:
    """
    @brief Verify three-level prefix accumulation for a branch with details.
    @return {None} Function return value.
    @satisfies TST-090
    """
    expected_output = (
        "Application_Configuration - Current configuration\n"
        "└── A - [Path: A]\n"
        "    branch note\n"
        "    ├── A:B - [Path: A:B]\n"
        "    │   ├── c1 = 1 (default)\n"
        "    │   └── c2 = 2 (default)\n"
        "    └── d = 4 (default)\n"
    )
    branch = _section(
        "A",
        details=("branch note",),
        children=(
            _section(
                "A:B",
                children=(
                    _param("c1", "c1 = 1 (default)"),
                    _param("c2", "c2 = 2 (default)"),
                ),
            ),
            _param("d", "d = 4 (default)"),
        ),
    )
    assert _render(_root(branch)) == expected_output


def test_selection_table_marks_exactly_one_active_row() -> None:
    """
    @brief Verify the `Sel | Value` selection table layout and active marker.
    @return {None} Function return value.
    @satisfies TST-090
    @satisfies TST-092
    """
    spec = CONFIG_PARAM_SPECS_BY_KEY["currency_symbols"]
    expected_lines = (
        "┌─────┬───────┐",
        "│ Sel │ Value │",
        "├─────┼───────┤",
        '│ [*] │ "$"   │',
        '│ [ ] │ "£"   │',
        '│ [ ] │ "€"   │',
        "└─────┴───────┘",
    )
    lines = format_selection_state_table(spec, "$")
    assert lines == expected_lines
    assert sum(line.count("[*]") for line in lines) == 1


def test_object_table_columns_match_schema_fields() -> None:
    """
    @brief Verify a rectangular object table with shared column boundaries.
    @return {None} Function return value.
    @satisfies TST-090
    @satisfies TST-092
    """
    expected_lines = (
        "┌─────────┬───────┐",
        "│ Key     │ Value │",
        "├─────────┼───────┤",
        '│ "codex" │ false │',
        "└─────────┴───────┘",
    )
    lines = format_config_table(("Key", "Value"), (('"codex"', "false"),))
    assert lines == expected_lines


def test_table_measures_wide_and_escaped_cells() -> None:
    """
    @brief Verify display-width measurement for wide and escaped cell data.
    @return {None} Function return value.
    @satisfies TST-092
    """
    assert display_width("漢字") == 4
    assert display_width("a\\nb") == 4
    expected_lines = (
        "┌─────────┬────────────────┐",
        "│ Pattern │ Value          │",
        "├─────────┼────────────────┤",
        '│ "漢字"  │ "line1\\nline2" │',
        "└─────────┴────────────────┘",
    )
    lines = format_config_table(("Pattern", "Value"), (('"漢字"', '"line1\\nline2"'),))
    assert lines == expected_lines


def test_empty_map_renders_hint_without_table() -> None:
    """
    @brief Verify empty maps emit a complete-path hint and no table lines.
    @return {None} Function return value.
    @satisfies TST-090
    """
    spec = CONFIG_PARAM_SPECS_BY_KEY["enabled_providers"]
    node = format_print_parameter({"enabled_providers": {}}, spec)
    assert node.details == ()
    assert node.heading == (
        "enabled_providers = (empty map | set key: "
        "--set enabled_providers:openai false)"
    )


def test_populated_map_attaches_key_value_table() -> None:
    """
    @brief Verify populated maps attach a `Key | Value` table as details.
    @return {None} Function return value.
    @satisfies TST-090
    """
    spec = CONFIG_PARAM_SPECS_BY_KEY["enabled_providers"]
    node = format_print_parameter(
        {"enabled_providers": {"codex": False, "openai": True}}, spec
    )
    assert node.heading == (
        "enabled_providers = (2 entries | key target: enabled_providers:<Key>)"
    )
    assert node.details[0] == "┌──────────┬───────┐"
    assert node.details[-1] == "└──────────┴───────┘"


def test_requested_subtree_root_has_no_marker_and_four_space_details() -> None:
    """
    @brief Verify a requested map entry renders marker-free with 4-space details.
    @return {None} Function return value.
    @satisfies TST-090
    """
    document = {"currency_symbols": {"openai": "$"}}
    expected_output = (
        'currency_symbols:openai = "$"\n'
        "    ┌─────┬───────┐\n"
        "    │ Sel │ Value │\n"
        "    ├─────┼───────┤\n"
        '    │ [*] │ "$"   │\n'
        '    │ [ ] │ "£"   │\n'
        '    │ [ ] │ "€"   │\n'
        "    └─────┴───────┘\n"
    )
    assert _render(build_print_tree(document, "currency_symbols:openai")) == (
        expected_output
    )


def test_tree_node_rejects_embedded_line_breaks() -> None:
    """
    @brief Verify tree text rejects line breaks and ANSI escape characters.
    @return {None} Function return value.
    @satisfies TST-091
    """
    for forbidden_text in ("a\nb", "a\tb", "a\x1b[0mb"):
        try:
            ConfigTreeNode(
                token="p",
                canonical_path="p",
                kind=ConfigNodeKind.PARAMETER,
                heading=forbidden_text,
            )
        except ValueError:
            continue
        raise AssertionError("Tree node accepted forbidden control characters.")
