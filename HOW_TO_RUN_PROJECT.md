# How to Run Hackathon0Silver - Complete Step-by-Step Guide

**Status:** ✅ Ready to Run
**Last Updated:** 2026-02-14
**Tier:** Silver ⭐⭐

---

## 🔗 Cross-Reference

| Need | See |
|------|-----|
| **Quick commands for daily use** | → `QUICK_RUN.md` ⚡ |
| **Detailed step-by-step setup** | → This file 📖 |
| **Gmail credentials setup** | → `GMAIL_WATCHER_SETUP.md` |
| **Browser authentication** | → `BROWSER_WATCHERS_SETUP.md` |
| **Full project history & context** | → `history/README.md` |

---

## 🚀 Quick Start (5 Minutes)

If you just want to see it working:

```bash
# 1. Check status
pm2 list

# 2. See watcher logs
pm2 logs whatsapp_watcher

# 3. Check /Needs_Action folder for saved items
ls -la Needs_Action/
```

---

## 📋 Complete Setup & Run Guide

### Phase 1: Prerequisites (10 minutes)

#### 1.1 Check Python Installation
```bash
python --version
# Expected: Python 3.10+ (tested on 3.14)
```

#### 1.2 Check Node.js Installation (for Email MCP)
```bash
node --version
npm --version
```

#### 1.3 Check PM2 Installation
```bash
pm2 --version
# If not installed: npm install -g pm2
```

#### 1.4 Verify Project Structure
```bash
# You should have these folders:
ls -la Needs_Action Pending_Approval Approved Done Plans Logs session watchers skills tools schedulers mcp_servers
```

**All folders exist?** ✅ Continue to Phase 2

**Missing folders?** Create them:
```bash
mkdir -p Needs_Action Pending_Approval Approved Done Plans Logs session/{whatsapp,linkedin} watchers skills tools schedulers mcp_servers
```

---

### Phase 2: Gmail Watcher Setup (15 minutes)

#### 2.1 Get Google Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: `Hackathon0Silver`
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop app)
5. Download `credentials.json`
6. Place in project root: `C:\path\to\Hackathon0Silver\credentials.json`

#### 2.1a Add Test User (Important!)
7. Go back to OAuth consent screen
8. In the left sidebar menu, click **"Audience"** (NOT Overview)
   ```
   Left sidebar menu:
   ├── Overview
   ├── Branding
   ├── Audience  ← CLICK HERE
   ├── Clients
   ├── Data Access
   ├── Verification Center
   └── Settings
   ```
9. Click "+ Add Users" button
10. Enter your email: `14loansllc@gmail.com` (or your actual Gmail)
11. Click "Add"

**Why?** Google requires test users to be added before unverified apps can access Gmail API. This prevents the 403 access_denied error.

#### 2.2 Install Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### 2.3 Test Gmail Watcher (First Run Only)
```bash
# This will open a browser for OAuth2 authentication
python watchers/gmail_watcher.py

# Expected output:
# [OK] Gmail authentication successful
# [OK] Found 0 unread important emails with keywords
```

**Success?** ✅ Continue to Phase 3

**Failed?** See troubleshooting below

---

### Phase 3: WhatsApp Watcher Setup (10 minutes)

#### 3.1 Install Playwright (if not already installed)
```bash
pip install playwright
playwright install chromium
```

#### 3.2 Run WhatsApp Watcher (First Time)
```bash
# This will open Chromium browser showing WhatsApp Web
python watchers/whatsapp_watcher.py

# Expected:
# 1. Browser window opens
# 2. Shows WhatsApp Web QR code
# 3. Scan QR code with your phone
# 4. Wait for: [OK] WhatsApp Web authenticated
# 5. Press Ctrl+C to stop (or let it run)
```

**Success?** ✅ Session saved, move to Phase 4

**Failed?** Check: Is browser window opening? If not, see troubleshooting

---

### Phase 4: LinkedIn Watcher Setup (10 minutes)

#### 4.1 Run LinkedIn Watcher (First Time)
```bash
# This will open Chromium browser for LinkedIn login
python watchers/linkedin_watcher.py

# Expected:
# 1. Browser window opens (LinkedIn.com)
# 2. Shows login page (if not logged in)
# 3. Enter email and password
# 4. Wait for: [OK] LinkedIn authenticated
# 5. Press Ctrl+C to stop
```

**Success?** ✅ Session saved, move to Phase 5

**Failed?** Make sure you're logged into LinkedIn

---

### Phase 5: Start All Watchers with PM2 (5 minutes)

#### 5.1 Start Each Watcher
```bash
# Gmail Watcher
pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python

# WhatsApp Watcher
pm2 start watchers/whatsapp_watcher.py --name whatsapp_watcher --interpreter python

# LinkedIn Watcher
pm2 start watchers/linkedin_watcher.py --name linkedin_watcher --interpreter python
```

#### 5.2 Verify All Running
```bash
pm2 list

# Expected output:
# ┌────┬──────────────────┬─────────┐
# │ id │ name             │ status  │
# ├────┼──────────────────┼─────────┤
# │ 0  │ gmail_watcher    │ online  │
# │ 1  │ whatsapp_watcher │ online  │
# │ 2  │ linkedin_watcher │ online  │
# └────┴──────────────────┴─────────┘
```

