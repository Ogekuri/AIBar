"""
@file
@brief Antigravity (AGY) quota usage provider.
@details Extracts Antigravity CLI quota metrics by executing `agy -p /usage`
as one local subprocess, stripping ANSI escape sequences, and parsing
tab-separated `<group>\\t<field>\\t<value>` rows into normalized per-quota
used-percentage metrics covering `G 7d`, `G 5h`, `CG 7d`, `CG 5h`, and `A 7d`.
"""

import re
import shutil
import subprocess

from aibar.providers.base import (
    BaseProvider,
    ProviderError,
    ProviderName,
    ProviderResult,
    UsageMetrics,
    WindowPeriod,
)

_ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_PERCENTAGE_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]+)?%")
_AUTH_ERROR_PATTERN = re.compile(
    r"authentication failed|unauthorized|not authenticated|please log in|login expired",
    re.IGNORECASE,
)
_NOT_CONFIGURED_MESSAGE = (
    "Not configured. Install the Antigravity CLI (agy) and log in."
)
_AUTH_ERROR_MESSAGE = "Authentication failed: please log in to the Antigravity CLI (agy)."
_NO_QUOTA_MESSAGE = "No AGY quota data returned by 'agy /usage'."


class AntigravityProvider(BaseProvider):
    """
    @brief Define Antigravity (AGY) quota provider component.
    @details Encapsulates Antigravity quota retrieval and normalization for
    AIBar runtime flows. The provider executes one local `agy -p /usage`
    subprocess call, strips ANSI escape sequences from the combined output,
    and parses tab-separated rows into the five canonical quota records
    carrying remaining percentages normalized to used percentages.
    @satisfies REQ-158
    @satisfies REQ-165
    """

    name = ProviderName.AGY
    USAGE_COMMAND = ["agy", "-p", "/usage"]
    _QUOTA_SPECS = (
        ("gemini_weekly", "G 7d", "Gemini Models", "Weekly Limit Remaining"),
        ("gemini_five_hour", "G 5h", "Gemini Models", "Five Hour Limit Remaining"),
        (
            "claude_gpt_weekly",
            "CG 7d",
            "Claude and GPT models",
            "Weekly Limit Remaining",
        ),
        (
            "claude_gpt_five_hour",
            "CG 5h",
            "Claude and GPT models",
            "Five Hour Limit Remaining",
        ),
        (
            "argon_weekly",
            "A 7d",
            "Gemini 4 Argon",
            "Gemini 4 Argon Weekly Limit",
        ),
    )

    def is_configured(self) -> bool:
        """
        @brief Report whether the Antigravity CLI executable is available.
        @details Resolves the `agy` executable from `PATH` via `shutil.which`.
        @return {bool} True when the `agy` executable is found in `PATH`.
        @satisfies REQ-167
        """
        return shutil.which(self.USAGE_COMMAND[0]) is not None

    def get_config_help(self) -> str:
        """
        @brief Render Antigravity configuration guidance.
        @return {str} Human-readable configuration help text.
        """
        return """Antigravity (AGY) Usage Provider Configuration:

1. Install the Antigravity CLI and ensure the `agy` executable is in PATH.
2. Authenticate once with the Antigravity CLI login flow.
3. AIBar reads quotas by executing `agy -p /usage` locally.
"""

    async def fetch(self, window: WindowPeriod = WindowPeriod.DAY_7) -> ProviderResult:
        """
        @brief Fetch Antigravity quota data from the local CLI.
        @details Ignores the requested window because `agy -p /usage` returns
        all quotas in one document and the provider is treated as a
        fixed-window provider with effective window `30d`. Classifies
        authentication failures from output text, maps non-zero subprocess
        exit status to error results, and normalizes missing quota rows by
        omission.
        @param window {WindowPeriod} Requested window (ignored; effective window is `30d`).
        @return {ProviderResult} Normalized Antigravity quota result.
        @throws {ProviderError} When the subprocess cannot be executed.
        @satisfies REQ-158
        @satisfies REQ-165
        @satisfies REQ-166
        """
        effective_window = WindowPeriod.DAY_30
        if not self.is_configured():
            return self._make_error_result(
                window=effective_window,
                error=_NOT_CONFIGURED_MESSAGE,
            )

        from aibar.config import get_api_call_timeout_seconds

        try:
            completed = subprocess.run(
                self.USAGE_COMMAND,
                capture_output=True,
                text=True,
                timeout=get_api_call_timeout_seconds(),
            )
        except subprocess.TimeoutExpired:
            return self._make_error_result(
                window=effective_window,
                error="Command timed out",
                raw={"timeout": True},
            )
        except OSError as exc:
            raise ProviderError(f"Failed to execute agy CLI: {exc}") from exc

        output = self._strip_ansi(
            (completed.stdout or "") + (completed.stderr or "")
        )
        if self._is_auth_error(output):
            return self._make_error_result(
                window=effective_window,
                error=_AUTH_ERROR_MESSAGE,
                raw={"auth_error": True},
            )
        if completed.returncode != 0:
            return self._make_error_result(
                window=effective_window,
                error=f"AGY CLI exited with status {completed.returncode}",
                raw={"status_code": completed.returncode, "body": output},
            )
        quotas = self._extract_quotas(output)
        if not quotas:
            return self._make_error_result(
                window=effective_window,
                error=_NO_QUOTA_MESSAGE,
                raw={"body": output},
            )
        return self._parse_response(quotas, effective_window)

    @staticmethod
    def _strip_ansi(output: str) -> str:
        """
        @brief Remove ANSI escape sequences from CLI output text.
        @details Strips `\x1b[...` escape sequences (any letter terminator) so
        terminal color codes never interfere with TSV metric parsing.
        @param output {str} Raw CLI output text.
        @return {str} Output text with ANSI escapes removed.
        @satisfies REQ-158
        """
        return _ANSI_ESCAPE_PATTERN.sub("", output)

    @staticmethod
    def _is_auth_error(output: str) -> bool:
        """
        @brief Detect Antigravity authentication failure text.
        @details Matches `authentication failed`, `unauthorized`,
        `not authenticated`, `please log in`, or `login expired`
        case-insensitively in the CLI output.
        @param output {str} ANSI-stripped CLI output text.
        @return {bool} True when output indicates an authentication failure.
        @satisfies REQ-166
        """
        return _AUTH_ERROR_PATTERN.search(output) is not None

    @staticmethod
    def _parse_tsv_rows(output: str) -> list[list[str]]:
        """
        @brief Parse tab-separated `<group>\\t<field>\\t<value>` rows.
        @details Splits each output line on tab characters and keeps rows with
        at least three columns, trimming surrounding whitespace per column.
        @param output {str} ANSI-stripped CLI output text.
        @return {list[list[str]]} Parsed TSV rows with three or more columns.
        @satisfies REQ-158
        """
        rows: list[list[str]] = []
        for line in output.splitlines():
            parts = [part.strip() for part in line.split("\t")]
            if len(parts) >= 3:
                rows.append(parts)
        return rows

    @classmethod
    def _find_remaining_percent(
        cls, rows: list[list[str]], group: str, field: str
    ) -> float | None:
        """
        @brief Resolve one quota remaining percentage from parsed TSV rows.
        @details Matches the first row whose group and field columns equal the
        requested names, then extracts the first percentage matching
        `[0-9]+([.][0-9]+)?%` in the value column.
        @param rows {list[list[str]]} Parsed TSV rows.
        @param group {str} Expected group column value.
        @param field {str} Expected field column value.
        @return {float | None} Remaining percentage or None when absent.
        @satisfies REQ-162
        """
        for parts in rows:
            if parts[0] != group or parts[1] != field:
                continue
            match = _PERCENTAGE_PATTERN.search(parts[2])
            if match is None:
                continue
            try:
                return float(match.group(0)[:-1])
            except ValueError:
                continue
        return None

    @classmethod
    def _extract_quotas(cls, output: str) -> list[dict]:
        """
        @brief Map parsed TSV rows into normalized AGY quota records.
        @details Projects each canonical `(quota_key, label, group, field)`
        specification onto the parsed rows, clamps each remaining percentage
        to `[0.0, 100.0]`, normalizes the used percentage as
        `100.0 - remaining`, and omits quotas whose rows are missing so no
        quota values are fabricated.
        @param output {str} ANSI-stripped CLI output text.
        @return {list[dict]} Ordered normalized quota records.
        @satisfies REQ-159
        @satisfies REQ-160
        @satisfies REQ-161
        @satisfies REQ-162
        @satisfies REQ-163
        @satisfies REQ-164
        """
        rows = cls._parse_tsv_rows(output)
        quotas: list[dict] = []
        for quota_key, label, group, field in cls._QUOTA_SPECS:
            remaining = cls._find_remaining_percent(rows, group, field)
            if remaining is None:
                continue
            remaining = max(0.0, min(100.0, remaining))
            quotas.append(
                {
                    "quota_key": quota_key,
                    "label": label,
                    "remaining_percent": remaining,
                    "percentage": 100.0 - remaining,
                }
            )
        return quotas

    def _parse_response(
        self, quotas: list[dict], window: WindowPeriod
    ) -> ProviderResult:
        """
        @brief Project normalized AGY quota records into a provider result.
        @details Derives the representative aggregate percentage as the maximum
        quota used percentage so the status bar and panel icon reflect the
        most-consumed quota, and attaches the normalized `agy_quotas` array to
        `raw` for deterministic CLI and GNOME rendering.
        @param quotas {list[dict]} Normalized AGY quota records.
        @param window {WindowPeriod} Effective window (always `30d`).
        @return {ProviderResult} Normalized AGY result with per-quota raw data.
        @satisfies REQ-163
        @satisfies REQ-164
        """
        from aibar.config import resolve_currency_symbol

        currency_symbol = resolve_currency_symbol({}, self.name.value)
        max_percentage = self._max_percentage(quotas)
        metrics = UsageMetrics(
            cost=None,
            total_cost=None,
            requests=None,
            input_tokens=None,
            output_tokens=None,
            remaining=100.0 - max_percentage,
            limit=100.0,
            reset_at=None,
            currency_symbol=currency_symbol,
        )
        return ProviderResult(
            provider=self.name,
            window=window,
            metrics=metrics,
            raw={"agy_quotas": quotas},
        )

    @staticmethod
    def _max_percentage(quotas: list[dict]) -> float:
        """
        @brief Compute the maximum quota used percentage for aggregation.
        @param quotas {list[dict]} Normalized AGY quota records.
        @return {float} Maximum used percentage clamped to `>= 0`.
        @satisfies REQ-170
        """
        percentages = [
            quota["percentage"]
            for quota in quotas
            if isinstance(quota.get("percentage"), (int, float))
        ]
        if not percentages:
            return 0.0
        return float(max(percentages))
