# PHR: Create Daily Briefing Scheduler

**ID:** 006
**Stage:** implementation | silver-tier
**Date:** 2026-02-14
**Status:** COMPLETE ✅ (Renamed: summary → briefing)

---

## Task Summary

Create a daily scheduling system that generates briefing summaries of completed tasks from `/Done/` folder at 8AM, saved to `/Logs/daily_briefing_[date].md`.

---

## Implementation Details

**Files Created:**
1. `schedulers/daily_briefing_generator.py` (304 lines) - Core generator
2. `schedulers/daily_scheduler.sh` (109 lines) - Linux/Mac wrapper
3. `schedulers/daily_scheduler.ps1` (136 lines) - Windows wrapper
4. Documentation guides (4 files)

---

## Components

### 1. Python Generator
**File:** `schedulers/daily_briefing_generator.py`

**Purpose:** Scan completed tasks and generate briefing

**Process:**
```
Scan /Done/ folder
    ↓
Read YAML metadata from .md files
    ↓
Categorize by type (email, linkedin, approval, plan)
    ↓
Count occurrences
    ↓
Extract details (sender, content, action)
    ↓
Generate markdown briefing
    ↓
Save to /Logs/daily_briefing_YYYY-MM-DD.md
```

**Output Format:**
```markdown
---
type: daily_briefing
date: 2026-02-14
generated: 2026-02-14T10:30:45.123456
total_completed: 5
---

# Daily Briefing - Friday, February 14, 2026

**Generated:** 10:30:45

---

## 📈 Metrics

| Metric | Count |
|--------|-------|
| **Total Completed** | 5 |
| Emails Sent | 2 |
| LinkedIn Posts | 1 |
| Approvals Processed | 2 |
| Plans Created | 0 |

---

## 📧 Emails (2)

- Invoice #123 → client@example.com
- Project Update → team@example.com

---

## 📱 LinkedIn Posts (1)

- Excited to announce our new feature...

---

## ✅ Approvals Processed (2)

- send_email: executed
- post_linkedin: executed

---

## 💡 Insights

- 📧 High email volume today (2 emails)
- 📱 Successfully posted 1 LinkedIn post(s)
- ✅ Processed 2 approval(s) with HITL

---

*Next briefing: 2026-02-15 at 08:00 AM*
```

---

### 2. Linux/Mac Cron Wrapper
**File:** `schedulers/daily_scheduler.sh`

**Features:**
- Bash script for cron execution
- Colored output for terminal
- Automatic logging
- Project path resolution
- Python path detection

**Setup (2 minutes):**
```bash
# 1. Make executable
chmod +x schedulers/daily_scheduler.sh

# 2. Get absolute path
pwd
# Example output: /Users/john/Desktop/Hackathon0Silver

# 3. Edit crontab
crontab -e

# 4. Add line
0 8 * * * /Users/john/Desktop/Hackathon0Silver/schedulers/daily_scheduler.sh

# 5. Verify
crontab -l
```

---

### 3. Windows PowerShell Wrapper
**File:** `schedulers/daily_scheduler.ps1`

**Features:**
- PowerShell script for Task Scheduler
- UTF-8 encoding support
- Colored console output
- Automatic logging
- Windows-friendly paths

**Setup (2 minutes):**
```powershell
# 1. Run PowerShell as Administrator

# 2. Create scheduled task
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"C:\path\to\daily_scheduler.ps1`""
$Trigger = New-ScheduledTaskTrigger -Daily -At 08:00AM
Register-ScheduledTask -TaskName "Silver Tier Daily Briefing" -Action $Action -Trigger $Trigger -User $env:USERNAME -Force

# 3. Verify
Get-ScheduledTask -TaskName "Silver Tier Daily Briefing"
```

---

## Scheduling Options

### Option 1: Every Day at 8AM (Production)
```bash
# Cron
0 8 * * * /path/to/daily_scheduler.sh

# Task Scheduler
New-ScheduledTaskTrigger -Daily -At 08:00AM
```

### Option 2: Every Weekday (Mon-Fri)
```bash
# Cron
0 8 * * 1-5 /path/to/daily_scheduler.sh
```

### Option 3: Multiple Times Daily
```bash
# Cron (8AM and 2PM)
0 8,14 * * * /path/to/daily_scheduler.sh
```

---

## Briefing Categories

The generator automatically categorizes tasks by type:

| Category | Detects | Icon |
|----------|---------|------|
| Emails | type: email_approval | 📧 |
| LinkedIn | type: linkedin_approval | 📱 |
| Approvals | type: *_approval | ✅ |
| Plans | type: plan | 📋 |
| Other | Anything else | 💡 |

---

## Files Generated

**Location:** `/Logs/`

**Files:**
- `daily_briefing_2026-02-14.md` - Today's briefing
- `daily_briefing_2026-02-13.md` - Yesterday's
- `scheduler.log` - Execution log

**Naming Pattern:** `daily_briefing_YYYY-MM-DD.md`

---

## Integration Points

**Reads From:**
- `/Done/` - Completed task files
- File YAML metadata (type, details)

**Writes To:**
- `/Logs/daily_briefing_YYYY-MM-DD.md` - Briefing file
- `/Logs/scheduler.log` - Execution log

**Integrates With:**
- All watcher scripts (source of completed tasks)
- Ralph Loop (source of completed plans)
- HITL Approval Handler (source of approvals)
- Email MCP (source of sent emails)

---

## Testing

### Phase 1: Create Test Files
```bash
mkdir -p Done

cat > Done/test_email.md << 'EOF'
---
type: email_approval
action: send_email
to: client@example.com
subject: Invoice #123
status: executed
---

# Email Sent
EOF
```

### Phase 2: Run Generator
```bash
python schedulers/daily_briefing_generator.py
```

### Phase 3: Verify Output
```bash
cat Logs/daily_briefing_$(date +%Y-%m-%d).md
```

**Expected:** Briefing file with metrics and sections

### Phase 4: Verify Scheduling
```bash
# Linux/Mac: check crontab
crontab -l

# Windows: check Task Scheduler
Get-ScheduledTask -TaskName "Silver Tier Daily Briefing"

# Wait for 8AM and verify file created
ls -la Logs/daily_briefing_*.md
```

---

## Naming Changes Applied

**Renaming from "summary" to "briefing":**
- ✅ `daily_summary_generator.py` → `daily_briefing_generator.py`
- ✅ Class: `DailySummaryGenerator` → `DailyBriefingGenerator`
- ✅ Method: `generate_summary()` → `generate_briefing()`
- ✅ Variable: `summary_content` → `briefing_content`
- ✅ Output files: `daily_summary_*.md` → `daily_briefing_*.md`
- ✅ All documentation updated

---

## Documentation

**Files:**
- `DAILY_BRIEFING_SETUP.md` - Complete setup guide (15KB)
- `DAILY_BRIEFING_QUICK_START.md` - 5-minute setup (4.8KB)
- `DAILY_BRIEFING_TEST_GUIDE.md` - Testing guide with expected outputs

---

## Features

✅ Automatic task categorization
✅ Markdown formatting with emojis
✅ YAML frontmatter for metadata
✅ Metrics tables for quick overview
✅ Execution logging
✅ Cross-platform support (Windows/Mac/Linux)
✅ Error handling and recovery

---

**Progress:** ✅ COMPLETE | Status: Ready for production
**Next:** End-to-end system testing

