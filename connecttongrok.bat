@echo off
:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"
set "NGROK_PATH=%SCRIPT_DIR%ngrok.exe"

:: Authenticate with ngrok
%NGROK_PATH% authtoken 2mCaH2JFVG8YiKB0KK9e3BMLNbC_7bDuwUcRaBQxLsa4ayAyf

:: Start ngrok with the specified domain and port
wscript.exe ngrok.vbs

exit
