' ==============================================================================
' Zieork Silent Windows Launcher (Suppresses Console Window)
' ==============================================================================
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

ScriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
BatPath = ScriptDir & "\start_zieork.bat"

' Run bat file hidden (0 = hide window, false = don't wait for completion)
WshShell.Run Chr(34) & BatPath & Chr(34), 0, False
Set WshShell = Nothing
Set FSO = Nothing
