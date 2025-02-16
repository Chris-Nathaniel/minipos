@echo off
:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"

:: Change to the script directory
cd /d "%SCRIPT_DIR%"

:: Activate the virtual environment
call venv\Scripts\activate 

:: Run the Python application
python app.py