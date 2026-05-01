# Daily Briefing - Silver Tier Setup Guide

**Status:** ✅ Ready for Production
**Created:** 2026-02-14
**Tier:** Silver ⭐⭐

## Overview

The Daily Scheduler generates a daily briefing of completed tasks from `/Done` and saves to `/Logs/daily_briefing_[date].md` at 8AM each day.

**Components:**
- `schedulers/daily_briefing_generator.py` - Python script that generates briefing
- `schedulers/daily_scheduler.sh` - Linux/Mac cron wrapper
- `schedulers/daily_scheduler.ps1` - Windows PowerShell wrapper

## Quick Setup

### Linux/Mac (Cron)
```bash
# 1. Make script executable
chmod +x schedulers/daily_scheduler.sh

# 2. Open crontab editor
crontab -e

# 3. Add this line
0 8 * * * /full/path/to/daily_scheduler.sh

# 4. Verify
crontab -l
```

### Windows (Task Scheduler)
```powershell
# 1. Open PowerShell as Administrator
# Start → PowerShell → Right-click → Run as administrator

# 2. Run setup command (see Windows section below)

# Or manually create task in Task Scheduler GUI (see instructions below)
```

---

## Platform-Specific Setup

### Linux/Mac Setup (Cron)

#### Step 1: Make Script Executable
```bash
cd /path/to/Hackathon0Silver
chmod +x schedulers/daily_scheduler.sh
```

#### Step 2: Get Absolute Path
```bash
# Print absolute path to scheduler
pwd
# Output: /home/user/Desktop/Hackathon0Silver
# Full path: /home/user/Desktop/Hackathon0Silver/schedulers/daily_scheduler.sh
```

#### Step 3: Edit Crontab
```bash
crontab -e
```

This opens your default editor (vi, nano, etc).

#### Step 4: Add Cron Job
Add this line to run at 8AM every day:
```bash
0 8 * * * /full/path/to/daily_scheduler.sh
```

**Example:**
```bash
# Every day at 8AM
0 8 * * * /home/user/Desktop/Hackathon0Silver/schedulers/daily_scheduler.sh

# Or with email notification
0 8 * * * /home/user/Desktop/Hackathon0Silver/schedulers/daily_scheduler.sh 2>&1 | mail -s "Daily Summary" user@example.com
```

#### Step 5: Verify Cron Job
```bash
crontab -l
# Should show:
# 0 8 * * * /home/user/Desktop/Hackathon0Silver/schedulers/daily_scheduler.sh
```

#### Step 6: Check Logs
```bash
# View cron execution logs
tail -f Logs/scheduler.log

# View generated briefing
cat Logs/daily_briefing_$(date +%Y-%m-%d).md
```

#### Cron Syntax Reference
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * *

Examples:
0 8 * * *         Every day at 8:00 AM
0 8 * * 1-5       Weekdays (Mon-Fri) at 8:00 AM
0 8,14 * * *      Every day at 8:00 AM and 2:00 PM
0 8 1 * *         First day of month at 8:00 AM
*/15 * * * *      Every 15 minutes
```

#### Troubleshooting Cron (Linux/Mac)

**Issue: Cron job not running**
```bash
# Check if cron daemon is running
sudo systemctl status cron          # Linux
sudo launchctl list | grep cron     # Mac

# Check system log
sudo tail -f /var/log/syslog        # Linux
log stream --predicate 'process == "cron"'  # Mac

# Verify script permissions
ls -l schedulers/daily_scheduler.sh
# Should have 'x' (executable) permission
```

**Issue: Python not found**
```bash
# Use full path to Python in crontab
0 8 * * * /usr/bin/python3 /full/path/to/daily_briefing_generator.py >> /path/to/Logs/scheduler.log 2>&1
```

**Issue: Working directory issues**
```bash
# Add cd command before running script
0 8 * * * cd /full/path/to/project && /full/path/to/daily_scheduler.sh
```

---

### Windows Setup (Task Scheduler)

#### Option 1: PowerShell Script (Recommended)

**Step 1: Get Absolute Path**
```powershell
# Open PowerShell and navigate to project
cd C:\path\to\Hackathon0Silver
pwd
# Output: C:\Users\YourName\Desktop\Hackathon0Silver
```

**Step 2: Create Scheduled Task**
```powershell
# Run PowerShell as Administrator
# Windows Start → PowerShell → Right-click → Run as administrator

