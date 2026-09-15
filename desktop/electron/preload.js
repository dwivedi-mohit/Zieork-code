/**
 * Preload script for Zieork Desktop Application.
 * Exposes secure IPC bridges between the native desktop shell and web renderer.
 */
const { contextBridge, ipcRenderer, shell } = require("electron");

contextBridge.exposeInMainWorld("zieorkDesktop", {
  isDesktop: true,
  platform: process.platform,
  version: "2.5.0",
  
  // Window controls
  minimize: () => ipcRenderer.send("window-minimize"),
  maximize: () => ipcRenderer.send("window-maximize"),
  close: () => ipcRenderer.send("window-close"),

  // Native desktop notification
  notify: (title, body) => {
    ipcRenderer.send("desktop-notification", { title, body });
  },

  // Open external links in default OS browser
  openExternal: (url) => {
    shell.openExternal(url);
  }
});
