@echo off
REM Ralph Wiggum Loop - Windows Command Wrapper
REM Wraps ralph_loop_runner.py for easy invocation on Windows

setlocal enabledelayedexpansion

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR:~0,-1%
cd /d "%PROJECT_DIR%\.."

REM Check if running from correct directory
if not exist "%SCRIPT_DIR%ralph_loop_runner.py" (
    echo ❌ Error: ralph_loop_runner.py not found
    echo Make sure you're in the project root directory
    exit /b 1
)

REM Run the Python script with all arguments
python3 "%SCRIPT_DIR%ralph_loop_runner.py" %*
