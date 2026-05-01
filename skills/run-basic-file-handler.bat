@echo off
REM Bronze Tier Skill: Basic File Handler
REM Wrapper for Windows systems

setlocal enabledelayedexpansion

REM Get the project root (parent of .specify folder)
for %%A in ("%~dp0..\.") do set "PROJECT_ROOT=%%~fA"

cd /d "%PROJECT_ROOT%"

echo.
echo Launching Basic File Handler...
echo Project Root: %PROJECT_ROOT%
echo.

python "%PROJECT_ROOT%\.specify\skills\basic_file_handler.py"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Skill execution failed (exit code: %errorlevel%)
    pause
    exit /b %errorlevel%
)

endlocal
