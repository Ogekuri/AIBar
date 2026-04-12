"""
@file test_extension_esmodule_imports.py
@brief GNOME Shell ES module import compliance tests.
@details Verifies that extension.js uses GNOME Shell 45+ ES6 import syntax and does NOT use
the legacy globalThis.imports API that causes SyntaxError in GNOME Shell 45+.

The root cause of the SyntaxError is: extension.js used globalThis.imports.ui.main to access
the GNOME Shell main module. In GNOME Shell 45+, this triggers the legacy module loader to load
main.js in a non-module (script) context. Since main.js uses ES6 import at line 3, the runtime
raises: SyntaxError: import declarations may only appear at top level of a module.

Fix: replace globalThis.imports.* bindings with ES6 gi:// and resource:// imports.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXTENSION_PATH = (
    PROJECT_ROOT
    / "src"
    / "aibar"
    / "aibar"
    / "gnome-extension"
    / "aibar@aibar.panel"
    / "extension.js"
)


def test_extension_does_not_use_legacy_globalthis_imports() -> None:
    """
    @brief Verify extension.js does not use globalThis.imports (GNOME Shell ≤44 legacy API).
    @details globalThis.imports was removed in GNOME Shell 45. Its use in an ES module context
    triggers a SyntaxError when loading GNOME Shell's own main.js via the legacy module loader.
    The extension targets shell-version 45-48 (metadata.json), so this legacy API must be absent.
    @satisfies PRJ-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "globalThis.imports" not in source


def test_extension_uses_gi_esmodule_imports() -> None:
    """
    @brief Verify extension.js imports GNOME introspection libraries via ES module gi:// scheme.
    @details The gi:// import scheme is the GNOME Shell 45+ way to access GObject introspection
    libraries. Without these imports, the extension cannot bind to the GNOME APIs it relies on.
    @satisfies PRJ-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "import GLib from 'gi://GLib';" in source
    assert "import St from 'gi://St';" in source
    assert "import Gio from 'gi://Gio';" in source
    assert "import Clutter from 'gi://Clutter';" in source
    assert "import GObject from 'gi://GObject';" in source


def test_extension_uses_resource_esmodule_imports() -> None:
    """
    @brief Verify extension.js imports GNOME Shell UI modules via ES module resource:// scheme.
    @details The resource:// import scheme is required in GNOME Shell 45+ for shell UI modules.
    Using globalThis.imports.ui.* instead causes the legacy loader to load those files as scripts,
    which fails for any GNOME Shell 45+ module that itself contains ES6 import statements.
    @satisfies PRJ-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert "import * as Main from 'resource:///org/gnome/shell/ui/main.js';" in source
    assert "import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';" in source
    assert "import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';" in source


def test_extension_imports_extension_base_class_and_extends_it() -> None:
    """
    @brief Verify AIBarExtension imports and extends the GNOME Shell Extension base class.
    @details GNOME Shell 45+ requires extensions to extend the Extension class from the extensions
    API. This provides lifecycle integration (uuid, metadata, dir) required by addToStatusArea.
    @satisfies PRJ-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    assert (
        "import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';"
        in source
    )
    assert "export default class AIBarExtension extends Extension" in source


def test_extension_file_ends_after_extension_class_closure() -> None:
    """
    @brief Verify extension.js has no trailing tokens after AIBarExtension closing brace.
    @details Prevents parse-time module SyntaxError caused by stray trailing braces or
    garbage tokens after the exported extension class block.
    @satisfies PRJ-004
    """
    source = EXTENSION_PATH.read_text(encoding="utf-8")
    expected_tail = (
        "    disable() {\n"
        "        console.debug('aibar: Disabling extension');\n\n"
        "        if (this._indicator) {\n"
        "            this._indicator.destroy();\n"
        "            this._indicator = null;\n"
        "        }\n"
        "    }\n"
        "}\n"
    )
    assert source.rstrip().endswith(expected_tail.rstrip())
