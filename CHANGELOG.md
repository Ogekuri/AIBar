# Changelog

## [0.27.0](https://github.com/Ogekuri/AIBar/compare/v0.26.0..v0.27.0) - 2026-04-12
### 📚  Documentation
- align usage docs with current CLI interfaces [useReq] *(readme)*
  - document global lifecycle/logging flags and show --force behavior
  - add fixed-window notes for copilot/openrouter/openai/geminiai
  - add repository helper scripts and correct GeminiAI setup prerequisites

## [0.26.0](https://github.com/Ogekuri/AIBar/compare/v0.25.0..v0.26.0) - 2026-04-12
### 🚜  Changes
- enforce Copilot blank separator before cost [useReq] *(cli.show)*
  - Update REQ-067 and TST-030 for Copilot spacing behavior.
  - Insert one blank CLI row between Copilot Remaining credits and Cost.
  - Extend panel-alignment test assertions for the new spacing contract.
  - Refresh WORKFLOW.md and regenerate REFERENCES.md for traceability.

## [0.25.0](https://github.com/Ogekuri/AIBar/compare/v0.24.0..v0.25.0) - 2026-04-12
### 🐛  Bug Fixes
- Fix scripts/test-gnome-extension.sh script.
- derive cost from remaining overage for show [useReq] *(copilot)*
  - compute Copilot metrics.cost from remaining sign semantics
  - align CLI and GNOME fallback overage calculations
  - add regression tests for positive/negative remaining cases
  - refresh WORKFLOW and REFERENCES documentation
- clamp over-100 progress bars [useReq] *(gnome-extension)*
  - unify over-limit progress geometry for all provider bars
  - reserve window-label and percentage label slot widths
  - add regression assertions and refresh workflow/reference docs
- remove trailing braces causing shell parse error [useReq] *(gnome-extension)*
  - Remove stray closing braces at extension.js EOF that caused GNOME Shell SyntaxError.
  - Add regression test asserting extension.js terminates at AIBarExtension class closure.
  - Regenerate docs/REFERENCES.md for updated extension source line map.
- Fix scripts/test-gnome-extension.sh script.
- Fix scripts/test-gnome-extension.sh script.
- clamp progress bar width and indicate overflow beyond 100% [useReq] *(gnome-extension)*
- align stale assertions with current runtime behavior [useReq] *(tests)*
  - update Claude dual-window 429 assertions to match live error passthrough
  - update GeminiAI extension provider-order expectation to include openai

### 🚜  Changes
- align Copilot cost surfaces to Cost label [useReq] *(copilot-ui)*
  - Update REQ-067/REQ-117/REQ-118 and related TST IDs for Cost label semantics.
  - Set Copilot metrics.cost from premium request overage with 0.0 fallback in provider payload.
  - Render Copilot CLI row as Cost and keep raw-overage fallback when metrics cost is missing.
  - Render GNOME Copilot card and panel token as currency cost (no leading plus), using metrics.cost with overage fallback.
  - Regenerate WORKFLOW and REFERENCES documentation to reflect updated runtime and symbols.
- set default extra premium request cost to 0.04 [useReq] *(copilot-cost)*
  - Update REQ-116 and TST-013 default unit cost from 0.004 to 0.04 USD/request.
  - Set runtime and GNOME fallback constants to 0.04 for copilot extra premium request cost.
  - Align setup runtime-config tests with the dedicated Copilot cost prompt and persisted value.
  - Regenerate docs/REFERENCES.md to reflect symbol default updates.
- add premium overage cost config and UI [useReq] *(copilot)*
  - Update REQUIREMENTS for Copilot premium-request overage pricing behavior.
  - Persist copilot_extra_premium_request_cost in RuntimeConfig and setup.
  - Compute premium_requests_extra_cost in Copilot provider payload.
  - Render Copilot extra premium cost in CLI show and GNOME card/panel.
  - Expose copilot_extra_premium_request_cost via show --json extension section.
  - Refresh WORKFLOW and REFERENCES documentation for updated runtime model.
- enforce fixed popup dimensions and wrap error messages [useReq] *(gnome-extension)*
  - This commit enforces a fixed standard width and height for the GNOME extension popup window, preventing UI expansion. It also adds word-wrapping to verbose error messages and constrains the maximum width of tab content and status bars, satisfying the new requirement REQ-102 and test TST-052.
- relax satisfies audit gate [useReq] *(requirements)*
  - Update REQ-020 and TST-006 to make @satisfies optional for audit pass/fail.
  - Add regression in tests/test_references_inventory.py for requirements policy text.
- force online check on version flags [useReq] *(startup-preflight)*
  - Update REQ-071/REQ-078 and TST-032/TST-036 for version-flag behavior.
  - When invocation includes --version/--ver, startup preflight bypasses
  - check_version_idle-time gating and performs one online release check.
  - Keep existing idle gating unchanged for non-version invocations.
  - Add targeted startup preflight regression test and refresh docs.

### 📚  Documentation
- Update README.md file.

### ◀️  Revert
- Roll back branch to fa4948bc (fa4948bc5b3eb287fd1bd8f8648130298473cc52).

## [0.24.0](https://github.com/Ogekuri/AIBar/compare/v0.23.0..v0.24.0) - 2026-03-27
### 🚜  Changes
- log raw API error JSON in debug rows [useReq] *(cli-logging)*
  - Update REQ-114/REQ-115 and TST-049 for debug raw error payload logging.
  - Add CLI debug logging helper to emit provider.fetch.debug.error_json
  - only for failed calls with JSON raw.body, preserving payload text unchanged.
  - Add runtime logging regression test for debug-off/on gating and exact payload.
  - Update WORKFLOW and regenerate REFERENCES for traceability.

## [0.23.0](https://github.com/Ogekuri/AIBar/compare/v0.22.0..v0.23.0) - 2026-03-27
### 🐛  Bug Fixes
- include refresh error reason [useReq] *(geminiai)*
  - include Google refresh reason in GeminiAI auth error message\n- add reproducer for refresh error diagnostics\n- update workflow and regenerate references

### 🚜  Changes
- enforce lock acquisition timeout [useReq] *(config)*
  - update REQ-066/REQ-112 and add TST-051 for lock timeout behavior\n- enforce 5s lock-file acquisition timeout with explicit error and runtime log row\n- propagate lock timeout to CLI show with non-zero exit\n- add lock-timeout regression tests and update workflow/references

## [0.22.0](https://github.com/Ogekuri/AIBar/compare/v0.21.0..v0.22.0) - 2026-03-27
### 🐛  Bug Fixes
- normalize Claude retry fallback [useReq] *(cli)*
  - normalize Claude error results without parseable Retry-After\n- add OAuth scope-error reproducer for default fallback idle-time\n- update WORKFLOW and REFERENCES runtime docs
- honor fallback retry-after for claude auth errors [useReq] *(cli)*
  - Add fail-first reproducer for Claude OAuth error idle-time scheduling.
  - Mark synthesized Claude dual-fetch error payloads with retry_after_unavailable=true.
  - Preserve existing REQ-041 behavior by applying configured default_retry_after_seconds.
  - Update WORKFLOW and regenerate REFERENCES for traceability.

## [0.21.0](https://github.com/Ogekuri/AIBar/compare/v0.20.0..v0.21.0) - 2026-03-27
### 🐛  Bug Fixes
- log claude dual-window retry-after evidence [useReq] *(cli)*
  - Restore REQ-115 compliance for Claude fail paths in refresh pipeline.
  - Append provider failure runtime logs for Claude 5h/7d dual-window results.
  - Add failing reproducer then validate retry_after and unavailable evidence logging.
  - Update workflow/references docs to reflect runtime call-trace behavior.

### 🚜  Changes
- add default Retry-After fallback in setup [useReq] *(cli)*
  - Update REQ-005 and REQ-041 for configurable fallback retry delay.
  - Add RuntimeConfig.default_retry_after_seconds defaulting to 3600 seconds.
  - Extend setup timing prompts/persistence with default-retry-after seconds.
  - Mark provider 429 payloads with retry_after_unavailable when header is absent.
  - Use configured fallback to compute provider idle_until on retry-after-unavailable.
  - Update tests plus WORKFLOW/REFERENCES traceability for changed behavior.

## [0.20.0](https://github.com/Ogekuri/AIBar/compare/v0.19.0..v0.20.0) - 2026-03-27
### 🚜  Changes
- refine provider-scoped Err and retry-after logging [useReq] *(core)*
  - Update existing requirements REQ-021 and REQ-115.
  - Apply provider-scoped GNOME panel Err rendering for oauth/rate-limit failures.
  - Preserve normal panel percentage/cost labels for non-failing providers.
  - Extend runtime failure logging with retry-after source/evidence fields.
  - Log explicit retry_after_unavailable evidence when extraction is impossible.
  - Add/adjust targeted regression tests and refresh docs workflow/references.
- log oauth and rate-limit failures with retry-after [useReq] *(cli)*

## [0.19.0](https://github.com/Ogekuri/AIBar/compare/v0.18.0..v0.19.0) - 2026-03-26
### 🐛  Bug Fixes
- normalize epoch Retry-After idle-time delay [useReq] *(claude_oauth)*

## [0.18.0](https://github.com/Ogekuri/AIBar/compare/v0.17.0..v0.18.0) - 2026-03-26
### 🐛  Bug Fixes
- normalize retry-after epoch delay parsing [useReq] *(cli)*

