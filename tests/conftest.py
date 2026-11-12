"""
@file
@brief Pytest fixtures for CLI startup preflight determinism and GNOME extension isolation.
@details Provides autouse fixtures that replace startup update preflight with an
in-memory no-op for tests that do not explicitly target startup preflight
behavior, and that redirect the GNOME Shell extension installation target to a
pytest temporary directory so no test can mutate the developer's real extension
installation.
@satisfies TST-031, TST-009
"""

import pytest

import aibar.cli as cli_module


def _noop_startup_preflight() -> None:
    """
    @brief Execute no-op startup preflight for deterministic tests.
    @details Replaces startup update-check side effects during unit tests not
    focused on startup preflight behavior.
    @return {None} Function return value.
    """
    return None


@pytest.fixture(autouse=True)
def disable_startup_preflight_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    @brief Disable startup update-check preflight in tests by default.
    @details Applies a module-level monkeypatch so test cases only exercise
    startup preflight when they intentionally restore the real implementation.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies TST-031
    """
    monkeypatch.setattr(cli_module, "_run_startup_update_preflight", _noop_startup_preflight)


@pytest.fixture(autouse=True)
def isolate_gnome_extension_target_dir(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    @brief Redirect the GNOME extension installation target into a temporary directory.
    @details Sets `AIBAR_EXT_TARGET_DIR` to a function-scoped pytest temporary path so
    `gnome-install` and `gnome-uninstall` executions can never create, copy into, disable,
    enable, or remove the real `~/.local/share/gnome-shell/extensions/aibar@aibar.panel`
    installation. The override is the structural defense required by the HDT isolation
    principle: a test that forgets an explicit target mock still cannot corrupt the
    developer's installed extension.
    @param tmp_path {pathlib.Path} Pytest function-scoped temporary directory fixture.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies TST-009
    @satisfies REQ-026
    @satisfies REQ-081
    """
    isolated_target = tmp_path / "gnome-shell-extensions" / cli_module._EXT_UUID
    monkeypatch.setenv(cli_module._EXT_TARGET_DIR_ENV_VAR, str(isolated_target))
