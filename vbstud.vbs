Dim WinScriptHost
Set WinScriptHost = CreateObject("WScript.Shell")
WinScriptHost.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\Users\abilenes.silva\true\scan_dns_loop.ps1""", 0, False
Set WinScriptHost = Nothing