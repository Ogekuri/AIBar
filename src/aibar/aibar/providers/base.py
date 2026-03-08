"""
@file
@brief Base provider abstractions and normalized metric models.
@details Defines provider/window enums, normalized usage/result payloads, provider exception hierarchy, and the abstract provider interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WindowPeriod(str, Enum):
    """
    @brief Define window period component.
    @details Encapsulates window period state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    HOUR_5 = "5h"
    DAY_7 = "7d"
    DAY_30 = "30d"


class ProviderName(str, Enum):
    """
    @brief Define provider name component.
    @details Encapsulates provider name state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    CLAUDE = "claude"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    COPILOT = "copilot"
    CODEX = "codex"


class UsageMetrics(BaseModel):
    """
    @brief Define usage metrics component.
    @details Encapsulates normalized provider usage metrics for AIBar runtime flows.
    Field `currency_symbol` annotates all monetary fields (`cost`, `remaining`, `limit`)
    and defaults to `"$"` when not resolved from API response or provider config.
    @satisfies CTN-002
    @satisfies REQ-050
    @satisfies REQ-051
    @satisfies REQ-052
    @satisfies REQ-053
    """

    cost: float | None = Field(default=None, description="Total cost in USD")
    requests: int | None = Field(default=None, description="Number of API requests")
    input_tokens: int | None = Field(default=None, description="Total input tokens")
    output_tokens: int | None = Field(default=None, description="Total output tokens")
    remaining: float | None = Field(default=None, description="Remaining quota/budget")
    limit: float | None = Field(default=None, description="Total quota/budget limit")
    reset_at: datetime | None = Field(default=None, description="When quota resets")
    currency_symbol: str = Field(default="$", description="Currency symbol for monetary fields (cost, remaining, limit)")

    @property
    def usage_percent(self) -> float | None:
        """
        @brief Execute usage percent.
        @details Applies usage percent logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {float | None} Function return value.
        """
        if self.limit is None or self.limit == 0:
            return None
        if self.remaining is not None:
            return ((self.limit - self.remaining) / self.limit) * 100
        return None

    @property
    def total_tokens(self) -> int | None:
        """
        @brief Execute total tokens.
        @details Applies total tokens logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {int | None} Function return value.
        """
        if self.input_tokens is None and self.output_tokens is None:
            return None
        return (self.input_tokens or 0) + (self.output_tokens or 0)


class ProviderResult(BaseModel):
    """
    @brief Define provider result component.
    @details Encapsulates provider result state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    provider: ProviderName
    window: WindowPeriod
    metrics: UsageMetrics
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    raw: dict[str, Any] = Field(default_factory=dict, description="Raw API response")
    error: str | None = Field(default=None, description="Error message if fetch failed")

    @property
    def is_error(self) -> bool:
        """
        @brief Execute is error.
        @details Applies is error logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        return self.error is not None


class ProviderError(Exception):
    """
    @brief Define provider error component.
    @details Encapsulates provider error state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    pass


class AuthenticationError(ProviderError):
    """
    @brief Define authentication error component.
    @details Encapsulates authentication error state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    pass


class RateLimitError(ProviderError):
    """
    @brief Define rate limit error component.
    @details Encapsulates rate limit error state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    pass


class BaseProvider(ABC):
    """
    @brief Define base provider component.
    @details Encapsulates base provider state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    name: ProviderName

    @abstractmethod
    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Execute fetch.
        @details Applies fetch logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param window {WindowPeriod} Input parameter `window`.
        @return {ProviderResult} Function return value.
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """
        @brief Execute is configured.
        @details Applies is configured logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        pass

    @abstractmethod
    def get_config_help(self) -> str:
        """
        @brief Execute get config help.
        @details Applies get config help logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str} Function return value.
        """
        pass

    def _make_error_result(
        self, window: WindowPeriod, error: str, raw: dict[str, Any] | None = None
    ) -> ProviderResult:
        """
        @brief Execute make error result.
        @details Applies make error result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param window {WindowPeriod} Input parameter `window`.
        @param error {str} Input parameter `error`.
        @param raw {dict[str, Any] | None} Input parameter `raw`.
        @return {ProviderResult} Function return value.
        """
        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=UsageMetrics(),
            error=error,
            raw=raw or {},
        )
