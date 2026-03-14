# AIBar GNOME Extension Plan (Current Implementation Contract)

## 1. Scope
- Artifact: `src/aibar/gnome-extension/aibar@aibar.panel/extension.js`
- Supporting artifacts: `src/aibar/gnome-extension/aibar@aibar.panel/metadata.json`, `src/aibar/gnome-extension/aibar@aibar.panel/stylesheet.css`, `scripts/install-gnome-extension.sh`, `scripts/test-gnome-extension.sh`
- Goal: keep GNOME extension behavior aligned with `docs/REQUIREMENTS.md` and implemented runtime flow.

## 2. Requirement Anchors
- `PRJ-004`: extension identity and GNOME nested-shell testing contract.
- `DES-005`: env-file parsing in extension runtime.
- `DES-006`: refresh interval from JSON `extension.gnome_refresh_interval_seconds`; forced refresh action uses `--force`.
- `REQ-003`: CLI JSON envelope consumed by extension.
- `REQ-016`: env injection before subprocess execution.
- `REQ-017`: popup labels, reset text, quota labels, per-card update timestamp.
- `REQ-018`: error state (`Err`) handling requirement.
- `REQ-019`: deterministic provider sort with fallback lexical order.
- `REQ-021`: fixed panel status label order.
- `REQ-022`: provider class/color mapping and zero-cost visibility rule.
- `REQ-053`: no aggregated total panel cost.
- `REQ-061`: GeminiAI provider integration and ordering.
- `REQ-062`: display label `GEMINIAI` while key remains `geminiai`.
- `REQ-069`: icon color/blink thresholds.
- `REQ-025`/`REQ-026`/`REQ-027`/`REQ-028`/`REQ-029`/`REQ-030`/`REQ-031`/`REQ-032`/`REQ-033`: install/test script behavior.

## 3. Canonical Runtime JSON Contract
Extension input comes from `aibar show --json` with top-level sections:

```json
{
  "payload": {
    "claude": {
      "provider": "claude",
      "window": "7d",
      "metrics": {
        "cost": 0.0,
        "currency_symbol": "$"
      },
      "updated_at": "2026-01-01T12:00:00Z",
      "raw": {},
      "error": null
    }
  },
  "status": {
    "claude": {
      "7d": {
        "result": "OK",
        "error": null,
        "updated_at": "2026-01-01T12:00:00Z",
        "status_code": 200
      }
    }
  },
  "extension": {
    "gnome_refresh_interval_seconds": 60
  }
}
```

## 4. UI and Interaction Contract

### 4.1 Extension Identity and Branding
- Metadata `name`: `AIBar Monitor`.
- Popup header title: `AIBar`.
- Popup actions: `Refresh Now`, `Open AIBar Report`.
- Provider display mapping includes `geminiai -> GEMINIAI`.

### 4.2 Provider Ordering
- Internal provider priority array: `['claude', 'openrouter', 'copilot', 'codex', 'geminiai']`.
- Unknown providers: appended after known providers and sorted alphabetically.

### 4.3 Panel Status Labels (ordered)
1. Claude 5h percentage
2. Claude 7d percentage
3. Claude cost
4. OpenRouter cost
5. Copilot 30d percentage
6. Codex 5h percentage
7. Codex 7d percentage
8. Codex cost
9. OpenAI cost
10. GeminiAI cost

### 4.4 Cost and Quota Rendering
- Panel cost labels use per-provider `metrics.currency_symbol`.
- Zero numeric cost is rendered; unavailable cost is hidden.
- Quota-only cards render `Remaining credits: <remaining>/<limit>` with bold remaining value.
- Reset labels use `Reset in:` prefix.
- Displayed `100.0%` for quota providers appends `⚠️ Limit reached!`.

### 4.5 Refresh and Scheduling
- Default refresh constant: `REFRESH_INTERVAL_SECONDS = 60`.
- Automatic refresh executes `aibar show --json`.
- Popup `Refresh Now` executes `aibar show --json --force`.
- Parsed `extension.gnome_refresh_interval_seconds` updates timer dynamically.

### 4.6 Environment Injection
- Extension reads `~/.config/aibar/env`.
- Parsed key/value pairs are injected into subprocess environment before CLI spawn.

### 4.7 Error Path
- Command or parse failure sets panel label `Err` and resets panel metrics visibility.
- Provider-card error source precedence: cached `status` error over payload inline error.

### 4.8 Icon Severity
- `<= 25`: bright white.
- `> 25`: bright yellow.
- `> 50`: bright orange.
- `> 75`: bright red.
- `> 90`: blinking bright-red/dim-red.

## 5. File-Level Implementation Map
- `src/aibar/gnome-extension/aibar@aibar.panel/extension.js`
  - Lifecycle: `AIBarExtension.enable(...)`, `AIBarExtension.disable(...)`
  - Runtime: `_refreshData(forceRefresh = false)`, `_parseOutput(...)`, `_updateUI(...)`, `_populateProviderCard(...)`, `_handleError(...)`
- `src/aibar/gnome-extension/aibar@aibar.panel/metadata.json`
  - Identity and owner metadata for GNOME extension package.
- `src/aibar/gnome-extension/aibar@aibar.panel/stylesheet.css`
  - Provider tab/progress class styling including GeminiAI class variants.
- `scripts/install-gnome-extension.sh`
  - Git-root resolution, source validation, copy with `cp -a`, extension enable.
- `scripts/test-gnome-extension.sh`
  - Update via installer then nested shell launch at `MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800`.

## 6. Installation and Execution Flow

### 6.1 Install/Update Extension
```bash
scripts/install-gnome-extension.sh
```

### 6.2 Nested GNOME Test Session
```bash
scripts/test-gnome-extension.sh
```

Equivalent nested-shell launch contract:
```bash
env MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland
```

## 7. Regression Checklist
- JSON contract includes `payload`, `status`, `extension`.
- Popup action `Refresh Now` uses forced refresh path.
- Popup action `Open AIBar Report` opens CLI report command.
- Provider order preserves GeminiAI position after Codex.
- Display label for provider key `geminiai` is `GEMINIAI`.
- Panel cost labels are per-provider; no total aggregated panel cost.
- Panel icon severity follows threshold ladder and blink behavior.
- Installer remains invocable from any repository subdirectory.
- Nested-shell helper keeps fixed resolution `1024x800` and no subcommand interface.

## 8. Anti-Patterns (Do Not Reintroduce)
- Legacy top-level JSON payload without `payload/status/extension` envelope.
- Hardcoded popup label variants not matching `AIBar` branding.
- Hardcoded total panel cost summary across providers.
- Omission of GeminiAI from provider ordering/rendering pipeline.
