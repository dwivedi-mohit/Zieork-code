@echo off
title Build Zieork Windows Standalone Executable (.exe)
setlocal

echo ======================================================================
echo ⚡ BUILD ZIEORK STANDALONE WINDOWS APP (.EXE)
echo ======================================================================

set SCRIPT_DIR=%~dp0..
cd /d "%SCRIPT_DIR%\desktop\electron"

echo [*] Checking Node.js and npm...
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm was not found. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [*] Installing Electron & Electron-Builder...
call npm install

echo [*] Packaging Standalone Windows Installer and Portable Executable...
call npm run dist:win

echo ======================================================================
echo ✅ Build complete!
echo Check the 'dist' folder for your Windows .exe installer:
echo     %SCRIPT_DIR%\dist\
echo ======================================================================
pause
