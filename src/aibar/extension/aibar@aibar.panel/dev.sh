#!/bin/bash
# @file dev.sh
# @brief Development helper commands for aibar GNOME extension.
# @details Wraps nested-shell start, enable/disable/reload, and log tail commands for local extension workflows with fixed 1024x800 nested-shell resolution.

EXT_UUID="aibar@aibar.panel"

case "$1" in
    start)
        echo "Starting nested GNOME Shell at 1024x800..."
        env MUTTER_DEBUG_DUMMY_MODE_SPECS=1024x800 dbus-run-session -- gnome-shell --nested --wayland
        ;;
    enable)
        gnome-extensions enable "$EXT_UUID"
        echo "Extension enabled"
        ;;
    disable)
        gnome-extensions disable "$EXT_UUID"
        echo "Extension disabled"
        ;;
    reload)
        gnome-extensions disable "$EXT_UUID"
        sleep 1
        gnome-extensions enable "$EXT_UUID"
        echo "Extension reloaded"
        ;;
    logs)
        journalctl -f -o cat /usr/bin/gnome-shell | grep -i "aibar"
        ;;
    *)
        echo "Usage: $0 {start|enable|disable|reload|logs}"
        exit 1
        ;;
esac