All online? ✅ Continue to Phase 6

---

### Phase 6: Setup Scheduler (Daily 8AM Briefing) (10 minutes)

#### 6.1 Choose Your OS

##### For Linux/Mac (Cron):
```bash
# Make script executable
chmod +x schedulers/daily_scheduler.sh

# Get absolute path
pwd
# Example output: /Users/john/Desktop/Hackathon0Silver

# Edit crontab
crontab -e

# Add this line (replace with your path):
0 8 * * * /Users/john/Desktop/Hackathon0Silver/schedulers/daily_scheduler.sh

# Verify
crontab -l
# Should show your new line
```

##### For Windows (Task Scheduler):
```powershell
# Open PowerShell as Administrator
# Run this command (replace path with yours):

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"C:\Users\YourName\Desktop\Hackathon0Silver\schedulers\daily_scheduler.ps1`""
$Trigger = New-ScheduledTaskTrigger -Daily -At 08:00AM
Register-ScheduledTask -TaskName "Silver Tier Daily Briefing" -Action $Action -Trigger $Trigger -User $env:USERNAME -Force

# Verify
Get-ScheduledTask -TaskName "Silver Tier Daily Briefing"
```

#### 6.2 Test Scheduler (Manual Run)
```bash
# Linux/Mac
bash schedulers/daily_scheduler.sh

# Windows (PowerShell as Admin)
powershell -ExecutionPolicy Bypass -File "schedulers\daily_scheduler.ps1"

# Expected output:
# ======================================================================
# DAILY BRIEFING GENERATOR
# ======================================================================
# [INFO] ✓ Found X completed tasks
# [INFO] 📊 Generating daily briefing...
# [INFO] ✓ Briefing saved: Logs/daily_briefing_2026-02-14.md
# ======================================================================
```

Success? ✅ Scheduler configured

---

### Phase 7: Email MCP Server Setup (Optional, 5 minutes)

#### 7.1 Install Node Dependencies
```bash
cd mcp_servers/email-mcp
npm install
cd ../..
```

#### 7.2 Verify MCP Configuration
```bash
# Check mcp.json exists in project root
ls -la mcp.json

# Should output something like:
# -rw-r--r-- mcp.json
```

#### 7.3 Start MCP Server (Optional)
```bash
# Automatically starts with auto-start configuration
# Or start manually:
node mcp_servers/email-mcp/index.js

# Expected output:
# MCP Server starting on port 3000...
```

---

## 🎯 Complete System Running

At this point, you have:

✅ **Gmail Watcher** - Monitoring emails every 120 seconds
✅ **WhatsApp Watcher** - Monitoring messages every 30 seconds
✅ **LinkedIn Watcher** - Monitoring notifications every 60 seconds
✅ **Daily Briefing** - Scheduled for 8AM daily
✅ **PM2** - Managing all processes
✅ **Email MCP** - Ready for email integration

---

## 🧪 Test the System

### Test 1: Send Test Messages

#### Send Email (Gmail)
```bash
# Send yourself an email with subject containing keyword:
# Subject: "URGENT: invoice #123 - Test"
#
# Wait 120 seconds, then check:
ls -la Needs_Action/
# Should have: Needs_Action/email_*.md
```

#### Send WhatsApp Message
```bash
# Open WhatsApp on phone
# Send message to monitored account:
# "URGENT invoice #456 test"
#
# Wait 30 seconds, then check:
ls -la Needs_Action/
# Should have new file with WhatsApp message
```

#### Send LinkedIn Message
```bash
# Send DM on LinkedIn with keyword:
# "sales opportunity for project X"
#
# Wait 60 seconds, then check:
ls -la Needs_Action/
# Should have new file with LinkedIn message
```

### Test 2: Check Logs

```bash
# View live logs for each watcher
pm2 logs gmail_watcher
pm2 logs whatsapp_watcher
pm2 logs linkedin_watcher