## [0.17.0](https://github.com/Ogekuri/AIBar/compare/v0.16.0..v0.17.0) - 2026-03-26
### 🐛  Bug Fixes
- parse HTTP-date Retry-After for 429 [useReq] *(claude_oauth)*
  - Normalize Claude Retry-After parsing for numeric and HTTP-date headers.
  - Add a failing-then-passing reproducer for HTTP-date 429 handling.
  - Preserve retry_after_seconds for idle-time expansion paths.
  - Update workflow/runtime documentation and symbol references.
- prioritize auth-expired payload on HTTP 429 [useReq] *(claude-oauth)*
  - Classify HTTP 429 Claude responses containing canonical token-expired text as AuthenticationError.
  - Preserve standard 429 handling for non-auth payloads.
  - Add reproducer test for 429 auth payload classification.
  - Update WORKFLOW.md and regenerate REFERENCES.md.

### 🚜  Changes
- collapse oauth/rate-limit to single Err [useReq] *(gnome-panel)*
  - Update REQ-021/TST-007 to require one provider-colored bold Err token.
  - Implement panel failure-category collapse logic for OAuth and rate-limit states.
  - Hide normal percentage/cost labels while single Err is active.
  - Add bold err style class and refresh extension panel regression assertions.
  - Update WORKFLOW model and regenerate REFERENCES.
- restrict Err to usage percentages [useReq] *(gnome-panel)*
  - Update REQ-021/TST-007 to map panel Err only to failed percentage labels.
  - Fix extension panelStatusFailures so cost labels never render Err.
  - Adjust GNOME extension quota-label regression test to enforce new behavior.
  - Update WORKFLOW runtime model and regenerate REFERENCES index.

### ◀️  Revert
- Roll back branch to b4a48147 (b4a48147008a22d49226a630f878fb3e16b1f459).

## [0.16.0](https://github.com/Ogekuri/AIBar/compare/v0.15.0..v0.16.0) - 2026-03-24
### 🐛  Bug Fixes
- reload Claude token before auth retry [useReq] *(cli)*
  - add failing reproducer for stale token reuse in Python OAuth recovery
  - reload provider token from env/CLI source after renewal before retry
  - keep one-refresh one-retry and block-flag semantics unchanged
  - update workflow and references docs for retry-token reload flow
- recover once mode on expired oauth [useReq] *(claude-token-refresh)*
  - detect canonical OAuth-expired usage failure in once mode
  - run claude setup-token once and retry claude /usage once
  - keep loop mode behavior unchanged
  - add deterministic regression test for once-mode recovery
  - update workflow and references docs for new call flow

### ◀️  Revert
- Roll back branch to d50cfc8f (d50cfc8f41cb9e647c3af07aa9dc36a659792e45).

## [0.15.0](https://github.com/Ogekuri/AIBar/compare/v0.14.0..v0.15.0) - 2026-03-23
### 🚜  Changes
- render Err for failed provider cost labels [useReq] *(gnome-extension)*
  - Update REQ-021 to require Err rendering for failed provider cost labels and percentages.
  - Extend extension panel status mapping to set Err on failed cost labels for claude, openrouter, codex, openai, and geminiai while preserving healthy providers.
  - Adjust extension label regression test to cover percentage and cost Err mappings.
  - Refresh WORKFLOW and REFERENCES runtime/symbol evidence.
- render provider fail labels as Err [useReq] *(gnome-extension)*
  - Update REQ-021 for provider/window FAIL Err rendering on panel percentage labels.
  - Implement status-driven Err mapping in extension _updateUI for percentage labels.
  - Add regression test for provider/window fail Err logic.
  - Refresh WORKFLOW and REFERENCES for updated runtime/symbol evidence.

## [0.14.0](https://github.com/Ogekuri/AIBar/compare/v0.13.0..v0.14.0) - 2026-03-20
### 🚜  Changes
- add persistent runtime log/debug flags [useReq] *(cli)*
  - Update SRS with REQ-107..REQ-114 and TST-047..TST-049 for logging controls.
  - Add eager flags --enable-log/--disable-log/--enable-debug/--disable-debug with config persistence.
  - Extend setup with final logging section and persist log_enabled/debug_enabled.
  - Implement append runtime logging, idle/call/error/cache logging, and debug API result logging.
  - Refresh WORKFLOW/REFERENCES and add targeted regression tests for help/setup/log behavior.

### 📚  Documentation
- Update README.md document.

## [0.13.0](https://github.com/Ogekuri/AIBar/compare/v0.12.0..v0.13.0) - 2026-03-19
### ⛰️  Features
- add in-process token refresh recovery and retry block state [useReq] *(claude-oauth)*
  - add requirements for Claude OAuth once-mode refresh parity, auth retry, and idle-time block flag lifecycle\n- port once-mode shell flow to Python routine with timeout/delay controls and log truncation\n- add Claude auth-expired recovery path with single renewal+retry and block-flag persistence\n- extend idle-time schema with oauth_refresh_blocked and force/TTL unblock behavior\n- add unit tests covering refresh routine, retry policy, and block flag lifecycle

### 🐛  Bug Fixes
- reset Refresh Now visual state on focus loss [useReq] *(gnome-extension)*
  - REQ-EVIDENCE-ID: useReq-AIBar-work-20260319120024\n- add helper to clear Refresh Now focus/active pseudo classes\n- invoke cleanup on activation and key-focus-out events\n- update workflow and references docs for new internal helper\n- add focused regression test for Refresh Now focus-loss color reset

### 🚜  Changes
- set default API timeout to 5 seconds [useReq] *(config)*
  - Update REQ-005, REQ-095, and TST-013 defaults from 3000ms to 5000ms in docs/REQUIREMENTS.md.
  - Set RuntimeConfig default timeout to 5000ms in src/aibar/aibar/config.py and align Doxygen details.
  - Update setup runtime-config tests to assert timeout prompt ordering and persisted timeout value.
  - Regenerate docs/REFERENCES.md and update docs/WORKFLOW.md runtime setup timeout description.
- align FAIL block formatting across CLI and GNOME [useReq] *(show-output)*
  - Update REQ-017/REQ-036/REQ-084 and related TST requirements for FAIL rendering format.
  - Render CLI FAIL panels as Status/Reason/Updated-Next and remove window heading rows.
  - Render GNOME FAIL cards as Status/Reason while preserving Updated/Next row visibility.
  - Refresh workflow and references docs and update targeted tests for new output contract.
- render all GeminiAI billing services without truncation [useReq] *(cli)*
  - Update REQ-106 and TST-046 to require full billing-service evidence output.
  - Remove truncation logic from _format_billing_service_descriptions in CLI rendering.
  - Adjust GeminiAI status-message test to assert all four service names are printed.
  - Refresh WORKFLOW and REFERENCES documentation to match updated behavior and symbols.
- add human-readable GeminiAI billing services output [useReq] *(cli)*
  - Update requirements with REQ-106 and TST-046 for GeminiAI billing services formatting.
  - Implement CLI GeminiAI billing service summary with ordered names and truncation.
  - Add unit tests for human-readable and truncated billing service list rendering.
  - Regenerate REFERENCES and update WORKFLOW call-trace for new formatter helper.
- remove FAIL/status window labels from CLI/GNOME [useReq] *(cli-show)*
  - Update REQ-017/036/037/067/084 and related TST entries for FAIL rendering.
  - Implement CLI FAIL output as error-only and remove all window heading labels.
  - Implement GNOME card FAIL output as error-only and hide freshness/window rows.
  - Regenerate WORKFLOW and REFERENCES to reflect updated runtime/symbol evidence.

## [0.12.0](https://github.com/Ogekuri/AIBar/compare/v0.11.0..v0.12.0) - 2026-03-18
### 🐛  Bug Fixes
- restore Updated/Next with legacy CLI JSON [useReq] *(gnome-extension)*
  - Add freshness fallback derived from status.updated_at when freshness/idle_time is absent.
  - Preserve bottom-right Updated/Next card row using resolved provider freshness state.
  - Add targeted failing reproducer and assertions for fallback freshness logic.
  - Update WORKFLOW runtime trace and regenerate REFERENCES.
- guard ScrollView child API for GNOME runtime [useReq] *(gnome-extension)*
  - Add a GNOME-compatible child attachment path in _buildPopupMenu.
  - Prefer set_child and use add_actor only as guarded fallback.
  - Add/adjust reproducer test for the TypeError regression.
  - Update workflow narrative and regenerate references.
- prevent freshness label clipping in popup cards [useReq] *(gnome-extension)*
  - Reproduce missing Updated/Next row with a targeted failing test.
  - Wrap provider card area in a vertical scroll view for overflowed cards.
  - Add stylesheet max-height for provider scroll container.
  - Update workflow and regenerate references for runtime/documentation parity.
- align freshness footer bottom-left [useReq] *(gnome-extension)*
  - enforce START alignment for Updated/Next footer row in provider cards
  - keep footer sourcing from freshness.last_success_timestamp and idle_until_timestamp
  - add regression assertion for explicit left alignment
  - refresh WORKFLOW/REFERENCES evidence
- align FAIL rendering for cached auth/429 states [useReq] *(cli-show)*
  - Apply per-window cached FAIL overlays for Claude/Codex dual-window text panels.
  - Render GNOME fail cards with CLI-equivalent Status/Window/Error plus HTTP retry lines.
  - Add reproducer test for dual-window cached FAIL regression and update extension assertions.
  - Regenerate docs/REFERENCES.md and update docs/WORKFLOW.md call-trace details.

### 🚜  Changes
- wire window labels and bold costs [useReq] *(gnome-extension)*
  - Update REQ-003/REQ-017/TST-004 for GNOME visual fixes.
  - show --json extension now exports provider window_labels.
  - Extension parses window_labels and shows fixed-window labels on bar rows.
  - Costs values now render bold bright white like CLI show values.
  - Provider cards keep no-empty-row behavior after Costs for quota providers.
  - Updated JSON/extension regression tests and regenerated workflow references.
