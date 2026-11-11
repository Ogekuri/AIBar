"""
@file
@brief Schema-driven configuration CLI subsystem for aibar.
@details Defines the single canonical configuration schema, canonical path
resolution, typed value parsing and validation, atomic persistence, and the one
deterministic tree/table renderer shared by `--print` and `--info`. All output
is English and every published example is derived from the schema table, so the
schema, CLI behavior, and schema documentation cannot diverge.
@satisfies REQ-200
@satisfies REQ-222
@satisfies REQ-235
@satisfies REQ-238
"""

import json
import math
import shlex
import sys
import unicodedata
import copy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, BinaryIO, Sequence, TextIO

from pydantic import ValidationError

from aibar import config as config_module
from aibar.config import RuntimeConfig, write_json_document_atomic
from aibar.providers.base import ProviderName

# Tree rendering characters (UTF-8 box drawing).
TREE_VERTICAL = "│"
TREE_BRANCH = "├── "
TREE_LAST = "└── "
TREE_INDENT = "    "
TREE_CONTINUE = "│   "

# Displayed virtual root label; never a CLI path token.
VIRTUAL_ROOT_LABEL = "Application_Configuration"
ROOT_PRINT_HEADING = f"{VIRTUAL_ROOT_LABEL} - Current configuration"
ROOT_INFO_HEADING = f"{VIRTUAL_ROOT_LABEL} - Configuration schema"

# Array-operation tokens reserved by the shared path grammar. The aibar schema
# defines no array parameter, so every occurrence is rejected.
RESERVED_ARRAY_OPERATION_TOKENS = frozenset({"append", "+", "insert"})

_FORBIDDEN_TEXT_CHARACTERS = ("\n", "\r", "\t", "\x1b")


class ConfigCliError(Exception):
    """
    @brief Report one user-facing configuration CLI failure.
    @details Carries a deterministic English diagnostic that callers route to
    stderr before exiting with status 1. Invalid paths, invalid values, invalid
    documents, and persistence failures all use this single error type.
    @satisfies REQ-202
    @satisfies REQ-217
    """

    pass


class ConfigParamKind(str, Enum):
    """
    @brief Enumerate the schema value kinds supported by the configuration CLI.
    @details `MAP` denotes a dynamic `Map[String, Value]` parameter; `SELECTION`
    denotes one value drawn from a closed domain; the remaining members denote
    primitive scalar parameters.
    @satisfies REQ-201
    """

    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    STRING = "string"
    OPTIONAL_STRING = "optional_string"
    SELECTION = "selection"
    MAP = "map"


class ConfigNodeKind(str, Enum):
    """
    @brief Enumerate configuration tree node kinds.
    @details Only `SECTION` nodes carry a `[Path: ...]` badge; `PARAMETER` nodes
    carry a value or schema heading.
    @satisfies REQ-222
    """

    SECTION = "section"
    PARAMETER = "parameter"


_CURRENCY_MEANINGS: dict[str, str] = {
    "$": "US dollar",
    "£": "Pound sterling",
    "€": "Euro",
}


@dataclass(frozen=True)
class ConfigParamSpec:
    """
    @brief Describe one `RuntimeConfig` field for every configuration CLI surface.
    @details Single source for path tokens, description text, constraint labels,
    `--set` examples, map action examples, and selection domains. Defaults are
    resolved from `RuntimeConfig` model fields by `field_default(...)` so the
    schema, validation, rendering, and `--info` documentation cannot diverge.
    @satisfies REQ-235
    """

    key: str
    kind: ConfigParamKind
    description: str
    example_value: Any = None
    minimum: float | None = None
    non_empty: bool = False
    map_value_kind: ConfigParamKind | None = None
    map_example_key: str = ""
    map_example_value: Any = None
    full_map_example: tuple[tuple[str, Any], ...] = ()
    selection_options: tuple[tuple[str, str], ...] = ()
    selection_default: str = ""

    @property
    def type_label(self) -> str:
        """
        @brief Render the constraint label used inside `--info` headings.
        @details Derives the label from the declared constraint fields so a
        constraint edit automatically updates the published documentation.
        @return {str} Type-and-constraints label text.
        @satisfies REQ-231
        @satisfies REQ-235
        """
        if self.kind is ConfigParamKind.INTEGER:
            if self.minimum is None:
                return "Integer"
            return f"Integer: >= {int(self.minimum)}"
        if self.kind is ConfigParamKind.FLOAT:
            if self.minimum is None:
                return "Float"
            return f"Float: >= {int(self.minimum)}"
        if self.kind is ConfigParamKind.BOOLEAN:
            return "Boolean"
        if self.kind is ConfigParamKind.STRING:
            return "String: non-empty" if self.non_empty else "String"
        if self.kind is ConfigParamKind.OPTIONAL_STRING:
            return (
                "Optional[String]: non-empty" if self.non_empty else "Optional[String]"
            )
        if self.kind is ConfigParamKind.SELECTION:
            options = ", ".join(value for value, _ in self.selection_options)
            return f"Selection: {options}"
        if self.map_value_kind is ConfigParamKind.BOOLEAN:
            return "Map[String, Boolean]"
        if self.map_value_kind is ConfigParamKind.SELECTION:
            return "Map[String, Selection]"
        return "Map[String, String]"


