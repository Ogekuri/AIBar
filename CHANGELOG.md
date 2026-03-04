# Changelog

## [0.0.1](https://github.com/Ogekuri/AIBar/releases/tag/v0.0.1) - 2026-03-04
### ⛰️  Features
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
- Fix version numer.
- Include .req directory to support worktree.
- Rename aibar script.
- Rename extension folder.

### 🚜  Changes
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

- \[0.0.1\]: https://github.com/Ogekuri/AIBar/releases/tag/v0.0.1

[0.0.1]: https://github.com/Ogekuri/AIBar/releases/tag/v0.0.1
