"""
@file
@brief Command-line interface for aibar.
@details Defines command parsing, provider dispatch, formatted output, setup helpers, login flows, and UI launch hooks.
"""

import asyncio
import json
import sys

import click
from click.core import ParameterSource

from aibar.cache import ResultCache
from aibar.config import config
from aibar.providers import (
    ClaudeOAuthProvider,
    OpenAIUsageProvider,
    OpenRouterUsageProvider,
    CopilotProvider,
    CodexProvider,
)
from aibar.providers.base import BaseProvider, ProviderError, ProviderName, ProviderResult, WindowPeriod


def get_providers() -> dict[ProviderName, BaseProvider]:
    """
    @brief Execute get providers.
    @details Applies get providers logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {dict[ProviderName, BaseProvider]} Function return value.
    """
    return {
        ProviderName.CLAUDE: ClaudeOAuthProvider(),
        ProviderName.OPENAI: OpenAIUsageProvider(),
        ProviderName.OPENROUTER: OpenRouterUsageProvider(),
        ProviderName.COPILOT: CopilotProvider(),
        ProviderName.CODEX: CodexProvider(),
    }


def parse_window(window: str) -> WindowPeriod:
    """
    @brief Execute parse window.
    @details Applies parse window logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param window {str} Input parameter `window`.
    @return {WindowPeriod} Function return value.
    @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
    """
    mapping = {
        "5h": WindowPeriod.HOUR_5,
        "7d": WindowPeriod.DAY_7,
        "30d": WindowPeriod.DAY_30,
    }
    if window not in mapping:
        raise click.BadParameter(f"Invalid window. Choose from: {', '.join(mapping.keys())}")
    return mapping[window]


def parse_provider(provider: str) -> ProviderName | None:
    """
    @brief Execute parse provider.
    @details Applies parse provider logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param provider {str} Input parameter `provider`.
    @return {ProviderName | None} Function return value.
    @throws {Exception} Propagates explicit raised error states from internal validation or provider operations.
    """
    if provider == "all":
        return None
    try:
        return ProviderName(provider)
    except ValueError:
        valid = ", ".join([p.value for p in ProviderName] + ["all"])
        raise click.BadParameter(f"Invalid provider. Choose from: {valid}")


def _fetch_result(
    provider: BaseProvider,
    window: WindowPeriod,
    cache: ResultCache | None = None,
) -> ProviderResult:
    """
    @brief Execute provider fetch with cache lookup, store, and last-good fallback.
    @details Checks cache before API call (CTN-004). On successful fetch, stores
    result in cache. On error, falls back to last-known-good cached result when available.
    @param provider {BaseProvider} Provider instance to fetch from.
    @param window {WindowPeriod} Time window for the fetch.
    @param cache {ResultCache | None} Optional cache instance for TTL-based result reuse.
    @return {ProviderResult} Cached, fresh, or last-good fallback result.
    """
    if cache is not None:
        cached = cache.get(provider.name, window)
        if cached is not None:
            return cached
        if cache.is_rate_limited(provider.name):
            last_good = cache.get_last_good(provider.name, window)
            if last_good is not None:
                return last_good

    try:
        result = asyncio.run(provider.fetch(window))
    except ProviderError as exc:
        result = provider._make_error_result(window=window, error=str(exc))
    except Exception as exc:
        result = provider._make_error_result(window=window, error=f"Unexpected error: {exc}")

    if cache is not None:
        cache.set(result)
        if result.is_error:
            last_good = cache.get_last_good(provider.name, window)
            if last_good is not None:
                return last_good

    return result


def _fetch_claude_dual(
    provider: ClaudeOAuthProvider,
    cache: ResultCache,
) -> tuple[ProviderResult, ProviderResult]:
    """
    @brief Fetch Claude 5h and 7d results via a single API call.
    @details Uses ClaudeOAuthProvider.fetch_all_windows to avoid redundant
    HTTP requests. Checks cache before calling API; stores results after;
    falls back to last-known-good on error.
    @param provider {ClaudeOAuthProvider} Claude provider instance.
    @param cache {ResultCache} Cache instance for TTL-based result reuse.
    @return {tuple[ProviderResult, ProviderResult]} (5h_result, 7d_result).
    """
    windows = [WindowPeriod.HOUR_5, WindowPeriod.DAY_7]
    cached_results = {}
    missing_windows = []
    for w in windows:
        cached = cache.get(provider.name, w)
        if cached is not None:
            cached_results[w] = cached
        else:
            missing_windows.append(w)

    if not missing_windows:
        return cached_results[WindowPeriod.HOUR_5], cached_results[WindowPeriod.DAY_7]

    if cache.is_rate_limited(provider.name):
        for w in missing_windows:
            last_good = cache.get_last_good(provider.name, w)
            if last_good is not None:
                cached_results[w] = last_good
            else:
                cached_results[w] = provider._make_error_result(
                    window=w, error="Rate limited. Try again later.",
                )
        return cached_results[WindowPeriod.HOUR_5], cached_results[WindowPeriod.DAY_7]

    try:
        fetched = asyncio.run(provider.fetch_all_windows(missing_windows))
    except ProviderError as exc:
        fetched = {
            w: provider._make_error_result(window=w, error=str(exc))
            for w in missing_windows
        }
    except Exception as exc:
        fetched = {
            w: provider._make_error_result(window=w, error=f"Unexpected error: {exc}")
            for w in missing_windows
        }

    for w, result in fetched.items():
        cache.set(result)
        if result.is_error:
            last_good = cache.get_last_good(provider.name, w)
            if last_good is not None:
                fetched[w] = last_good

    all_results = {**cached_results, **fetched}
    return all_results[WindowPeriod.HOUR_5], all_results[WindowPeriod.DAY_7]


