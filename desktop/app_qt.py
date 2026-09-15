"""Zieork Native Desktop Application (PyQt6 + QtWebEngine).

Provides an instant, cross-platform native desktop app for Linux & Windows
matching Claude Desktop and Codex Desktop.
"""
import sys
import os
import time
import subprocess
import signal
import urllib.request
import urllib.error

# Ensure local proxy does not intercept localhost
os.environ["no_proxy"] = "127.0.0.1,localhost"
os.environ["NO_PROXY"] = "127.0.0.1,localhost"

# Ensure root directory is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

BACKEND_URL = "http://127.0.0.1:5000/manager" if "--manager" in sys.argv else "http://127.0.0.1:5000"
BACKEND_HEALTH = "http://127.0.0.1:5000/api/info"

def is_backend_alive(timeout=1.5):
    """Check if the Zieork Flask backend is responding."""
    try:
        req = urllib.request.Request(BACKEND_HEALTH, headers={"User-Agent": "ZieorkDesktop/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200
    except Exception:
        return False

def check_headless():
    """Detect if running in a purely headless environment without X11/Wayland."""
    if sys.platform.startswith("linux"):
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            return True
    return False

def main():
    # Support --check-only or --test for CI / headless environments
    if "--check-only" in sys.argv or "--test" in sys.argv:
        print("[Zieork Desktop] Running verification self-test...")
        from PyQt6.QtCore import QCoreApplication
        app = QCoreApplication(sys.argv)
        alive = is_backend_alive()
        print(f"[Zieork Desktop] Qt6 Core loaded successfully. Backend alive: {alive}")
        sys.exit(0)

    # Handle Headless Linux fallback
    if check_headless():
        print("[Zieork Desktop] Warning: No DISPLAY or WAYLAND_DISPLAY found.")
        print("[Zieork Desktop] Zieork server is running at http://localhost:5000")
        print("[Zieork Desktop] To run the desktop GUI, please launch inside a desktop session (GNOME, KDE, etc.)")
        sys.exit(0)

    # Import GUI modules
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QSystemTrayIcon, QMenu,
        QFileDialog, QMessageBox, QSplashScreen, QLabel, QVBoxLayout, QWidget
    )
    from PyQt6.QtCore import Qt, QUrl, QTimer
    from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest

    # Initialize QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Zieork Neural Intelligence")
    app.setApplicationDisplayName("Zieork")
    app.setDesktopFileName("zieork.desktop")

    # Set Application Icon
    icon_path = os.path.join(ROOT_DIR, "desktop", "assets", "icon.png")
    app_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
    app.setWindowIcon(app_icon)

    # Backend process handle
    backend_proc = None

    # Check if backend needs to be started
    if not is_backend_alive():
        print("[Zieork Desktop] Starting local Zieork backend daemon...")
        backend_cmd = [sys.executable, os.path.join(ROOT_DIR, "app.py")]
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=ROOT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Wait up to 15 seconds for backend to become ready
        attempts = 0
        while attempts < 30:
            time.sleep(0.5)
            if is_backend_alive():
                print("[Zieork Desktop] Backend successfully online.")
                break
            attempts += 1

    # Main Window
    class ZieorkMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Zieork — Autonomous Neural Intelligence System")
            self.setWindowIcon(app_icon)
            self.resize(1380, 880)
            self.setMinimumSize(1024, 720)
            
            # Center on screen
            screen = QApplication.primaryScreen()
            if screen:
                screen_geom = screen.availableGeometry()
                x = (screen_geom.width() - 1380) // 2
                y = (screen_geom.height() - 880) // 2
                self.move(max(0, x), max(0, y))

            # Dark Background Style
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #0b0f19;
                }
            """)

            # WebEngine Browser View
            self.webview = QWebEngineView(self)
            self.setCentralWidget(self.webview)

            # Configure Profile
            profile = self.webview.page().profile()
            profile.setHttpUserAgent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 ZieorkDesktop/2.0")
            profile.downloadRequested.connect(self.on_download_requested)

            # Load Zieork
            self.webview.setUrl(QUrl(BACKEND_URL))

            # Setup System Tray
            self.setup_tray()

        def on_download_requested(self, download: QWebEngineDownloadRequest):
            """Handle native OS file download dialog."""
            suggested_filename = download.suggestedFileName()
            default_path = os.path.join(os.path.expanduser("~/Downloads"), suggested_filename)
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                default_path
            )
            if file_path:
                download.setDownloadDirectory(os.path.dirname(file_path))
                download.setDownloadFileName(os.path.basename(file_path))
                download.accept()
            else:
                download.cancel()

        def setup_tray(self):
            """Initialize system tray icon and menu."""
            if not QSystemTrayIcon.isSystemTrayAvailable():
                return

            self.tray_icon = QSystemTrayIcon(app_icon, self)
            self.tray_icon.setToolTip("Zieork Autonomous Neural System")

            tray_menu = QMenu()
            action_show = tray_menu.addAction("Show Zieork")
            action_show.triggered.connect(self.show_and_raise)

            action_new = tray_menu.addAction("New Session")
            action_new.triggered.connect(lambda: self.webview.setUrl(QUrl(BACKEND_URL)))

            tray_menu.addSeparator()

            action_quit = tray_menu.addAction("Quit Zieork")
            action_quit.triggered.connect(self.quit_application)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self.on_tray_activated)
            self.tray_icon.show()

        def on_tray_activated(self, reason):
            if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
                if self.isVisible():
                    self.hide()
                else:
                    self.show_and_raise()

        def show_and_raise(self):
            self.show()
            self.raise_()
            self.activateWindow()

        def quit_application(self):
            nonlocal backend_proc
            if backend_proc and backend_proc.poll() is None:
                try:
                    backend_proc.terminate()
                    backend_proc.wait(timeout=2)
                except Exception:
                    backend_proc.kill()
            QApplication.quit()

        def closeEvent(self, event):
            # Minimize to tray if tray is available, otherwise prompt/quit
            if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
                self.hide()
                self.tray_icon.showMessage(
                    "Zieork Running in Background",
                    "Zieork is still active in the system tray. Click to reopen.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
                event.ignore()
            else:
                self.quit_application()
                event.accept()

    window = ZieorkMainWindow()
    window.show()

    # Clean shutdown on SIGINT / Ctrl+C
    signal.signal(signal.SIGINT, lambda sig, frame: window.quit_application())

    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