CONFIG_PARAM_SPECS: tuple[ConfigParamSpec, ...] = (
    ConfigParamSpec(
        key="idle_delay_seconds",
        kind=ConfigParamKind.INTEGER,
        description=(
            "Idle gating delay in seconds before a provider refresh becomes "
            "eligible again."
        ),
        example_value=600,
        minimum=1,
    ),
    ConfigParamSpec(
        key="api_call_delay_milliseconds",
        kind=ConfigParamKind.INTEGER,
        description=(
            "Minimum delay in milliseconds between two consecutive provider API calls."
        ),
        example_value=250,
        minimum=1,
    ),
    ConfigParamSpec(
        key="api_call_timeout_milliseconds",
        kind=ConfigParamKind.INTEGER,
        description=(
            "HTTP response timeout in milliseconds applied to every provider API call."
        ),
        example_value=8000,
        minimum=1,
    ),
    ConfigParamSpec(
        key="default_retry_after_seconds",
        kind=ConfigParamKind.INTEGER,
        description=(
            "Retry delay in seconds used when a provider failure reports no "
            "retry-after value."
        ),
        example_value=1800,
        minimum=1,
    ),
    ConfigParamSpec(
        key="gnome_refresh_interval_seconds",
        kind=ConfigParamKind.INTEGER,
        description="GNOME extension automatic refresh interval in seconds.",
        example_value=30,
        minimum=1,
    ),
    ConfigParamSpec(
        key="billing_data",
        kind=ConfigParamKind.STRING,
        description=(
            "Google BigQuery billing-export dataset name used for GeminiAI "
            "billing queries."
        ),
        example_value="billing_export",
        non_empty=True,
    ),
    ConfigParamSpec(
        key="enabled_providers",
        kind=ConfigParamKind.MAP,
        description=(
            "Provider activation flags keyed by provider name; a missing key "
            "enables the provider."
        ),
        map_value_kind=ConfigParamKind.BOOLEAN,
        map_example_key="openai",
        map_example_value=False,
        full_map_example=(("openai", False),),
    ),
    ConfigParamSpec(
        key="copilot_extra_premium_request_cost",
        kind=ConfigParamKind.FLOAT,
        description=(
            "Unit price in USD for one Copilot premium request above the "
            "included plan quota."
        ),
        example_value=0.05,
        minimum=0,
    ),
    ConfigParamSpec(
        key="currency_symbols",
        kind=ConfigParamKind.MAP,
        description=(
            "Currency symbol per provider for monetary metrics; a missing key "
            "falls back to the default symbol."
        ),
        map_value_kind=ConfigParamKind.SELECTION,
        map_example_key="openai",
        map_example_value=config_module.DEFAULT_CURRENCY_SYMBOL,
        full_map_example=(("openai", config_module.DEFAULT_CURRENCY_SYMBOL),),
        selection_options=tuple(
            (symbol, _CURRENCY_MEANINGS[symbol])
            for symbol in config_module.VALID_CURRENCY_SYMBOLS
        ),
        selection_default=config_module.DEFAULT_CURRENCY_SYMBOL,
    ),
    ConfigParamSpec(
        key="log_enabled",
        kind=ConfigParamKind.BOOLEAN,
        description=(
            "Append runtime execution logging to ~/.cache/aibar/aibar.log when true."
        ),
        example_value=True,
    ),
    ConfigParamSpec(
        key="debug_enabled",
        kind=ConfigParamKind.BOOLEAN,
        description=(
            "Append provider API debug response summaries when true and "
            "runtime logging is enabled."
        ),
        example_value=True,
    ),
    ConfigParamSpec(
        key="geminiai_project_id",
        kind=ConfigParamKind.OPTIONAL_STRING,
        description=(
            "Google Cloud project identifier used for GeminiAI Monitoring and "
            "billing queries."
        ),
        example_value="aibar-gcp-project",
        non_empty=True,
    ),
)

CONFIG_PARAM_SPECS_BY_KEY: dict[str, ConfigParamSpec] = {
    spec.key: spec for spec in CONFIG_PARAM_SPECS
}


@dataclass(frozen=True)
class ResolvedConfigPath:
    """
    @brief Represent one resolved canonical configuration path.
    @details Carries the addressed schema parameter and the optional dynamic map
    key so callers never re-parse display text.
    @satisfies REQ-201
    """

    spec: ConfigParamSpec
    map_key: str | None = None

    @property
    def canonical_path(self) -> str:
        """
        @brief Render the canonical colon-separated path of the resolved target.
        @return {str} Canonical path text.
        @satisfies REQ-201
        """
        if self.map_key is None:
            return self.spec.key
        return f"{self.spec.key}:{self.map_key}"


@dataclass(frozen=True)
class ConfigTreeNode:
    """
    @brief Represent one real configuration tree node.
    @details `heading` is one logical line rendered after the structural marker;
    `details` are attached metadata/table lines rendered with the node detail
    prefix; `children` are real configuration nodes only.
    @satisfies REQ-222
    @satisfies REQ-227
    """

    token: str
    canonical_path: str
    kind: ConfigNodeKind
    heading: str
    details: tuple[str, ...] = ()
    children: tuple["ConfigTreeNode", ...] = ()

    def __post_init__(self) -> None:
        """
        @brief Reject tree text that would break the one-line-per-node contract.
        @details Raises when a heading or detail line embeds a newline, carriage
        return, tab, or ANSI escape so structural output can never be corrupted
        by configuration values.
        @throws {ValueError} When structural text contains a control character.
        @satisfies REQ-227
        """
        for text in (self.heading, *self.details):
            for forbidden in _FORBIDDEN_TEXT_CHARACTERS:
                if forbidden in text:
                    raise ValueError(
                        "Configuration tree text MUST NOT contain line breaks "
                        "or control characters."
                    )


def field_default(key: str) -> Any:
    """
    @brief Resolve the declared schema default of one configuration field.
    @details Reads the `RuntimeConfig` model field default (calling a factory
    when declared) so defaults have exactly one source of truth.
    @param key {str} `RuntimeConfig` field name.
    @return {Any} Declared default value.
    @satisfies REQ-209
    @satisfies REQ-235
    """
    field_info = RuntimeConfig.model_fields[key]
    return field_info.get_default(call_default_factory=True)


def _verify_schema_alignment() -> None:
    """
    @brief Verify the CLI schema table matches the `RuntimeConfig` model.
    @details Raises at import time when the schema table omits, reorders, or
    adds fields relative to `RuntimeConfig`, and validates every declared
    default against its own schema rules.
    @return {None} Function return value.
    @throws {RuntimeError} When schema fields and model fields diverge.
    @satisfies REQ-236
    """
    schema_keys = tuple(spec.key for spec in CONFIG_PARAM_SPECS)
    model_keys = tuple(RuntimeConfig.model_fields)
    if schema_keys != model_keys:
        raise RuntimeError(
            "Configuration schema table diverges from RuntimeConfig fields: "
            f"schema={schema_keys} model={model_keys}"
        )
    for spec in CONFIG_PARAM_SPECS:
        validate_schema_value(spec, field_default(spec.key), path_label=spec.key)


def _verify_single_line(text: str) -> str:
    """
    @brief Reject multi-line or control-character text in one output line.
    @param text {str} Candidate output line.
    @return {str} Unmodified text when clean.
    @throws {ConfigCliError} When the text embeds a forbidden character.
    @satisfies REQ-227
    """
    for forbidden in _FORBIDDEN_TEXT_CHARACTERS:
        if forbidden in text:
            raise ConfigCliError(
                "Configuration output text MUST NOT contain line breaks or "
                "control characters."
            )
    return text


def _split_path_tokens(path_text: str) -> list[str]:
    """
    @brief Split one canonical configuration path into validated tokens.
    @details Rejects empty paths, empty tokens, virtual-root tokens, and reserved
    array-operation tokens before schema resolution runs.
    @param path_text {str} Canonical colon-separated path text.
    @return {list[str]} Validated path tokens.
    @throws {ConfigCliError} When the path grammar is violated.
    @satisfies REQ-202
    @satisfies REQ-203
    @satisfies REQ-204
    """
    if not path_text:
        raise ConfigCliError("A configuration path is required.")
    tokens = path_text.split(":")
    for token in tokens:
        if not token:
            raise ConfigCliError(f"Path '{path_text}' contains an empty token.")
        if token == VIRTUAL_ROOT_LABEL:
            raise ConfigCliError(
                f"Path '{path_text}' uses the virtual root label "
                f"'{VIRTUAL_ROOT_LABEL}'; configuration paths start at a "
                "field name."
            )
        if token in RESERVED_ARRAY_OPERATION_TOKENS:
            raise ConfigCliError(
                f"Path '{path_text}' uses reserved array-operation token "
                f"'{token}'; the aibar schema defines no array parameter."
            )
    return tokens


