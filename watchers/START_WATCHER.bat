@echo off
REM Bronze Tier File System Watcher - Windows Launcher
REM This script starts the filesystem watcher

setlocal enabledelayedexpansion

REM Get the project root (parent of watchers folder)
for %%A in ("%~dp0.") do set "PROJECT_ROOT=%%~fA"

echo.
echo ======================================================================
echo  Bronze Tier File System Watcher Launcher
echo ======================================================================
echo.
echo Project Root: %PROJECT_ROOT%
echo Script: %~f0
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if watchdog is installed
python -c "import watchdog" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: watchdog library is not installed
    echo Installing watchdog...
    python -m pip install watchdog
    if %errorlevel% neq 0 (
        echo Failed to install watchdog
        pause
        exit /b 1
    )
)

echo.
echo Starting watcher...
echo Press Ctrl+C to stop
echo.
echo ======================================================================
echo.

REM Start the watcher
python "%PROJECT_ROOT%\watchers\filesystem_watcher.py"

if %errorlevel% neq 0 (
    echo.
    echo ======================================================================
    echo ERROR: Watcher exited with error code %errorlevel%
    echo ======================================================================
    pause
    exit /b %errorlevel%
)

endlocal
