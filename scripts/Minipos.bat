@echo off
:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"

:: Start the Ngrok and Python scripts minimized
start /min "" "%SCRIPT_DIR%minipos_start.bat"
timeout /t 1 /nobreak >nul
::start /min "" "%SCRIPT_DIR%ngrokconnect.bat"

:: Wait for a short time to ensure they are up
timeout /t 4 /nobreak >nul



exit