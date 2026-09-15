#!/usr/bin/env bash
# ==============================================================================
# Zieork Sovereign Desktop Launcher (Linux / Cross-Platform)
# ==============================================================================

# Resolve symlinks to find the real physical project directory
TARGET="${BASH_SOURCE[0]}"
while [ -h "$TARGET" ]; do
    DIR="$(cd -P "$(dirname "$TARGET")" >/dev/null 2>&1 && pwd)"
    TARGET="$(readlink "$TARGET")"
    [[ $TARGET != /* ]] && TARGET="$DIR/$TARGET"
done
SCRIPT_DIR="$(cd -P "$(dirname "$TARGET")" >/dev/null 2>&1 && pwd)"
cd "$SCRIPT_DIR"

export no_proxy="127.0.0.1,localhost"
export NO_PROXY="127.0.0.1,localhost"

# Check arguments
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Zieork Desktop Launcher"
    echo "Usage: ./run_desktop.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --qt         Launch native PyQt6 desktop app (Default, instant launch)"
    echo "  --manager    Launch directly into Antigravity Agent Manager Screen"
    echo "  --electron   Launch Electron desktop shell (requires npm install in desktop/electron)"
    echo "  --check      Run environment and backend verification self-test"
    echo "  --help       Show this help message"
    exit 0
fi

if [ "$1" = "--check" ]; then
    echo "[Zieork] Running environment self-test..."
    python3 "$SCRIPT_DIR/desktop/app_qt.py" --check-only
    exit $?
fi

# If electron requested
if [ "$1" = "--electron" ]; then
    if [ ! -d "$SCRIPT_DIR/desktop/electron/node_modules" ]; then
        echo "[Zieork] Installing Electron dependencies in desktop/electron..."
        (cd "$SCRIPT_DIR/desktop/electron" && npm install)
    fi
    echo "[Zieork] Launching Electron desktop app..."
    cd "$SCRIPT_DIR/desktop/electron" && npx electron .
    exit $?
fi

# Default: Launch PyQt6 native desktop app
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo "======================================================================"
    echo "⚡ ZIEORK DESKTOP SYSTEM"
    echo "======================================================================"
    echo "Note: No X11/Wayland display server detected in this terminal."
    echo "The Zieork neural engine is active at: http://localhost:5000"
    echo ""
    echo "To launch the native desktop GUI window, run this command inside your"
    echo "desktop session (Ubuntu desktop, GNOME, KDE, or XFCE):"
    echo "    cd $SCRIPT_DIR && ./run_desktop.sh"
    echo "======================================================================"
    exit 0
fi

echo "[Zieork] Launching native desktop window..."
exec python3 "$SCRIPT_DIR/desktop/app_qt.py" "$@"
