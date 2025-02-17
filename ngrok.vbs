Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "ngrok.exe http --domain=amused-fit-wasp.ngrok-free.app 5000", 0 
