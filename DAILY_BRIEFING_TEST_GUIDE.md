# Daily Briefing - Complete Testing Guide

**Test Time:** ~10 minutes
**Required:** Python 3, project root directory

---

## Test 1: Run Generator Directly (2 minutes)

### Step 1.1: Create Test Files in /Done

First, create some test completed tasks so the generator has something to count:

```bash
# Linux/Mac
mkdir -p Done

cat > Done/test_email_sent.md << 'EOF'
---
type: email_approval
action: send_email
to: client@example.com
subject: Invoice #123
status: executed
---

# Email Sent
EOF

cat > Done/test_linkedin_post.md << 'EOF'
---
type: linkedin_approval
action: post_linkedin
content: "Excited to announce our new feature!"
status: executed
---

# LinkedIn Post
EOF

cat > Done/test_approval.md << 'EOF'
---
type: email_approval
action: send_email
status: executed
---

# Approval
EOF
```

Or manually create these files in `Done/` folder using your file manager.

### Step 1.2: Run the Generator

```bash
# Linux/Mac
python3 schedulers/daily_briefing_generator.py

# Windows (PowerShell)
python schedulers\daily_briefing_generator.py
```

**Expected Output:**

```
======================================================================
DAILY BRIEFING GENERATOR
======================================================================
[INFO] ✓ Found 3 completed tasks
[INFO] 📊 Generating daily briefing...
[INFO] ✓ Briefing saved: Logs/daily_briefing_2026-02-14.md
======================================================================
```

### Step 1.3: Verify Output File Created

```bash
# Linux/Mac
ls -la Logs/daily_briefing_*.md
cat Logs/daily_briefing_$(date +%Y-%m-%d).md

# Windows (PowerShell)
dir Logs\daily_briefing_*.md
$Today = Get-Date -Format "yyyy-MM-dd"
Get-Content Logs\daily_briefing_$Today.md
```

**Expected Output:**

```markdown
---
type: daily_briefing
date: 2026-02-14
generated: 2026-02-14T10:30:45.123456
total_completed: 3
---

# Daily Briefing - Friday, February 14, 2026

**Generated:** 10:30:45

---

## 📈 Metrics

| Metric | Count |
|--------|-------|
| **Total Completed** | 3 |
| Emails Sent | 1 |
| LinkedIn Posts | 1 |
| Approvals Processed | 1 |
| Plans Created | 0 |
| Other | 0 |

...
```

✅ **Test 1 Passed** if:
- Generator runs without errors
- Output file created at `Logs/daily_briefing_YYYY-MM-DD.md`
- File contains metrics and briefing content

---

## Test 2: Run Full Scheduler Script (2 minutes)

### Step 2.1: Run Scheduler Wrapper

```bash
# Linux/Mac
bash schedulers/daily_scheduler.sh

# Windows (PowerShell as Administrator)
powershell -ExecutionPolicy Bypass -File "schedulers\daily_scheduler.ps1"
```

**Expected Output:**

```
========================================
  Daily Briefing Generator - Scheduler
========================================

[2026-02-14 10:30:45] Daily scheduler started
✓ Python 3 found
✓ Generator script found
✓ Working directory: /full/path/to/project

Running daily briefing generator...

======================================================================
DAILY BRIEFING GENERATOR
======================================================================
[INFO] ✓ Found 3 completed tasks
[INFO] 📊 Generating daily briefing...
[INFO] ✓ Briefing saved: Logs/daily_briefing_2026-02-14.md
======================================================================

========================================
  Generated Briefing Preview
========================================

# Daily Briefing - Friday, February 14, 2026

**Generated:** 10:30:45

## 📈 Metrics

| Metric | Count |
|--------|-------|
| **Total Completed** | 3 |
| Emails Sent | 1 |
...

[... briefing continues ...]

========================================
  Next scheduled run: Tomorrow at 8:00 AM
========================================
```

### Step 2.2: Check Logs

```bash
# Linux/Mac
tail -20 Logs/scheduler.log

# Windows
Get-Content Logs\scheduler.log -Tail 20
```

**Expected Output:**

```
[2026-02-14 10:30:45] Daily scheduler started
[2026-02-14 10:30:45] Python 3 found
[2026-02-14 10:30:45] Generator script found
[2026-02-14 10:30:45] Working directory: /path/to/project
[2026-02-14 10:30:45] Running daily briefing generator...
[2026-02-14 10:30:46] ✓ Daily briefing generated successfully
[2026-02-14 10:30:46] ✓ Briefing file: /path/to/Logs/daily_briefing_2026-02-14.md
[2026-02-14 10:30:46] Daily scheduler completed successfully
```

✅ **Test 2 Passed** if:
- Scheduler runs without errors
- Briefing file generated
- Log entries appear in `Logs/scheduler.log`
- Output shows success messages

---

## Test 3: Verify Briefing Content (1 minute)

### Step 3.1: Check Metrics