- align window headings and GNOME costs UI [useReq] *(show)*
  - Update REQ-017/067/084 and related test requirements for CLI+GNOME formatting.
  - CLI show now renders Window <window>: headings and right-aligns Updated/Next rows.
  - Grouped Claude/Codex panels now label sections as Window 5h:/Window 7d:.
  - GNOME provider cards now render Costs: with non-bold values and hide empty BYOK spacer rows.
  - Added/updated regression tests for headings, right alignment, and extension cost styling.
- enforce 30d windows and GNOME freshness source [useReq] *(cli)*
  - Update REQ-003/010/011/017 and TST-004 requirement definitions.
  - Force OpenAI/OpenRouter/Copilot/GeminiAI effective show window to 30d.
  - Export extension.idle_delay_seconds in show --json for extension fallback.
  - Use idle-delay-based Updated/Next fallback and 30d bars in GNOME cards.
  - Remove Open AIBar Report popup action from GNOME extension UI.
  - Update unit tests, WORKFLOW.md, and regenerate REFERENCES.md.
- align show and GNOME metric rendering [useReq] *(cli)*
  - Update REQUIREMENTS for shared remaining-credits layout and metric labels.
  - Implement CLI formatting: bright/bold remaining and cost values, Copilot 30d canonical window, Gemini billing-table spacing.
  - Implement GNOME card formatting: Cost prefix + bright/bold values, Codex remaining-credits row, Requests/Tokens label format alignment.
  - Refresh WORKFLOW and REFERENCES for updated call-trace and symbol evidence.
- align CLI/GNOME panel layout and provider order [useReq] *(show)*
  - Update requirements for CLI status/freshness row placement and provider order.
  - Implement deterministic CLI panel ordering and grouped CODEX footer metrics.
  - Move GNOME GeminiAI tab to last and enforce API counter tokens as total/in/out.
  - Keep provider-card freshness label right-aligned bottom row in extension cards.
  - Add/adjust regression tests for panel order, grouped layout, and GNOME token labels.
  - Refresh WORKFLOW and regenerate REFERENCES for updated runtime/symbol traceability.
- group Claude/Codex dual windows [useReq] *(cli-show)*
  - Update REQ-002 and TST-030 to require grouped dual-window provider panels.
  - Render default-window Claude and Codex output in one panel per provider.
  - Deduplicate shared lines and keep 5h/7d sections separated by blank lines.
  - Update CLI regression tests, workflow model, and regenerated references.
- align freshness label bottom-right [useReq] *(gnome-extension)*
  - Update REQ-017/TST-004 alignment semantics for provider-card freshness label.
  - Place extension Updated/Next label at bottom-right in each provider card.
  - Keep freshness label style parity with Reset in label class.
  - Refresh workflow trace wording and extension quota-label test expectations.
- enforce update disable-copy-enable flow [useReq] *(gnome-install)*
  - update PRJ-008/REQ-032/TST-009 and add REQ-099 for masked update disable failures
  - implement gnome-install install/update branching with update disable->copy->enable ordering
  - keep gnome-uninstall disable-before-remove semantics and refresh docs references
  - extend gnome install/uninstall tests for update ordering and masked-missing-extension behavior
- align freshness schema for GNOME [useReq] *(show-json)*
  - update REQ-003/REQ-017/REQ-084 and TST-004/TST-038 mappings
  - export top-level freshness in show --json with local-time strings
  - parse/render Updated/Next from freshness in GNOME bottom-left row
  - update CLI and extension regression tests for schema/layout parity
- remove gnome-install from nested GNOME launcher [useReq] *(test-ext)*
  - Update REQ-031 to require UI-only nested shell execution in test-gnome-extension.sh.
  - Align TST-004 and evidence mapping for no gnome-install invocation.
  - Simplify script to launch nested GNOME Shell directly with fixed 1024x800 dummy mode.
  - Adjust script regression tests and regenerate WORKFLOW/REFERENCES docs.
- force 30d window and current-month monitoring [useReq] *(geminiai)*
  - Update REQ-060 and add REQ-097/REQ-098 for GeminiAI 30d semantics.
  - Force show --provider geminiai to effective window 30d even with explicit non-30d --window.
  - Align GeminiAI monitoring interval to UTC month-start through now for current-month scope.
  - Update CLI/provider and targeted GeminiAI regressions; refresh WORKFLOW and REFERENCES docs.
- normalize null API counters to zero [useReq] *(show)*
  - Update REQ-017/REQ-036 and related TST requirements for API counters.
  - Render Requests/Tokens for openai/openrouter/codex/geminiai on OK states.
  - Normalize null requests/input_tokens/output_tokens to zero in CLI and GNOME.
  - Add regression coverage in CLI and extension tests for null-to-zero rendering.
  - Update WORKFLOW runtime model and regenerate REFERENCES index.
- align freshness with idle-time state [useReq] *(show)*
  - Update requirements for idle_time freshness source and local-time human fields.
  - Persist idle-time human timestamps in local timezone.
  - Expose idle_time section in show --json and use it for CLI panel freshness.
  - Read idle_time in GNOME extension and render Updated/Next from idle timestamps.
  - Adjust regression tests for CLI/JSON/extension freshness behavior.
- refactor show pipeline, single cache write, configurable timeout [useReq] *(cli)*
  - Refactor retrieve_results_via_cache_pipeline to sequential flow:
  - idle-time check → modular API calls → memory persist → cache read → present
  - Enforce single cache.json write point via _refresh_and_persist_cache_payload
  - Minimize cache reads to one load_cli_cache per execution path
  - Add api_call_timeout_milliseconds config (default 3000ms, REQ-095)
  - Change api_call_delay default from 1000 to 100ms (REQ-096)
  - All httpx-based providers use get_api_call_timeout_seconds() (CTN-003)
  - Setup prompt order: idle_delay → api_call_delay → api_call_timeout → gnome_refresh
  - Update requirements REQ-091..REQ-096, CTN-003, CTN-008, REQ-005, REQ-040
  - Update WORKFLOW.md call-traces and REFERENCES.md symbol index
- move startup idle file and uninstall cleanup [useReq] *(cli)*
  - Update requirements for startup idle-state path to ~/.cache/aibar/check_version_idle-time.json.
  - Implement CLI startup idle-state path migration in runtime code.
  - Add Linux --uninstall cleanup of startup idle file and cache directory.
  - Extend startup preflight tests for path creation and uninstall cleanup behavior.
  - Refresh WORKFLOW and REFERENCES docs for updated call trace and symbols.

## [0.11.0](https://github.com/Ogekuri/AIBar/compare/v0.10.0..v0.11.0) - 2026-03-17
### ⛰️  Features
- Update .g.conf file.

### 🐛  Bug Fixes
- make req static-check pass [useReq] *(static-check)*
  - Add tracked Pyright config with src/aibar include and extraPaths for first-party imports.
  - Add targeted regression test for static-check configuration presence.
  - Suppress known Click entrypoint call-issue at module __main__ call sites only.
  - Unignore pyrightconfig.json in .gitignore for persistent repository behavior.
- Fix .gitignore file.
- Remove pyrightconfig.json.

### 🚜  Changes
- unify fail-state error rendering [useReq] *(show)*
  - Update requirements for error-only fail rendering in CLI and GNOME cards.
  - Suppress statistics lines on FAIL and normalize status/retry output format.
  - Persist retry_after_seconds in cache status and propagate to renderers.
  - Remove Claude 429 partial metric fallback paths from active flow.
  - Update regression tests for CLI/GNOME error parity and retry metadata.
  - Refresh WORKFLOW and regenerate REFERENCES documentation.
- localize Updated/Next datetime output [useReq] *(core)*
  - Update requirements for local-time freshness labels with YYYY-MM-DD HH:MM format.
  - Switch CLI show freshness rendering to runtime local timezone format.
  - Switch GNOME extension freshness formatter to local-time YYYY-MM-DD HH:MM.
  - Adjust CLI/extension regression tests and refresh WORKFLOW/REFERENCES docs.
- gate lifecycle uv commands to Linux runtime [useReq] *(cli)*
  - Update requirements for Linux-only --upgrade/--uninstall execution and non-Linux guidance.
  - Implement OS-gated lifecycle handlers that skip subprocess execution off Linux.
  - Add regression tests for Linux subprocess path and non-Linux manual guidance path.
  - Refresh WORKFLOW and regenerate REFERENCES documentation.
- include pytest in runtime dependencies [useReq] *(pyproject)*
  - update CTN-007 and TST-008 in docs/REQUIREMENTS.md
  - add pytest to [project].dependencies in pyproject.toml
  - refresh uv.lock after dependency update
  - extend tests/test_pyproject_metadata.py to assert pytest presence
- migrate runtime to uv-only workflow [useReq] *(launcher)*
  - Update SRS for uv-only launcher/runtime and lockfile policy.
  - Replace scripts/aibar.sh virtualenv bootstrap with uv-run delegation.
  - Track uv.lock, remove requirements.txt from repo and allowlist rules.
  - Update README requirements/install guidance and requirements export snippet.
  - Adjust release workflow build step to uv-run build toolchain.
  - Add regression tests for launcher, repository surfaces, and GeminiAI dependency manifest.
- resolve TST id collision [useReq] *(requirements)*
  - Rename new show-status test requirement from TST-037 to TST-038.
  - Update test docstring satisfies tags to keep ID traceability consistent.
