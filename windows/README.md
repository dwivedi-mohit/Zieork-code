# ⚡ Zieork Desktop for Windows (Claude & Codex Class)

This folder contains everything needed to launch or build **Zieork as a native Windows Desktop Application**.

---

## 🚀 Quick Start (Running on Windows)

### Option 1: One-Click Launch (Recommended)
Simply double-click:
```
windows\start_silent.vbs
```
*(Or `windows\start_zieork.bat`)*

**What it does:**
1. Checks if the local Zieork neural backend is running; if not, starts it silently in the background.
2. Automatically launches the native desktop window (or your default browser).

---

### Option 2: Install Desktop & Start Menu Shortcuts
Right-click `windows\install_shortcut.ps1` and choose **"Run with PowerShell"** (or run `powershell -ExecutionPolicy Bypass -File windows\install_shortcut.ps1`).

This installs:
- A branded **Zieork** shortcut on your **Windows Desktop**.
- A **Zieork** shortcut in your **Windows Start Menu**.

---

## 📦 Building a Standalone Windows Installer (`.exe`)

To package Zieork into a standalone installer (`.exe` NSIS installer or portable executable) using Electron:

1. Ensure **Node.js** (v18+) is installed on Windows from [nodejs.org](https://nodejs.org/).
2. Double-click:
   ```
   windows\build_windows_exe.bat
   ```
3. Once completed, your installer will be in:
   ```
   dist\Zieork Setup 2.5.0.exe
   ```

---

## ⌨️ Desktop Keyboard Shortcuts
- **`Ctrl+Shift+Z`**: Toggle Zieork visibility (Summon / Minimize from anywhere on your desktop).
- **System Tray**: Right-click the Zieork icon in your system tray (bottom-right taskbar) for quick actions.
