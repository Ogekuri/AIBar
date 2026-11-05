"""
@file
@brief Unit tests for PyPI release automation compliance.
@details Verifies the renamed release workflow `.github/workflows/release-pypi.yml`
preserves the canonical tag-triggered release pipeline, declares PyPI Trusted
Publishing via `pypa/gh-action-pypi-publish` under `id-token: write`, pins the
Python 3.12 setup version, and that `README.md` documents PyPI installation
commands. All assertions are static file-content checks: deterministic,
isolated, and free of network/filesystem side effects beyond repository reads.
@satisfies TST-065
@satisfies TST-068
@satisfies TST-069
@satisfies TST-071
@satisfies PRJ-012
@satisfies PRJ-013
"""

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "release-pypi.yml"
LEGACY_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "release-uvx+extension.yml"
README_PATH = REPO_ROOT / "README.md"
PYTHON_VERSION_PATH = REPO_ROOT / ".python-version"


@pytest.fixture(scope="module")
def workflow_text() -> str:
    """
    @brief Load the release workflow YAML text.
    @details Reads `.github/workflows/release-pypi.yml` from the repository
    root and fails fast when the renamed workflow file is missing.
    @return {str} Raw workflow file content.
    """
    assert WORKFLOW_PATH.exists(), f"release workflow not found at {WORKFLOW_PATH}"
    return WORKFLOW_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def readme_text() -> str:
    """
    @brief Load the repository README text.
    @details Reads `README.md` from the repository root for PyPI installation
    command assertions.
    @return {str} Raw README content.
    """
    assert README_PATH.exists(), f"README not found at {README_PATH}"
    return README_PATH.read_text(encoding="utf-8")


class TestWorkflowRename:
    """
    @brief Validates the workflow rename from release-uvx+extension to release-pypi.
    @details Ensures exactly one release workflow exists under the new PyPI
    filename and the legacy filename is absent per PRJ-012.
    """

    def test_legacy_workflow_absent(self) -> None:
        """
        @brief Verify the legacy workflow file is absent.
        @details Asserts `.github/workflows/release-uvx+extension.yml` no longer
        exists so Trusted Publisher workflow-name matching resolves to
        `release-pypi.yml` only.
        @return {None} Function return value.
        @satisfies TST-068
        @satisfies PRJ-012
        """
        assert not LEGACY_WORKFLOW_PATH.exists(), (
            "legacy workflow release-uvx+extension.yml must be removed"
        )

    def test_tag_trigger_preserved(self, workflow_text: str) -> None:
        """
        @brief Verify the canonical tag push trigger is preserved.
        @details Asserts the workflow still triggers on pushed `vX.Y.Z` tags so
        release automation behavior is unchanged by the rename.
        @param workflow_text {str} Workflow YAML content.
        @return {None} Function return value.
        @satisfies PRJ-012
        """
        assert "push:" in workflow_text
        assert "tags:" in workflow_text
        assert "'v[0-9]+.[0-9]+.[0-9]+'" in workflow_text


class TestTrustedPublishing:
    """
    @brief Validates PyPI Trusted Publishing configuration.
    @details Ensures the workflow grants the OIDC `id-token: write` permission
    and publishes Python distributions through
    `pypa/gh-action-pypi-publish@release/v1` per PRJ-013.
    """

    def test_id_token_permission_declared(self, workflow_text: str) -> None:
        """
        @brief Verify id-token write permission for OIDC minting.
        @details Asserts `id-token: write` appears in the workflow permissions
        block required by PyPI Trusted Publishing.
        @param workflow_text {str} Workflow YAML content.
        @return {None} Function return value.
        @satisfies TST-068
        @satisfies PRJ-013
        """
        assert "id-token: write" in workflow_text, (
            "workflow must grant id-token: write for Trusted Publishing"
        )

    def test_pypi_publish_action_declared(self, workflow_text: str) -> None:
        """
        @brief Verify the pypa publish action is used.
        @details Asserts the workflow references
        `pypa/gh-action-pypi-publish@release/v1` in a dedicated publish job so
        sdist and wheel distributions reach the PyPI project `aibar`.
        @param workflow_text {str} Workflow YAML content.
        @return {None} Function return value.
        @satisfies TST-068
        @satisfies PRJ-013
        """
        assert "pypa/gh-action-pypi-publish@release/v1" in workflow_text, (
            "workflow must publish via pypa/gh-action-pypi-publish"
        )

    def test_publish_job_gated_on_build(self, workflow_text: str) -> None:
        """
        @brief Verify publishing runs after the gated build job.
        @details Asserts a `publish-pypi` job exists and depends on
        `build-release`, which itself is gated on the master-branch check, so
        distributions publish only for tagged master releases.
        @param workflow_text {str} Workflow YAML content.
        @return {None} Function return value.
        @satisfies PRJ-013
        """
        assert "publish-pypi:" in workflow_text
        assert "needs: build-release" in workflow_text