def resolve_config_path(path_text: str) -> ResolvedConfigPath:
    """
    @brief Resolve one canonical path against the configuration schema.
    @details Accepts `<Field>` for any parameter and `<Field>:<Key>` only for
    dynamic map parameters. Map keys are exact, case-sensitive JSON object keys
    and MUST NOT contain `:` because the colon separates path tokens.
    @param path_text {str} Canonical colon-separated path text.
    @return {ResolvedConfigPath} Resolved schema parameter and optional map key.
    @throws {ConfigCliError} When a token is unknown, surplus, or unusable.
    @satisfies REQ-201
    @satisfies REQ-202
    """
    tokens = _split_path_tokens(path_text)
    spec = CONFIG_PARAM_SPECS_BY_KEY.get(tokens[0])
    if spec is None:
        known_fields = ", ".join(spec_item.key for spec_item in CONFIG_PARAM_SPECS)
        raise ConfigCliError(
            f"Unknown configuration field '{tokens[0]}' in path "
            f"'{path_text}'. Known fields: {known_fields}."
        )
    if len(tokens) == 1:
        return ResolvedConfigPath(spec=spec)
    if len(tokens) > 2:
        raise ConfigCliError(
            f"Path '{path_text}' addresses too many levels; canonical aibar "
            "paths are '<Field>' or '<Field>:<Key>'."
        )
    if spec.kind is not ConfigParamKind.MAP:
        raise ConfigCliError(
            f"Field '{spec.key}' is not a dynamic map, so path '{path_text}' "
            "is not valid."
        )
    map_key = tokens[1]
    for forbidden in _FORBIDDEN_TEXT_CHARACTERS:
        if forbidden in map_key:
            raise ConfigCliError(
                f"Map key in path '{path_text}' MUST NOT contain control characters."
            )
    return ResolvedConfigPath(spec=spec, map_key=map_key)


def render_json_value(value: Any) -> str:
    """
    @brief Render one configuration value as a JSON literal.
    @details Strings become JSON-quoted strings so newlines and control
    characters render as visible escapes; numbers, booleans, null, arrays, and
    objects render as JSON literals.
    @param value {Any} JSON-compatible value.
    @return {str} JSON literal text.
    @satisfies REQ-228
    """
    return json.dumps(value, ensure_ascii=False)


def format_cli_argument(value: Any) -> str:
    """
    @brief Render one value as a shell-safe `--set` argument.
    @details Encodes the value as JSON and applies POSIX shell quoting so the
    published command is copy/paste executable for every value shape.
    @param value {Any} JSON-compatible value.
    @return {str} Shell-quoted JSON argument text.
    @satisfies REQ-235
    """
    return shlex.quote(render_json_value(value))


def format_set_command(path_text: str, value: Any) -> str:
    """
    @brief Build one copyable `--set` command for a canonical path.
    @param path_text {str} Canonical path text.
    @param value {Any} Schema-valid example value.
    @return {str} Copyable command text starting with `--set`.
    @satisfies REQ-235
    """
    return f"--set {path_text} {format_cli_argument(value)}"


def format_unset_command(path_text: str) -> str:
    """
    @brief Build one copyable `--unset` command for a canonical path.
    @param path_text {str} Canonical path text.
    @return {str} Copyable command text starting with `--unset`.
    @satisfies REQ-235
    """
    return f"--unset {path_text}"


def display_width(text: str) -> int:
    """
    @brief Measure the terminal display width of one already-escaped text.
    @details Counts East-Asian wide and fullwidth characters as two cells and
    ignores combining marks so table borders stay aligned for Unicode data.
    @param text {str} Escaped cell text without control characters.
    @return {int} Display width in terminal cells.
    @satisfies REQ-234
    """
    width = 0
    for character in text:
        if unicodedata.combining(character):
            continue
        if unicodedata.east_asian_width(character) in ("W", "F"):
            width += 2
        else:
            width += 1
    return width


def format_config_table(
    headers: Sequence[str], rows: Sequence[Sequence[str]]
) -> tuple[str, ...]:
    """
    @brief Render one rectangular box-drawing table.
    @details Column widths are measured from the header and every escaped cell,
    then shared by all border and row lines so `│`, `┬`, `┼`, and `┴`
    characters align on one boundary set. Every line is a single logical line
    that the tree renderer prefixes with the owner detail prefix.
    @param headers {Sequence[str]} Column header texts.
    @param rows {Sequence[Sequence[str]]} Escaped cell rows, one entry per column.
    @return {tuple[str, ...]} Table lines from top border to bottom border.
    @throws {ValueError} When a row does not match the header column count.
    @satisfies REQ-233
    @satisfies REQ-234
    """
    column_count = len(headers)
    for row in rows:
        if len(row) != column_count:
            raise ValueError("Table rows MUST match the header column count.")
    widths = [display_width(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], display_width(cell))

    def render_cells(cells: Sequence[str]) -> str:
        padded = (
            f" {cell}{' ' * (widths[index] - display_width(cell))} "
            for index, cell in enumerate(cells)
        )
        return f"{TREE_VERTICAL}{TREE_VERTICAL.join(padded)}{TREE_VERTICAL}"

    def render_border(left: str, junction: str, right: str) -> str:
        segments = ("─" * (width + 2) for width in widths)
        return f"{left}{junction.join(segments)}{right}"

    lines = [render_border("┌", "┬", "┐"), render_cells(tuple(headers))]
    lines.append(render_border("├", "┼", "┤"))
    lines.extend(render_cells(tuple(row)) for row in rows)
    lines.append(render_border("└", "┴", "┘"))
    return tuple(lines)


