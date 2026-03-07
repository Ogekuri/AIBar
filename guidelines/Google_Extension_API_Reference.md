# Google Extension API Reference

## Contract Metadata
- `scope`: `src/aibar/chrome-extension/background.js` message dispatcher.
- `transport`: `chrome.runtime.sendMessage(request)`.
- `response_envelope`: JSON object with top-level `ok: boolean`.
- `session_persisted_debug_flag`: `debugApiEnabled` defaults to `false`, persists in `chrome.storage.session` across service-worker restarts, and resets on browser process termination.
- `deterministic_debug_disabled_error`:
  - `code`: `DEBUG_API_DISABLED`
  - `error`: `Debug API disabled: enable it in popup configuration for this runtime session.`

## Message Routing Model
- `non_debug_routes`: always callable.
- `debug_routes`: any message where `type` starts with `debug.`; callable only when debug flag is enabled.
- `config_routes`: used to read/update debug flag and refresh interval.

## API Index
- `api.main.snapshot` (primary non-debug API)
- `usage.get_state` (legacy non-debug API)
- `usage.refresh_now` (non-debug trigger API)
- `config.debug_api.get` (non-debug config API)
- `config.debug_api.set` (non-debug config API)
- `config.refresh_interval.set` (non-debug config API)
- `debug.api.describe` (debug API)
- `debug.api.execute` (debug API)
  - `providers.pages.get` debug command available only via `debug.api.execute`
- `debug.get_logs` (debug API)
- `debug.clear_logs` (debug API)
- `debug.export_bundle` (debug API)
- `debug.set_refresh_interval` (debug API)
- `usage.updated` (push event message from background to popup)

## Primary API

### Route: `api.main.snapshot`
- `intent`: one-call payload for popup tab data model and progress-bar rendering for `claude`, `copilot`, `codex`.
- `request_schema`:
```json
{
  "type": "api.main.snapshot"
}
```
- `response_schema`:
```json
{
  "ok": true,
  "snapshot": {
    "endpoint": "api.main.snapshot",
    "tab_order": ["claude", "copilot", "codex"],
    "tab_windows": {
      "claude": ["5h", "7d"],
      "copilot": ["30d"],
      "codex": ["5h", "7d", "code_review"]
    },
    "refresh_interval_seconds": 180,
    "last_cycle_status": "idle|running|ok|partial_error",
    "updated_at": "ISO-8601|null",
    "cycle_counter": 0,
    "last_error": "string|null",
    "provider_fetch_sequence": [
      "https://claude.ai/settings/usage",
      "https://chatgpt.com/codex/settings/usage",
      "https://github.com/settings/copilot/features",
      "https://github.com/settings/billing/premium_requests_usage"
    ],
    "providers": {
      "claude|copilot|codex": {
        "provider": "claude|copilot|codex",
        "windows": {
          "5h|7d|30d": {
            "usage_percent": "number|null",
            "remaining": "number|null",
            "limit": "number|null",
            "reset_at": "ISO-8601|null"
          }
        },
        "error": "string|null",
        "parser": "object|null",
        "source_pages": ["url-string"],
        "extracted_at": "ISO-8601|null",
        "last_success_at": "ISO-8601|null",
        "last_failure_at": "ISO-8601|null"
      }
    }
  }
}
```
- `failure_schema`:
```json
{
  "ok": false,
  "error": "Invalid message payload|Unsupported message type|<runtime error>"
}
```

## Configuration API

### Route: `config.debug_api.get`
- `request_schema`:
```json
{
  "type": "config.debug_api.get"
}
```
- `response_schema`:
```json
{
  "ok": true,
  "debug_api_enabled": false,
  "persisted": true
}
```

### Route: `config.debug_api.set`
- `request_schema`:
```json
{
  "type": "config.debug_api.set",
  "enabled": true
}
```
- `response_schema`:
```json
{
  "ok": true,
  "debug_api_enabled": true,
  "persisted": true
}
```
- `validation_error_schema`:
```json
{
  "ok": false,
  "error": "config.debug_api.set requires boolean enabled"
}
```

### Route: `config.refresh_interval.set`
- `intent`: update refresh interval override with persistent storage and alarm reschedule; always callable without debug enablement.
- `request_schema`:
```json
{
  "type": "config.refresh_interval.set",
  "seconds": 180
}
```
- `response_schema`:
```json
{
  "ok": true,
  "refresh_interval_seconds": 180
}
```
- `validation_error_schema`:
```json
{
  "ok": false,
  "error": "Refresh interval must be >= 60 seconds"
}
```
- `persistence`: value is written to `chrome.storage.local` under `INTERVAL_OVERRIDE_STORAGE_KEY` and survives browser restarts.

## Debug API

### Shared Debug Disabled Error
- `applies_to`: all routes with `type` prefix `debug.`.
- `response_schema_when_disabled`:
```json
{
  "ok": false,
  "code": "DEBUG_API_DISABLED",
  "error": "Debug API disabled: enable it in popup configuration for this runtime session."
}
```

