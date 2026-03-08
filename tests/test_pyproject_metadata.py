"""
@file
@brief Unit tests for pyproject.toml metadata compliance.
@details Verifies PEP 621 metadata, build-system backend, console entry point,
runtime dependencies, and Python version constraint declared in pyproject.toml.
@satisfies TST-008
"""

import tomllib
from pathlib import Path

import pytest


PYPROJECT_PATH = Path(__file__).resolve().parent.parent / "pyproject.toml"


@pytest.fixture(scope="module")
def pyproject_data() -> dict:
    """
    @brief Load and parse pyproject.toml into a dictionary.
    @details Reads the pyproject.toml file from the repository root and
    parses it using tomllib. Fails if the file is missing.
    @return {dict} Parsed TOML content.
    """
    assert PYPROJECT_PATH.exists(), f"pyproject.toml not found at {PYPROJECT_PATH}"
    with open(PYPROJECT_PATH, "rb") as fh:
        return tomllib.load(fh)


class TestBuildSystem:
    """
    @brief Validates [build-system] section of pyproject.toml.
    @details Ensures hatchling is declared as the build backend per CTN-007.
    """

    def test_build_backend_is_hatchling(self, pyproject_data: dict) -> None:
        """
        @brief Verify build-backend is hatchling.
        @details Asserts that [build-system].build-backend equals 'hatchling.build'.
        @param pyproject_data {dict} Parsed pyproject.toml.
        """
        build_system = pyproject_data.get("build-system", {})
        assert build_system.get("build-backend") == "hatchling.build"

    def test_build_requires_includes_hatchling(self, pyproject_data: dict) -> None:
        """
        @brief Verify build requires includes hatchling.
        @details Asserts that [build-system].requires contains 'hatchling'.
        @param pyproject_data {dict} Parsed pyproject.toml.
        """
        build_system = pyproject_data.get("build-system", {})
        requires = build_system.get("requires", [])
        assert any("hatchling" in r for r in requires)


class TestProjectMetadata:
    """
    @brief Validates [project] section of pyproject.toml.
    @details Ensures required metadata fields are present per PRJ-006 and CTN-007.
    """

    def test_project_name(self, pyproject_data: dict) -> None:
        """
        @brief Verify project name is 'aibar'.
        @details Asserts [project].name equals 'aibar'.
        @param pyproject_data {dict} Parsed pyproject.toml.
        """
        project = pyproject_data.get("project", {})
        assert project.get("name") == "aibar"

    def test_requires_python(self, pyproject_data: dict) -> None:
        """
        @brief Verify requires-python constraint exists.
        @details Asserts [project].requires-python is a non-empty string
        containing a version constraint.
        @param pyproject_data {dict} Parsed pyproject.toml.
        """
        project = pyproject_data.get("project", {})
        requires_python = project.get("requires-python", "")
        assert requires_python, "requires-python must be defined"
        assert "3" in requires_python, "requires-python must reference Python 3.x"

    def test_dependencies_include_runtime_packages(self, pyproject_data: dict) -> None:
        """
        @brief Verify runtime dependencies are declared.
        @details Asserts [project].dependencies contains click, httpx, and pydantic
        as required by the application imports.
        @param pyproject_data {dict} Parsed pyproject.toml.
        """
        project = pyproject_data.get("project", {})
        deps = project.get("dependencies", [])
        dep_names = [
            d.split("[")[0]
            .split(">")[0]
            .split("<")[0]
            .split("=")[0]
            .split("!")[0]
            .strip()
            .lower()
            for d in deps
        ]
        for required in ("click", "httpx", "pydantic"):
            assert required in dep_names, f"Missing runtime dependency: {required}"


class TestConsoleEntryPoint:
    """
    @brief Validates [project.scripts] console entry point.
    @details Ensures the aibar console script points to aibar.cli:main per REQ-023.
    """

    def test_aibar_script_entry_point(self, pyproject_data: dict) -> None:
        """
        @brief Verify aibar console entry point.
        @details Asserts [project.scripts].aibar equals 'aibar.cli:main'.
        @param pyproject_data {dict} Parsed pyproject.toml.
        """
        scripts = pyproject_data.get("project", {}).get("scripts", {})
        assert "aibar" in scripts, "Missing 'aibar' entry in [project.scripts]"
        assert scripts["aibar"] == "aibar.cli:main"
