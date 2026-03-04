"""
@file
@brief Claude CLI credential extraction helpers.
@details Reads Claude CLI OAuth credential stores and exposes token/status accessors for provider authentication.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ClaudeCLIAuth:
    """
    @brief Define claude c l i auth component.
    @details Encapsulates claude c l i auth state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    DEFAULT_CREDS_PATH = Path.home() / ".claude" / ".credentials.json"

    def __init__(self, creds_path: Path | None = None) -> None:
        """
        @brief Execute init.
        @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param creds_path {Path | None} Input parameter `creds_path`.
        @return {None} Function return value.
        """
        self.creds_path = creds_path or self.DEFAULT_CREDS_PATH

    def is_available(self) -> bool:
        """
        @brief Execute is available.
        @details Applies is available logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        return self.creds_path.exists()

    def get_credentials(self) -> dict[str, Any] | None:
        """
        @brief Execute get credentials.
        @details Applies get credentials logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {dict[str, Any] | None} Function return value.
        """
        if not self.is_available():
            return None

        try:
            data = json.loads(self.creds_path.read_text())
            return data.get("claudeAiOauth")
        except Exception:
            return None

    def get_access_token(self) -> str | None:
        """
        @brief Execute get access token.
        @details Applies get access token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {str | None} Function return value.
        """
        creds = self.get_credentials()
        return creds.get("accessToken") if creds else None

    def is_token_expired(self) -> bool:
        """
        @brief Execute is token expired.
        @details Applies is token expired logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {bool} Function return value.
        """
        creds = self.get_credentials()
        if not creds or "expiresAt" not in creds:
            return True

        try:
            # expiresAt is a timestamp in milliseconds
            expires_at_ms = creds["expiresAt"]
            expires_at = datetime.fromtimestamp(expires_at_ms / 1000, tz=timezone.utc)
            return datetime.now(timezone.utc) >= expires_at
        except Exception:
            return True

    def get_token_info(self) -> dict[str, Any]:
        """
        @brief Execute get token info.
        @details Applies get token info logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {dict[str, Any]} Function return value.
        """
        creds = self.get_credentials()
        if not creds:
            return {
                "available": False,
                "error": "Claude CLI credentials not found",
            }

        token = creds.get("accessToken", "")
        expires_at = creds.get("expiresAt")
        expired = self.is_token_expired()

        info = {
            "available": True,
            "token_preview": f"{token[:15]}..." if token else None,
            "expires_at": expires_at,
            "expired": expired,
            "subscription_type": creds.get("subscriptionType"),
            "rate_limit_tier": creds.get("rateLimitTier"),
            "scopes": creds.get("scopes", []),
        }

        if expires_at:
            try:
                # expires_at is a timestamp in milliseconds
                exp_dt = datetime.fromtimestamp(expires_at / 1000, tz=timezone.utc)
                info["expires_at_formatted"] = exp_dt.isoformat()
                remaining = exp_dt - datetime.now(timezone.utc)
                if remaining.total_seconds() > 0:
                    hours = int(remaining.total_seconds() // 3600)
                    info["expires_in_hours"] = hours
            except Exception:
                pass

        return info


def extract_claude_cli_token() -> str | None:
    """
    @brief Execute extract claude cli token.
    @details Applies extract claude cli token logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {str | None} Function return value.
    """
    auth = ClaudeCLIAuth()
    return auth.get_access_token()
