@echo off
REM Check if pip is installed
where pip >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Pip is not installed. Please install pip first.
    exit /b 1
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
