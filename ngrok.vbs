Set WshShell = CreateObject("WScript.Shell")

' Get the domain from an environment variable
ngrokDomain = WshShell.ExpandEnvironmentStrings("%NGROK_DOMAIN%")

' Run ngrok with the dynamic domain
WshShell.Run "ngrok.exe http --domain=" & ngrokDomain & " 5000", 0
