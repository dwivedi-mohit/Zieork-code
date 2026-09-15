#!/usr/bin/env bash
# ==============================================================================
# Install Zieork into Linux Desktop Application Menu & Dock
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

APPS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"

mkdir -p "$APPS_DIR"
mkdir -p "$ICONS_DIR"

# Copy Icon
cp "$SCRIPT_DIR/desktop/assets/icon.png" "$ICONS_DIR/zieork.png"

# Generate desktop file with absolute paths
cat <<EOF > "$APPS_DIR/zieork.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=Zieork
GenericName=Autonomous Neural Intelligence System
Comment=Sovereign Edge-Native AI Desktop App (Claude & Codex Class)
Exec=$SCRIPT_DIR/run_desktop.sh
Icon=$ICONS_DIR/zieork.png
Terminal=false
Categories=Development;Utility;ArtificialIntelligence;Office;
StartupWMClass=Zieork
Keywords=AI;Neural;Claude;Codex;Coding;Agent;Intelligence;
Actions=NewSession;

[Desktop Action NewSession]
Name=New Session
Exec=$SCRIPT_DIR/run_desktop.sh
EOF

chmod +x "$APPS_DIR/zieork.desktop"
chmod +x "$SCRIPT_DIR/run_desktop.sh"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR"
fi

echo "======================================================================"
echo "✅ Zieork has been installed into your Linux Desktop Applications Menu!"
echo "You can now search for 'Zieork' in your GNOME/KDE/Ubuntu application menu"
echo "or dock and launch it like any native desktop app."
echo "======================================================================"