### Route: `debug.api.describe`
- `request_schema`:
```json
{
  "type": "debug.api.describe"
}
```
- `response_schema_when_enabled`:
```json
{
  "ok": true,
  "debug_api_enabled": true,
  "api": {
    "endpoint": "debug.api.execute",
    "commands": [
      "http.get",
      "parser.run",
      "provider.diagnose",
      "providers.diagnose",
      "providers.pages.get",
      "state.get",
      "refresh.run",
      "logs.get",
      "logs.clear",
      "interval.get",
      "interval.set"
    ],
    "defaults": {
      "http_get_max_chars": 16000,
      "max_allowed_chars": 120000,
      "parser_default_urls": {
        "claude": "https://claude.ai/settings/usage",
        "codex": "https://chatgpt.com/codex/settings/usage",
        "copilot_features": "https://github.com/settings/copilot/features",
        "copilot_premium": "https://github.com/settings/billing/premium_requests_usage"
      },
      "provider_diagnose_supported": [
        "claude",
        "codex",
        "copilot_features",
        "copilot_premium",
        "copilot_merged"
      ],
      "providers_diagnose_default": ["claude", "codex", "copilot_merged"],
      "providers_pages_get_urls": [
        "https://claude.ai/settings/usage",
        "https://github.com/settings/copilot/features",
        "https://github.com/settings/billing/premium_requests_usage",
        "https://chatgpt.com/codex/settings/usage"
      ],
      "providers_pages_get_default_related_limit": 6
    }
  }
}
```

### Route: `debug.api.execute`
- `request_schema`:
```json
{
  "type": "debug.api.execute",
  "command": "<command>",
  "args": {"...": "..."}
}
```
- `response_schema_success`:
```json
{
  "ok": true,
  "command": "<command>",
  "debug_api_enabled": true,
  "duration_ms": 123,
  "result": {"command_specific": "payload"}
}
```
- `response_schema_failure`:
```json
{
  "ok": false,
  "command": "<command>",
  "debug_api_enabled": true,
  "duration_ms": 123,
  "error": "<deterministic validation/runtime error>"
}
```

### `debug.api.execute` Command Matrix
- `http.get`
  - `args`: `url`, optional `max_chars`
  - `result_fields`: `response.body_preview`, `response.body_preview_tail`, `response.body_sha256`, `response.html_probe`, HTTP metadata
  - `constraints`: `https` protocol only; allowed hosts `claude.ai`, `chatgpt.com`, `github.com`
- `parser.run`
  - `args`: `provider`, optional `url`, optional inline HTML (`html`, `html_features`, `html_premium`)
  - `result_fields`: `html_probe`, `parser_signal_diagnostics`, `window_assignment_diagnostics`, `parser_payload`, `payload_quality`, `payload_assertion`
- `provider.diagnose`
  - `args`: `provider`, optional provider URL overrides, optional `max_chars`
  - `result_fields`: source response payloads + parser diagnostics and assertions
- `providers.diagnose`
  - `args`: optional `providers` array, optional `max_chars`
  - `result_fields`: `summary`, `providers` map with per-provider diagnostics
- `providers.pages.get`
  - `args`: optional `max_chars`, optional `max_related_resources`
  - `result_fields`:
    - `summary.total|ok|fail`
    - `providers.<provider_key>.diagnostics.response` (HTTP metadata + hash + previews + probe)
    - `providers.<provider_key>.diagnostics.parser_signal_diagnostics`
    - `providers.<provider_key>.diagnostics.window_assignment_diagnostics`
    - `providers.<provider_key>.diagnostics.parser_payload`
    - `providers.<provider_key>.diagnostics.payload_analysis`
    - `providers.<provider_key>.diagnostics.related_content.discovered_total|fetched_total|resources[]`
  - `constraints`:
    - primary URLs are fixed to the four provider settings pages.
    - related resources are auto-discovered from `<script src>` / `<link href>` in fetched HTML.
    - related resources are restricted to same-origin `https` URLs and host allowlist (`claude.ai`, `github.com`, `chatgpt.com`).
    - `max_related_resources` is clamped to `[0, 20]`.
- `state.get`
  - `result_fields`: cloned runtime state
- `refresh.run`
  - `effect`: triggers full refresh cycle
  - `result_fields`: cloned runtime state after refresh
- `logs.get`
  - `result_fields`: persisted debug log array
- `logs.clear`
  - `result_fields`: `cleared: true`
- `interval.get`
  - `result_fields`: `refresh_interval_seconds`
- `interval.set`
  - `args`: `seconds` (`>= 60`)
  - `result_fields`: updated `refresh_interval_seconds`

## Auxiliary Runtime APIs

### Route: `usage.get_state` (legacy)
- `intent`: backwards-compatible raw state retrieval plus normalized snapshot.
- `request_schema`: `{ "type": "usage.get_state" }`
- `response_schema`: `{ "ok": true, "state": {"..."}, "snapshot": {"...api.main.snapshot payload..."} }`

