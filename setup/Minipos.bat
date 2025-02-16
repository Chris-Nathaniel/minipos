@echo off

:: Start the Ngrok and Python scripts minimized
start /min "" "C:\Users\LEGION\.vscode\github\Source\minipos\setup\minipos_start.bat"
timeout /t 1 /nobreak >nul
start /min "" "C:\Users\LEGION\.vscode\github\Source\minipos\setup\connecttongrok.bat"

:: Wait for a short time to ensure they are up
timeout /t 4 /nobreak >nul

:: Start the main app
start "" "C:\Users\LEGION\.vscode\github\Source\minipos\setup\miniposapp.lnk"


