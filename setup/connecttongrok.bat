@echo off
set NGROK_PATH=C:\Users\LEGION\.vscode\github\Source\minipos\setup\ngrok.exe

:: Authenticate with ngrok (optional, if you haven't already)
%NGROK_PATH% authtoken 2mCaH2JFVG8YiKB0KK9e3BMLNbC_7bDuwUcRaBQxLsa4ayAyf

:: Start ngrok with the specified domain and port
%NGROK_PATH% http --domain=amused-fit-wasp.ngrok-free.app 5000


pause