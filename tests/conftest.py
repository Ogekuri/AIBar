"""
@file
@brief Pytest fixtures for CLI startup preflight determinism.
@details Provides an autouse fixture that replaces startup update preflight with
an in-memory no-op for tests that do not explicitly target startup preflight
behavior. This prevents real network side effects across legacy test modules.
@satisfies TST-031
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
