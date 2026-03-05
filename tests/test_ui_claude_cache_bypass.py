"""
@file
@brief Textual UI Claude cache-bypass test.
@details Verifies `AIBarUI.action_refresh` skips cache get/set operations for
Claude provider refresh cycles.
@satisfies REQ-009, CTN-004
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod
from aibar.ui import AIBarUI


class TestUIClaudeCacheBypass:
    """
    @brief Verify Textual refresh flow bypasses cache for Claude provider.
    @satisfies REQ-009
    """

    def test_action_refresh_skips_cache_for_claude(self) -> None:
        """
        @brief Verify action_refresh does not call cache.get/cache.set for Claude.
        """
        ui = AIBarUI()
        ui.window = WindowPeriod.DAY_7

        fresh_result = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(remaining=61.0, limit=100.0),
            raw={"five_hour": {"utilization": 39.0}},
        )

        provider = MagicMock()
        provider.is_configured.return_value = True
        provider.fetch = AsyncMock(return_value=fresh_result)

        ui.providers = {ProviderName.CLAUDE: provider}
        ui.cache = MagicMock()
        ui.cache.get.return_value = ProviderResult(
            provider=ProviderName.CLAUDE,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(remaining=99.0, limit=100.0),
            raw={"cached": True},
        )
        ui._get_card = MagicMock(return_value=None)
        ui._update_json_view = MagicMock()

        asyncio.run(ui.action_refresh())

        ui.cache.get.assert_not_called()
        ui.cache.set.assert_not_called()
        provider.fetch.assert_awaited_once_with(WindowPeriod.DAY_7)
        assert ui.results[ProviderName.CLAUDE].metrics.remaining == 61.0