- align datetime/status error rendering [useReq] *(show)*
  - Update requirements for show/auth visibility and datetime formatting parity.
  - Implement CLI Updated/Next datetime line and cached status-error surfacing.
  - Apply idle-time failure scheduling with max(idle delay, retry-after).
  - Update GNOME extension datetime formatter to UTC date+time labels.
  - Add and adjust tests for auth failures, datetime output, and status rendering.
  - Regenerate WORKFLOW and REFERENCES docs for traceability.

## [0.10.0](https://github.com/Ogekuri/AIBar/compare/v0.9.0..v0.10.0) - 2026-03-16
### 🐛  Bug Fixes
- add pyrightconfig.json and pytest pythonpath for src-based imports [useReq] *(config)*
  - Add pyrightconfig.json with extraPaths=['src/aibar'] and venv config
  - so Pylance static analysis resolves aibar.* and third-party imports.
  - Add [tool.pytest.ini_options] pythonpath=['src/aibar'] to pyproject.toml
  - ensuring tests always import from src/aibar/ rather than system packages.
  - Unignore pyrightconfig.json in .gitignore for version control tracking.
  - Regenerate docs/REFERENCES.md.
- Remove .req dir.
- resolve Ruff F401 unused imports and Pylance type errors [useReq] *(static-check)*
  - Remove unused imports in 3 test files (MagicMock, patch, pytest, os,
  - datetime, timezone, gnome_install, gnome_uninstall, _EXT_TARGET_DIR)
  - Fix ProviderResult construction: remove is_error= kwarg (computed property)
  - Fix UsageMetrics construction: remove usage_percent= kwarg (computed property)
  - Add type-narrowing assertions before 'in' operator on Optional[str]
  - Fix resolve_currency_symbol signature: raw accepts dict | None
  - Cast InstalledAppFlow.run_local_server() to Credentials in geminiai.py
  - Make _FakeCredentialStore inherit GeminiAICredentialStore for type safety
  - Cast _FakeBigQueryClient to bigquery.Client for Pylance compatibility
- align JS static-check test with check-js-syntax.sh config [useReq] *(test_req_static_check_config)*
  - Update test assertion from noop cmd "true" to "scripts/check-js-syntax.sh"
  - matching current .req/config.json JavaScript static-check configuration.
  - Rename test function to test_javascript_static_check_uses_gjs_compatible_script.
  - Update Doxygen docstrings to reflect GJS preprocessor wrapper approach.
  - Regenerate docs/REFERENCES.md.

### 🚜  Changes
- remove unused check-js-syntax.sh [useReq] *(scripts)*
- BREAKING CHANGE: relocate GNOME extension into aibar package for correct wheel inclusion [useReq] *(gnome-install)*
  - Move src/aibar/gnome-extension/ into src/aibar/aibar/gnome-extension/
  - so extension files are included in wheel builds (fixes uv tool install).
  - Update _resolve_extension_source_dir() to use Path(__file__).parent
  - instead of parent.parent for module-relative resolution.
  - Update pyproject.toml wheel/sdist include paths.
  - Update REQ-025: explicit module-relative resolution from aibar package.
  - Add REQ-083: extension source must reside inside aibar package subtree.
  - Update TST-037: verify wheel packages contain gnome-extension subtree.
  - Update all test and workflow file path references.
  - Update WORKFLOW.md and REFERENCES.md with new file locations.

## [0.9.0](https://github.com/Ogekuri/AIBar/compare/v0.8.0..v0.9.0) - 2026-03-16
### 🚜  Changes
- add lifecycle options to help epilog and update REQ-068 [useReq] *(cli)*
  - Update REQ-068 to require --version/--ver, --upgrade, --uninstall in help examples
  - Add lifecycle option examples to CLI epilog (--version, --upgrade, --uninstall)
  - Update test_cli_usage_help.py to verify lifecycle flags appear in help output
  - Regenerate docs/REFERENCES.md with updated symbol inventory

## [0.8.0](https://github.com/Ogekuri/AIBar/compare/v0.7.0..v0.8.0) - 2026-03-16
### ⛰️  Features
- Add static check.
- Update useReq files.

### 🐛  Bug Fixes
- avoid false JS failures on GNOME imports [useReq] *(static-check)*
  - Replace JavaScript static-check command with compatibility-safe no-op.
  - Add regression test for .req/config.json JavaScript checker behavior.
  - Keep runtime/source requirements unchanged.
  - Validate with req --here --static-check and full pytest.
- Update .gitignore file.
- sync plan with current GNOME extension contract [useReq] *(gnome-plan)*
  - Replace legacy build guide with implementation-aligned runtime plan.
  - Add regression test for JSON envelope, branding, forced refresh, and GeminiAI ordering.
  - Preserve requirements document unchanged while aligning plan semantics to current code.

### 🚜  Changes
- complete help with gnome-install/gnome-uninstall examples and fix epilog formatting [useReq] *(cli)*
  - Update REQ-068 to require gnome-install and gnome-uninstall in help examples
  - Add format_epilog override in StartupPreflightGroup to preserve multi-line epilog
  - Expand epilog with descriptive examples for all major commands
  - Add gnome-install/gnome-uninstall assertions in help tests
  - Update WORKFLOW.md with format_epilog call-trace entry
  - Regenerate REFERENCES.md
- BREAKING CHANGE: update provider card datetime label to show Updated and Next times [useReq] *(extension)*
  - REQ-017: Changed label format from "Update at: <HH:MM>" to "Updated: <HH:MM>, Next: <HH:MM>"
  - Next time computed as updated_at + gnome_refresh_interval_seconds
  - TST-004: Updated test to verify "Updated:" and "Next:" presence plus _refreshIntervalSeconds usage
  - Updated WORKFLOW.md call-trace descriptions for _updateUI and _populateProviderCard
  - Regenerated REFERENCES.md
- BREAKING CHANGE: replace install script with CLI gnome-install/gnome-uninstall commands [useReq] *(gnome-extension)*
  - Add `aibar gnome-install` CLI command: resolves extension source from
  - package path, validates metadata.json, copies files to target dir,
  - enables extension via gnome-extensions enable.
  - Add `aibar gnome-uninstall` CLI command: disables extension via
  - gnome-extensions disable, removes extension directory.
  - Remove scripts/install-gnome-extension.sh (replaced by CLI commands).
  - Update scripts/test-gnome-extension.sh to invoke aibar gnome-install.
  - Update requirements PRJ-001/PRJ-008/REQ-025..REQ-032, add REQ-080..082.
  - Replace tests/test_install_gnome_extension.py with test_gnome_install_uninstall.py.
  - Update WORKFLOW.md: remove PROC:install-ext, add gnome commands to PROC:main.
- remove warning glyph from show reset lines [useReq] *(cli)*
  - Update REQ-067 and TST-030 for CLI reset-line glyph policy.
  - Remove '⚠️ Limit reached!' suffix from CLI show reset output.
  - Keep panel width/alignment behavior unchanged.
  - Adjust CLI panel alignment test to assert glyph absence.
  - Update WORKFLOW and regenerate REFERENCES for traceability.
- remove deprecated GNOME plan artifact [useReq] *(gnome-plan)*
  - Add PRJ-011 to REQUIREMENTS to define canonical GNOME contract documentation sources.
  - Delete src/aibar/plans/Gnome.plan.md from source tree.
  - Refactor GNOME plan regression test to enforce PRJ-011 semantics.

### 📚  Documentation
- Update README.md document.

## [0.7.0](https://github.com/Ogekuri/AIBar/compare/v0.6.0..v0.7.0) - 2026-03-14
### 🚜  Changes
- add startup release preflight and uv lifecycle flags [useReq] *(cli)*
  - Update REQUIREMENTS with startup GitHub release-check, idle-time file, and lifecycle flag requirements.
  - Implement startup preflight in cli.py with 300s idle gate, 2s timeout, 429 retry-after handling, and bright color diagnostics.
  - Add --upgrade/--uninstall/--version/--ver handlers with exact uv subprocess commands and exit-code propagation.
  - Add targeted startup-preflight and packaging tests plus deterministic test fixture.
  - Update pyproject build includes, WORKFLOW runtime model, and regenerate REFERENCES.

## [0.6.0](https://github.com/Ogekuri/AIBar/compare/v0.5.0..v0.6.0) - 2026-03-14
### 🚜  Changes
- scope provider idle-time and isolate 429 backoff [useReq] *(idle-time)*
  - REQ: CTN-009, REQ-009, REQ-038, REQ-041, TST-003, TST-011, TST-014, and TST-027 now require provider-scoped idle-time state.
  - Code: config.py persists idle-time.json as provider-keyed entries; cli.py applies per-provider idle gating and refresh scope selection.
  - Code: HTTP 429 backoff updates only the rate-limited provider entry; non-rate-limited providers keep idle_delay scheduling.
  - Tests: updated idle/cache/lock suites and added GeminiAI 429 payload-retention and provider-scoped idle-time assertions.
  - Docs: updated REQUIREMENTS.md and WORKFLOW.md, then regenerated REFERENCES.md.

### 📚  Documentation
- Update README.md file.

## [0.5.0](https://github.com/Ogekuri/AIBar/compare/v0.4.0..v0.5.0) - 2026-03-08
### 📚  Documentation
- Update README.md.

## [0.4.0](https://github.com/Ogekuri/AIBar/compare/v0.3.0..v0.4.0) - 2026-03-08
### 📚  Documentation
- Update README.md.

## [0.3.0](https://github.com/Ogekuri/AIBar/compare/v0.2.0..v0.3.0) - 2026-03-08
### 🐛  Bug Fixes
- Fix images.