# View saved tasks
cat Needs_Action/*.md

# View today's briefing
cat Logs/daily_briefing_$(date +%Y-%m-%d).md  # Linux/Mac
# or
cat "Logs\daily_briefing_2026-02-14.md"       # Windows
```

---

## 📊 Monitoring & Management

### Monitor All Processes
```bash
# See all running processes
pm2 list

# See memory/CPU usage
pm2 monit

# See live logs
pm2 logs

# See logs for specific watcher
pm2 logs gmail_watcher -f
```

### Stop/Start Processes
```bash
# Stop all
pm2 stop all

# Start all
pm2 start all

# Restart specific
pm2 restart gmail_watcher

# Delete process
pm2 delete gmail_watcher

# Save PM2 configuration
pm2 save
```

### View Logs
```bash
# Tail logs (last 20 lines)
pm2 logs gmail_watcher --lines 20

# Follow logs in real-time
pm2 logs gmail_watcher -f

# View watcher-specific log files
cat watchers/logs/gmail_watcher.log
cat watchers/logs/whatsapp_watcher.log
cat watchers/logs/linkedin_watcher.log

# View scheduler logs
cat Logs/scheduler.log
```

---

## 🔄 Daily Workflow (After Setup)

### Every Morning (8AM)
```bash
# Automatic: Daily briefing generated and saved to:
Logs/daily_briefing_$(date +%Y-%m-%d).md

# View today's briefing:
cat Logs/daily_briefing_$(date +%Y-%m-%d).md  # Linux/Mac
```

### When Messages Arrive
```bash
# Watchers automatically save to:
Needs_Action/email_*.md
Needs_Action/whatsapp_*.md
Needs_Action/linkedin_*.md

# View pending items:
ls -la Needs_Action/
cat Needs_Action/email_*.md
```

### Review & Approve
```bash
# Items move to /Pending_Approval for human review

# To approve:
mv Pending_Approval/email_*.md Approved/

# To reject:
mv Pending_Approval/email_*.md Rejected/

# HITL Handler detects and executes approved actions
```

---

## 🛠️ Common Commands Reference

### Quick Status Check
```bash
pm2 list
```

### View Watchers Logs
```bash
pm2 logs
```

### Restart All
```bash
pm2 restart all
```

### Stop All
```bash
pm2 stop all
```

### Start All
```bash
pm2 start all
```

### Check Saved Items
```bash
ls -la Needs_Action/
ls -la Pending_Approval/
ls -la Approved/
ls -la Done/
```

### View Daily Briefing
```bash
cat Logs/daily_briefing_$(date +%Y-%m-%d).md    # Linux/Mac
dir Logs\daily_briefing_*.md                     # Windows list
type "Logs\daily_briefing_2026-02-14.md"        # Windows view
```

---

## ❌ Troubleshooting

### Issue: "Gmail watcher failed to start"
```bash
# Solution 1: Check if credentials.json exists
ls -la credentials.json

# Solution 2: Check Python path
which python
python --version

# Solution 3: Check if libraries installed
python -c "from googleapiclient import discovery; print('OK')"

# Solution 4: Check logs
pm2 logs gmail_watcher
```

### Issue: "WhatsApp browser window not appearing"
```bash
# Solution 1: Install Playwright
pip install playwright
playwright install chromium

# Solution 2: Check if process is running but hidden
tasklist | findstr chromium  # Windows
ps aux | grep chromium       # Linux/Mac

# Solution 3: Run with verbose output
python -u watchers/whatsapp_watcher.py
```

### Issue: "LinkedIn login timing out"
```bash
# Solution 1: Increase timeout in script
# Edit linkedin_watcher.py line 137:
# Change: timeout=120000  → timeout=300000  (5 minutes)

# Solution 2: Delete session and re-login
rm -rf session/linkedin
python watchers/linkedin_watcher.py  # Re-authenticate

# Solution 3: Check if LinkedIn blocked login
# Check browser window for 2FA or other prompts
```

### Issue: "PM2 processes not starting"
```bash
# Solution: Check PM2 status
pm2 status
pm2 list

# Restart PM2 daemon
pm2 kill
pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python

# Check PM2 logs
pm2 logs
```

### Issue: "Scheduled task not running"
```bash
# For Linux/Mac (Cron):
crontab -l  # Verify job exists
grep CRON /var/log/syslog | tail -20  # Check cron logs

# For Windows:
Get-ScheduledTask -TaskName "Silver Tier Daily Briefing"  # Verify exists
Get-ScheduledTask -TaskName "Silver Tier Daily Briefing" | fl  # Check status

# Run manually to test:
bash schedulers/daily_scheduler.sh  # Linux/Mac
powershell -ExecutionPolicy Bypass -File "schedulers\daily_scheduler.ps1"  # Windows
```

---

## 📚 Additional Resources

For detailed information, see:

- **Watchers:** `GMAIL_WATCHER_SETUP.md`, `BROWSER_WATCHERS_SETUP.md`
- **Skills:** `SKILL_QUICK_REFERENCE.md`
- **Scheduler:** `DAILY_BRIEFING_SETUP.md`, `DAILY_BRIEFING_QUICK_START.md`
- **Email MCP:** `EMAIL_MCP_SETUP.md`
- **Testing:** `DAILY_BRIEFING_TEST_GUIDE.md`
- **History:** `history/README.md`, `history/PROJECT_SUMMARY.md`

---

## ✅ Verification Checklist

- [ ] Python 3.10+ installed
- [ ] PM2 installed globally
- [ ] All project folders exist
- [ ] credentials.json downloaded and placed
- [ ] Gmail watcher tested and working
- [ ] WhatsApp watcher authenticated (QR scanned)
- [ ] LinkedIn watcher authenticated (logged in)
- [ ] All 3 watchers running in PM2
- [ ] Daily scheduler configured (cron/Task Scheduler)
- [ ] Scheduler tested manually
- [ ] Email MCP installed and configured
- [ ] Test messages sent and received in Needs_Action/

All checked? ✅ **System is ready to run!**

---

**Status:** ✅ Ready to Run
**Last Tested:** 2026-02-14
**Expected Uptime:** 24/7 (PM2 auto-restart on crash)

