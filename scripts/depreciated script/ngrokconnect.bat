@echo off
:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "NGROK_PATH=%SCRIPT_DIR%ngrok.exe"

:: Load .env variable using PowerShell
for /f "delims=" %%A in ('powershell -Command "(Get-Content '%PROJECT_DIR%\.env' | Select-String 'NGROK_AUTH' | ForEach-Object { ($_ -split '=')[1] }) -replace '^\s+|\s+$',''"') do set NGROK_AUTH=%%A
for /f "delims=" %%A in ('powershell -Command "(Get-Content '%PROJECT_DIR%\.env' | Select-String 'NGROK_DOMAIN' | ForEach-Object { ($_ -split '=')[1] }) -replace '^\s+|\s+$',''"') do set NGROK_DOMAIN=%%A

:: Display loaded values for debugging
echo NGROK_DOMAIN=%NGROK_DOMAIN%
echo NGROK_AUTH=%NGROK_AUTH%

:: Authenticate with ngrok
"%NGROK_PATH%" authtoken %NGROK_AUTH%

:: Start ngrok with the specified domain and port
::"%NGROK_PATH%" http --domain=%NGROK_DOMAIN% 5000
 wscript.exe "%SCRIPT_DIR%\ngrok.vbs"

exit