def validate_schema_value(
    spec: ConfigParamSpec, value: Any, *, path_label: str
) -> None:
    """
    @brief Validate one configuration value against its schema parameter.
    @details Map values are validated as JSON objects with string keys and
    per-entry value domains; scalar values are validated by type, minimum,
    non-empty, and selection-domain constraints.
    @param spec {ConfigParamSpec} Schema parameter declaration.
    @param value {Any} Candidate decoded value.
    @param path_label {str} Canonical path used inside diagnostics.
    @return {None} Function return value.
    @throws {ConfigCliError} When the value violates the declared constraints.
    @satisfies REQ-208
    @satisfies REQ-212
    """
    if spec.kind is not ConfigParamKind.MAP:
        _validate_scalar_value(spec, spec.kind, value, path_label=path_label)
        return
    if not isinstance(value, dict):
        raise ConfigCliError(
            f"Value for '{path_label}' MUST be a JSON object mapping keys to "
            f"{spec.map_value_kind.value if spec.map_value_kind else 'values'}."
        )
    map_value_kind = spec.map_value_kind or ConfigParamKind.STRING
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key:
            raise ConfigCliError(
                f"Map keys for '{path_label}' MUST be non-empty strings."
            )
        if ":" in map_key:
            raise ConfigCliError(
                f"Map key '{map_key}' in '{path_label}' MUST NOT contain ':' "
                "because ':' separates canonical path tokens."
            )
        for forbidden in _FORBIDDEN_TEXT_CHARACTERS:
            if forbidden in map_key:
                raise ConfigCliError(
                    f"Map key '{map_key}' in '{path_label}' MUST NOT contain "
                    "control characters."
                )
        _validate_scalar_value(
            spec,
            map_value_kind,
            map_value,
            path_label=f"{path_label}:{map_key}",
        )


def _validate_scalar_value(
    spec: ConfigParamSpec,
    kind: ConfigParamKind,
    value: Any,
    *,
    path_label: str,
) -> None:
    """
    @brief Validate one scalar value against a schema kind.
    @param spec {ConfigParamSpec} Schema parameter supplying constraints.
    @param kind {ConfigParamKind} Scalar kind to enforce.
    @param value {Any} Candidate decoded value.
    @param path_label {str} Canonical path used inside diagnostics.
    @return {None} Function return value.
    @throws {ConfigCliError} When the value violates the declared constraints.
    @satisfies REQ-212
    """
    if kind is ConfigParamKind.INTEGER:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ConfigCliError(
                f"Value for '{path_label}' MUST be a JSON integer, got "
                f"{render_json_value(value)}."
            )
        if spec.minimum is not None and value < spec.minimum:
            raise ConfigCliError(
                f"Value for '{path_label}' MUST be >= {int(spec.minimum)}, got {value}."
            )
        return
    if kind is ConfigParamKind.FLOAT:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ConfigCliError(
                f"Value for '{path_label}' MUST be a JSON number, got "
                f"{render_json_value(value)}."
            )
        numeric_value = float(value)
        if not math.isfinite(numeric_value):
            raise ConfigCliError(f"Value for '{path_label}' MUST be a finite number.")
        if spec.minimum is not None and numeric_value < spec.minimum:
            raise ConfigCliError(
                f"Value for '{path_label}' MUST be >= {int(spec.minimum)}, "
                f"got {numeric_value}."
            )
        return
    if kind is ConfigParamKind.BOOLEAN:
        if not isinstance(value, bool):
            raise ConfigCliError(
                f"Value for '{path_label}' MUST be a JSON boolean, got "
                f"{render_json_value(value)}."
            )
        return
    if kind in (ConfigParamKind.STRING, ConfigParamKind.OPTIONAL_STRING):
        if value is None and kind is ConfigParamKind.OPTIONAL_STRING:
            return
        if not isinstance(value, str):
            raise ConfigCliError(
                f"Value for '{path_label}' MUST be a JSON string, got "
                f"{render_json_value(value)}."
            )
        if spec.non_empty and not value:
            raise ConfigCliError(
                f"Value for '{path_label}' MUST be a non-empty string."
            )
        return
    if kind is ConfigParamKind.SELECTION:
        allowed_values = tuple(option for option, _ in spec.selection_options)
        if not isinstance(value, str) or value not in allowed_values:
            raise ConfigCliError(
                f"Value for '{path_label}' MUST be one of "
                f"{', '.join(render_json_value(item) for item in allowed_values)}."
            )
        return
    raise ConfigCliError(f"Unsupported schema kind '{kind.value}' for '{path_label}'.")


def validate_config_document(document: Any) -> None:
    """
    @brief Validate one complete configuration document against the schema.
    @details Rejects non-object roots, fields absent from `RuntimeConfig`, and
    values violating declared constraints, then confirms the document against
    the `RuntimeConfig` model. Missing fields are accepted because defaults
    apply at load time.
    @param document {Any} Decoded configuration document.
    @return {None} Function return value.
    @throws {ConfigCliError} When the document is not schema-valid.
    @satisfies REQ-208
    @satisfies REQ-209
    """
    if not isinstance(document, dict):
        raise ConfigCliError("Configuration document root MUST be a JSON object.")
    unknown_keys = sorted(
        key for key in document if key not in CONFIG_PARAM_SPECS_BY_KEY
    )
    if unknown_keys:
        raise ConfigCliError(
            "Configuration document contains unknown field(s): "
            f"{', '.join(unknown_keys)}."
        )
    for spec in CONFIG_PARAM_SPECS:
        if spec.key in document:
            validate_schema_value(spec, document[spec.key], path_label=spec.key)
    try:
        RuntimeConfig.model_validate(document)
    except ValidationError as error:
        raise ConfigCliError(
            f"Configuration document failed schema validation: {error}"
        ) from error


def configuration_file_path() -> Path:
    """
    @brief Resolve the global configuration file path.
    @details Resolves the module-level `RUNTIME_CONFIG_PATH` at call time so the
    configuration CLI always targets `~/.config/aibar/config.json`; the
    application defines no project-local configuration layer.
    @return {Path} Absolute global configuration file path.
    @satisfies REQ-205
    """
    return config_module.RUNTIME_CONFIG_PATH


def display_configuration_path(path: Path) -> str:
    """
    @brief Render one configuration path with a `~` home abbreviation.
    @param path {Path} Absolute configuration path.
    @return {str} Display path text.
    @satisfies REQ-238
    """
    home = Path.home()
    try:
        return f"~/{path.relative_to(home)}"
    except ValueError:
        return str(path)


def schema_default_document() -> dict[str, Any]:
    """
    @brief Build the default configuration document from the schema.
    @details Uses `RuntimeConfig` model defaults so bootstrap content matches
    the canonical schema exactly.
    @return {dict[str, Any]} JSON-compatible default document.
    @satisfies REQ-206
    """
    return RuntimeConfig().model_dump(mode="json")


