#!/bin/bash

# Daily Scheduler - Silver Tier
# Runs daily at 8AM (configured via cron)
# Generates daily briefing from /Done files

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="$PROJECT_ROOT/schedulers"
GENERATOR="$SCRIPT_DIR/daily_briefing_generator.py"
LOG_FILE="$PROJECT_ROOT/Logs/scheduler.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure log directory exists
mkdir -p "$PROJECT_ROOT/Logs"

# Log function
log_message() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo "[$TIMESTAMP] ✓ $1" >> "$LOG_FILE"
    echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
    echo "[$TIMESTAMP] ✗ ERROR: $1" >> "$LOG_FILE"
    echo -e "${RED}✗ ERROR: $1${NC}"
}

# Header
echo ""
echo "========================================"
echo "  Daily Briefing Generator - Scheduler"
echo "========================================"
echo ""

log_message "Daily scheduler started"

# Verify Python is installed
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 not found. Please install Python 3."
    exit 1
fi

log_success "Python 3 found"

# Verify script exists
if [ ! -f "$GENERATOR" ]; then
    log_error "Generator script not found: $GENERATOR"
    exit 1
fi

log_success "Generator script found"

# Change to project root
cd "$PROJECT_ROOT" || exit 1
log_success "Working directory: $PROJECT_ROOT"

# Run the generator
log_message "Running daily briefing generator..."
echo ""

python3 "$GENERATOR"
GENERATOR_EXIT=$?

echo ""

# Check result
if [ $GENERATOR_EXIT -eq 0 ]; then
    log_success "Daily briefing generated successfully"

    # Show generated file
    TODAY=$(date "+%Y-%m-%d")
    SUMMARY_FILE="$PROJECT_ROOT/Logs/daily_briefing_$TODAY.md"

    if [ -f "$SUMMARY_FILE" ]; then
        log_success "Summary file: $SUMMARY_FILE"
        echo ""
        echo "========================================"
        echo "  Generated Summary Preview"
        echo "========================================"
        head -30 "$SUMMARY_FILE"
        echo ""
        echo "[... briefing continues ...]"
        echo ""
    fi
else
    log_error "Generator failed with exit code: $GENERATOR_EXIT"
    exit 1
fi

log_message "Daily scheduler completed successfully"
echo ""
echo "========================================"
echo "  Next scheduled run: Tomorrow at 8:00 AM"
echo "========================================"
echo ""

exit 0