### Route: `usage.refresh_now`
- `intent`: trigger manual refresh and return state/snapshot.
- `request_schema`: `{ "type": "usage.refresh_now" }`
- `response_schema`: `{ "ok": true, "state": {"..."}, "snapshot": {"...api.main.snapshot payload..."} }`

### Route: `debug.get_logs`
- `request_schema`: `{ "type": "debug.get_logs" }`
- `response_schema_when_enabled`: `{ "ok": true, "logs": [] }`
- `response_schema_when_disabled`: shared `DEBUG_API_DISABLED` response.

### Route: `debug.clear_logs`
- `request_schema`: `{ "type": "debug.clear_logs" }`
- `response_schema_when_enabled`: `{ "ok": true }`
- `response_schema_when_disabled`: shared `DEBUG_API_DISABLED` response.

### Route: `debug.export_bundle`
- `request_schema`: `{ "type": "debug.export_bundle" }`
- `response_schema_when_enabled`: `{ "ok": true, "bundle": {"state": {}, "logs": []} }`
- `response_schema_when_disabled`: shared `DEBUG_API_DISABLED` response.

### Route: `debug.set_refresh_interval`
- `request_schema`: `{ "type": "debug.set_refresh_interval", "seconds": 180 }`
- `response_schema_when_enabled`: `{ "ok": true, "refresh_interval_seconds": 180 }`
- `validation_error`: `{ "ok": false, "error": "Refresh interval must be >= 60 seconds" }`
- `response_schema_when_disabled`: shared `DEBUG_API_DISABLED` response.

### Push Event: `usage.updated`
- `direction`: background -> popup.
- `event_payload_schema`:
```json
{
  "type": "usage.updated",
  "snapshot": {"...api.main.snapshot payload..."}
}
```

## Integration Rules
- Always call `config.debug_api.get` on popup initialization to synchronize UI toggle state.
- Call `config.debug_api.set` explicitly to enable debug routes for current browser session.
- Do not assume debug enablement persistence across browser restarts.
- Consume `api.main.snapshot` as the canonical one-call source for tab rendering model (`tab_order`, `tab_windows`, `providers[*].windows`).

## Simple API Call Examples

### Example: Primary snapshot (always available)
```js
const snapshotResponse = await chrome.runtime.sendMessage({ type: "api.main.snapshot" });
if (!snapshotResponse?.ok) {
  throw new Error(snapshotResponse?.error ?? "api.main.snapshot failed");
}
console.log(snapshotResponse.snapshot.providers.claude.windows["5h"]);
```

### Example: Enable debug API for current browser session
```js
const enableDebugResponse = await chrome.runtime.sendMessage({
  type: "config.debug_api.set",
  enabled: true,
});
if (!enableDebugResponse?.ok) {
  throw new Error(enableDebugResponse?.error ?? "config.debug_api.set failed");
}
console.log(enableDebugResponse.debug_api_enabled);
```

### Example: Discover debug command catalog
```js
const describeResponse = await chrome.runtime.sendMessage({ type: "debug.api.describe" });
if (!describeResponse?.ok) {
  throw new Error(describeResponse?.error ?? "debug.api.describe failed");
}
console.log(describeResponse.api.commands);
```

### Example: Execute `debug.api.execute` with `providers.pages.get`
```js
const diagnosticsResponse = await chrome.runtime.sendMessage({
  type: "debug.api.execute",
  command: "providers.pages.get",
  args: {
    max_chars: 12000,
    max_related_resources: 4,
  },
});

if (!diagnosticsResponse?.ok) {
  if (diagnosticsResponse?.code === "DEBUG_API_DISABLED") {
    throw new Error("Enable debug API first via config.debug_api.set");
  }
  throw new Error(diagnosticsResponse?.error ?? "debug.api.execute failed");
}
console.log(diagnosticsResponse.result.summary);
```

## HTTP CLI Examples (`curl` / `wget`)
- `scope_note`: direct `curl`/`wget` calls can fetch provider pages immediately; runtime message payload examples require an external local bridge that forwards HTTP payloads to `chrome.runtime.sendMessage`.

### Example: `curl` request
```bash
curl -sS \
  -H "Cookie: <session-cookie>" \
  "https://chatgpt.com/codex/settings/usage"
```

### Example: `wget` request
```bash
wget -qO- \
  --header="Cookie: <session-cookie>" \
  "https://github.com/settings/copilot/features"
```

### Example: `curl` JSON payload for `debug.api.execute` bridge
```bash
curl -sS -X POST "http://127.0.0.1:8765/extension/message" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "debug.api.execute",
    "command": "http.get",
    "args": {
      "url": "https://claude.ai/settings/usage",
      "max_chars": 12000
    }
  }'
```

### Example: `wget` JSON payload for `api.main.snapshot` bridge
```bash
wget -qO- \
  --header="Content-Type: application/json" \
  --post-data='{"type":"api.main.snapshot"}' \
  "http://127.0.0.1:8765/extension/message"
```