@click.group()
@click.version_option()
def main() -> None:
    """
    @brief Execute main.
    @details Applies main logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    pass


@main.command()
@click.option(
    "--provider",
    "-p",
    default="all",
    help="Provider to query (claude, openai, openrouter, copilot, codex, all)",
)
@click.option(
    "--window",
    "-w",
    default="7d",
    help="Time window (5h, 7d, 30d)",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output raw JSON instead of formatted text",
)
def show(provider: str, window: str, output_json: bool) -> None:
    """
    @brief Execute show with per-provider TTL cache and single-call dual-window optimization.
    @details Instantiates a ResultCache for CLI-path caching (CTN-004). For Claude
    dual-window mode, uses fetch_all_windows to make one API call instead of two.
    Falls back to last-known-good cached results on provider errors.
    @param provider {str} CLI provider selector string.
    @param window {str} CLI window period string.
    @param output_json {bool} When True, emit JSON output instead of formatted text.
    @return {None} Function return value.
    """
    window_period = parse_window(window)
    provider_filter = parse_provider(provider)

    ctx = click.get_current_context()
    window_source = ctx.get_parameter_source("window")

    providers = get_providers()
    cache = ResultCache()

    # Filter to specific provider if requested
    if provider_filter:
        if provider_filter not in providers:
            click.echo(f"Provider {provider_filter.value} not implemented yet.", err=True)
            sys.exit(1)
        providers = {provider_filter: providers[provider_filter]}

    results = {}
    for name, prov in providers.items():
        if not prov.is_configured():
            if not output_json:
                click.echo(f"\n{name.value}: Not configured")
                click.echo(f"  Set {config.ENV_VARS.get(name)} environment variable")
            continue

        # Show both 5h and 7d windows for quota-based providers when using default window
        show_dual_windows = (
            not output_json
            and window_source == ParameterSource.DEFAULT
            and name in {ProviderName.CLAUDE, ProviderName.CODEX}
        )

        if show_dual_windows:
            if name == ProviderName.CLAUDE and isinstance(prov, ClaudeOAuthProvider):
                result_5h, result_7d = _fetch_claude_dual(prov, cache)
            else:
                result_5h = _fetch_result(prov, WindowPeriod.HOUR_5, cache)
                result_7d = _fetch_result(prov, WindowPeriod.DAY_7, cache)
            results[name.value] = result_7d
            _print_result(name, result_5h, label="5h")
            _print_result(name, result_7d, label="7d")
        else:
            result = _fetch_result(prov, window_period, cache)
            results[name.value] = result
            if not output_json:
                _print_result(name, result)

    if output_json:
        output = {k: v.model_dump(mode="json") for k, v in results.items()}
        click.echo(json.dumps(output, indent=2))


def _print_result(name: ProviderName, result, label: str | None = None) -> None:
    """
    @brief Execute print result.
    @details Applies print result logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param name {ProviderName} Input parameter `name`.
    @param result {None} Input parameter `result`.
    @param label {str | None} Input parameter `label`.
    @return {None} Function return value.
    """
    title = name.value.upper()
    if label:
        title = f"{title} ({label})"
    click.echo(f"\n{click.style(title, bold=True)}")
    click.echo("-" * 40)

    if result.is_error:
        click.echo(click.style(f"Error: {result.error}", fg="red"))
        return

    m = result.metrics

    # Usage percentage (Claude)
    if m.usage_percent is not None:
        pct = m.usage_percent
        color = "green" if pct < 50 else ("yellow" if pct < 80 else "red")
        bar = _progress_bar(pct)
        click.echo(f"Usage:    {bar} {click.style(f'{pct:.1f}%', fg=color)}")

    # Reset time
    if m.reset_at:
        from datetime import datetime, timezone

        delta = m.reset_at - datetime.now(timezone.utc)
        if delta.total_seconds() > 0:
            click.echo(f"Resets in: {_format_reset_duration(delta.total_seconds())}")

    if (
        name in (ProviderName.CLAUDE, ProviderName.CODEX, ProviderName.COPILOT)
        and m.remaining is not None
        and m.limit is not None
    ):
        click.echo(f"Remaining credits: {m.remaining:.1f} / {m.limit:.1f}")

    # Cost
    if m.cost is not None:
        click.echo(f"Cost:     ${m.cost:.4f}")

    # Requests
    if m.requests is not None:
        click.echo(f"Requests: {m.requests:,}")

    # Tokens
    if m.input_tokens is not None or m.output_tokens is not None:
        total = (m.input_tokens or 0) + (m.output_tokens or 0)
        click.echo(
            f"Tokens:   {total:,} ({m.input_tokens or 0:,} in / {m.output_tokens or 0:,} out)"
        )


def _format_reset_duration(seconds: float) -> str:
    """
    @brief Execute format reset duration.
    @details Applies format reset duration logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param seconds {float} Input parameter `seconds`.
    @return {str} Function return value.
    """
    total_minutes = int(seconds // 60)
    days = total_minutes // (24 * 60)
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    return f"{hours}h {minutes}m"


def _progress_bar(percent: float, width: int = 20) -> str:
    """
    @brief Execute progress bar.
    @details Applies progress bar logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param percent {float} Input parameter `percent`.
    @param width {int} Input parameter `width`.
    @return {str} Function return value.
    """
    filled = int(width * percent / 100)
    empty = width - filled
    return f"[{'#' * filled}{'-' * empty}]"


@main.command()
def doctor() -> None:
    """
    @brief Execute doctor.
    @details Applies doctor logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    click.echo("Usage UI Doctor")
    click.echo("=" * 40)
    click.echo()

    providers = get_providers()
    all_ok = True

    for name, provider in providers.items():
        info = config.get_provider_status(name)

        click.echo(f"{click.style(info['name'], bold=True)}")

        # Check configuration
        if info["configured"]:
            click.echo(f"  Config:     {click.style('OK', fg='green')} ({info['token_preview']})")
        else:
            click.echo(f"  Config:     {click.style('MISSING', fg='red')}")
            click.echo(f"              Set: {info['env_var']}")
            all_ok = False
            click.echo()
            continue

        # Test connectivity
        click.echo("  Testing:    ", nl=False)
        result = _fetch_result(provider, WindowPeriod.HOUR_5)
        if result.is_error:
            click.echo(click.style(f"FAILED - {result.error}", fg="red"))
            all_ok = False
        else:
            click.echo(click.style("OK", fg="green"))

        # Show notes
        if info.get("note"):
            click.echo(f"  Note:       {info['note']}")

        click.echo()

    # Summary
    click.echo("-" * 40)
    if all_ok:
        click.echo(click.style("All providers healthy!", fg="green"))
    else:
        click.echo(click.style("Some providers need attention.", fg="yellow"))


