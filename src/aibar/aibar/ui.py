"""
@file
@brief Textual terminal UI for usage metrics.
@details Implements provider cards, refresh controls, window switching, and raw JSON visualization over normalized provider results.
"""

# pyright: reportMissingImports=false

import json
from datetime import datetime, timezone

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Label,
    ProgressBar,
    Static,
    TabbedContent,
    TabPane,
)

from aibar.cache import ResultCache
from aibar.config import config
from aibar.providers import (
    ClaudeOAuthProvider,
    CodexProvider,
    CopilotProvider,
    OpenAIUsageProvider,
    OpenRouterUsageProvider,
)
from aibar.providers.base import (
    BaseProvider,
    ProviderName,
    ProviderResult,
    WindowPeriod,
)


class ProviderCard(Static):
    """
    @brief Define provider card component.
    @details Encapsulates provider card state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    DEFAULT_CSS = """
    ProviderCard {
        width: 100%;
        height: auto;
        margin: 1 0;
        padding: 1 2;
        border: solid $primary;
        background: $surface;
    }

    ProviderCard.error {
        border: solid $error;
    }

    ProviderCard.unconfigured {
        border: dashed $warning;
        opacity: 0.7;
    }

    ProviderCard .card-title {
        text-style: bold;
        color: $text;
    }

    ProviderCard .card-subtitle {
        color: $text-muted;
        margin-bottom: 1;
    }

    ProviderCard .metric-row {
        width: 100%;
        height: auto;
    }

    ProviderCard .metric-label {
        width: 15;
        color: $text-muted;
    }

    ProviderCard .metric-value {
        color: $success;
        text-style: bold;
    }

    ProviderCard .metric-value.warning {
        color: $warning;
    }

    ProviderCard .metric-value.error {
        color: $error;
    }

    ProviderCard ProgressBar {
        width: 100%;
        margin: 1 0;
    }

    ProviderCard .error-message {
        color: $error;
        margin-top: 1;
    }

    ProviderCard .stale-indicator {
        color: $warning;
        text-style: italic;
    }
    """

    result: reactive[ProviderResult | None] = reactive(None)
    is_loading: reactive[bool] = reactive(False)

    def __init__(
        self,
        provider_name: ProviderName,
        **kwargs,
    ) -> None:
        """
        @brief Execute init.
        @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider_name {ProviderName} Input parameter `provider_name`.
        @param kwargs {None} Input parameter `kwargs`.
        @return {None} Function return value.
        """
        super().__init__(**kwargs)
        self.provider_name = provider_name
        self.provider_info = config.get_provider_status(provider_name)

    def compose(self) -> ComposeResult:
        """
        @brief Execute compose.
        @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {ComposeResult} Function return value.
        """
        name = self.provider_info["name"]
        configured = self.provider_info["configured"]

        yield Label(name, classes="card-title")

        if not configured:
            yield Label(
                f"Not configured - set {self.provider_info['env_var']}",
                classes="card-subtitle",
            )
            self.add_class("unconfigured")
            return

        yield Label("Loading...", id="status-line", classes="card-subtitle")
        if self.provider_name == ProviderName.COPILOT:
            yield Label("Window: 30d only", classes="card-subtitle")
        yield VerticalGroup(id="metrics-container")

    def watch_result(self, result: ProviderResult | None) -> None:
        """
        @brief Execute watch result.
        @details Applies watch result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param result {ProviderResult | None} Input parameter `result`.
        @return {None} Function return value.
        """
        if result is None:
            return

        self.remove_class("error")
        self.remove_class("unconfigured")

        status_line = self.query_one("#status-line", Label)
        metrics_container = self.query_one("#metrics-container", VerticalGroup)
        metrics_container.remove_children()

        if result.is_error:
            self.add_class("error")
            status_line.update(f"Error: {result.error}")
            return

        # Update status line with last update time
        age = datetime.now(timezone.utc) - result.updated_at.replace(tzinfo=timezone.utc)
        age_str = self._format_age(age.total_seconds())
        status_line.update(f"Updated {age_str} ago | Window: {result.window.value}")

        # Build metrics display
        metrics = result.metrics

        # Usage bar for Claude (has limit/remaining)
        if metrics.usage_percent is not None:
            pct = metrics.usage_percent
            bar = ProgressBar(total=100, show_eta=False)
            bar.progress = pct
            metrics_container.mount(bar)

            pct_label = Label(f"{pct:.1f}% used", classes="metric-value")
            if pct > 80:
                pct_label.add_class("warning")
            if pct > 95:
                pct_label.add_class("error")
            metrics_container.mount(pct_label)

        # Reset time
        if metrics.reset_at:
            reset_delta = metrics.reset_at - datetime.now(timezone.utc)
            if reset_delta.total_seconds() > 0:
                reset_str = self._format_duration(reset_delta.total_seconds())
                metrics_container.mount(
                    Horizontal(
                        Label("Resets in:", classes="metric-label"),
                        Label(reset_str, classes="metric-value"),
                        classes="metric-row",
                    )
                )

        # Cost
        if metrics.cost is not None:
            metrics_container.mount(
                Horizontal(
                    Label("Cost:", classes="metric-label"),
                    Label(f"${metrics.cost:.4f}", classes="metric-value"),
                    classes="metric-row",
                )
            )

        # Requests
        if metrics.requests is not None:
            metrics_container.mount(
                Horizontal(
                    Label("Requests:", classes="metric-label"),
                    Label(f"{metrics.requests:,}", classes="metric-value"),
                    classes="metric-row",
                )
            )

        # Tokens
        if metrics.total_tokens is not None:
            tokens_str = f"{metrics.total_tokens:,}"
            if metrics.input_tokens and metrics.output_tokens:
                tokens_str += f" ({metrics.input_tokens:,} in / {metrics.output_tokens:,} out)"
            metrics_container.mount(
                Horizontal(
                    Label("Tokens:", classes="metric-label"),
                    Label(tokens_str, classes="metric-value"),
                    classes="metric-row",
                )
            )

    def watch_is_loading(self, loading: bool) -> None:
        """
        @brief Execute watch is loading.
        @details Applies watch is loading logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param loading {bool} Input parameter `loading`.
        @return {None} Function return value.
        """
        if not self.provider_info["configured"]:
            return
        status_line = self.query_one("#status-line", Label)
        if loading:
            status_line.update("Loading...")

    def _format_age(self, seconds: float) -> str:
        """
        @brief Execute format age.
        @details Applies format age logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param seconds {float} Input parameter `seconds`.
        @return {str} Function return value.
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m"
        else:
            return f"{int(seconds / 3600)}h"

    def _format_duration(self, seconds: float) -> str:
        """
        @brief Execute format duration.
        @details Applies format duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param seconds {float} Input parameter `seconds`.
        @return {str} Function return value.
        """
        total_minutes = int(seconds // 60)
        days = total_minutes // (24 * 60)
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0 or days > 0:
            parts.append(f"{hours}h")
        parts.append(f"{minutes}m")
        return " ".join(parts)


class RawJsonView(Static):
    """
    @brief Define raw json view component.
    @details Encapsulates raw json view state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    DEFAULT_CSS = """
    RawJsonView {
        width: 100%;
        height: 1fr;
        padding: 1;
        background: $surface;
    }

    RawJsonView .json-content {
        width: 100%;
        overflow: auto;
    }
    """

    data: reactive[dict | None] = reactive(None)

    def compose(self) -> ComposeResult:
        """
        @brief Execute compose.
        @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {ComposeResult} Function return value.
        """
        yield VerticalScroll(
            Static("No data", id="json-display"),
            classes="json-content",
        )

    def watch_data(self, data: dict | None) -> None:
        """
        @brief Execute watch data.
        @details Applies watch data logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param data {dict | None} Input parameter `data`.
        @return {None} Function return value.
        """
        display = self.query_one("#json-display", Static)
        if data is None:
            display.update("No data")
        else:
            formatted = json.dumps(data, indent=2, default=str)
            display.update(formatted)


class AIBarUI(App):
    """
    @brief Define a i bar u i component.
    @details Encapsulates a i bar u i state and operations for AIBar runtime flows with deterministic behavior and explicit interfaces.
    """

    CSS = """
    Screen {
        background: $background;
    }

    TabbedContent {
        height: 1fr;
        width: 1fr;
    }

    ContentSwitcher {
        height: 1fr;
    }

    TabPane {
        height: 1fr;
    }

    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    #overview-tab {
        width: 100%;
        height: 1fr;
        padding: 1;
    }

    #controls {
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    #controls Button {
        margin-right: 1;
    }

    .window-button {
        min-width: 6;
    }

    .window-button.active {
        background: $primary;
    }

    #cards-container {
        width: 100%;
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("5", "window_5h", "5 Hours"),
        Binding("7", "window_7d", "7 Days"),
        Binding("j", "toggle_json", "Toggle JSON"),
    ]

    TITLE = "Usage Metrics UI"

    window: reactive[WindowPeriod] = reactive(WindowPeriod.DAY_7)
    show_json: reactive[bool] = reactive(False)

    def __init__(self) -> None:
        """
        @brief Execute init.
        @details Applies init logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        super().__init__()
        self.cache = ResultCache()
        self.providers: dict[ProviderName, BaseProvider] = {
            ProviderName.CLAUDE: ClaudeOAuthProvider(),
            ProviderName.OPENAI: OpenAIUsageProvider(),
            ProviderName.OPENROUTER: OpenRouterUsageProvider(),
            ProviderName.COPILOT: CopilotProvider(),
            ProviderName.CODEX: CodexProvider(),
        }
        self.results: dict[ProviderName, ProviderResult | None] = {}

    def compose(self) -> ComposeResult:
        """
        @brief Execute compose.
        @details Applies compose logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {ComposeResult} Function return value.
        """
        yield Header()
        with Container(id="main-container"):
            with TabbedContent():
                with TabPane("Overview", id="overview-tab"):
                    yield Horizontal(
                        Button("Refresh", id="refresh-btn", variant="primary"),
                        Button("5h", id="btn-5h", classes="window-button"),
                        Button("7d", id="btn-7d", classes="window-button active"),
                        id="controls",
                    )
                    yield VerticalScroll(
                        ProviderCard(ProviderName.CLAUDE, id="card-claude"),
                        ProviderCard(ProviderName.OPENAI, id="card-openai"),
                        ProviderCard(ProviderName.OPENROUTER, id="card-openrouter"),
                        ProviderCard(ProviderName.COPILOT, id="card-copilot"),
                        ProviderCard(ProviderName.CODEX, id="card-codex"),
                        id="cards-container",
                    )
                with TabPane("Raw JSON", id="json-tab"):
                    yield RawJsonView(id="json-view")
        yield Footer()

    async def on_mount(self) -> None:
        """
        @brief Execute on mount.
        @details Applies on mount logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        self._update_window_buttons()
        await self.action_refresh()

    @on(Button.Pressed, "#refresh-btn")
    async def on_refresh_pressed(self) -> None:
        """
        @brief Execute on refresh pressed.
        @details Applies on refresh pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        await self.action_refresh()

    @on(Button.Pressed, "#btn-5h")
    async def on_5h_pressed(self) -> None:
        """
        @brief Execute on 5h pressed.
        @details Applies on 5h pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        await self.action_window_5h()

    @on(Button.Pressed, "#btn-7d")
    async def on_7d_pressed(self) -> None:
        """
        @brief Execute on 7d pressed.
        @details Applies on 7d pressed logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        await self.action_window_7d()

    async def action_refresh(self) -> None:
        """
        @brief Execute action refresh.
        @details Applies action refresh logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects. Cache hits are used only for non-Claude providers.
        @return {None} Function return value.
        @satisfies REQ-009
        """
        for provider_name, provider in self.providers.items():
            if not provider.is_configured():
                continue

            card = self._get_card(provider_name)
            if card:
                card.is_loading = True

            use_cache = provider_name != ProviderName.CLAUDE
            if use_cache:
                # Check cache first for non-Claude providers.
                cached = self.cache.get(provider_name, self.window)
                if cached:
                    self.results[provider_name] = cached
                    if card:
                        card.result = cached
                        card.is_loading = False
                    continue

            # Fetch fresh data
            try:
                result = await provider.fetch(self.window)
                if use_cache:
                    self.cache.set(result)
                self.results[provider_name] = result
            except Exception as e:
                result = provider._make_error_result(self.window, str(e))
                self.results[provider_name] = result

            if card:
                card.result = result
                card.is_loading = False

        # Update JSON view
        self._update_json_view()

    async def action_window_5h(self) -> None:
        """
        @brief Execute action window 5h.
        @details Applies action window 5h logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        self.window = WindowPeriod.HOUR_5
        self._update_window_buttons()
        self.cache.invalidate()  # Clear cache to force refresh with new window
        await self.action_refresh()

    async def action_window_7d(self) -> None:
        """
        @brief Execute action window 7d.
        @details Applies action window 7d logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        self.window = WindowPeriod.DAY_7
        self._update_window_buttons()
        self.cache.invalidate()
        await self.action_refresh()

    async def action_toggle_json(self) -> None:
        """
        @brief Execute action toggle json.
        @details Applies action toggle json logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        self.show_json = not self.show_json
        tabbed = self.query_one(TabbedContent)
        if self.show_json:
            tabbed.active = "json-tab"
        else:
            tabbed.active = "overview-tab"

    def _get_card(self, provider: ProviderName) -> ProviderCard | None:
        """
        @brief Execute get card.
        @details Applies get card logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @param provider {ProviderName} Input parameter `provider`.
        @return {ProviderCard | None} Function return value.
        """
        card_id = f"card-{provider.value}"
        try:
            return self.query_one(f"#{card_id}", ProviderCard)
        except Exception:
            return None

    def _update_window_buttons(self) -> None:
        """
        @brief Execute update window buttons.
        @details Applies update window buttons logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        buttons = {
            WindowPeriod.HOUR_5: "#btn-5h",
            WindowPeriod.DAY_7: "#btn-7d",
        }
        for period, btn_id in buttons.items():
            try:
                btn = self.query_one(btn_id, Button)
                if period == self.window:
                    btn.add_class("active")
                else:
                    btn.remove_class("active")
            except Exception:
                pass

    def _update_json_view(self) -> None:
        """
        @brief Execute update json view.
        @details Applies update json view logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
        @return {None} Function return value.
        """
        json_view = self.query_one("#json-view", RawJsonView)
        data = {}
        for provider_name, result in self.results.items():
            if result:
                data[provider_name.value] = result.model_dump(mode="json")
        json_view.data = data


def run_ui() -> None:
    """
    @brief Execute run ui.
    @details Applies run ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    app = AIBarUI()
    app.run()


if __name__ == "__main__":
    run_ui()
