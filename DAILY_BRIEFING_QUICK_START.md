# Daily Briefing - Quick Start (5 Minutes)

**Status:** ✅ Ready
**Location:** `schedulers/`
**Runs at:** 8:00 AM daily

## What It Does

```
8:00 AM Every Day
  ↓
Scans /Done for completed tasks
  ↓
Counts emails, posts, approvals, etc.
  ↓
Generates briefing
  ↓
Saves to /Logs/daily_briefing_2026-02-14.md
```

## Quick Setup

### Option 1: Linux/Mac (Cron) - 2 Minutes

```bash
# 1. Make executable
chmod +x schedulers/daily_scheduler.sh

# 2. Get full path
pwd
# Copy output path

# 3. Edit crontab
crontab -e

# 4. Add this line (replace with your path):
0 8 * * * /full/path/to/daily_scheduler.sh

# 5. Verify
crontab -l
```

### Option 2: Windows (PowerShell) - 2 Minutes

```powershell
# 1. Open PowerShell as Administrator
# Right-click PowerShell → Run as administrator

# 2. Run this command (replace path):
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"C:\path\to\schedulers\daily_scheduler.ps1`""
$Trigger = New-ScheduledTaskTrigger -Daily -At 08:00AM
Register-ScheduledTask -TaskName "Silver Tier Daily Summary" -Action $Action -Trigger $Trigger -User $env:USERNAME -Force

# 3. Verify in Task Scheduler:
Get-ScheduledTask -TaskName "Silver Tier Daily Summary"
```

## Test It (1 Minute)

### Test 1: Run Generator Directly
```bash
# Linux/Mac
python3 schedulers/daily_briefing_generator.py

# Windows (PowerShell)
python schedulers\daily_briefing_generator.py
```

Should create: `Logs/daily_briefing_2026-02-14.md`

### Test 2: Run Full Scheduler
```bash
# Linux/Mac
bash schedulers/daily_scheduler.sh

# Windows (PowerShell as Admin)
powershell -ExecutionPolicy Bypass -File "schedulers\daily_scheduler.ps1"
```

### Test 3: Check Output
```bash
# Linux/Mac
cat Logs/daily_briefing_$(date +%Y-%m-%d).md

# Windows
$Today = Get-Date -Format "yyyy-MM-dd"
Get-Content Logs\daily_briefing_$Today.md
```

## Cron Quick Reference

```bash
# Every day at 8AM
0 8 * * * /path/to/daily_scheduler.sh

# Every weekday (Mon-Fri) at 8AM
0 8 * * 1-5 /path/to/daily_scheduler.sh

# Every 6 hours
0 */6 * * * /path/to/daily_scheduler.sh

# At 8AM and 2PM
0 8,14 * * * /path/to/daily_scheduler.sh
```

## What Gets Counted

```
📧 Emails Sent
📱 LinkedIn Posts
✅ Approvals Processed
📋 Plans Created
🎯 Other Actions
```

## View Generated Summary

```bash
# Latest briefing
cat Logs/daily_briefing_$(date +%Y-%m-%d).md

# List all summaries
ls -la Logs/daily_briefing_*.md
```

## Monitor Execution

```bash
# Watch logs in real-time
tail -f Logs/scheduler.log

# Check last run (Linux/Mac)
grep "scheduler" Logs/scheduler.log | tail -5
```

## Verify It's Running

### Linux/Mac
```bash
# List cron jobs
crontab -l

# Should show:
# 0 8 * * * /full/path/to/daily_scheduler.sh
```

### Windows
```powershell
# Check task exists
Get-ScheduledTask -TaskName "Silver Tier Daily Summary"

# Check last run time
Get-ScheduledTask -TaskName "Silver Tier Daily Summary" | select LastRunTime, LastTaskResult
```

## Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| "Command not found" | Use full absolute path, not relative |
| "Python not found" | Use full path: `/usr/bin/python3` (Linux/Mac) |
| "Permission denied" | Run `chmod +x schedulers/daily_scheduler.sh` |
| "Not running" | Check crontab with `crontab -l` or Task Scheduler |
| "Wrong time" | Check system time, verify cron/Task Scheduler setting |

## Summary Content

```markdown
# Daily Summary - [Day], [Month] [Date], [Year]

## 📈 Metrics

| Metric | Count |
|--------|-------|
| **Total Completed** | 5 |
| Emails Sent | 2 |
| LinkedIn Posts | 1 |
| Approvals Processed | 2 |
| Plans Created | 0 |

## 📧 Emails (2)

- Invoice #123 → client@example.com
- Project Update → team@example.com

## 📱 LinkedIn Posts (1)

- Excited to announce new feature...

## ✅ Approvals Processed (2)

- send_email: executed
- post_linkedin: executed

## 💡 Insights

- High email volume today (2 emails)
- Successfully posted 1 LinkedIn post(s)
- Processed 2 approval(s) with HITL
```

## Files

```
schedulers/
├── daily_scheduler.sh              ← Linux/Mac script
├── daily_scheduler.ps1             ← Windows script
└── daily_briefing_generator.py      ← Python generator

Logs/
├── scheduler.log                   ← Execution log
└── daily_briefing_2026-02-14.md    ← Today's briefing
```

## Schedule Check

### Check Cron (Linux/Mac)
```bash
crontab -l
```

### Check Task (Windows)
- Open Task Scheduler
- Search for "Silver Tier Daily Summary"
- Check "Last Run Time"

## Next Scheduled Run

Tomorrow at 8:00 AM ✓

---

## Full Setup Guide

For detailed instructions, see: `DAILY_SCHEDULER_SETUP.md`

---

**Ready!** 🚀
Your daily summaries will run automatically at 8AM.
Check back tomorrow morning to see the first briefing!
