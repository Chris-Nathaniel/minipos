@echo off
setlocal

:: Get the current script's directory
set "SCRIPT_DIR=%~dp0"

:: Set the target batch file
set "TARGET_FILE=%SCRIPT_DIR%Minipos.bat"

:: Get the user's Desktop path
for /f "tokens=*" %%a in ('powershell -command "[System.Environment]::GetFolderPath('Desktop')"') do (
    set "DESKTOP_PATH=%%a"
)

:: Define shortcut location
set "SHORTCUT_PATH=%DESKTOP_PATH%\Minipos.lnk"

:: Create the shortcut using PowerShell
powershell -command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET_FILE%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"

echo Shortcut created at %SHORTCUT_PATH%
pause


