"""
@file
@brief Optional GeminiAI system-auth integration verification.
@details Executes a live GeminiAI provider fetch using host OAuth credentials and
project configuration when explicitly enabled via environment variable.
@satisfies REQ-056
@satisfies REQ-057
@satisfies REQ-060
"""

import asyncio
import os

import pytest

from aibar.providers.base import WindowPeriod
from aibar.providers.geminiai import GeminiAIProvider


SYSTEM_AUTH_TEST_ENV = "AIBAR_RUN_GEMINIAI_SYSTEM_AUTH_TEST"


def test_geminiai_system_auth_fetch_reports_usage_and_billing() -> None:
    """
    @brief Validate live GeminiAI fetch with system OAuth credentials.
    @details The test is opt-in and skipped unless
    `AIBAR_RUN_GEMINIAI_SYSTEM_AUTH_TEST=1` is set.
    @return {None} Function return value.
    @satisfies REQ-056
    @satisfies REQ-057
    @satisfies REQ-060
    """
    if os.environ.get(SYSTEM_AUTH_TEST_ENV) != "1":
        pytest.skip("Set AIBAR_RUN_GEMINIAI_SYSTEM_AUTH_TEST=1 to run live system-auth test.")

    provider = GeminiAIProvider()
    if not provider.is_configured():
        pytest.skip("GeminiAI provider is not configured on this system.")

    result = asyncio.run(provider.fetch(WindowPeriod.DAY_7))
    assert not result.is_error, result.error
    assert result.metrics.requests is not None
    assert result.metrics.cost is not None
    assert isinstance(result.raw, dict)
    assert "billing" in result.raw