# Create task to run daily at 8AM
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"C:\path\to\schedulers\daily_scheduler.ps1`""
$Trigger = New-ScheduledTaskTrigger -Daily -At 08:00AM
$Settings = New-ScheduledTaskSettingsSet -RunOnlyIfNetworkAvailable
Register-ScheduledTask -TaskName "Silver Tier Daily Summary" -Action $Action -Trigger $Trigger -Settings $Settings -User $env:USERNAME -Force
```

**Step 3: Verify Task Created**
```powershell
# List scheduled tasks
Get-ScheduledTask -TaskName "Silver Tier Daily Summary"

# Or check Task Scheduler GUI
# Control Panel → Administrative Tools → Task Scheduler
```

**Step 4: Test Run**
```powershell
# Run task manually
Start-ScheduledTask -TaskName "Silver Tier Daily Summary"

# Check result
Get-Content Logs\scheduler.log -Tail 20
```

#### Option 2: Task Scheduler GUI

**Step 1: Open Task Scheduler**
- Windows Start → Type "Task Scheduler" → Press Enter
- Or: Control Panel → Administrative Tools → Task Scheduler

**Step 2: Create Basic Task**
1. Right-click "Task Scheduler Library" → Create Basic Task
2. Name: `Silver Tier Daily Summary`
3. Description: `Generate daily briefing of completed tasks`
4. Click Next

**Step 3: Set Trigger**
1. Select "Daily"
2. Set time: 08:00
3. Recurrence: Every 1 day
4. Click Next

**Step 4: Set Action**
1. Select "Start a program"
2. Program: `powershell.exe`
3. Arguments: `-ExecutionPolicy Bypass -File "C:\full\path\to\schedulers\daily_scheduler.ps1"`
4. Start in: `C:\full\path\to\Hackathon0Silver`
5. Click Next

**Step 5: Complete**
1. Review briefing
2. Check "Open the Properties dialog when I click Finish"
3. Click Finish

**Step 6: Configure Advanced Options**
In Properties dialog:
- General tab:
  - User: Your account
  - Check "Run whether user is logged in or not"
- Triggers tab:
  - Edit to change time if needed
- Settings tab:
  - Check "If the task fails, restart every: 5 minutes"
  - Retry count: 3

**Step 7: Test Task**
1. Right-click task → Run
2. Check Task Scheduler for "Last Run Result"
3. Should show 0 (success)

#### Verify Task Execution (Windows)

**Check Logs**
```powershell
# View scheduler log
Get-Content Logs\scheduler.log -Tail 20

# View daily briefing
$Today = Get-Date -Format "yyyy-MM-dd"
Get-Content Logs\daily_briefing_$Today.md
```

**Check Task History**
1. Open Task Scheduler
2. Select task
3. View "Last Run Time" and "Last Run Result"
4. Right-click → View All Properties → History tab

**Troubleshooting (Windows)**

**Issue: Task not running**
```powershell
# Check if task exists
Get-ScheduledTask -TaskName "Silver Tier Daily Summary"

# Get task status
Get-ScheduledTask -TaskName "Silver Tier Daily Summary" | fl

# Enable task if disabled
Enable-ScheduledTask -TaskName "Silver Tier Daily Summary"
```

**Issue: Python not found**
```powershell
# Find Python path
where python
# Or search manually: C:\Python311\python.exe

