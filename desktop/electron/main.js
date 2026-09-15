/**
 * Zieork Sovereign Desktop Application (Electron Main Process).
 * Cross-platform desktop shell for Windows & Linux.
 */
const { app, BrowserWindow, Tray, Menu, globalShortcut, ipcMain, Notification, shell } = require("electron");
const path = require("path");
const http = require("http");
const { spawn } = require("child_process");

const ROOT_DIR = path.resolve(__dirname, "../../");
const BACKEND_URL = "http://127.0.0.1:5000";
const HEALTH_URL = `${BACKEND_URL}/api/info`;

let mainWindow = null;
let splashWindow = null;
let tray = null;
let backendProcess = null;
let isQuitting = false;

// Determine platform-specific icon
const isWin = process.platform === "win32";
const iconFile = isWin ? "icon.ico" : "icon.png";
const iconPath = path.join(ROOT_DIR, "desktop", "assets", iconFile);

/**
 * Ping backend health endpoint to verify if Flask server is responsive.
 */
function checkBackendHealth() {
  return new Promise((resolve) => {
    const req = http.get(HEALTH_URL, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on("error", () => resolve(false));
    req.setTimeout(1200, () => {
      req.abort();
      resolve(false);
    });
  });
}

/**
 * Automatically launch python backend if not already running.
 */
async function ensureBackendRunning() {
  const alive = await checkBackendHealth();
  if (alive) {
    console.log("[Desktop Main] Backend is already running on port 5000.");
    return true;
  }

  console.log("[Desktop Main] Spawning local Zieork backend...");
  const pythonCmd = isWin ? "python" : "python3";
  const appPyPath = path.join(ROOT_DIR, "app.py");

  try {
    backendProcess = spawn(pythonCmd, [appPyPath], {
      cwd: ROOT_DIR,
      stdio: "ignore",
      detached: false
    });

    backendProcess.on("error", (err) => {
      console.error("[Desktop Main] Failed to spawn backend:", err);
    });

    // Poll until ready (up to 20 seconds)
    for (let i = 0; i < 40; i++) {
      await new Promise((r) => setTimeout(r, 500));
      if (await checkBackendHealth()) {
        console.log("[Desktop Main] Backend is now online and ready!");
        return true;
      }
    }
  } catch (err) {
    console.error("[Desktop Main] Error launching backend process:", err);
  }

  return false;
}

/**
 * Create sleek splash screen window.
 */
function createSplashScreen() {
  splashWindow = new BrowserWindow({
    width: 440,
    height: 340,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    center: true,
    show: false,
    icon: iconPath,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  splashWindow.loadFile(path.join(__dirname, "splash.html"));
  splashWindow.once("ready-to-show", () => {
    splashWindow.show();
  });
}

/**
 * Create main application window.
 */
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1380,
    height: 880,
    minWidth: 1024,
    minHeight: 720,
    show: false,
    backgroundColor: "#0b0f19",
    icon: iconPath,
    title: "Zieork — Autonomous Neural Intelligence System",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
      spellcheck: true
    }
  });

  // Load local web UI
  mainWindow.loadURL(BACKEND_URL);

  mainWindow.once("ready-to-show", () => {
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.close();
      splashWindow = null;
    }
    mainWindow.show();
    mainWindow.focus();
  });

  // Intercept new window requests to open in native default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("http://") || url.startsWith("https://")) {
      shell.openExternal(url);
    }
    return { action: "deny" };
  });

  // Minimize to tray instead of closing on close button (optional preference)
  mainWindow.on("close", (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      if (Notification.isSupported()) {
        new Notification({
          title: "Zieork Active",
          body: "Zieork is running in the background. Press Ctrl+Shift+Z or click the tray icon to reopen.",
          icon: iconPath
        }).show();
      }
    }
  });
}

/**
 * Initialize system tray icon and menu.
 */
function createTray() {
  try {
    tray = new Tray(iconPath);
    tray.setToolTip("Zieork — Autonomous Neural System");

    const contextMenu = Menu.buildFromTemplate([
      {
        label: "Open Zieork",
        click: () => {
          if (mainWindow) {
            mainWindow.show();
            mainWindow.focus();
          }
        }
      },
      {
        label: "New Session",
        click: () => {
          if (mainWindow) {
            mainWindow.loadURL(BACKEND_URL);
            mainWindow.show();
          }
        }
      },
      { type: "separator" },
      {
        label: "Toggle Shortcut (Ctrl+Shift+Z)",
        enabled: false
      },
      { type: "separator" },
      {
        label: "Quit Zieork",
        click: () => {
          isQuitting = true;
          app.quit();
        }
      }
    ]);

    tray.setContextMenu(contextMenu);

    tray.on("double-click", () => {
      if (mainWindow) {
        if (mainWindow.isVisible()) {
          mainWindow.hide();
        } else {
          mainWindow.show();
          mainWindow.focus();
        }
      }
    });
  } catch (err) {
    console.warn("[Desktop Main] System tray not available:", err.message);
  }
}

/**
 * Register global hotkey (Ctrl+Shift+Z / Cmd+Shift+Z) to summon Zieork.
 */
function registerGlobalHotkeys() {
  const shortcut = "CommandOrControl+Shift+Z";
  const registered = globalShortcut.register(shortcut, () => {
    if (mainWindow) {
      if (mainWindow.isVisible() && mainWindow.isFocused()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });

  if (registered) {
    console.log(`[Desktop Main] Registered global hotkey: ${shortcut}`);
  }
}

// IPC Handlers
ipcMain.on("window-minimize", () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on("window-maximize", () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

ipcMain.on("window-close", () => {
  if (mainWindow) mainWindow.close();
});

ipcMain.on("desktop-notification", (event, { title, body }) => {
  if (Notification.isSupported()) {
    new Notification({
      title: title || "Zieork",
      body: body || "",
      icon: iconPath
    }).show();
  }
});

// App lifecycle
app.whenReady().then(async () => {
  createSplashScreen();
  await ensureBackendRunning();
  createMainWindow();
  createTray();
  registerGlobalHotkeys();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    } else if (mainWindow) {
      mainWindow.show();
    }
  });
});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});

app.on("before-quit", () => {
  isQuitting = true;
  if (backendProcess && !backendProcess.killed) {
    console.log("[Desktop Main] Terminating backend process...");
    try {
      backendProcess.kill();
    } catch (e) {
      // ignore
    }
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    // Keep running in tray unless explicit quit
    if (isQuitting) {
      app.quit();
    }
  }
});