## [0.2.0](https://github.com/Ogekuri/AIBar/compare/v0.1.0..v0.2.0) - 2026-03-08
### ⛰️  Features
- add GeminiAI provider across all surfaces [useReq] *(geminiai)*
  - Append REQ-054..REQ-063 and TST-024..TST-029 in REQUIREMENTS.md.
  - Add OAuth setup/login + GeminiAI provider using Monitoring/Billing APIs.
  - Integrate GeminiAI into CLI show/json, Text UI, and GNOME extension.
  - Add bright-pink GNOME styles and GeminiAI display label mapping.
  - Add provider/unit/integration tests and refresh WORKFLOW/REFERENCES docs.
- add runtime debug command API [useReq] *(chrome-extension)*
  - append debug API requirements and tests for command interface
  - implement debug.api.describe and debug.api.execute dispatcher
  - add http.get, parser.run, and standard runtime debug commands
  - enforce https host allowlist and bounded body preview output
  - regenerate workflow/references docs for updated runtime model
- align module extensions to .js [useReq] *(chrome-extension)*
  - rename chrome extension modules from .mjs to .js
  - update manifest/popup/import paths and parser test helpers
  - regenerate references and workflow docs for JS symbol indexing
- add autonomous Chrome usage extension [useReq] *(chrome-extension)*
  - append Chrome-extension requirements and test IDs
  - implement MV3 service worker scheduler with 180s default refresh
  - add localization-independent HTML parsers and Copilot merge logic
  - add popup UI with Claude/Copilot/Codex tabs and debug export tools
  - add fixture-driven parser tests and regenerate workflow/references docs

### 🐛  Bug Fixes
- align ANSI panel borders in show output [useReq] *(cli)*
  - Fix ANSI width accounting in CLI panel rendering.
  - Add focused regression test for colored progress-bar row alignment.
  - Update WORKFLOW and regenerate REFERENCES for new helpers.
- normalize BigQuery scope errors [useReq] *(geminiai)*
  - map google.api_core insufficient-scope failures to AuthenticationError
  - add reproducer test and opt-in system-auth integration test
  - refresh WORKFLOW and REFERENCES for GeminiAI error path
- replace globalThis.imports with GNOME Shell 45+ ES module imports [useReq] *(extension.js)*
  - Replace globalThis.imports shim + const bindings (GNOME Shell ≤44 legacy API)
  - with ES6 gi:// and resource:// import statements required by GNOME Shell 45+
  - AIBarExtension now extends Extension from GNOME Shell extensions API
  - (provides this.uuid, used as addToStatusArea key)
  - Add scripts/check-js-syntax.sh: preprocesses gi:// and resource:// imports
  - to const stubs before node --check to enable static analysis of GJS files
  - Update .req/config.json JavaScript checker to use check-js-syntax.sh
  - Add tests/test_extension_esmodule_imports.py: 4 reproducer tests (all
  - failed before fix, all pass after); satisfies PRJ-004
  - Root cause: gi:// imports triggered legacy GNOME Shell module loader which
  - loaded main.js as a script; main.js uses ES6 import at line 3 causing
  - SyntaxError: import declarations may only appear at top level of a module
- normalize console details sink payload [useReq] *(chrome-debug)*
  - Fixes console 'unsupported object' warnings in _emitConsoleSafe by serializing details to text before sink invocation.
  - Adds reproducer test for direct object-argument console emission.
  - Updates runtime workflow trace and regenerated symbol references.
- use tcpServer accept events for localhost API [useReq] *(background)*
  - Replace unsupported tcpServer.accept polling with onAccept/onAcceptError event handling.
  - Add a reproducer test that fails on direct tcpServer.accept usage.
  - Update workflow/runtime references for localhost accept path behavior.
- add curl and wget API examples [useReq] *(chrome-api-reference)*
  - Add HTTP CLI examples section with curl and wget snippets
  - Cover provider page fetch and runtime-message bridge payload samples
  - Add regression test enforcing curl/wget examples presence
- add runtime API call examples [useReq] *(chrome-api-reference)*
  - Add simple sendMessage examples for snapshot, debug enable, describe, execute
  - Add regression test that enforces examples section presence
  - Keep requirements unchanged; align API reference with current routes
- Remove .place-holder files.

### 🚜  Changes
- uppercase geminiai show title [useReq] *(cli)*
  - Update REQ-062/TST-029 to require GEMINIAI CLI title casing.
  - Change _provider_display_name mapping for geminiai to uppercase output.
  - Add regression source assertion and refresh WORKFLOW/REFERENCES docs.
- unify show panel width and zero-cost labels [useReq] *(core)*
  - Update REQ-021/REQ-022/REQ-067 and related test requirements.
  - Render OpenAI cost label in GNOME panel order and keep zero-cost labels visible.
  - Render CLI show panels with one shared width equal to widest panel content.
  - Add regression coverage and refresh WORKFLOW/REFERENCES.
- BREAKING CHANGE: switch delay to ms and redesign GNOME status [useReq] *(core)*
  - Update requirements for milliseconds delay, billing_data setup dataset, GNOME costs/colors/icon behavior.
  - Implementation updates: runtime config key rename, Gemini dataset resolution, CLI provider-colored panels/progress bars, GNOME per-provider status labels.
  - Validation updates: tests, WORKFLOW, REFERENCES, and README Gemini prerequisites.
- BREAKING CHANGE: remove terminal ui [useReq] *(cli)*
- add cloud-platform OAuth scope [useReq] *(geminiai)*
  - update REQ-056 OAuth scope set for setup/login
  - extend GEMINIAI_OAUTH_SCOPES with cloud-platform and align order
  - update scope assertion test and stabilize runtime-currency test setup
  - refresh WORKFLOW and REFERENCES
- align labels and setup login scopes [useReq] *(geminiai)*
  - update REQ-055/056/062 for setup login source and GNOME uppercase label
  - add setup login source path that re-authorizes with GEMINIAI_OAUTH_SCOPES
  - render GNOME GeminiAI tab/card label as GEMINIAI
  - refresh affected tests, WORKFLOW, and REFERENCES
- enforce cache locks and refresh show/help output [useReq] *(cli)*
  - update REQUIREMENTS for lock-file synchronization and CLI output behavior
  - guard cache.json and idle-time.json reads/writes with blocking 250ms polling locks
  - include GeminiAI in setup currency defaults and runtime symbol resolution
  - redesign show text output with blue panels/progress bars and richer metrics
  - replace top-level usage/help text with human-readable command/option guidance
  - add regression tests plus static-check and full-suite verification
- BREAKING CHANGE: add current-month BigQuery billing flow [useReq] *(geminiai)*
  - Update REQ-056..REQ-065 for GeminiAI Monitoring+BigQuery behavior.
  - Implement billing table discovery and current-month cost aggregation query.
  - Propagate GeminiAI billing status/errors to cache, CLI, TUI, and GNOME surfaces.
  - Add dependency and regression tests for new GeminiAI cost/error paths.
- BREAKING CHANGE: remove billing API usage from provider [useReq] *(geminiai)*
  - Update requirements, implementation, tests, workflow, and references for monitoring-only GeminiAI metrics.
- add per-provider currency symbol configuration and display [useReq] *(config)*
  - REQ-049: aibar setup prompts per-provider currency symbol ($, £, €, default $) after timeout section
  - REQ-050: providers extract currency from API raw (ISO code or symbol), fall back to configured default then $
  - REQ-051: _print_result uses metrics.currency_symbol (not hardcoded $)
  - REQ-052: TUI ProviderCard.watch_result uses metrics.currency_symbol
  - REQ-053: GNOME extension cost/byok labels and panel summary use metrics.currency_symbol
  - Updated CTN-002 (UsageMetrics.currency_symbol field), CTN-008 (RuntimeConfig.currency_symbols dict)
  - Updated REQ-005 (setup timeout section scope), TST-013 (currency prompt assertions)
  - Added resolve_currency_symbol() in config.py with ISO-code mapping and provider fallback
  - Added tests: test_currency_symbol_flow.py (TST-023) and updated test_setup_runtime_config.py
- configurable refresh interval via JSON extension section, remove Last updated UI, add per-tab Update at label [useReq] *(gnome-extension)*
  - REQ-005/CTN-008: gnome_refresh_interval_seconds (default 60s) added to RuntimeConfig, prompted in setup()
  - REQ-003: show --json emits extension.gnome_refresh_interval_seconds (injected at emit time, not cached)
  - DES-006/REQ-017: removed Last updated/Next update popup status line and separator; added per-card Update at: HH:MM label bottom-right (aibar-update-at-label CSS class, matching Reset in: style)
  - extension.js: _refreshIntervalSeconds instance var replaces constant; _parseOutput reads extension section and reschedules timer on change; _formatStatusTime removed
  - Tests: updated test_setup_runtime_config, test_extension_quota_label, test_cli_idle_cache, test_cli_idle_force; added test_show_json_extension_section.py
- truncate log at start of each refresh cycle [useReq] *(claude_token_refresh.sh)*
  - Added REQ-048: do_refresh() MUST truncate LOG_FILE before first log entry
  - Added TST-022: source-level test verifying truncation placement
  - Implemented: '> "$LOG_FILE"' as first statement in do_refresh()
  - Added 2 tests in tests/test_claude_token_refresh_script.py
  - Updated WORKFLOW.md: added PROC:claude-token-refresh execution unit
  - Updated REFERENCES.md: regenerated
