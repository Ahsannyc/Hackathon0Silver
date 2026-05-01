@echo off
REM Bronze Tier Skill: Task Analyzer
REM Wrapper for Windows systems

setlocal enabledelayedexpansion

REM Get the project root (parent of .specify folder)
for %%A in ("%~dp0..\.") do set "PROJECT_ROOT=%%~fA"

cd /d "%PROJECT_ROOT%"

echo.
echo Launching Task Analyzer...
echo Project Root: %PROJECT_ROOT%
echo.

python "%PROJECT_ROOT%\.specify\skills\task_analyzer.py"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Skill execution failed (exit code: %errorlevel%)
    pause
    exit /b %errorlevel%
)

endlocal