class TestPythonVersionPins:
    """
    @brief Validates Python 3.12 interpreter pins.
    @details Ensures the workflow setup pins python-version "3.12" and the
    repository `.python-version` tracks 3.12 so release builds and local uv
    execution resolve the same interpreter floor.
    """

    def test_workflow_pins_python_312(self, workflow_text: str) -> None:
        """
        @brief Verify workflow python-version pin equals 3.12.
        @details Asserts `python-version: "3.12"` appears in the workflow
        setup steps.
        @param workflow_text {str} Workflow YAML content.
        @return {None} Function return value.
        @satisfies TST-065
        """
        assert 'python-version: "3.12"' in workflow_text, (
            'release workflow must pin python-version: "3.12"'
        )

    def test_python_version_file_tracks_312(self) -> None:
        """
        @brief Verify .python-version content equals 3.12.
        @details Asserts the repository root interpreter pin file contains the
        `3.12` floor used by uv run resolution.
        @return {None} Function return value.
        @satisfies TST-065
        """
        assert PYTHON_VERSION_PATH.exists(), ".python-version must be tracked"
        assert PYTHON_VERSION_PATH.read_text(encoding="utf-8").strip() == "3.12"


class TestReadmePyPIInstallDocs:
    """
    @brief Validates README PyPI installation documentation.
    @details Ensures the README documents `uv tool install aibar` and `uvx aibar`
    commands for the published PyPI package per PRJ-015.
    """

    def test_readme_documents_pypi_install_commands(self, readme_text: str) -> None:
        """
        @brief Verify README contains PyPI install and uvx commands.
        @details Asserts both `uv tool install aibar` and `uvx aibar` appear in
        the README installation documentation.
        @param readme_text {str} README content.
        @return {None} Function return value.
        @satisfies TST-069
        @satisfies PRJ-015
        """
        assert "uv tool install aibar" in readme_text, (
            "README must document uv tool install aibar from PyPI"
        )
        assert "uvx aibar" in readme_text, (
            "README must document uvx aibar live execution from PyPI"
        )


class TestReadmePipxPrimaryInstallDocs:
    """
    @brief Validates README pipx primary installation documentation.
    @details Ensures the README documents the canonical pipx bootstrap flow
    (`sudo apt install pipx`, `pipx ensurepath`, `pipx install aibar`) as the
    primary installation method, ordered before alternative pip and uv/uvx
    methods, per PRJ-016 and PRJ-017.
    """

    def test_readme_documents_pipx_primary_install_flow(
        self, readme_text: str
    ) -> None:
        """
        @brief Verify README contains the canonical pipx install commands.
        @details Asserts the exact pipx bootstrap sequence `sudo apt install
        pipx`, `pipx ensurepath`, and `pipx install aibar` appears in the
        README installation section.
        @param readme_text {str} README content.
        @return {None} Function return value.
        @satisfies TST-071
        @satisfies PRJ-016
        """
        assert "sudo apt install pipx" in readme_text, (
            "README must document sudo apt install pipx"
        )
        assert "pipx ensurepath" in readme_text, (
            "README must document pipx ensurepath"
        )
        assert "pipx install aibar" in readme_text, (
            "README must document pipx install aibar as primary method"
        )

    def test_pipx_flow_precedes_alternative_methods(
        self, readme_text: str
    ) -> None:
        """
        @brief Verify pipx primary flow is documented before alternatives.
        @details Asserts the `pipx install aibar` command index precedes the
        alternative `pip install aibar` and `uv tool install aibar` command
        indexes so the README presents pipx as the primary method.
        @param readme_text {str} README content.
        @return {None} Function return value.
        @satisfies TST-071
        @satisfies PRJ-017
        """
        pipx_index = readme_text.index("pipx install aibar")
        pip_index = readme_text.index("pip install aibar")
        uv_index = readme_text.index("uv tool install aibar")
        assert pipx_index < pip_index, (
            "pipx install must be documented before the pip alternative"
        )
        assert pipx_index < uv_index, (
            "pipx install must be documented before the uv alternative"
        )