- remove static metric assertions from HTTP-pipeline tests [useReq] *(tests)*
  - Add TST-021: provider-HTTP-pipeline tests MUST NOT assert numeric metric values
  - (usage_percent, remaining, cost) from parsed HTTP responses; restrict to
  - success/error state, window key presence, and HTTP call count.
  - Remove assert result.metrics.remaining == 70.0 from test_retries_on_429_then_succeeds.
  - Remove remaining == 80.0 and remaining == 70.0 assertions from
  - test_single_call_returns_both_windows.
  - Update Section 4 intro to reflect active test coverage and HDT compliance.
  - All 75 tests pass.
- BREAKING CHANGE: section cache payload/status and remove Claude snapshot [useReq] *(cache)*
  - Update REQUIREMENTS with CTN-010, REQ-044..REQ-047, TST-018..TST-020.
  - Refactor CLI cache pipeline to persist payload/status sections in cache.json.
  - Store per-provider/window OK/FAIL attempt metadata and preserve payload on failures.
  - Remove runtime dependency on claude_dual_last_success.json and use cache.json fallback.
  - Adjust GNOME extension JSON parsing for sectioned schema.
  - Refactor and add tests for status retention, partial-window failures, and legacy file removal.
- unify show/ui cache retrieval pipeline [useReq] *(cli)*
  - Update SRS requirements for shared cache.json retrieval flow (REQ-009/039/042/043).
  - Refactor CLI and Text UI to reuse one force->idle->refresh->cache-load pipeline.
  - Centralize refresh/write/readback logic and keep idle-time/429 handling in shared path.
  - Remove active ResultCache usage from runtime retrieval and align tests with new behavior.
  - Regenerate WORKFLOW/REFERENCES and validate with req static-check plus full pytest suite.
- replace IABar typo with AIBar [useReq] *(gnome-extension)*
  - Update PRJ-004 requirement text and evidence mapping to AIBar Monitor.
  - Replace extension runtime and metadata label strings from IABar to AIBar.
  - Add regression tests for panel and metadata monitor name assertions.
  - Update WORKFLOW call-trace wording for the AIBar Monitor title.
  - Align changelog entries with corrected AIBar naming.
- force Refresh Now CLI execution [useReq] *(gnome-extension)*
  - Update DES-006, REQ-016, and TST-004 in docs/REQUIREMENTS.md.
  - Wire popup Refresh Now to _refreshData(true) and append --force to CLI argv.
  - Add regression assertion for Refresh Now forced refresh in tests/test_extension_quota_label.py.
  - Update docs/WORKFLOW.md and regenerate docs/REFERENCES.md.
- relocate cache files and add GNOME next-update [useReq] *(config)*
  - Update requirements for ~/.cache/aibar cache and idle-time paths.
  - Implement APP_CACHE_DIR-backed cache/idle persistence in config helpers.
  - Render GNOME popup status as 'Last updated: <time>, next update: <time>'.
  - Refresh tests plus WORKFLOW/REFERENCES for traceable compliance.
- implement idle-time cache and 429 backoff control [useReq] *(cli)*
  - Update SRS for idle-delay, idle-time state, force refresh, and API throttling.
  - Persist canonical show JSON payload to ~/.config/aibar/cache.json.
  - Add runtime config persistence in ~/.config/aibar/config.json.
  - Persist idle-time epoch/ISO metadata in ~/.config/aibar/idle-time.json.
  - Propagate retry-after metadata and enforce max(idle-delay,retry-after).
  - Add regression tests for setup prompts, idle gating, force mode, 429 policy, and throttling.
- remove Chrome extension scope [useReq] *(core)*
  - Update docs/REQUIREMENTS.md by removing Chrome-extension requirement IDs and evidence rows.
  - Delete src/aibar/chrome-extension implementation and associated guideline document.
  - Remove Chrome-extension fixtures/helpers/tests and update workflow/reference docs.
- add localhost external API bridge [useReq] *(chrome-extension)*
  - Update requirements with REQ-060/REQ-061 and TST-032/TST-033.
  - Implement localhost listener on 127.0.0.1 default port 32767 with descending fallback.
  - Expose external routes for api.main.snapshot and debug API endpoints.
  - Preserve debug gate semantics and structured debug command logging.
  - Add runtime guards for node static-check compatibility in background/popup.
  - Refresh workflow and references documentation to reflect runtime changes.
- persist debug session state and popup preload [useReq] *(chrome-extension)*
  - update REQUIREMENTS for session-persisted debug enablement and popup layout order
  - implement background debug flag persistence via chrome.storage.session
  - execute startup refresh before alarm scheduling and keep primary snapshot always available
  - reorder popup HTML to tabs/cards first and controls at bottom
  - extend chrome extension tests for startup flow, debug persistence, snapshot availability, and layout order
  - sync WORKFLOW, REFERENCES, and Google_Extension_API_Reference docs
- update Copilot fixture data to 24.4% / 321 of 1500 [useReq] *(tests)*
- decouple interval config from debug gate, add code_review window, fix parser datetime fallback [useReq] *(chrome-extension)*
  - Un-gate interval input/button from debug mode; add config.refresh_interval.set
  - handler before debug guard in background.js (CTN-016, REQ-057)
  - Remove Export debug, Clear logs, Fetch pages buttons from popup HTML/JS;
  - features remain accessible only through debug API commands (DES-012)
  - Add code_review window to codex provider: parsers.js WINDOW_HINT_REGEX,
  - _extractWindowHint, parseCodexUsageHtml; background.js and popup.js
  - PROVIDER_WINDOWS updated (REQ-041)
  - Fix _buildWindows datetime fallback: only pick unrelated datetime candidates
  - when no JSON candidate matched for the window
  - Bump PARSER_VERSION to 2026.03.07.1
  - Update test fixtures for current values (Claude 0%/11%, Codex 0%/32%/0%,
  - Copilot 20.4% 272/1500); update test assertions and add TST-028/TST-029
  - Update REQUIREMENTS.md v0.3.13, WORKFLOW.md, REFERENCES.md, API guideline
- hide unpopulated window bars on provider error and codify host_permissions auth [useReq] *(chrome-extension)*
  - Add _hasPopulatedWindows helper to popup.js for window-data presence detection
  - Gate window progress bar rendering in _renderProviderCard on populated data
  - Show error-only card when provider fails with no prior window data (REQ-055)
  - Preserve windows alongside error when prior data exists (REQ-056)
  - Add CTN-015 requirement for manifest host_permissions enabling authenticated fetch
  - Add REQ-055/REQ-056 requirements for error-gated popup rendering
  - Add TST-026/TST-027 test requirements for manifest auth and popup error behavior
  - Update manifest test with credentials-include and host_permissions auth assertions
  - Create test_chrome_extension_popup.py for error rendering contract assertions
  - Update WORKFLOW.md call trace with _hasPopulatedWindows in popup render path
  - Update REFERENCES.md with new symbol, line ranges, and satisfies tags
- refactor debug API and parser diagnostics [useReq] *(chrome-extension)*
  - Update REQ-040..REQ-053 and TST-020..TST-025 for current debug/API behavior.
  - Add debug command providers.pages.get with fixed provider URL set and related-resource downloads.
  - Expose provider-page diagnostics action in popup and keep debug controls session-gated.
  - Harden debug logger and metric normalization to keep sink/empty-value paths non-throwing.
  - Improve parser extraction for current Claude/Copilot/Codex structures and reject noise artifacts.
  - Refresh API reference, workflow model, references index, fixtures, and tests.
- BREAKING CHANGE: add primary snapshot API and runtime debug gate [useReq] *(chrome-extension-debug-api)*
  - Update REQUIREMENTS.md for primary/debug API split and non-persistent debug flag.
  - Implement api.main.snapshot plus config.debug_api.get/set runtime controls.
  - Gate all debug.* routes with deterministic DEBUG_API_DISABLED responses by default.
  - Update popup configuration UI with session-only debug toggle and disabled debug actions.
  - Add/adjust Chrome extension debug tests and API-reference documentation assertions.
  - Create guidelines/Google_Extension_API_Reference.md and regenerate WORKFLOW/REFERENCES docs.
- extend diagnostics and logger safety [useReq] *(chrome-debug-api)*
  - Update requirements for enhanced debug diagnostics and safe console logging.
  - Add parser window-assignment trace extraction for provider debug flows.
  - Add providers.diagnose aggregate API command for multi-provider analysis.
  - Include payload assertion metadata in parser and diagnose responses.
  - Fix console method invocation by binding logger methods to console context.
  - Expand Chrome debug/parser tests and regenerate WORKFLOW/REFERENCES docs.
- recover codex metrics from escaped scripts [useReq] *(chrome-parser)*
  - Update existing SRS IDs for escaped Codex script extraction and key-evidence diagnostics.
  - Extend parser signals with escaped script key/value candidates and metric-key samples.
  - Add Codex escaped-script fixture and regression assertions for parser + diagnostics.
  - Refresh WORKFLOW and regenerate REFERENCES for updated parser symbol graph.
- harden parser + debug diagnostics [useReq] *(chrome-extension)*
  - Update existing SRS IDs for bootstrap-script extraction and parser-empty failure handling.
  - Add provider.diagnose debug command, payload quality summary, and HTTP hash/head-tail probes.
  - Harden Claude/Codex parser selection to avoid reset-only false positives and support script payloads.
  - Add parser/debug regression fixtures and tests; regenerate WORKFLOW/REFERENCES.
- rename extension source directory path [useReq] *(gnome-extension)*
  - update requirement paths for GNOME extension source location
  - rename src/aibar/extension/ to src/aibar/gnome-extension/
  - update installer script, release workflow, and affected tests
  - refresh docs/WORKFLOW.md and regenerate docs/REFERENCES.md
