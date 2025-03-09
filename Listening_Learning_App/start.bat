@echo off
setlocal

REM Get the directory of this script
set "SCRIPT_DIR=%~dp0"

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Check for virtual environment
if exist "venv" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist "..\venv" (
    echo Activating parent virtual environment...
    call ..\venv\Scripts\activate.bat
)

REM Run the application with auto-install and dependency checks
python run.py --auto-install %*

REM Pause at the end if there was an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred. Press any key to exit...
    pause > nul
)

endlocal 