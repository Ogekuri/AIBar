"""
@file
@brief DeepSeek provider, CLI panel, and GNOME surface tests.
@details Verifies the DeepSeek balance provider normalizes
`is_available`/`balance_infos[]` into `raw.deepseek_balance_infos` and
`UsageMetrics`, uses the fixed `30d` effective window, renders CLI monetary
balance rows without usage counters, and appears last in the GNOME extension
provider ordering with rose style classes.
@satisfies TST-108
@satisfies TST-109
@satisfies TST-111
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

from aibar.cli import _build_result_panel
from aibar.providers.base import AuthenticationError, ProviderName, WindowPeriod
from aibar.providers.deepseek import DeepSeekProvider

CLI_PATH = Path("src/aibar/aibar/cli.py")
EXTENSION_PATH = Path(
    "src/aibar/aibar/gnome-extension/aibar@aibar.panel/extension.js"
)
STYLESHEET_PATH = Path(
    "src/aibar/aibar/gnome-extension/aibar@aibar.panel/stylesheet.css"
)

BALANCE_PAYLOAD: dict[str, Any] = {
    "is_available": True,
    "balance_infos": [
        {
            "currency": "USD",
            "total_balance": "12.50",
            "granted_balance": "2.50",
            "topped_up_balance": "10.00",
        }
    ],
}


class _FakeResponse:
    """
    @brief Minimal httpx.Response substitute for DeepSeek fetch tests.
    @details Carries one status code, header map, text body, and decoded JSON
    payload so provider error mapping and success parsing stay deterministic.
    """

    def __init__(
        self,
        status_code: int = 200,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """
        @brief Initialize one fake HTTP response.
        @param status_code {int} HTTP status code to expose.
        @param payload {dict[str, Any] | None} JSON payload returned by `json()`.
        @param headers {dict[str, str] | None} Response header map.
        @return {None} Function return value.
        """
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.headers = headers or {}
        self.text = json.dumps(self._payload)

    def json(self) -> dict[str, Any]:
        """
        @brief Return the decoded JSON payload.
        @return {dict[str, Any]} Response payload.
        """
        return self._payload


class _FakeAsyncClient:
    """
    @brief Minimal httpx.AsyncClient substitute recording DeepSeek requests.
    @details Exposes one asynchronous `get` call, records the requested URL and
    headers, and returns the response supplied at construction time.
    """

    def __init__(self, response: _FakeResponse, recorder: dict[str, Any]) -> None:
        """
        @brief Initialize the fake async client.
        @param response {_FakeResponse} Response returned by every request.
        @param recorder {dict[str, Any]} Mutable request recorder.
        @return {None} Function return value.
        """
        self._response = response
        self._recorder = recorder

    async def __aenter__(self) -> "_FakeAsyncClient":
        """
        @brief Enter the asynchronous context manager.
        @return {_FakeAsyncClient} The same client instance.
        """
        return self

    async def __aexit__(self, *exc_info: object) -> bool:
        """
        @brief Exit the asynchronous context manager.
        @param exc_info {tuple[object, ...]} Exception triple (unused).
        @return {bool} False so exceptions propagate.
        """
        del exc_info
        return False

    async def get(
        self, url: str, headers: dict[str, str] | None = None
    ) -> _FakeResponse:
        """
        @brief Record one GET request and return the configured response.
        @param url {str} Request URL.
        @param headers {dict[str, str] | None} Request headers.
        @return {_FakeResponse} Configured fake response.
        """
        self._recorder["url"] = url
        self._recorder["headers"] = headers
        return self._response


def _install_fake_transport(
    monkeypatch: pytest.MonkeyPatch,
    response: _FakeResponse,
) -> dict[str, Any]:
    """
    @brief Install a deterministic httpx transport substitute.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @param response {_FakeResponse} Response returned by the fake client.
    @return {dict[str, Any]} Mutable request recorder.
    """
    recorder: dict[str, Any] = {}
    monkeypatch.setattr(
        "aibar.providers.deepseek.httpx.AsyncClient",
        lambda *args, **kwargs: _FakeAsyncClient(response, recorder),
    )
    monkeypatch.setattr(
        "aibar.config.get_api_call_timeout_seconds", lambda: 1.0
    )
    return recorder


def test_balance_mapping_preserves_fixed_window_and_null_counters() -> None:
    """
    @brief Verify DeepSeek balance normalization and effective window.
    @details Asserts `balance_infos[]` records are normalized with parsed
    monetary values, `metrics.remaining` mirrors the preferred total balance,
    the effective window is always `30d`, and usage counters stay unset.
    @return {None} Function return value.
    @satisfies REQ-241
    @satisfies REQ-242
    @satisfies REQ-243
    @satisfies REQ-246
    @satisfies TST-108
    """
    provider = DeepSeekProvider(api_key="deepseek-key")
    result = provider._parse_response(dict(BALANCE_PAYLOAD), WindowPeriod.DAY_30)

    assert result.provider == ProviderName.DEEPSEEK
    assert result.window == WindowPeriod.DAY_30
    assert result.is_error is False
    assert result.metrics.remaining == 12.5
    assert result.metrics.limit is None
    assert result.metrics.cost is None
    assert result.metrics.total_cost is None
    assert result.metrics.requests is None
    assert result.metrics.input_tokens is None
    assert result.metrics.output_tokens is None
    assert result.metrics.usage_percent is None
    assert result.metrics.currency_symbol == "$"
    assert result.raw["is_available"] is True
    assert result.raw["deepseek_balance_infos"] == [
        {
            "currency": "USD",
            "currency_symbol": "$",
            "total_balance": 12.5,
            "granted_balance": 2.5,
            "topped_up_balance": 10.0,
        }
    ]


def test_fetch_ignores_requested_window_and_uses_bearer_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    @brief Verify DeepSeek fetch request contract and window normalization.
    @details Installs a fake transport, invokes `fetch` with a `5h` request, and
    asserts the balance endpoint, bearer headers, and `30d` effective window.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-239
    @satisfies REQ-243
    @satisfies TST-108
    """
    recorder = _install_fake_transport(monkeypatch, _FakeResponse())
    provider = DeepSeekProvider(api_key="deepseek-key")

    result = asyncio.run(provider.fetch(WindowPeriod.HOUR_5))

    assert recorder["url"] == "https://api.deepseek.com/user/balance"
    assert recorder["headers"]["Authorization"] == "Bearer deepseek-key"
    assert recorder["headers"]["Accept"] == "application/json"
    assert result.window == WindowPeriod.DAY_30


