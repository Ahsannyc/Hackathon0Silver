# Daily Scheduler - Silver Tier (Windows PowerShell)
# Runs daily at 8AM (configured via Windows Task Scheduler)
# Generates daily briefing from /Done files
#
# Setup Instructions:
# ==================
#
# 1. Open PowerShell as Administrator:
#    Start → PowerShell → Right-click → Run as administrator
#
# 2. Create scheduled task:
#    powershell -ExecutionPolicy Bypass -File "C:\path\to\schedulers\daily_scheduler.ps1"
#
# 3. Or use Windows Task Scheduler GUI (see SETUP.md)
#
# Run this script manually:
#    powershell -ExecutionPolicy Bypass -File ".\schedulers\daily_scheduler.ps1"

# Set error action
$ErrorActionPreference = "Stop"

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ScriptDir = "$ProjectRoot\schedulers"
$Generator = "$ScriptDir\daily_briefing_generator.py"
$LogFile = "$ProjectRoot\Logs\scheduler.log"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Ensure directories exist
$LogsDir = "$ProjectRoot\Logs"
if (!(Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
}

# Logging functions
function Write-Log {
    param([string]$Message)
    $LogMessage = "[$Timestamp] $Message"
    Add-Content -Path $LogFile -Value $LogMessage -Encoding UTF8
    Write-Host $Message -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    $LogMessage = "[$Timestamp] ✓ $Message"
    Add-Content -Path $LogFile -Value $LogMessage -Encoding UTF8
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    $LogMessage = "[$Timestamp] ✗ ERROR: $Message"
    Add-Content -Path $LogFile -Value $LogMessage -Encoding UTF8
    Write-Host "✗ ERROR: $Message" -ForegroundColor Red
}

# Header
Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "  Daily Summary Generator - Scheduler" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

Write-Log "Daily scheduler started"

# Check Python installation
try {
    $PythonVersion = python --version 2>&1
    Write-Success "Python found: $PythonVersion"
} catch {
    Write-Error-Custom "Python not found. Please install Python 3."
    exit 1
}

# Verify script exists
if (!(Test-Path $Generator)) {
    Write-Error-Custom "Generator script not found: $Generator"
    exit 1
}

Write-Success "Generator script found"

# Change to project root
Set-Location $ProjectRoot
Write-Success "Working directory: $ProjectRoot"

# Run the generator
Write-Log "Running daily briefing generator..."
Write-Host ""

try {
    & python "$Generator"
    $GeneratorExit = $LASTEXITCODE
} catch {
    Write-Error-Custom "Failed to run generator: $_"
    exit 1
}

Write-Host ""

# Check result
if ($GeneratorExit -eq 0) {
    Write-Success "Daily briefing generated successfully"

    # Show generated file
    $Today = Get-Date -Format "yyyy-MM-dd"
    $SummaryFile = "$ProjectRoot\Logs\daily_briefing_$Today.md"

    if (Test-Path $SummaryFile) {
        Write-Success "Summary file: $SummaryFile"
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Blue
        Write-Host "  Generated Summary Preview" -ForegroundColor Blue
        Write-Host "========================================" -ForegroundColor Blue

        $Content = Get-Content $SummaryFile
        $Preview = $Content[0..29] -join "`n"
        Write-Host $Preview

        Write-Host ""
        Write-Host "[... briefing continues ...]"
        Write-Host ""
    }
} else {
    Write-Error-Custom "Generator failed with exit code: $GeneratorExit"
    exit 1
}

Write-Log "Daily scheduler completed successfully"
Write-Host ""
Write-Host "========================================" -ForegroundColor Blue
Write-Host "  Next scheduled run: Tomorrow at 8:00 AM" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

exit 0
