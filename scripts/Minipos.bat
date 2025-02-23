@echo off
:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"

:: Change to the script directory
cd /d "%SCRIPT_DIR:~0,-1%\.."

:: Run the Python application
python app.py

exit