def load_config_document(*, create_if_missing: bool) -> dict[str, Any]:
    """
    @brief Load and strictly validate the global configuration document.
    @details Creates the configuration directory and file from schema defaults
    only when the file is absent and `create_if_missing` is true. Unparsable
    JSON, non-object roots, and schema-invalid documents raise instead of being
    rewritten.
    @param create_if_missing {bool} Bootstrap the file when it is missing.
    @return {dict[str, Any]} Validated configuration document.
    @throws {ConfigCliError} When the file is missing or not schema-valid.
    @satisfies REQ-206
    @satisfies REQ-207
    @satisfies REQ-208
    """
    path = configuration_file_path()
    display_path = display_configuration_path(path)
    if not path.exists():
        if not create_if_missing:
            raise ConfigCliError(f"Configuration file {display_path} is absent.")
        document = schema_default_document()
        try:
            write_json_document_atomic(path, document)
        except OSError as error:
            raise ConfigCliError(f"Cannot create {display_path}: {error}") from error
        return document
    try:
        raw_bytes = path.read_bytes()
    except OSError as error:
        raise ConfigCliError(f"Cannot read {display_path}: {error}") from error
    try:
        decoded = json.loads(raw_bytes.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ConfigCliError(
            f"Configuration file {display_path} is not valid UTF-8."
        ) from error
    except ValueError as error:
        raise ConfigCliError(
            f"Configuration file {display_path} is not valid JSON: {error}"
        ) from error
    validate_config_document(decoded)
    return decoded


def get_config_value(document: dict[str, Any], resolved: ResolvedConfigPath) -> Any:
    """
    @brief Read one value addressed by a resolved canonical path.
    @details Fields absent from the document resolve to schema defaults; a map
    key absent from the stored map is a path error.
    @param document {dict[str, Any]} Validated configuration document.
    @param resolved {ResolvedConfigPath} Resolved canonical path.
    @return {Any} Addressed value.
    @throws {ConfigCliError} When the map key is not set.
    @satisfies REQ-202
    @satisfies REQ-209
    """
    if resolved.map_key is None:
        if resolved.spec.key in document:
            return document[resolved.spec.key]
        return field_default(resolved.spec.key)
    stored_map = document.get(resolved.spec.key, field_default(resolved.spec.key))
    if not isinstance(stored_map, dict) or resolved.map_key not in stored_map:
        raise ConfigCliError(
            f"Path '{resolved.canonical_path}' does not exist: map key "
            f"'{resolved.map_key}' is not set in '{resolved.spec.key}'."
        )
    return stored_map[resolved.map_key]


def _parse_json_text(raw_value: str) -> tuple[bool, Any]:
    """
    @brief Attempt to decode one CLI value as JSON.
    @param raw_value {str} Raw CLI argument text.
    @return {tuple[bool, Any]} Pair `(is_json, decoded_value)`.
    @satisfies REQ-210
    """
    try:
        return (True, json.loads(raw_value))
    except ValueError:
        return (False, None)


def parse_cli_value(resolved: ResolvedConfigPath, raw_value: str) -> Any:
    """
    @brief Parse one CLI value into the schema type of its target path.
    @details JSON-parseable input must already match the target type. Non-JSON
    text is accepted as a literal string only for `String` and
    `Optional[String]` targets. Whole-map targets require one JSON object.
    @param resolved {ResolvedConfigPath} Resolved canonical path.
    @param raw_value {str} Raw CLI argument text.
    @return {Any} Typed schema value.
    @throws {ConfigCliError} When parsing or type-checking fails.
    @satisfies REQ-210
    @satisfies REQ-211
    """
    spec = resolved.spec
    path_label = resolved.canonical_path
    if spec.kind is ConfigParamKind.MAP and resolved.map_key is None:
        is_json, decoded = _parse_json_text(raw_value)
        if not is_json or not isinstance(decoded, dict):
            raise ConfigCliError(
                f"Value for '{path_label}' MUST be one JSON object such as "
                f"{render_json_value(dict(spec.full_map_example))}."
            )
        validate_schema_value(spec, decoded, path_label=path_label)
        return decoded
    target_kind = (
        spec.map_value_kind
        if spec.kind is ConfigParamKind.MAP and spec.map_value_kind is not None
        else spec.kind
    )
    is_json, decoded = _parse_json_text(raw_value)
    if target_kind in (
        ConfigParamKind.STRING,
        ConfigParamKind.OPTIONAL_STRING,
        ConfigParamKind.SELECTION,
    ):
        if is_json and isinstance(decoded, str):
            parsed_value: Any = decoded
        elif (
            is_json
            and decoded is None
            and target_kind is (ConfigParamKind.OPTIONAL_STRING)
        ):
            parsed_value = None
        elif is_json:
            raise ConfigCliError(
                f"Value for '{path_label}' is JSON but not a string; quote the "
                "text to store it as a string."
            )
        else:
            parsed_value = raw_value
        if spec.kind is ConfigParamKind.MAP:
            _validate_scalar_value(
                spec, target_kind, parsed_value, path_label=path_label
            )
        else:
            validate_schema_value(spec, parsed_value, path_label=path_label)
        return parsed_value
    if not is_json:
        raise ConfigCliError(
            f"Value for '{path_label}' MUST be valid JSON of type "
            f"'{target_kind.value}'."
        )
    if target_kind is ConfigParamKind.FLOAT and isinstance(decoded, (int, float)):
        decoded = float(decoded)
    _validate_scalar_value(spec, target_kind, decoded, path_label=path_label)
    return decoded


def set_config_value(
    document: dict[str, Any], resolved: ResolvedConfigPath, raw_value: str
) -> dict[str, Any]:
    """
    @brief Apply one `--set` mutation to a copy of the configuration document.
    @details Parses the CLI value into the schema type, replaces the addressed
    field or map entry, and validates the complete candidate document before it
    is returned for persistence.
    @param document {dict[str, Any]} Validated configuration document.
    @param resolved {ResolvedConfigPath} Resolved canonical path.
    @param raw_value {str} Raw CLI argument text.
    @return {dict[str, Any]} Validated candidate document.
    @throws {ConfigCliError} When parsing or validation fails.
    @satisfies REQ-208
    @satisfies REQ-221
    """
    parsed_value = parse_cli_value(resolved, raw_value)
    candidate = copy.deepcopy(document)
    if resolved.map_key is None:
        candidate[resolved.spec.key] = parsed_value
    else:
        stored_map = candidate.get(resolved.spec.key)
        updated_map = dict(stored_map) if isinstance(stored_map, dict) else {}
        updated_map[resolved.map_key] = parsed_value
        candidate[resolved.spec.key] = updated_map
    validate_config_document(candidate)
    return candidate


def unset_config_value(
    document: dict[str, Any], resolved: ResolvedConfigPath
) -> tuple[dict[str, Any], bool]:
    """
    @brief Apply one `--unset` mutation to a copy of the configuration document.
    @details Field resets remove the addressed field so schema defaults apply;
    map resets delete exactly the addressed map key. Missing fields are a no-op,
    while missing map keys are rejected.
    @param document {dict[str, Any]} Validated configuration document.
    @param resolved {ResolvedConfigPath} Resolved canonical path.
    @return {tuple[dict[str, Any], bool]} Candidate document plus change flag.
    @throws {ConfigCliError} When the addressed map key is absent.
    @satisfies REQ-219
    @satisfies REQ-220
    """
    candidate = copy.deepcopy(document)
    if resolved.map_key is None:
        if resolved.spec.key not in candidate:
            return candidate, False
        del candidate[resolved.spec.key]
        validate_config_document(candidate)
        return candidate, True
    stored_map = candidate.get(resolved.spec.key)
    if not isinstance(stored_map, dict) or resolved.map_key not in stored_map:
        raise ConfigCliError(
            f"Path '{resolved.canonical_path}' does not exist: map key "
            f"'{resolved.map_key}' is not set in '{resolved.spec.key}'."
        )
    updated_map = dict(stored_map)
    del updated_map[resolved.map_key]
    candidate[resolved.spec.key] = updated_map
    validate_config_document(candidate)
    return candidate, True


def _persist_config_document(document: dict[str, Any]) -> None:
    """
    @brief Persist one validated configuration document atomically.
    @param document {dict[str, Any]} Validated configuration document.
    @return {None} Function return value.
    @throws {ConfigCliError} When the atomic write fails.
    @satisfies REQ-212
    @satisfies REQ-214
    """
    path = configuration_file_path()
    try:
        write_json_document_atomic(path, document)
    except OSError as error:
        raise ConfigCliError(
            f"Cannot write {display_configuration_path(path)}: {error}"
        ) from error


def format_print_parameter(
    document: dict[str, Any], spec: ConfigParamSpec
) -> ConfigTreeNode:
    """
    @brief Build one `--print` node for a configuration parameter.
    @details Scalars render as JSON literals with a default/custom status suffix.
    Dynamic maps render an entry-count summary with a `Key | Value` table, or an
    actionable empty-map hint without any table.
    @param document {dict[str, Any]} Validated configuration document.
    @param spec {ConfigParamSpec} Schema parameter declaration.
    @return {ConfigTreeNode} Parameter node with attached detail lines.
    @satisfies REQ-228
    @satisfies REQ-229
    @satisfies REQ-230
    """
    default_value = field_default(spec.key)
    stored_value = document.get(spec.key, default_value)
    if spec.kind is ConfigParamKind.MAP:
        stored_map = stored_value if isinstance(stored_value, dict) else {}
        entries = sorted(stored_map.items())
        if not entries:
            example_path = f"{spec.key}:{spec.map_example_key}"
            heading = (
                f"{spec.key} = (empty map | set key: "
                f"{format_set_command(example_path, spec.map_example_value)})"
            )
            return ConfigTreeNode(
                token=spec.key,
                canonical_path=spec.key,
                kind=ConfigNodeKind.PARAMETER,
                heading=_verify_single_line(heading),
            )
        heading = (
            f"{spec.key} = ({len(entries)} entries | key target: {spec.key}:<Key>)"
        )
        rows = tuple(
            (render_json_value(entry_key), render_json_value(entry_value))
            for entry_key, entry_value in entries
        )
        return ConfigTreeNode(
            token=spec.key,
            canonical_path=spec.key,
            kind=ConfigNodeKind.PARAMETER,
            heading=_verify_single_line(heading),
            details=format_config_table(("Key", "Value"), rows),
        )
    rendered_value = render_json_value(stored_value)
    if stored_value == default_value:
        status = "(default)"
    else:
        status = f"(custom | default: {render_json_value(default_value)})"
    heading = f"{spec.key} = {rendered_value} {status}"
    return ConfigTreeNode(
        token=spec.key,
        canonical_path=spec.key,
        kind=ConfigNodeKind.PARAMETER,
        heading=_verify_single_line(heading),
    )


def build_print_tree(
    document: dict[str, Any], path_text: str | None = None
) -> ConfigTreeNode:
    """
    @brief Build the `--print` display tree for a whole document or one path.
    @details With no path the virtual root renders every schema parameter in
    declaration order. With a path the addressed parameter (or map entry) is the
    marker-free display root without invented ancestors.
    @param document {dict[str, Any]} Validated configuration document.
    @param path_text {str | None} Optional canonical path selector.
    @return {ConfigTreeNode} Display root node.
    @throws {ConfigCliError} When the selected path is invalid.
    @satisfies REQ-223
    @satisfies REQ-226
    """
    if not path_text:
        children = tuple(
            format_print_parameter(document, spec) for spec in CONFIG_PARAM_SPECS
        )
        return ConfigTreeNode(
            token=VIRTUAL_ROOT_LABEL,
            canonical_path="",
            kind=ConfigNodeKind.SECTION,
            heading=ROOT_PRINT_HEADING,
            children=children,
        )
    resolved = resolve_config_path(path_text)
    if resolved.map_key is None:
        return format_print_parameter(document, resolved.spec)
    selected_value = get_config_value(document, resolved)
    details: tuple[str, ...] = ()
    if resolved.spec.map_value_kind is ConfigParamKind.SELECTION:
        details = format_selection_state_table(resolved.spec, selected_value)
    return ConfigTreeNode(
        token=resolved.canonical_path,
        canonical_path=resolved.canonical_path,
        kind=ConfigNodeKind.PARAMETER,
        heading=_verify_single_line(
            f"{resolved.canonical_path} = {render_json_value(selected_value)}"
        ),
        details=details,
    )


def _selection_rows(spec: ConfigParamSpec) -> tuple[tuple[str, str, str], ...]:
    """
    @brief Build `Allowed Values` rows for one selection domain.
    @param spec {ConfigParamSpec} Map parameter carrying the selection domain.
    @return {tuple[tuple[str, str, str], ...]} Value, default marker, and meaning.
    @satisfies REQ-232
    """
    return tuple(
        (
            render_json_value(option_value),
            render_json_value(option_value)
            if option_value == spec.selection_default
            else "-",
            meaning,
        )
        for option_value, meaning in spec.selection_options
    )


def format_selection_state_table(
    spec: ConfigParamSpec, current_value: Any
) -> tuple[str, ...]:
    """
    @brief Render the `Sel | Value` table for one selection-typed value.
    @details Marks exactly one row with `[*]` for the active selection and every
    remaining domain member with `[ ]`, using the shared measured table
    formatter.
    @param spec {ConfigParamSpec} Schema parameter carrying the selection domain.
    @param current_value {Any} Currently stored selection value.
    @return {tuple[str, ...]} Table lines for the attached detail block.
    @satisfies REQ-232
    """
    rows = tuple(
        (
            "[*]" if option_value == current_value else "[ ]",
            render_json_value(option_value),
        )
        for option_value, _ in spec.selection_options
    )
    return format_config_table(("Sel", "Value"), rows)


def build_info_parameter(spec: ConfigParamSpec) -> ConfigTreeNode:
    """
    @brief Build one `--info` node documenting a configuration parameter.
    @details Emits the typed heading plus attached `Default`, `Set cmd`,
    `Reset cmd`/map action, and selection-domain detail lines, all with complete
    canonical paths and schema-derived valid examples.
    @param spec {ConfigParamSpec} Schema parameter declaration.
    @return {ConfigTreeNode} Documentation node with attached detail lines.
    @satisfies REQ-231
    @satisfies REQ-232
    @satisfies REQ-235
    """
    default_value = field_default(spec.key)
    details: list[str] = [
        f"Default : {render_json_value(default_value)} "
        f"(restored via: {format_unset_command(spec.key)})",
    ]
    if spec.kind is ConfigParamKind.MAP:
        example_path = f"{spec.key}:{spec.map_example_key}"
        details.append(
            f"Set key : {format_set_command(example_path, spec.map_example_value)}"
        )
        details.append(f"Remove key : {format_unset_command(example_path)}")
        details.append(
            "Full overwrite : "
            f"{format_set_command(spec.key, dict(spec.full_map_example))}"
        )
        details.append(f"Reset map : {format_unset_command(spec.key)}")
        if spec.map_value_kind is ConfigParamKind.SELECTION:
            details.append("Allowed Values:")
            details.extend(
                format_config_table(
                    ("Value", "Default", "Meaning"), _selection_rows(spec)
                )
            )
            details.append(
                "Note : Missing provider keys fall back to "
                f"{render_json_value(config_module.DEFAULT_CURRENCY_SYMBOL)}."
            )
        else:
            details.append(
                "Keys : " + ", ".join(provider.value for provider in ProviderName)
            )
            details.append("Note : Missing provider keys are treated as enabled.")
    else:
        details.append(f"Set cmd : {format_set_command(spec.key, spec.example_value)}")
        details.append(f"Reset cmd : {format_unset_command(spec.key)}")
    heading = f"{spec.key} - [{spec.type_label}] {spec.description}"
    return ConfigTreeNode(
        token=spec.key,
        canonical_path=spec.key,
        kind=ConfigNodeKind.PARAMETER,
        heading=_verify_single_line(heading),
        details=tuple(_verify_single_line(line) for line in details),
    )


def build_info_map_key(resolved: ResolvedConfigPath) -> ConfigTreeNode:
    """
    @brief Build one `--info` node documenting a dynamic map key.
    @details Documents the resolved map-entry domain, its effective fallback, and
    the copyable `--set`/`--unset` commands for the concrete key.
    @param resolved {ResolvedConfigPath} Resolved canonical map-entry path.
    @return {ConfigTreeNode} Documentation node with attached detail lines.
    @satisfies REQ-223
    @satisfies REQ-231
    """
    spec = resolved.spec
    canonical_path = resolved.canonical_path
    if spec.map_value_kind is ConfigParamKind.SELECTION:
        type_label = "Selection: " + ", ".join(
            value for value, _ in spec.selection_options
        )
        description = (
            f"Currency symbol for provider '{resolved.map_key}'; a missing key "
            f"falls back to {render_json_value(spec.selection_default)}."
        )
        default_text = render_json_value(spec.selection_default)
    else:
        type_label = "Boolean"
        description = (
            f"Provider activation flag for '{resolved.map_key}'; a missing key "
            "enables the provider."
        )
        default_text = "true"
    details: list[str] = [
        f"Default : {default_text}",
        f"Set cmd : {format_set_command(canonical_path, spec.map_example_value)}",
        f"Remove key : {format_unset_command(canonical_path)}",
    ]
    if spec.map_value_kind is ConfigParamKind.SELECTION:
        details.append("Allowed Values:")
        details.extend(
            format_config_table(("Value", "Default", "Meaning"), _selection_rows(spec))
        )
    heading = f"{canonical_path} - [{type_label}] {description}"
    return ConfigTreeNode(
        token=canonical_path,
        canonical_path=canonical_path,
        kind=ConfigNodeKind.PARAMETER,
        heading=_verify_single_line(heading),
        details=tuple(_verify_single_line(line) for line in details),
    )


def build_info_tree(path_text: str | None = None) -> ConfigTreeNode:
    """
    @brief Build the `--info` display tree for the whole schema or one path.
    @details Uses the same node model as `--print`; only the heading and detail
    formatters differ. A requested path becomes the marker-free display root.
    @param path_text {str | None} Optional canonical path selector.
    @return {ConfigTreeNode} Documentation root node.
    @throws {ConfigCliError} When the selected path is invalid.
    @satisfies REQ-222
    @satisfies REQ-223
    """
    if not path_text:
        children = tuple(build_info_parameter(spec) for spec in CONFIG_PARAM_SPECS)
        return ConfigTreeNode(
            token=VIRTUAL_ROOT_LABEL,
            canonical_path="",
            kind=ConfigNodeKind.SECTION,
            heading=ROOT_INFO_HEADING,
            children=children,
        )
    resolved = resolve_config_path(path_text)
    if resolved.map_key is None:
        return build_info_parameter(resolved.spec)
    return build_info_map_key(resolved)


def render_config_tree(root: ConfigTreeNode) -> tuple[str, ...]:
    """
    @brief Render one configuration tree into deterministic output lines.
    @details Implements the normative prefix algorithm: the display root has no
    marker, every real node has exactly one `├── ` or `└── ` marker preceded by
    one ancestor segment per ancestor with a later sibling, and every attached
    detail line uses the owner ancestor segments plus one own continuation
    segment. Table lines are details and never add a structural depth.
    @param root {ConfigTreeNode} Display root node.
    @return {tuple[str, ...]} Physical output lines in emission order.
    @satisfies REQ-222
    @satisfies REQ-224
    @satisfies REQ-225
    @satisfies REQ-226
    """
    lines: list[str] = [root.heading]
    lines.extend(f"{TREE_INDENT}{detail}" for detail in root.details)
    child_count = len(root.children)
    for index, child in enumerate(root.children):
        _emit_config_node(child, [], index == child_count - 1, lines)
    return tuple(lines)


def _emit_config_node(
    node: ConfigTreeNode,
    ancestor_has_next: list[bool],
    is_last: bool,
    lines: list[str],
) -> None:
    """
    @brief Emit one real configuration node and its subtree.
    @param node {ConfigTreeNode} Node to emit.
    @param ancestor_has_next {list[bool]} Later-sibling flags of real ancestors.
    @param is_last {bool} True when the node is the final real sibling.
    @param lines {list[str]} Mutable output accumulator.
    @return {None} Function return value.
    @satisfies REQ-224
    @satisfies REQ-225
    """
    prefix = "".join(
        TREE_CONTINUE if has_next else TREE_INDENT for has_next in ancestor_has_next
    )
    edge = TREE_LAST if is_last else TREE_BRANCH
    lines.append(f"{prefix}{edge}{node.heading}")
    detail_prefix = prefix + (TREE_INDENT if is_last else TREE_CONTINUE)
    lines.extend(f"{detail_prefix}{detail}" for detail in node.details)
    child_count = len(node.children)
    for index, child in enumerate(node.children):
        _emit_config_node(
            child,
            [*ancestor_has_next, not is_last],
            index == child_count - 1,
            lines,
        )


def _resolve_text_stream(stream: TextIO | None, *, error: bool) -> TextIO:
    """
    @brief Resolve one text output stream with late-bound defaults.
    @param stream {TextIO | None} Explicit stream override.
    @param error {bool} True to fall back to stderr instead of stdout.
    @return {TextIO} Resolved text stream.
    @satisfies REQ-217
    """
    if stream is not None:
        return stream
    return sys.stderr if error else sys.stdout


def _write_lines(stream: TextIO, lines: Sequence[str]) -> None:
    """
    @brief Write complete output lines to one text stream.
    @param stream {TextIO} Destination text stream.
    @param lines {Sequence[str]} Lines without trailing newlines.
    @return {None} Function return value.
    @satisfies REQ-217
    """
    for line in lines:
        stream.write(f"{line}\n")
    stream.flush()


def _write_diagnostic(stream: TextIO, message: str) -> None:
    """
    @brief Write one error diagnostic line to stderr.
    @param stream {TextIO} Destination error stream.
    @param message {str} Diagnostic text.
    @return {None} Function return value.
    @satisfies REQ-217
    """
    stream.write(f"error: {message}\n")
    stream.flush()


def run_config_print(
    path_text: str | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """
    @brief Execute `--print` for the whole configuration or one path.
    @param path_text {str | None} Optional canonical path selector.
    @param stdout {TextIO | None} Optional stdout override.
    @param stderr {TextIO | None} Optional stderr override.
    @return {int} Process exit status.
    @satisfies REQ-217
    @satisfies REQ-223
    """
    output = _resolve_text_stream(stdout, error=False)
    error_output = _resolve_text_stream(stderr, error=True)
    try:
        document = load_config_document(create_if_missing=True)
        root = build_print_tree(document, path_text)
        lines = render_config_tree(root)
    except ConfigCliError as error:
        _write_diagnostic(error_output, str(error))
        return 1
    _write_lines(output, lines)
    return 0


def run_config_info(
    path_text: str | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """
    @brief Execute `--info` for the whole schema or one path.
    @param path_text {str | None} Optional canonical path selector.
    @param stdout {TextIO | None} Optional stdout override.
    @param stderr {TextIO | None} Optional stderr override.
    @return {int} Process exit status.
    @satisfies REQ-217
    @satisfies REQ-222
    """
    output = _resolve_text_stream(stdout, error=False)
    error_output = _resolve_text_stream(stderr, error=True)
    try:
        root = build_info_tree(path_text)
        lines = render_config_tree(root)
    except ConfigCliError as error:
        _write_diagnostic(error_output, str(error))
        return 1
    _write_lines(output, lines)
    return 0


def run_config_print_raw(
    *,
    binary_stdout: BinaryIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """
    @brief Execute `--print-raw` byte-preserving output.
    @details Bootstraps a missing configuration file from schema defaults, then
    emits the selected file bytes exactly as stored without validation,
    reformatting, headings, or appended text.
    @param binary_stdout {BinaryIO | None} Optional binary stdout override.
    @param stderr {TextIO | None} Optional stderr override.
    @return {int} Process exit status.
    @satisfies REQ-216
    @satisfies REQ-217
    """
    error_output = _resolve_text_stream(stderr, error=True)
    path = configuration_file_path()
    try:
        if not path.exists():
            write_json_document_atomic(path, schema_default_document())
        raw_bytes = path.read_bytes()
    except OSError as error:
        _write_diagnostic(
            error_output,
            f"Cannot read {display_configuration_path(path)}: {error}",
        )
        return 1
    if binary_stdout is not None:
        binary_stdout.write(raw_bytes)
        binary_stdout.flush()
        return 0
    fallback_buffer = getattr(sys.stdout, "buffer", None)
    if fallback_buffer is not None:
        fallback_buffer.write(raw_bytes)
        fallback_buffer.flush()
        return 0
    sys.stdout.write(raw_bytes.decode("utf-8", errors="replace"))
    sys.stdout.flush()
    return 0


def run_config_get(
    path_text: str,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """
    @brief Execute `--get` for one canonical path.
    @details Emits exactly one JSON value plus one newline on stdout so the
    output can be piped into JSON tools.
    @param path_text {str} Canonical path text.
    @param stdout {TextIO | None} Optional stdout override.
    @param stderr {TextIO | None} Optional stderr override.
    @return {int} Process exit status.
    @satisfies REQ-215
    @satisfies REQ-217
    """
    output = _resolve_text_stream(stdout, error=False)
    error_output = _resolve_text_stream(stderr, error=True)
    try:
        resolved = resolve_config_path(path_text)
        document = load_config_document(create_if_missing=True)
        value = get_config_value(document, resolved)
    except ConfigCliError as error:
        _write_diagnostic(error_output, str(error))
        return 1
    _write_lines(output, (render_json_value(value),))
    return 0


def run_config_set(
    path_text: str,
    raw_value: str,
    *,
    stderr: TextIO | None = None,
) -> int:
    """
    @brief Execute `--set` for one canonical path and value.
    @param path_text {str} Canonical path text.
    @param raw_value {str} Raw CLI value text.
    @param stderr {TextIO | None} Optional stderr override.
    @return {int} Process exit status.
    @satisfies REQ-217
    @satisfies REQ-218
    @satisfies REQ-221
    """
    error_output = _resolve_text_stream(stderr, error=True)
    try:
        resolved = resolve_config_path(path_text)
        document = load_config_document(create_if_missing=True)
        candidate = set_config_value(document, resolved, raw_value)
        _persist_config_document(candidate)
    except ConfigCliError as error:
        _write_diagnostic(error_output, str(error))
        return 1
    return 0


def run_config_unset(
    path_text: str,
    *,
    stderr: TextIO | None = None,
) -> int:
    """
    @brief Execute `--unset` for one canonical path.
    @param path_text {str} Canonical path text.
    @param stderr {TextIO | None} Optional stderr override.
    @return {int} Process exit status.
    @satisfies REQ-217
    @satisfies REQ-218
    @satisfies REQ-219
    """
    error_output = _resolve_text_stream(stderr, error=True)
    try:
        resolved = resolve_config_path(path_text)
        document = load_config_document(create_if_missing=True)
        candidate, changed = unset_config_value(document, resolved)
        if changed:
            _persist_config_document(candidate)
    except ConfigCliError as error:
        _write_diagnostic(error_output, str(error))
        return 1
    return 0


_verify_schema_alignment()
