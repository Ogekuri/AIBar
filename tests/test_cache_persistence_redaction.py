"""
@file
@brief ResultCache persistence and redaction tests for non-Claude providers.
@details Verifies successful non-Claude results are persisted, sensitive raw keys
are redacted on disk, and error results are not persisted.
@satisfies TST-003, CTN-004, DES-004
"""

import json
from pathlib import Path

from aibar.cache import ResultCache
from aibar.providers.base import ProviderName, ProviderResult, UsageMetrics, WindowPeriod


class TestResultCachePersistence:
    """
    @brief Verify non-Claude cache persistence and redaction behavior.
    @satisfies TST-003
    """

    def test_successful_non_claude_result_persists_with_redacted_raw(
        self,
        tmp_path: Path,
    ) -> None:
        """
        @brief Verify successful OpenAI result is persisted and sensitive keys are redacted.
        """
        cache = ResultCache(cache_dir=tmp_path)
        result = ProviderResult(
            provider=ProviderName.OPENAI,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(cost=1.25, requests=10),
            raw={
                "token": "secret-token",
                "nested": {
                    "authorization": "Bearer abc",
                    "key": "inner-key",
                    "keep": "value",
                },
            },
        )

        cache.set(result)

        disk_path = tmp_path / "openai_7d.json"
        assert disk_path.exists()

        persisted = json.loads(disk_path.read_text())
        assert persisted["raw"]["token"] == "[REDACTED]"
        assert persisted["raw"]["nested"]["authorization"] == "[REDACTED]"
        assert persisted["raw"]["nested"]["key"] == "[REDACTED]"
        assert persisted["raw"]["nested"]["keep"] == "value"

    def test_error_non_claude_result_is_not_persisted(self, tmp_path: Path) -> None:
        """
        @brief Verify error OpenAI result does not produce a disk cache payload.
        """
        cache = ResultCache(cache_dir=tmp_path)
        error_result = ProviderResult(
            provider=ProviderName.OPENAI,
            window=WindowPeriod.DAY_7,
            metrics=UsageMetrics(),
            error="API failed",
            raw={"status_code": 500, "token": "secret-token"},
        )

        cache.set(error_result)

        disk_path = tmp_path / "openai_7d.json"
        assert not disk_path.exists()
