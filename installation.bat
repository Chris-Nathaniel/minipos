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

pause

