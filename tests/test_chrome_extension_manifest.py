"""
@file
@brief Chrome extension manifest and popup wiring assertions.
@details Validates extension package structure, icon reuse, popup tab set, and
service-worker configuration for AIBar Chrome runtime.
@satisfies TST-013
@satisfies REQ-038
"""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXT_ROOT = PROJECT_ROOT / "src" / "aibar" / "chrome-extension"
MANIFEST_PATH = EXT_ROOT / "manifest.json"
POPUP_HTML_PATH = EXT_ROOT / "popup.html"


def test_manifest_declares_popup_and_service_worker_module() -> None:
    """
    @brief Verify manifest declares popup action and module service-worker.
    @satisfies TST-013
    """
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert manifest["action"]["default_popup"] == "popup.html"
    assert manifest["action"]["default_title"] == "AIBar"
    assert manifest["background"]["service_worker"] == "background.mjs"
    assert manifest["background"]["type"] == "module"


def test_manifest_declares_required_host_permissions() -> None:
    """
    @brief Verify host permissions include Claude, ChatGPT Codex, and GitHub sources.
    @satisfies REQ-040
    @satisfies REQ-041
    @satisfies REQ-042
    """
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    host_permissions = set(manifest["host_permissions"])
    assert "https://claude.ai/*" in host_permissions
    assert "https://chatgpt.com/*" in host_permissions
    assert "https://github.com/*" in host_permissions


def test_manifest_icons_exist_and_match_gnome_monitor_icon_set() -> None:
    """
    @brief Verify icon entries are present and icon files exist.
    @satisfies DES-007
    """
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    icon_paths = set(manifest["icons"].values()) | set(manifest["action"]["default_icon"].values())
    for rel_path in icon_paths:
        assert (EXT_ROOT / rel_path).is_file(), rel_path


def test_popup_contains_only_claude_copilot_codex_tabs() -> None:
    """
    @brief Verify popup tab bar exposes only required providers.
    @satisfies REQ-038
    """
    source = POPUP_HTML_PATH.read_text(encoding="utf-8")
    assert 'data-provider="claude"' in source
    assert 'data-provider="copilot"' in source
    assert 'data-provider="codex"' in source
    assert 'data-provider="openai"' not in source
    assert 'data-provider="openrouter"' not in source
