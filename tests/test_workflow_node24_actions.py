"""
@file
@brief Unit tests for Node24 runtime pinning of the release workflow actions.
@details Verifies that every JavaScript-based GitHub Action referenced by
`.github/workflows/release-pypi.yml` resolves to a major version whose upstream
`runs.using` runtime is `node24` or later, that Node20-era majors are absent,
and that transitional Node20 opt-out environment variables are not declared.
All assertions are static file-content checks: deterministic, isolated, and
free of network/clock/process side effects beyond repository reads.
@satisfies TST-080
@satisfies TST-081
@satisfies CTN-021
"""

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "release-pypi.yml"

#: Node24-native upstream major versions, verified against each action's
#: `action.yml` `runs.using` declaration at the resolved major tag.
NODE24_ACTION_MAJORS: dict[str, str] = {
    "actions/checkout": "actions/checkout@v7",
    "actions/setup-python": "actions/setup-python@v7",
    "astral-sh/setup-uv": "astral-sh/setup-uv@v10",
    "actions/attest-build-provenance": "actions/attest-build-provenance@v4",
    "mikepenz/release-changelog-builder-action": (
        "mikepenz/release-changelog-builder-action@v6"
    ),
    "softprops/action-gh-release": "softprops/action-gh-release@v3",
    "actions/upload-artifact": "actions/upload-artifact@v7",
    "actions/download-artifact": "actions/download-artifact@v8",
}

#: Node20-era major versions replaced by the Node24 migration; none may remain.
NODE20_LEGACY_PINS: tuple[str, ...] = (
    "actions/checkout@v4",
    "actions/setup-python@v5",
    "astral-sh/setup-uv@v3",
    "actions/attest-build-provenance@v1",
    "softprops/action-gh-release@v2",
    "actions/upload-artifact@v4",
    "actions/download-artifact@v4",
)

#: Transitional Node20 opt-out variables that must never appear in workflows.
TRANSITIONAL_NODE20_OPTOUT_VARS: tuple[str, ...] = (
    "ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION",
    "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24",
)

#: Node-independent action pin preserved unchanged by the migration.
NODE_INDEPENDENT_PUBLISH_PIN = "pypa/gh-action-pypi-publish@release/v1"


@pytest.fixture(scope="module")
def workflow_text() -> str:
    """
    @brief Load the release workflow YAML text.
    @details Reads `.github/workflows/release-pypi.yml` from the repository
    root and fails fast when the workflow file is missing.
    @return {str} Raw workflow file content.
    """
    assert WORKFLOW_PATH.exists(), f"release workflow not found at {WORKFLOW_PATH}"
    return WORKFLOW_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def workflow_uses_pins(workflow_text: str) -> list[str]:
    """
    @brief Extract every `uses:` action reference from the workflow text.
    @details Scans line starts for `uses:` declarations, strips surrounding
    whitespace, and returns the action reference tokens in file order.
    @param workflow_text {str} Workflow YAML content.
    @return {list[str]} Ordered action reference tokens without the `uses: ` prefix.
    """
    pins: list[str] = []
    for line in workflow_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("uses:"):
            pins.append(stripped.removeprefix("uses:").strip())
    return pins


class TestNode24ActionPins:
    """
    @brief Validates Node24 runtime migration of release workflow actions.
    @details Ensures the Node24-native major set is pinned, Node20-era majors
    are absent, transitional opt-out variables are absent, and the
    Node-independent Docker-based publish action is preserved.
    """

    def test_all_javascript_actions_pin_node24_native_majors(
        self, workflow_uses_pins: list[str]
    ) -> None:
        """
        @brief Verify every JavaScript-based action pin is Node24-native.
        @details Asserts each expected Node24-native major appears in the
        workflow `uses:` references so every JavaScript action resolves to an
        upstream `runs.using: node24` runtime or later.
        @param workflow_uses_pins {list[str]} Workflow action references.
        @return {None} Function return value.
        @satisfies TST-080
        @satisfies CTN-021
        """
        expected_output: list[str] = sorted(set(NODE24_ACTION_MAJORS.values()))
        for expected_pin in expected_output:
            assert expected_pin in workflow_uses_pins, (
                f"workflow must pin Node24-native major: {expected_pin}"
            )

    def test_workflow_declares_no_unexpected_javascript_pins(
        self, workflow_uses_pins: list[str]
    ) -> None:
        """
        @brief Verify workflow JavaScript pins are exactly the Node24-native set.
        @details Asserts every non-Node-independent pin belongs to the expected
        Node24-native map, so no unmanaged JavaScript action reference exists.
        @param workflow_uses_pins {list[str]} Workflow action references.
        @return {None} Function return value.
        @satisfies TST-080
        @satisfies CTN-021
        """
        expected_output: set[str] = (
            set(NODE24_ACTION_MAJORS.values()) | {NODE_INDEPENDENT_PUBLISH_PIN}
        )
        unexpected = [pin for pin in workflow_uses_pins if pin not in expected_output]
        assert unexpected == [], f"unexpected action pins found: {unexpected}"

    def test_node20_legacy_major_pins_absent(self, workflow_text: str) -> None:
        """
        @brief Verify Node20-era major pins are removed from the workflow.
        @details Asserts none of the pre-migration Node20-era pin strings
        remain in the workflow text so no action resolves to a Node20 runtime.
        @param workflow_text {str} Workflow YAML content.
        @return {None} Function return value.
        @satisfies TST-080
        """
        for legacy_pin in NODE20_LEGACY_PINS:
            assert legacy_pin not in workflow_text, (
                f"Node20-era pin must be removed: {legacy_pin}"
            )

    def test_transitional_node20_optout_vars_absent(self, workflow_text: str) -> None:
        """
        @brief Verify transitional Node20 opt-out variables are absent.
        @details Asserts neither `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION` nor
        `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` appears anywhere in the workflow,
        so runners keep the Node24 default without opt-out workarounds.
        @param workflow_text {str} Workflow YAML content.
        @return {None} Function return value.
        @satisfies TST-081
        """
        for optout_var in TRANSITIONAL_NODE20_OPTOUT_VARS:
            assert optout_var not in workflow_text, (
                f"transitional Node20 opt-out variable must be absent: {optout_var}"
            )

    def test_node_independent_publish_pin_preserved(
        self, workflow_uses_pins: list[str]
    ) -> None:
        """
        @brief Verify the Docker-based PyPI publish action pin is preserved.
        @details Asserts `pypa/gh-action-pypi-publish@release/v1` remains
        referenced because it executes in a Docker container and is
        Node-independent, preserving Trusted Publishing behavior unchanged.
        @param workflow_uses_pins {list[str]} Workflow action references.
        @return {None} Function return value.
        @satisfies TST-080
        """
        expected_output: str = NODE_INDEPENDENT_PUBLISH_PIN
        assert expected_output in workflow_uses_pins, (
            "Node-independent Docker publish action must remain pinned"
        )