```bash
# Linux/Mac
cat Logs/daily_briefing_$(date +%Y-%m-%d).md | head -40

# Windows
$Today = Get-Date -Format "yyyy-MM-dd"
(Get-Content Logs\daily_briefing_$Today.md | Select-Object -First 40)
```

**Verify Contains:**
- ✅ `---` YAML frontmatter
- ✅ `type: daily_briefing`
- ✅ `date: YYYY-MM-DD`
- ✅ Metrics table
- ✅ Email count
- ✅ LinkedIn posts count
- ✅ Approvals count
- ✅ Section headings (📧, 📱, ✅, 📋, 💡)

### Step 3.2: View Full Briefing

```bash
# Linux/Mac
cat Logs/daily_briefing_$(date +%Y-%m-%d).md

# Windows
$Today = Get-Date -Format "yyyy-MM-dd"
Get-Content Logs\daily_briefing_$Today.md
```

✅ **Test 3 Passed** if:
- All expected sections present
- Metrics are accurate
- No errors in YAML
- Briefing is readable

---

## Test 4: Test Scheduling Setup (2 minutes)

### For Linux/Mac (Cron)

#### Step 4.1: Add Cron Job

```bash
# Get absolute path
pwd
# Output: /Users/yourname/Desktop/Hackathon0Silver

# Open crontab
crontab -e

# Add this line (change path to your absolute path):
# For immediate test, run every minute:
* * * * * /Users/yourname/Desktop/Hackathon0Silver/schedulers/daily_scheduler.sh

# For 8AM production cron:
# 0 8 * * * /Users/yourname/Desktop/Hackathon0Silicon/schedulers/daily_scheduler.sh
```

#### Step 4.2: Verify Cron Job Added

```bash
crontab -l

# Should show:
# * * * * * /Users/yourname/Desktop/Hackathon0Silver/schedulers/daily_scheduler.sh
```

#### Step 4.3: Wait for Execution

If you used `* * * * *` (every minute), wait 1-2 minutes for cron to execute.

```bash
# Watch logs
tail -f Logs/scheduler.log

# Or check file
ls -la Logs/daily_briefing_*.md
```

✅ **Test 4 Passed** if:
- Cron job appears in `crontab -l`
- Log shows execution after 1-2 minutes
- New briefing file created

#### Step 4.4: Return to 8AM Schedule

```bash
crontab -e

# Change back to:
0 8 * * * /Users/yourname/Desktop/Hackathon0Silver/schedulers/daily_scheduler.sh
```

### For Windows (Task Scheduler)

#### Step 4.1: Create Test Task (Runs Every Minute)

```powershell
# PowerShell as Administrator

# Replace path with your actual path
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"C:\Users\YourName\Desktop\Hackathon0Silver\schedulers\daily_scheduler.ps1`""
$Trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Hours 1) -Once -At (Get-Date)
Register-ScheduledTask -TaskName "Test Daily Briefing" -Action $Action -Trigger $Trigger -User $env:USERNAME -Force
```

#### Step 4.2: Wait for Test Execution

Wait 1-2 minutes and check if task ran:

```powershell
# Check task history
Get-ScheduledTask -TaskName "Test Daily Briefing" | fl

# Or check logs
Get-Content Logs\scheduler.log -Tail 10
```

#### Step 4.3: Delete Test Task

```powershell
Unregister-ScheduledTask -TaskName "Test Daily Briefing" -Confirm:$false
```

#### Step 4.4: Create Production Task (8AM Daily)

```powershell
# PowerShell as Administrator

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"C:\Users\YourName\Desktop\Hackathon0Silver\schedulers\daily_scheduler.ps1`""
$Trigger = New-ScheduledTaskTrigger -Daily -At 08:00AM
Register-ScheduledTask -TaskName "Silver Tier Daily Briefing" -Action $Action -Trigger $Trigger -User $env:USERNAME -Force
```

#### Step 4.5: Verify Task Created

```powershell
Get-ScheduledTask -TaskName "Silver Tier Daily Briefing"

# Should show task details
```

✅ **Test 4 Passed** if:
- Task created successfully
- Task ran as expected (check logs)
- No errors in execution
- File generated at expected time

---

## Complete Test Checklist

### Minimal Test (5 minutes)
- [ ] Create test files in /Done/
- [ ] Run: `python3 schedulers/daily_briefing_generator.py`
- [ ] Check: `Logs/daily_briefing_YYYY-MM-DD.md` exists
- [ ] Verify: File contains metrics and briefing content

### Full Test (10 minutes)
- [ ] Create test files in /Done/
- [ ] Run generator directly
- [ ] Run scheduler script (sh or ps1)
- [ ] Check briefing file created
- [ ] Check scheduler.log shows success
- [ ] Setup cron/Task Scheduler
- [ ] Wait for scheduled execution
- [ ] Verify execution completed

### Production Verification
- [ ] Cron job added: `crontab -l` (Linux/Mac)
- [ ] Task created in Task Scheduler (Windows)
- [ ] Logs show recent execution
- [ ] Briefing file generated today
- [ ] Content is accurate

---

## Troubleshooting During Testing

### Issue: "Python not found"

```bash
# Linux/Mac - Check Python installed
python3 --version

