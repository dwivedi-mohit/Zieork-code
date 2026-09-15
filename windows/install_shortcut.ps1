# ==============================================================================
# PowerShell script to install Windows Desktop & Start Menu Shortcuts
# ==============================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RootDir = Resolve-Path "$ScriptDir\.."
$VbsPath = "$ScriptDir\start_silent.vbs"
$IconPath = "$RootDir\desktop\assets\icon.ico"

$WshShell = New-Object -ComObject WScript.Shell

# 1. Create Desktop Shortcut
$DesktopDir = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$DesktopShortcut = $WshShell.CreateShortcut("$DesktopDir\Zieork.lnk")
$DesktopShortcut.TargetPath = "wscript.exe"
$DesktopShortcut.Arguments = "`"$VbsPath`""
$DesktopShortcut.WorkingDirectory = "$RootDir"
$DesktopShortcut.IconLocation = "$IconPath,0"
$DesktopShortcut.Description = "Zieork — Autonomous Neural Intelligence System"
$DesktopShortcut.Save()

# 2. Create Start Menu Shortcut
$StartMenuDir = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::StartMenu)
$ProgramsDir = "$StartMenuDir\Programs"
$StartShortcut = $WshShell.CreateShortcut("$ProgramsDir\Zieork.lnk")
$StartShortcut.TargetPath = "wscript.exe"
$StartShortcut.Arguments = "`"$VbsPath`""
$StartShortcut.WorkingDirectory = "$RootDir"
$StartShortcut.IconLocation = "$IconPath,0"
$StartShortcut.Description = "Zieork — Autonomous Neural Intelligence System"
$StartShortcut.Save()

Write-Host "======================================================================" -ForegroundColor Green
Write-Host "✅ Zieork desktop & Start Menu shortcuts successfully created!" -ForegroundColor Green
Write-Host "You can now launch Zieork directly from your Windows Desktop or Start Menu." -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