# Update task with correct Python path in script
```

**Issue: File access denied**
```powershell
# Ensure script path uses correct slashes (backslash on Windows)
# Correct: "C:\path\to\schedulers\daily_scheduler.ps1"
# Wrong: "C:/path/to/schedulers/daily_scheduler.ps1"
```

**Issue: ExecutionPolicy error**
```powershell
# Check current policy
Get-ExecutionPolicy

# Set to allow script execution (for current user)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use bypass in task (already in command)
```

---

## Manual Testing

### Test 1: Run Generator Directly
```bash
# Linux/Mac
python3 schedulers/daily_briefing_generator.py

# Windows (PowerShell)
python schedulers\daily_briefing_generator.py
```

**Expected Output:**
```
========================================================================
DAILY SUMMARY GENERATOR
========================================================================
[INFO] ✓ Found 5 completed tasks
[INFO] 📊 Generating daily briefing...
[INFO] ✓ Summary saved: Logs/daily_briefing_2026-02-14.md
========================================================================
```

### Test 2: Run Scheduler Script
```bash
# Linux/Mac
bash schedulers/daily_scheduler.sh

# Windows (PowerShell as Administrator)
powershell -ExecutionPolicy Bypass -File "schedulers\daily_scheduler.ps1"
```

**Expected Output:**
```
========================================
  Daily Summary Generator - Scheduler
========================================

[2026-02-14 10:30:45] Daily scheduler started
✓ Python 3 found
✓ Generator script found
✓ Working directory: /path/to/project

Running daily briefing generator...

========================================
  Generated Summary Preview
========================================

# Daily Summary - Wednesday, February 14, 2026
...
```

### Test 3: Verify Output File
```bash
# Linux/Mac
cat Logs/daily_briefing_$(date +%Y-%m-%d).md

# Windows (PowerShell)
$Today = Get-Date -Format "yyyy-MM-dd"
Get-Content Logs\daily_briefing_$Today.md
```

**Expected Output:**
```markdown
---
type: daily_briefing
date: 2026-02-14
generated: 2026-02-14T10:30:45.123456
total_completed: 5
---

# Daily Summary - Wednesday, February 14, 2026

**Generated:** 10:30:45

---

## 📈 Metrics

| Metric | Count |
|--------|-------|
| **Total Completed** | 5 |
| Emails Sent | 2 |
| LinkedIn Posts | 1 |
| Approvals Processed | 2 |
...
```

---

## Generated Summary Format

### Location
```
/Logs/daily_briefing_YYYY-MM-DD.md
```

### Content Structure
```markdown
---
type: daily_briefing
date: 2026-02-14
generated: 2026-02-14T10:30:45.123456
total_completed: 5
---

# Daily Summary - [Day], [Month] [Date], [Year]

**Generated:** HH:MM:SS

---

## 📈 Metrics

| Metric | Count |
|--------|-------|
| **Total Completed** | 5 |
| Emails Sent | 2 |
| LinkedIn Posts | 1 |
| Approvals Processed | 2 |
| Plans Created | 0 |
| Other | 0 |

---

## 📧 Emails (2)

- **Invoice #123** → client@example.com
- **Project Update** → team@example.com

---

## 📱 LinkedIn Posts (1)

- Excited to announce our new feature...

---

## ✅ Approvals Processed (2)

- send_email: executed
- post_linkedin: executed

---

## 📋 Plans Created (0)

- No plans created today

---

## 💡 Insights

- 📧 High email volume today (2 emails)
- 📱 Successfully posted 1 LinkedIn post(s)
- ✅ Processed 2 approval(s) with HITL

---

**Summary Generated by Daily Scheduler**
*Next briefing: 2026-02-15 at 08:00 AM*
```

---

## Logs and Monitoring

### Scheduler Log
**Location:** `Logs/scheduler.log`

**Contains:**
- Execution start/end times
- Generator output
- Errors and warnings
- Summary file locations

**View Log:**
```bash
# Linux/Mac
tail -f Logs/scheduler.log

