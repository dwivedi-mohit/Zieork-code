@echo off
title Zieork Neural Desktop Launcher
setlocal EnableDelayedExpansion

echo ======================================================================
echo ⚡ ZIEORK SOVEREIGN DESKTOP LAUNCHER (WINDOWS)
echo ======================================================================

set SCRIPT_DIR=%~dp0..
cd /d "%SCRIPT_DIR%"

:: Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python was not found in your PATH.
        echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
        pause
        exit /b 1
    ) else (
        set PYTHON_BIN=py
    )
) else (
    set PYTHON_BIN=python
)

echo [*] Checking local Zieork Neural Server...
%PYTHON_BIN% -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/info', timeout=1.0)" >nul 2>nul
if %errorlevel% neq 0 (
    echo [*] Starting local Zieork backend server...
    start /min "Zieork Server" %PYTHON_BIN% app.py
    timeout /t 3 /nobreak >nul
) else (
    echo [*] Zieork backend is already active on port 5000.
)

:: Check if Electron app is built or present
if exist "%SCRIPT_DIR%\desktop\electron\node_modules\electron" (
    echo [*] Launching Electron Desktop Window...
    cd /d "%SCRIPT_DIR%\desktop\electron"
    start "" npx electron .
    exit /b 0
)

:: Check if PyQt6 desktop app is available
%PYTHON_BIN% -c "import PyQt6.QtWebEngineWidgets" >nul 2>nul
if %errorlevel% equ 0 (
    echo [*] Launching Native PyQt6 Desktop Window...
    start "" %PYTHON_BIN% "%SCRIPT_DIR%\desktop\app_qt.py"
    exit /b 0
)

:: Fallback to default browser web window
echo [*] Launching Zieork in your default browser...
start http://localhost:5000

exit /b 0