@main.command()
def ui() -> None:
    """
    @brief Execute ui.
    @details Applies ui logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.ui import run_ui

    run_ui()


@main.command()
def env() -> None:
    """
    @brief Execute env.
    @details Applies env logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    click.echo(config.get_env_var_help())


@main.command()
def setup() -> None:
    """
    @brief Execute setup.
    @details Applies setup logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.config import ENV_FILE_PATH, write_env_file

    click.echo()
    click.echo("Usage UI Setup")
    click.echo("=" * 40)
    click.echo()
    click.echo(f"Keys will be saved to: {ENV_FILE_PATH}")
    click.echo("Press Enter to skip any key.")
    click.echo()

    updates: dict[str, str] = {}

    # OpenRouter API key
    click.echo(click.style("OpenRouter", bold=True))
    click.echo("  Get your API key from: https://openrouter.ai/keys")
    openrouter_key = click.prompt("  OPENROUTER_API_KEY", default="", show_default=False).strip()
    if openrouter_key:
        updates["OPENROUTER_API_KEY"] = openrouter_key
        click.echo("  -> Set")
    else:
        click.echo("  -> Skipped")
    click.echo()

    # OpenAI Admin key
    click.echo(click.style("OpenAI", bold=True))
    click.echo("  Requires organization admin API key.")
    click.echo("  Get it from: https://platform.openai.com/settings/organization/admin-keys")
    openai_key = click.prompt("  OPENAI_ADMIN_KEY", default="", show_default=False).strip()
    if openai_key:
        updates["OPENAI_ADMIN_KEY"] = openai_key
        click.echo("  -> Set")
    else:
        click.echo("  -> Skipped")
    click.echo()

    # GitHub token (optional)
    click.echo(click.style("GitHub Copilot", bold=True))
    click.echo("  Optional: provide a GitHub token, or use device flow login later.")
    click.echo("  Recommended: run 'aibar login --provider copilot' instead.")
    github_token = click.prompt("  GITHUB_TOKEN", default="", show_default=False).strip()
    if github_token:
        updates["GITHUB_TOKEN"] = github_token
        click.echo("  -> Set")
    else:
        click.echo("  -> Skipped")
    click.echo()

    # Claude - print instructions only
    click.echo(click.style("Claude Code", bold=True))
    click.echo("  Uses Claude CLI credentials automatically.")
    click.echo("  To set up:")
    click.echo("    npm install -g @anthropics/claude")
    click.echo("    claude setup-token")
    click.echo()

    # Codex - print instructions only
    click.echo(click.style("OpenAI Codex", bold=True))
    click.echo("  Uses Codex CLI credentials automatically.")
    click.echo("  To set up:")
    click.echo("    npm install -g @openai/codex")
    click.echo("    codex")
    click.echo()

    # Write to env file
    if updates:
        write_env_file(updates)
        click.echo("-" * 40)
        click.echo(click.style("Configuration saved!", fg="green"))
        click.echo(f"File: {ENV_FILE_PATH}")
        click.echo()
        click.echo("Keys saved:")
        for key in updates:
            click.echo(f"  {key}: set")
    else:
        click.echo("-" * 40)
        click.echo("No keys provided. Nothing saved.")

    click.echo()
    click.echo("Next steps:")
    click.echo("  aibar show --json")
    click.echo("  aibar show")
    click.echo("  aibar doctor")
    click.echo("  aibar ui")


@main.command()
@click.option(
    "--provider",
    "-p",
    default="claude",
    help="Provider to login to (claude, copilot)",
)
def login(provider: str) -> None:
    """
    @brief Execute login.
    @details Applies login logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @param provider {str} Input parameter `provider`.
    @return {None} Function return value.
    """
    if provider == "claude":
        _login_claude()
    elif provider == "copilot":
        _login_copilot()
    else:
        click.echo(f"Login not supported for provider: {provider}")
        click.echo("Supported providers: claude, copilot")
        sys.exit(1)


def _login_claude() -> None:
    """
    @brief Execute login claude.
    @details Applies login claude logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.claude_cli_auth import ClaudeCLIAuth

    auth = ClaudeCLIAuth()

    if not auth.is_available():
        click.echo(click.style("\n Claude CLI credentials not found", fg="red"))
        click.echo()
        click.echo("To set up Claude CLI:")
        click.echo("  1. Install: npm install -g @anthropics/claude")
        click.echo("  2. Authenticate: claude setup-token")
        click.echo("  3. Then run 'aibar login' again")
        sys.exit(1)

    info = auth.get_token_info()

    if info["expired"]:
        click.echo(click.style("\n Token expired", fg="yellow"))
        click.echo()
        click.echo("Run this to refresh:")
        click.echo("  claude setup-token")
        sys.exit(1)

    token = auth.get_access_token()

    if token:
        click.echo()
        click.echo("=" * 60)
        click.echo(click.style(" Token extracted successfully!", fg="green", bold=True))
        click.echo()
        click.echo(f"  Token:      {token[:15]}...")
        if expires_in := info.get("expires_in_hours"):
            click.echo(f"  Expires in: {expires_in} hours")
        if scopes := info.get("scopes"):
            click.echo(f"  Scopes:     {', '.join(scopes)}")
        click.echo()
        click.echo("Token auto-loaded from ~/.claude/.credentials.json")
        click.echo("You can now run: aibar show --provider claude")
        click.echo("=" * 60)
    else:
        click.echo(click.style("\n Could not extract token", fg="red"))
        sys.exit(1)


def _login_copilot() -> None:
    """
    @brief Execute login copilot.
    @details Applies login copilot logic for AIBar runtime behavior with explicit input/output contracts and deterministic side effects.
    @return {None} Function return value.
    """
    from aibar.providers.copilot import CopilotProvider

    click.echo()
    click.echo("GitHub Copilot Login")
    click.echo("=" * 40)
    click.echo()

    provider = CopilotProvider()

    try:
        asyncio.run(provider.login())
        click.echo()
        click.echo(click.style(" Login successful!", fg="green", bold=True))
        click.echo()
        click.echo("  Token saved to: ~/.config/aibar/copilot.json")
        click.echo()
        click.echo("You can now run: aibar show --provider copilot")
    except Exception as e:
        click.echo(click.style(f"\n Login failed: {e}", fg="red"))
        sys.exit(1)


if __name__ == "__main__":
    main()
