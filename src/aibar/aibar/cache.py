"""
@file
@brief Provider result caching primitives.
@details Implements in-memory and disk cache entries, TTL invalidation, and raw-payload sanitization for provider metrics.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from aibar.providers.base import ProviderName, ProviderResult, WindowPeriod


class CacheEntry(BaseModel):
    """
    @brief Define cache entry component.
    @details Encapsulates cache entry state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    result: ProviderResult
    cached_at: datetime
    ttl_seconds: int

    def is_expired(self) -> bool:
        """
        @brief Execute is expired.
        @details Applies is expired logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        now = datetime.now(timezone.utc)
        cached_at_utc = self.cached_at.replace(tzinfo=timezone.utc)
        return now > cached_at_utc + timedelta(seconds=self.ttl_seconds)


class ResultCache:
    """
    @brief Define result cache component.
    @details Encapsulates result cache state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    DEFAULT_TTL = 120  # 2 minutes
    PROVIDER_TTLS = {
        ProviderName.CLAUDE: 60,  # 1 minute - quota changes quickly
        ProviderName.OPENAI: 180,  # 3 minutes - usage data is historical
        ProviderName.OPENROUTER: 180,  # 3 minutes - credits update periodically
        ProviderName.COPILOT: 300,  # 5 minutes - reports are slow to update
    }

    def __init__(self, cache_dir: Path | None = None) -> None:
        """
        @brief Execute init.
        @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param cache_dir {Path | None} Input parameter `cache_dir`.
        @return {None} Function return value.
        """
        self._memory_cache: dict[str, CacheEntry] = {}
        self._cache_dir = cache_dir or self._default_cache_dir()
        self._ensure_cache_dir()

    def _default_cache_dir(self) -> Path:
        """
        @brief Execute default cache dir.
        @details Applies default cache dir logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {Path} Function return value.
        """
        xdg_cache = os.environ.get("XDG_CACHE_HOME")
        base = Path(xdg_cache) if xdg_cache else Path.home() / ".cache"
        return base / "aibar"

    def _ensure_cache_dir(self) -> None:
        """
        @brief Execute ensure cache dir.
        @details Applies ensure cache dir logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, provider: ProviderName, window: WindowPeriod) -> str:
        """
        @brief Execute cache key.
        @details Applies cache key logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @param window {WindowPeriod} Input parameter `window`.
        @return {str} Function return value.
        """
        return f"{provider.value}:{window.value}"

    def _disk_path(self, provider: ProviderName, window: WindowPeriod) -> Path:
        """
        @brief Execute disk path.
        @details Applies disk path logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @param window {WindowPeriod} Input parameter `window`.
        @return {Path} Function return value.
        """
        return self._cache_dir / f"{provider.value}_{window.value}.json"

    def get(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None:
        """
        @brief Execute get.
        @details Applies get logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @param window {WindowPeriod} Input parameter `window`.
        @return {ProviderResult | None} Function return value.
        """
        key = self._cache_key(provider, window)

        # Check memory cache first
        if entry := self._memory_cache.get(key):
            if not entry.is_expired():
                return entry.result
            del self._memory_cache[key]

        # Fall back to disk cache
        return self._load_from_disk(provider, window)

    def set(self, result: ProviderResult) -> None:
        """
        @brief Execute set.
        @details Applies set logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param result {ProviderResult} Input parameter `result`.
        @return {None} Function return value.
        """
        key = self._cache_key(result.provider, result.window)
        ttl = self.PROVIDER_TTLS.get(result.provider, self.DEFAULT_TTL)

        entry = CacheEntry(
            result=result,
            cached_at=datetime.now(timezone.utc),
            ttl_seconds=ttl,
        )
        self._memory_cache[key] = entry

        # Persist to disk if successful
        if not result.is_error:
            self._save_to_disk(result)

    def get_last_good(self, provider: ProviderName, window: WindowPeriod) -> ProviderResult | None:
        """
        @brief Execute get last good.
        @details Applies get last good logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @param window {WindowPeriod} Input parameter `window`.
        @return {ProviderResult | None} Function return value.
        """
        return self._load_from_disk(provider, window, ignore_ttl=True)

    def invalidate(
        self, provider: ProviderName | None = None, window: WindowPeriod | None = None
    ) -> None:
        """
        @brief Execute invalidate.
        @details Applies invalidate logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName | None} Input parameter `provider`.
        @param window {WindowPeriod | None} Input parameter `window`.
        @return {None} Function return value.
        """
        if provider is None and window is None:
            # Clear all
            self._memory_cache.clear()
            return

        keys_to_remove = []
        for key in self._memory_cache:
            p, w = key.split(":")
            if (provider is None or p == provider.value) and (window is None or w == window.value):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._memory_cache[key]

    def _save_to_disk(self, result: ProviderResult) -> None:
        """
        @brief Execute save to disk.
        @details Applies save to disk logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param result {ProviderResult} Input parameter `result`.
        @return {None} Function return value.
        """
        path = self._disk_path(result.provider, result.window)
        try:
            # Sanitize raw data to remove any potential tokens
            sanitized = result.model_copy(deep=True)
            sanitized.raw = self._sanitize_raw(sanitized.raw)

            with open(path, "w") as f:
                f.write(sanitized.model_dump_json(indent=2))
        except (OSError, IOError):
            # Silently fail on disk write errors
            pass

    def _load_from_disk(
        self,
        provider: ProviderName,
        window: WindowPeriod,
        ignore_ttl: bool = False,
    ) -> ProviderResult | None:
        """
        @brief Execute load from disk.
        @details Applies load from disk logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @param window {WindowPeriod} Input parameter `window`.
        @param ignore_ttl {bool} Input parameter `ignore_ttl`.
        @return {ProviderResult | None} Function return value.
        """
        path = self._disk_path(provider, window)
        if not path.exists():
            return None

        try:
            with open(path) as f:
                data = json.load(f)
            result = ProviderResult.model_validate(data)

            if ignore_ttl:
                return result

            # Check if disk cache is still valid
            ttl = self.PROVIDER_TTLS.get(provider, self.DEFAULT_TTL)
            age = datetime.now(timezone.utc) - result.updated_at.replace(tzinfo=timezone.utc)
            if age.total_seconds() <= ttl:
                return result

            return None
        except (OSError, IOError, json.JSONDecodeError, ValueError):
            return None

    def _sanitize_raw(self, raw: dict[str, Any]) -> dict[str, Any]:
        """
        @brief Execute sanitize raw.
        @details Applies sanitize raw logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param raw {dict[str, Any]} Input parameter `raw`.
        @return {dict[str, Any]} Function return value.
        """
        sensitive_keys = {"token", "key", "secret", "password", "authorization"}

        def clean(obj: Any) -> Any:
            """
            @brief Execute clean.
            @details Applies clean logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
            @param obj {Any} Input parameter `obj`.
            @return {Any} Function return value.
            """
            if isinstance(obj, dict):
                return {
                    k: "[REDACTED]" if k.lower() in sensitive_keys else clean(v)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [clean(item) for item in obj]
            return obj

        return clean(raw)