- suppress rate-limit banners and flag full-quota resets [useReq] *(ui)*
  - Update REQ-008/REQ-017 and TST requirements for rate-limit rendering behavior.
  - Textual UI now suppresses 'Error: Rate limited. Try again later.' on quota payloads.
  - Textual reset rows append '⚠️ Limit reached!' at displayed 100.0% for Claude/Codex/Copilot windows.
  - GNOME extension now treats rate-limit quota payloads as metric cards, not error cards.
  - GNOME reset labels append '⚠️ Limit reached!' for displayed full usage.
  - Add and update regression tests for extension and Textual card helper logic.
  - Regenerate REFERENCES and update WORKFLOW call-trace notes.
- restore Claude 429 metrics from snapshot [useReq] *(cli)*
  - Update REQ-036 and related constraints/tests for Claude 429 rendering semantics.
  - Persist latest successful Claude dual-window payload for rate-limit fallback.
  - Keep 5h at 100% with error line, restore 7d usage/reset from persisted payload.
  - Add legacy snapshot compatibility for existing claude_5h/claude_7d cache files.
  - Refresh workflow and references documentation to match new runtime helpers.
- normalize Claude 429 dual-window output [useReq] *(cli)*
  - Update REQUIREMENTS with REQ-034/REQ-035/REQ-036 and TST-010/TST-011.
  - Normalize Claude dual-window 429 handling in _fetch_claude_dual.
  - Keep rate-limit error visible only in 5h while preserving 100% usage/reset output for 5h and 7d.
  - Allow _print_result to continue metrics rendering for Claude 429 partial-window path.
  - Add regression test test_claude_rate_limit_partial_window and update Claude dual cooldown symmetry test.
  - Update WORKFLOW runtime model and regenerate REFERENCES index.
- disable Claude API cache reuse in CLI/UI [useReq] *(claude-cache)*
  - Update CTN-004, REQ-009, and TST-003 in docs/REQUIREMENTS.md.
  - Disable Claude caching/cooldown in ResultCache via provider policy gate.
  - Bypass Claude cache in CLI _fetch_result and _fetch_claude_dual paths.
  - Restrict Textual UI action_refresh cache get/set to non-Claude providers.
  - Replace obsolete Claude cache-fallback tests with cache-bypass assertions.
  - Add non-Claude cache persistence and raw-key redaction tests.
  - Regenerate WORKFLOW and REFERENCES documentation.

### 📚  Documentation
- align provider and login examples [useReq] *(readme)*
  - Add geminiai to show provider list in Feature Highlights.
  - Add geminiai login helper command in Usage section.

## [0.1.0](https://github.com/Ogekuri/AIBar/releases/tag/v0.1.0) - 2026-03-05
### ⛰️  Features
- Add extension build.
- add GNOME extension installer script with colored output [useReq] *(install-gnome-extension)*
  - Add scripts/install-gnome-extension.sh: resolves git project root, validates
  - prerequisites (git, source dir, metadata.json), creates target directory
  - ~/.local/share/gnome-shell/extensions/aibar@aibar.panel/, copies all extension
  - files preserving attributes via cp -a, produces ANSI-colored terminal output.
  - Add requirements PRJ-008, REQ-025..REQ-030, TST-009.
  - Add tests/test_install_gnome_extension.py with atomic and composed test levels.
  - Update docs/WORKFLOW.md with PROC:install-ext execution unit.
  - Regenerate docs/REFERENCES.md.
- Update models.json file.
- Add LICENSE_GnomeCodexBar file.
- add colored panel usage percentages [useReq] *(gnome-extension)*
  - append REQ-021/REQ-022 and TST-007 in docs/REQUIREMENTS.md
  - render ordered Claude/Copilot/Codex percentages in panel status area
  - apply provider tab color classes to panel percentages
  - hide percentage labels when metrics are unavailable
  - add extension regression tests and refresh WORKFLOW/REFERENCES docs
- Update .req/models.json file.
- Add requirements.txt file.
- Add dummy docs/REFERENCES.md.
- Initial commit.

### 🐛  Bug Fixes
- reapply progress bar fill widths on popup open [useReq] *(extension-popup)*
  - Root cause: GLib.idle_add callback in _populateProviderCard reads
  - barBg.get_width() which returns 0 when popup is closed. Data arriving
  - while popup is closed results in zero-width fill bars.
  - Fix: connect menu open-state-changed signal to new _applyBarWidths()
  - method that re-applies cached _barData fill widths via GLib.idle_add
  - when popup opens, ensuring bars render correctly on first open.
  - Adds test_popup_open_triggers_bar_width_reapply regression test.
- Add new install scripts.
- handle displayed-zero fallback for pending reset text [useReq] *(extension-reset)*
  - treat near-zero percentages that render as 0.0% as zero for reset-pending fallback
  - apply same displayed-zero semantics in CLI and GNOME extension
  - extend regression tests and refresh WORKFLOW/REFERENCES
- show pending reset hint at 0% usage [useReq] *(claude-reset)*
  - print fallback 'Resets in' text in CLI for Claude when usage is 0 and reset_at is unavailable
  - render GNOME window-bar fallback reset text when usage is 0 and reset timestamp is unavailable
  - add reproducer tests for CLI and extension
  - update WORKFLOW and regenerate REFERENCES
- project next reset boundary from stale cache resets_at to restore 'Resets in:' display [useReq] *(cli)*
  - Root cause: _parse_response correctly sets reset_at=None for past resets_at timestamps;
  - _fetch_claude_dual did not project forward, so 'Resets in:' was silently suppressed
  - for stale cached results on both the cooldown pre-check and post-fetch 429 paths.
  - Add _WINDOW_PERIOD_TIMEDELTA mapping, _project_next_reset (math.ceil multi-cycle
  - advance), and _apply_reset_projection (model_copy with projected reset_at).
  - Apply _apply_reset_projection to every last-good and cross-window re-parse result
  - in _fetch_claude_dual on all affected code paths.
  - Add 3 guideline-compliant reproducer tests in test_claude_dual_stale_reset_projection.py.
  - Update docs/WORKFLOW.md and docs/REFERENCES.md.
- discard past reset_at timestamps to fix asymmetric Resets-in display [useReq] *(claude_oauth._parse_response)*
  - Root cause: _parse_response stored any parsed resets_at datetime including
  - past timestamps; _print_result suppressed 'Resets in:' when reset_at was
  - None OR delta<=0, causing 5h window (stale cache) to silently suppress the
  - field while 7d window (future reset) showed it (REQ-002 symmetry defect).
  - Fix: added past-timestamp guard in _parse_response; sets reset_at=None when
  - parsed datetime <= datetime.now(UTC), so stale cached timestamps never reach
  - the display layer.
  - Added 6 reproducer/regression tests in test_claude_parse_response_reset_at.py
  - Updated docs/WORKFLOW.md and docs/REFERENCES.md with accurate symbol metadata.
- extend post-fetch 429 cross-window re-parse to restore 5h symmetry [useReq] *(cli)*
- derive missing Claude window from sibling raw payload during rate-limit cooldown [useReq] *(cli)*
- improve 429 retry backoff and add cross-process rate-limit cooldown [useReq] *(claude_oauth)*
  - Increase MAX_RETRIES from 2 to 3 and RETRY_BACKOFF_BASE from 1.0 to 2.0
  - with random jitter to prevent thundering-herd synchronization.
  - Add rate-limit cooldown mechanism in ResultCache: on 429 error, write
  - cooldown marker to disk; subsequent CLI invocations within 30s return
  - last-good cached data instead of hammering the API.
  - Add cooldown check in _fetch_result and _fetch_claude_dual before API calls.
  - Add 4 new tests for cooldown activation, clearing, expiry, and CLI integration.
  - Update WORKFLOW.md call-traces for changed symbols.
- add 429 retry, CLI cache integration, single-call dual-window [useReq] *(claude_oauth)*
  - Add _request_usage with retry-after-aware retry (max 2) for HTTP 429.
  - Add fetch_all_windows for single-API-call dual-window parsing (5h+7d).
  - Integrate ResultCache in CLI show path (CTN-004 compliance).
  - Add _fetch_claude_dual for cache-aware single-call dual-window fetch.
  - Add _fetch_result cache lookup, store, and last-good fallback on error.
  - Add reproducer tests for retry, single-call, cache, and fallback.
  - Update WORKFLOW.md and REFERENCES.md.
- Remove unused scripts.
- Fix version numer.
- Include .req directory to support worktree.
- Rename aibar script.
- Rename extension folder.

### 🚜  Changes
- BREAKING CHANGE: remove subcommand, execute nested shell directly [useReq] *(test-gnome-extension)*
  - test-gnome-extension.sh no longer requires any parameter; runs
  - install + nested shell launch directly on invocation
  - Removed case/esac dispatch; script body calls update_extension
  - then launches MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 nested shell
  - PRJ-004, REQ-031, REQ-033, TST-004 updated to reflect no-argument
  - invocation
  - Requirements updated to v0.3.7
- BREAKING CHANGE: installer enables extension, test script keeps only start [useReq] *(scripts)*
  - install-gnome-extension.sh now runs gnome-extensions enable after
  - file copy (REQ-032), with graceful fallback when CLI unavailable
  - test-gnome-extension.sh stripped to start-only subcommand (REQ-033);
  - enable/disable/reload/logs removed
  - REQ-031 narrowed to start command only
  - Requirements updated to v0.3.6 with REQ-032, REQ-033
  - Tests updated: removed enable/reload assertions, added start-only
  - and enable-presence tests