# Windows
Get-Content Logs\scheduler.log -Wait -Tail 20
```

### Generated Summaries
**Location:** `Logs/daily_briefing_YYYY-MM-DD.md`

**List all summaries:**
```bash
# Linux/Mac
ls -la Logs/daily_briefing_*.md

# Windows
dir Logs\daily_briefing_*.md
```

---

## Configuration & Customization

### Change Scheduling Time

**Linux/Mac (Cron):**
```bash
# Edit crontab
crontab -e

# Change time (example: 10AM instead of 8AM)
0 10 * * * /full/path/to/daily_scheduler.sh
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Select "Silver Tier Daily Summary"
3. Right-click → Properties
4. Triggers tab → Edit → Change time

### Change Summary Content

Edit `schedulers/daily_briefing_generator.py`:
- `categorize_tasks()` - Add new categories
- `generate_briefing()` - Modify briefing format
- `scan_completed_tasks()` - Filter tasks differently

### Add Email Notifications

**Linux/Mac:**
```bash
# Send briefing via email
0 8 * * * /full/path/to/daily_scheduler.sh 2>&1 | mail -s "Daily Summary" user@example.com
```

**Windows:**
```powershell
# In Task Scheduler, add additional action to send email
# Or modify script to use Send-MailMessage
```

---

## Security Considerations

✅ **Scheduled Task Security:**
- Script runs with user permissions only
- No elevated privileges required (unless explicitly set)
- Logs contain no sensitive data
- Output files are markdown (plain text)

✅ **Recommendations:**
- Run with least privilege account
- Restrict file permissions on scripts
- Review scheduled tasks regularly
- Monitor log files for errors

---

## Troubleshooting

### General

| Issue | Solution |
|-------|----------|
| No briefing generated | Check /Done folder has files, check Logs/scheduler.log for errors |
| Wrong time | Verify cron/Task Scheduler time setting, check system time |
| Python errors | Verify Python 3 installed, check pythonpath, install pyyaml |
| Permission denied | Check file execute permissions (Linux/Mac), run as Administrator (Windows) |
| Path not found | Use absolute paths, not relative paths in cron/scheduler |

### Linux/Mac Cron

```bash
# Check if cron is running
sudo systemctl status cron

# View cron logs
grep CRON /var/log/syslog | tail -20

# Test script directly
bash -x /path/to/daily_scheduler.sh

# Enable cron debugging
SHELL=/bin/bash
*/1 * * * * /path/to/daily_scheduler.sh >> /tmp/cron_debug.log 2>&1
```

### Windows Task Scheduler

```powershell
# View task details
Get-ScheduledTaskInfo -TaskName "Silver Tier Daily Summary"

# Check last run result
(Get-ScheduledTask -TaskName "Silver Tier Daily Summary").LastTaskResult

# Run task with verbose output
Start-ScheduledTask -TaskName "Silver Tier Daily Summary"
Get-ScheduledTask -TaskName "Silver Tier Daily Summary" | select LastRunTime, LastTaskResult
```

---

## Next Steps

1. ✅ Choose platform (Linux/Mac or Windows)
2. ✅ Follow setup instructions
3. ✅ Test manually: `python3 schedulers/daily_briefing_generator.py`
4. ✅ Test scheduler: Run daily_scheduler.sh or daily_scheduler.ps1
5. ✅ Verify in Task Scheduler / crontab
6. ✅ Check generated briefing at 8AM tomorrow
7. ✅ Monitor Logs/scheduler.log

---

## Files Reference

```
schedulers/
├── daily_scheduler.sh              # Linux/Mac cron wrapper
├── daily_scheduler.ps1             # Windows PowerShell wrapper
└── daily_briefing_generator.py      # Python briefing generator

Logs/
├── scheduler.log                   # Scheduler execution log
└── daily_briefing_YYYY-MM-DD.md    # Generated daily summaries
```

---

**Status:** ✅ Ready for Production
**Created:** 2026-02-14
**Tier:** Silver ⭐⭐
**Next Summary:** Tomorrow at 8:00 AM