# Windows - Check Python installed
python --version

# If not installed, install Python 3 first
```

### Issue: "Generator script not found"

```bash
# Verify file exists
ls -la schedulers/daily_briefing_generator.py    # Linux/Mac
dir schedulers\daily_briefing_generator.py       # Windows

# Verify you're in project root
pwd     # Linux/Mac
cd      # Windows
```

### Issue: "Permission denied" (Linux/Mac)

```bash
# Make script executable
chmod +x schedulers/daily_scheduler.sh

# Try again
bash schedulers/daily_scheduler.sh
```

### Issue: "No briefing file created"

```bash
# Check /Done/ has test files
ls -la Done/          # Linux/Mac
dir Done\             # Windows

# Check /Logs/ folder exists
ls -la Logs/          # Linux/Mac
dir Logs\             # Windows

# Run generator with verbose output
python3 schedulers/daily_briefing_generator.py
```

### Issue: "Task won't run on schedule" (Windows)

```powershell
# Check if task exists
Get-ScheduledTask -TaskName "Silver Tier Daily Briefing"

# Check if task is enabled
Get-ScheduledTask -TaskName "Silver Tier Daily Briefing" | fl

# Check last run result
(Get-ScheduledTask -TaskName "Silver Tier Daily Briefing").LastTaskResult

# Run manually to test
Start-ScheduledTask -TaskName "Silver Tier Daily Briefing"

# Wait and check result
Get-Content Logs\scheduler.log -Tail 5
```

---

## Expected Test Results

### Test 1: Direct Generator Run
```
✅ Generator runs successfully
✅ Briefing file created: Logs/daily_briefing_YYYY-MM-DD.md
✅ File contains YAML frontmatter
✅ File contains metrics table
✅ File contains section headers
```

### Test 2: Scheduler Script
```
✅ Scheduler script runs without errors
✅ Generator called successfully
✅ Briefing file created
✅ scheduler.log updated with execution details
✅ Output shows success messages
```

### Test 3: Briefing Content
```
✅ Contains: type: daily_briefing
✅ Contains: date: YYYY-MM-DD
✅ Contains: Metrics section
✅ Contains: Emails count
✅ Contains: LinkedIn Posts count
✅ Contains: Approvals count
✅ Contains: Insights section
```

### Test 4: Scheduled Execution
```
✅ Cron job added (Linux/Mac) or Task created (Windows)
✅ Automatic execution happens at configured time
✅ Briefing file generated automatically
✅ Log entries appear for scheduled run
✅ No errors in execution
```

---

## After Testing

### If All Tests Pass ✅

1. **Clean up test cron** (if you created one every minute)
   ```bash
   crontab -e
   # Remove test line
   # Keep production line: 0 8 * * * /path/to/daily_scheduler.sh
   ```

2. **Clean up test task** (if you created one on Windows)
   ```powershell
   Unregister-ScheduledTask -TaskName "Test Daily Briefing" -Confirm:$false
   ```

3. **Verify production schedule is set**
   ```bash
   # Linux/Mac
   crontab -l

   # Windows
   Get-ScheduledTask -TaskName "Silver Tier Daily Briefing"
   ```

4. **Monitor tomorrow**
   - Check at 8:00 AM
   - Verify briefing file created
   - Check `Logs/scheduler.log`

### If Tests Fail ❌

Check the troubleshooting section above for your specific error, then:

1. Fix the issue
2. Re-run the specific test
3. Verify it passes
4. Continue testing

---

## Daily Monitoring (After Setup)

### Check Briefing Generated Today

```bash
# Linux/Mac
cat Logs/daily_briefing_$(date +%Y-%m-%d).md

# Windows
$Today = Get-Date -Format "yyyy-MM-dd"
Get-Content Logs\daily_briefing_$Today.md
```

### View Scheduler Logs

```bash
# Linux/Mac
tail -20 Logs/scheduler.log

# Windows
Get-Content Logs\scheduler.log -Tail 20
```

### List All Generated Briefings

```bash
# Linux/Mac
ls -la Logs/daily_briefing_*.md

# Windows
dir Logs\daily_briefing_*.md
```

---

## Summary

**Time to test:** ~10 minutes
**What you'll verify:**
- ✅ Generator works
- ✅ Scheduler wrapper works
- ✅ Briefing content is correct
- ✅ Scheduled execution works
- ✅ Logs are created
- ✅ Ready for production use

**After testing:** Briefings will generate automatically at 8:00 AM each day

---

**Test Status:** ✅ Ready to execute
**Next Step:** Run Test 1 above