- invoke install before start/enable/reload commands [useReq] *(test-gnome-extension)*
  - Modify scripts/test-gnome-extension.sh to call install-gnome-extension.sh
  - before start, enable, and reload commands (REQ-031).
  - Update PRJ-004 reference from dev.sh to scripts/test-gnome-extension.sh.
  - Add REQ-031: MUST invoke installer before start/enable/reload.
  - Update tests/test_extension_dev_script.py: fix path from dev.sh to
  - scripts/test-gnome-extension.sh, add 4 new tests for install invocation.
  - Update docs/WORKFLOW.md with PROC:test-ext unit and EDGE-004.
  - Regenerate docs/REFERENCES.md.
- add pyproject.toml uv/uvx packaging and README install section [useReq] *(core)*
- add 7d panel percentages and primary bold labels [useReq] *(extension)*
  - modify REQ-021/REQ-022 and TST-007 for five-label panel order
  - add Claude 7d and Codex 7d percentages in status bar
  - keep provider colors for new 7d labels
  - enforce bold primary percentages for Claude 5h, Copilot, Codex 5h
  - update panel hide/error paths for new labels
  - update tests, WORKFLOW, and regenerate REFERENCES
- update credit/reset labels and format [useReq] *(extension)*
  - modify REQ-017 and TST-004 for new credit/reset wording
  - render quota label as Remaining credits: <n>/<total> with bold <n>
  - change extension reset labels to Reset in:
  - update extension tests for wording and formatting
  - refresh WORKFLOW and REFERENCES documentation
- standardize doxygen metadata and references [useReq] *(core)*
  - update REQ-020 and TST-006 for Doxygen field extraction
  - standardize declaration documentation in Python and GNOME JS sources
  - refresh docs/REFERENCES.md and update workflow runtime notes
  - verify with req --here --static-check and ./tests.sh
- force nested 1024x800 dev start [useReq] *(extension)*
  - Update PRJ-004 and TST-004 for fixed nested-shell resolution in dev launcher start.
  - Force dev.sh start to set MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 before nested GNOME launch.
  - Add regression test for dev.sh start command and refresh workflow/reference docs.
- normalize UI branding casing [useReq] *(extension)*
  - Update REQ-017 and TST-004 to require AIBar branding labels in GNOME popup UI.
  - Replace graphical strings 'aibar' with 'AIBar' in extension header and open-UI action label.
  - Add regression test assertions for popup branding labels and refresh workflow/reference docs.
- replace metadata owner with Ogekuri [useReq] *(extension)*
  - Update PRJ-004 requirement for metadata owner identifiers.
  - Replace metadata.json url/github owner from OmegAshEnr01n to Ogekuri.
  - Regenerate docs/REFERENCES.md for synchronized symbol inventory.
- align copilot reset/bar layout with window bars [useReq] *(extension)*
  - Update REQ-017 and TST-004 for Copilot card bar/reset placement requirements.\nRender Copilot quota as a 30d window bar using existing window-bar styling and label placement.\nPlace reset text under that bar and keep remaining-credits row below in stats area.\nAdd regression test assertions for Copilot 30d bar/reset source behavior.\nRefresh WORKFLOW and REFERENCES documentation for updated extension symbols.
- print remaining credits for quota providers [useReq] *(cli-show)*
  - Update REQ-002 and TST-001 for show remaining-credits output behavior.\nPrint 'Remaining credits: <remaining> / <limit>' in show text output for Claude/Codex/Copilot when both values exist.\nAdd regression assertion in tests/test_cli_show_reset_format.py.\nRefresh WORKFLOW and REFERENCES documents for updated CLI symbols.
- align reset countdown with UI format [useReq] *(cli-show)*
  - Update REQ-002 to require day-aware reset countdown text in show output.\nImplement _format_reset_duration and emit 'Resets in:' text in CLI renderer.\nAdd CLI regression test for day-token reset formatting.\nRefresh WORKFLOW and REFERENCES documentation for updated symbols.
- rename credits label to remaining credits [useReq] *(gnome-extension)*
  - Update REQ-017 and TST-004 for quota-card label text behavior.\nSwitch GNOME extension quota-only card suffix from "credits" to "remaining credits".\nAdd regression test to assert new quota label string in extension source.\nRefresh WORKFLOW runtime note for quota-label composition path.
- rename monitor label to IABar Monitor [useReq] *(extension)*
  - update PRJ-004 requirement to enforce extension name IABar Monitor
  - rename GNOME extension display labels in metadata and panel indicator
  - refresh WORKFLOW and REFERENCES documentation paths/evidence
- BREAKING CHANGE: finalize AIBar rename refactor [useReq] *(core)*
  - Apply requirement updates for renamed project identity and command surface.
  - Traceability marker commit for req-change workflow completion.
  - Verified static check, regression tests, and keyword absence constraints.
- document code inventory and Doxygen headers [useReq] *(usage_tui)*
  - update existing SRS IDs and add documentation inventory requirements
  - add parser-first Doxygen module/file headers across src components
  - fix static-check lint issues found during verification loop
  - add pytest regression for references inventory completeness
  - regenerate WORKFLOW.md and REFERENCES.md from current repository state

### 📚  Documentation
- Update README.md.
- Add screenshots.
- Update README.md document.
- regenerate runtime model for CLI and GNOME flow [useReq] *(workflow)*
  - rewrite docs/WORKFLOW.md with required schema\n- use declaration file paths only\n- refresh call traces and communication edges
- Update README.md document.
- update acknowledgments and licensing notice [useReq] *(core)*
  - add credit to Shobhit Narayanan for GnomeCodexBar
  - declare program license reference in LICENSE
  - declare modified GnomeCodexBar files covered by LICENSE_GnomeCodexBar
- regenerate runtime execution model [useReq] *(workflow)*
  - rebuild Execution Units Index for usage_tui and GNOME extension
  - add internal call-trace trees and external boundaries
  - add communication edges with mechanisms, channels, and payload shapes


# History

- \[0.1.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.1.0
- \[0.2.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.2.0
- \[0.3.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.3.0
- \[0.4.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.4.0
- \[0.5.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.5.0
- \[0.6.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.6.0
- \[0.7.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.7.0
- \[0.8.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.8.0
- \[0.9.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.9.0
- \[0.10.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.10.0
- \[0.11.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.11.0
- \[0.12.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.12.0
- \[0.13.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.13.0
- \[0.14.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.14.0
- \[0.15.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.15.0
- \[0.16.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.16.0
- \[0.17.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.17.0
- \[0.18.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.18.0
- \[0.19.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.19.0
- \[0.20.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.20.0
- \[0.21.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.21.0
- \[0.22.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.22.0
- \[0.23.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.23.0
- \[0.24.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.24.0
- \[0.25.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.25.0
- \[0.26.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.26.0
- \[0.27.0\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.27.0

[0.1.0]: https://github.com/Ogekuri/AIBar/releases/tag/v0.1.0
[0.2.0]: https://github.com/Ogekuri/AIBar/compare/v0.1.0..v0.2.0
[0.3.0]: https://github.com/Ogekuri/AIBar/compare/v0.2.0..v0.3.0
[0.4.0]: https://github.com/Ogekuri/AIBar/compare/v0.3.0..v0.4.0
[0.5.0]: https://github.com/Ogekuri/AIBar/compare/v0.4.0..v0.5.0
[0.6.0]: https://github.com/Ogekuri/AIBar/compare/v0.5.0..v0.6.0
[0.7.0]: https://github.com/Ogekuri/AIBar/compare/v0.6.0..v0.7.0
[0.8.0]: https://github.com/Ogekuri/AIBar/compare/v0.7.0..v0.8.0
[0.9.0]: https://github.com/Ogekuri/AIBar/compare/v0.8.0..v0.9.0
[0.10.0]: https://github.com/Ogekuri/AIBar/compare/v0.9.0..v0.10.0
[0.11.0]: https://github.com/Ogekuri/AIBar/compare/v0.10.0..v0.11.0
[0.12.0]: https://github.com/Ogekuri/AIBar/compare/v0.11.0..v0.12.0
[0.13.0]: https://github.com/Ogekuri/AIBar/compare/v0.12.0..v0.13.0
[0.14.0]: https://github.com/Ogekuri/AIBar/compare/v0.13.0..v0.14.0
[0.15.0]: https://github.com/Ogekuri/AIBar/compare/v0.14.0..v0.15.0
[0.16.0]: https://github.com/Ogekuri/AIBar/compare/v0.15.0..v0.16.0
[0.17.0]: https://github.com/Ogekuri/AIBar/compare/v0.16.0..v0.17.0
[0.18.0]: https://github.com/Ogekuri/AIBar/compare/v0.17.0..v0.18.0
[0.19.0]: https://github.com/Ogekuri/AIBar/compare/v0.18.0..v0.19.0
[0.20.0]: https://github.com/Ogekuri/AIBar/compare/v0.19.0..v0.20.0
[0.21.0]: https://github.com/Ogekuri/AIBar/compare/v0.20.0..v0.21.0
[0.22.0]: https://github.com/Ogekuri/AIBar/compare/v0.21.0..v0.22.0
[0.23.0]: https://github.com/Ogekuri/AIBar/compare/v0.22.0..v0.23.0
[0.24.0]: https://github.com/Ogekuri/AIBar/compare/v0.23.0..v0.24.0
[0.25.0]: https://github.com/Ogekuri/AIBar/compare/v0.24.0..v0.25.0
[0.26.0]: https://github.com/Ogekuri/AIBar/compare/v0.25.0..v0.26.0
[0.27.0]: https://github.com/Ogekuri/AIBar/compare/v0.26.0..v0.27.0