def test_fetch_maps_authentication_and_rate_limit_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    @brief Verify DeepSeek HTTP error mapping into provider failures.
    @details Asserts HTTP `401` raises `AuthenticationError` and HTTP `429`
    returns a rate-limit error result carrying `retry_after_seconds`.
    @param monkeypatch {pytest.MonkeyPatch} Pytest monkeypatch fixture.
    @return {None} Function return value.
    @satisfies REQ-247
    """
    _install_fake_transport(monkeypatch, _FakeResponse(status_code=401))
    provider = DeepSeekProvider(api_key="deepseek-key")
    with pytest.raises(AuthenticationError):
        asyncio.run(provider.fetch())

    _install_fake_transport(
        monkeypatch,
        _FakeResponse(status_code=429, headers={"retry-after": "42"}),
    )
    rate_limited = asyncio.run(provider.fetch())
    assert rate_limited.is_error is True
    assert rate_limited.raw["status_code"] == 429
    assert rate_limited.raw["retry_after_seconds"] == 42.0
    assert rate_limited.raw["retry_after_unavailable"] is False


def test_cli_panel_renders_balance_without_usage_counters() -> None:
    """
    @brief Verify DeepSeek CLI panel monetary-only rendering.
    @details Asserts the panel renders `Status: OK` plus `Balance`, `Topped up`,
    and `Granted` monetary rows and never renders progress bars, `Usage:` rows,
    `Requests`, `Tokens`, `Spent`, or `Cost` rows.
    @return {None} Function return value.
    @satisfies REQ-245
    @satisfies REQ-246
    @satisfies REQ-251
    @satisfies REQ-252
    @satisfies TST-109
    @satisfies TST-112
    """
    provider = DeepSeekProvider(api_key="deepseek-key")
    result = provider._parse_response(dict(BALANCE_PAYLOAD), WindowPeriod.DAY_30)

    title, body_lines = _build_result_panel(ProviderName.DEEPSEEK, result)
    rendered = "\n".join(body_lines)

    assert title == "DEEPSEEK"
    assert "Status: OK" in body_lines
    assert "Balance: " in rendered
    assert "12.50" in rendered
    assert "Topped up: " in rendered
    assert "10.00" in rendered
    assert "Granted: " in rendered
    assert "2.50" in rendered
    assert "Usage:" not in rendered
    assert "Requests:" not in rendered
    assert "Tokens:" not in rendered
    assert "Spent:" not in rendered
    assert "Cost:" not in rendered
    assert "█" not in rendered
    assert "░" not in rendered


def test_gnome_extension_orders_deepseek_last_with_rose_surfaces() -> None:
    """
    @brief Verify GNOME extension DeepSeek ordering, styling, and reset wiring.
    @details Asserts the trailing provider order, rose style classes, monetary
    rows, panel balance token, and `_handleError` label reset for DeepSeek.
    @return {None} Function return value.
    @satisfies REQ-022
    @satisfies REQ-248
    @satisfies REQ-249
    @satisfies REQ-253
    @satisfies TST-111
    @satisfies TST-113
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    stylesheet = STYLESHEET_PATH.read_text(encoding="utf-8")
    cli_source = CLI_PATH.read_text(encoding="utf-8")

    assert (
        "this._providerOrder = ['agy', 'openrouter', 'copilot', 'codex', 'openai', 'geminiai', 'zai', 'deepseek'];"
        in source
    )
    assert "'zai',\n    'deepseek',\n]);" in source
    assert "deepseek: true," in source
    assert "deepseek: '30d'," in source
    assert "deepseek: 'aibar-progress-provider-deepseek'," in source
    assert "_panelDeepSeekBalanceLabel" in source
    assert "aibar-tab-label-deepseek" in source
    assert "this._panelDeepSeekBalanceLabel.set_text('');" in source
    assert "this._panelDeepSeekBalanceLabel.hide();" in source
    assert "['Balance', Number(metrics.remaining)]" in source
    assert "['Topped up', deepseekRecord.topped_up_balance]" in source
    assert "['Granted', deepseekRecord.granted_balance]" in source
    assert "`${deepseekRowLabel}: ${_boldWhiteMarkup(deepseekValueText)}`" in source
    assert "deepseekMarkup.join('\\n')" in source
    assert "Spent" not in source
    assert 'ProviderName.DEEPSEEK: "\\033[38;5;204m",' in cli_source
    assert "const PROGRESS_BAR_PROVIDERS = new Set(['agy', 'openrouter', 'copilot', 'codex', 'zai']);" in source
    assert "const API_COUNTER_PROVIDERS = new Set(['openai', 'codex', 'geminiai']);" in source
    assert "const TEXT_USAGE_PROVIDERS = new Set(['openai', 'geminiai', 'deepseek']);" in source
    assert ".aibar-tab-label-deepseek {" in stylesheet
    assert "#FF375F" in stylesheet
    assert "#4D6BFE" not in stylesheet
    assert "#FF375F" in stylesheet
