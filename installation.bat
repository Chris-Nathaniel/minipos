@echo off
REM Check if Python is installed
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Installing Python...
    REM Install Python (modify the URL with the latest version if needed)
    start https://www.python.org/downloads/
    exit /b 1
)

REM Check if pip is installed
where pip >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Pip is not installed. Installing pip...
    REM Install pip
    python -m ensurepip --upgrade
    REM If pip still doesn't work, prompt user to install manually
    where pip >nul 2>nul
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install pip. Please install pip manually.
        exit /b 1
    )
)

REM Check if requirements.txt exists
IF NOT EXIST requirements.txt (
    echo requirements.txt file not found.
    exit /b 1
)

REM Install the packages from requirements.txt
echo Installing required packages from requirements.txt...
pip install -r requirements.txt

REM Check if the installation was successful
IF %ERRORLEVEL% EQU 0 (
    echo All packages were installed successfully!
) ELSE (
    echo There was an error installing the packages.
)
REM create shortcut
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

:: Define the icon file (must be a .ico file)
set "ICON_FILE=%SCRIPT_DIR%icon.ico"

:: Check if the icon file exists
if not exist "%ICON_FILE%" (
    echo Warning: icon.ico not found! Using default icon.
) else (
    echo Using custom icon: %ICON_FILE%
)

:: Create the shortcut using PowerShell
powershell -command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET_FILE%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; if (Test-Path '%ICON_FILE%') { $s.IconLocation = '%ICON_FILE%' }; $s.Save()"

echo Shortcut created at %SHORTCUT_PATH%
pause





