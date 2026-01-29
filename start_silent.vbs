Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\plex-scrobbler"
WshShell.Run "run_scrobbler.bat", 0
Set WshShell = Nothing