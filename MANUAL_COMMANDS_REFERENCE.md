# Manual Commands Reference - Run Watchers in Terminal

**Location:** Open new terminal in project root directory

```bash
cd "C:\Users\14loa\Desktop\IT\GIAIC\Q4 spec kit\Hackathon0Silver"
```

---

## ⚡ QUICK START (Copy & Paste)

### Start All Watchers (Fresh)
```bash
pm2 start all
```

### Check If Running
```bash
pm2 list
```

### Watch Live
```bash
pm2 logs -f
```

### Restart All
```bash
pm2 restart all
```
**Note:** WhatsApp will restore session (NO QR needed - session persistence enabled!)

### Stop All
```bash
pm2 stop all
```

### Full Reset
```bash
pm2 delete all
pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python
pm2 start watchers/whatsapp_persistent.py --name whatsapp_watcher --interpreter python
pm2 start watchers/linkedin_persistent.py --name linkedin_watcher --interpreter python
```

---

## 🔍 CHECK SYSTEM STATUS

### 1. View All Running Watchers
```bash
pm2 list
```
**Shows:** Status, PID, uptime, restarts, memory usage for all 3 watchers

**Expected Output:**
```
┌────┬──────────────────┬─────────┐
│ id │ name             │ status  │
├────┼──────────────────┼─────────┤
│ 0  │ gmail_watcher    │ online  │
│ 1  │ whatsapp_watcher │ online  │
│ 2  │ linkedin_watcher │ online  │
└────┴──────────────────┴─────────┘
```

### 2. Check Captured Messages
```bash
ls -lah Needs_Action/
```
**Shows:** All captured messages with timestamps and sizes

### 3. Count Messages by Source
```bash
echo "Gmail: $(ls -1 Needs_Action/gmail_* 2>/dev/null | wc -l)"
echo "LinkedIn: $(ls -1 Needs_Action/linkedin_* 2>/dev/null | wc -l)"
echo "WhatsApp: $(ls -1 Needs_Action/whatsapp_* 2>/dev/null | wc -l)"
```
**Shows:** Breakdown of messages by source

### 4. View Recent Messages
```bash
ls -1t Needs_Action/ | head -5
```
**Shows:** 5 most recently captured messages

---

## 📊 VIEW LIVE LOGS

### 5. Watch All Watchers (Real-time)
```bash
pm2 logs -f
```
**Shows:** Live logs from all 3 watchers as they check for messages
**Exit:** Press `Ctrl+C`

### 6. Watch Only Gmail
```bash
pm2 logs gmail_watcher -f
```
**Shows:** Only Gmail watcher logs (checking every 120 seconds)

### 7. Watch Only WhatsApp
```bash
pm2 logs whatsapp_watcher -f
```
**Shows:** Only WhatsApp watcher logs (checking every 30 seconds)

### 8. Watch Only LinkedIn
```bash
pm2 logs linkedin_watcher -f
```
**Shows:** Only LinkedIn watcher logs (checking every 60 seconds)

### 9. View Last 50 Lines of Each Watcher
```bash
echo "=== GMAIL ===" && pm2 logs gmail_watcher --lines 50 --nostream
echo "" && echo "=== WHATSAPP ===" && pm2 logs whatsapp_watcher --lines 50 --nostream
echo "" && echo "=== LINKEDIN ===" && pm2 logs linkedin_watcher --lines 50 --nostream
```
**Shows:** Last 50 lines from each watcher's logs

---

## 🎮 CONTROL WATCHERS

### 10. Stop All Watchers
```bash
pm2 stop all
```
**Result:** All 3 watchers pause (messages won't be captured, processes still running)

### 11. Start All Watchers
```bash
pm2 start all
```
**Result:** All 3 watchers resume monitoring

### 12. Restart All Watchers
```bash
pm2 restart all
```
**Result:** Kill and restart all 3 watchers (loses session, re-authenticates)

### 13. Stop Specific Watcher
```bash
pm2 stop gmail_watcher
pm2 stop whatsapp_watcher
pm2 stop linkedin_watcher
```

### 14. Start Specific Watcher
```bash
pm2 start gmail_watcher
pm2 start whatsapp_watcher
pm2 start linkedin_watcher
```

### 15. Restart Specific Watcher
```bash
pm2 restart gmail_watcher
# Or:
pm2 restart whatsapp_watcher
# Or:
pm2 restart linkedin_watcher
```

### 16. Delete All Watchers
```bash
pm2 delete all
```
**⚠️ Warning:** Stops all processes. Will need to restart manually.

---

## ▶️ RUN WATCHERS MANUALLY (Direct Python)

### 17. Run Gmail Watcher Directly
```bash
python watchers/gmail_watcher.py
```
**Shows:** Live console output from Gmail watcher only
**Exit:** Press `Ctrl+C`
**Note:** Runs in foreground (blocks terminal)

### 18. Run WhatsApp Watcher Directly
```bash
python watchers/whatsapp_persistent.py
```
**Shows:** Live console output from WhatsApp watcher
**Shows:** Chromium browser window will appear
**Exit:** Press `Ctrl+C`
**Note:** Browser window stays open

### 19. Run LinkedIn Watcher Directly
```bash
python watchers/linkedin_persistent.py
```
**Shows:** Live console output from LinkedIn watcher
**Shows:** Chromium browser window will appear
**Exit:** Press `Ctrl+C`

### 20. Run All Three in Separate Windows (Best for Manual Testing)

**Terminal 1:**
```bash
python watchers/gmail_watcher.py
```

**Terminal 2:**
```bash
python watchers/whatsapp_persistent.py
```

**Terminal 3:**
```bash
python watchers/linkedin_persistent.py
```

**Now you can see all three running simultaneously with separate terminal windows**

---

## 📈 MONITOR PERFORMANCE

### 21. Watch Memory Usage
```bash
pm2 monit
```
**Shows:** Real-time CPU and memory usage for each process
**Navigation:** Use arrow keys to select, `q` to quit

### 22. View Detailed Process Info
```bash
pm2 info gmail_watcher
pm2 info whatsapp_watcher
pm2 info linkedin_watcher
```
**Shows:** PID, memory, CPU, uptime, restarts, and more

### 23. Show Running Time
```bash
pm2 list | grep -E "gmail|whatsapp|linkedin"
```
**Shows:** Uptime for each watcher

---

## 🧪 TEST CAPTURES

### 24. Send Test Gmail
```bash
# Manually send yourself an email with keywords:
# Subject: "URGENT invoice #12345"
# Gmail watcher will capture within 120 seconds
ls -lt Needs_Action/gmail_* | head -1
```

### 25. Send Test LinkedIn
```bash
# Go to LinkedIn and post or message with keyword:
# "Sales opportunity with our team"
# LinkedIn watcher will capture within 60 seconds
ls -lt Needs_Action/linkedin_* | head -1
```

### 26. Send Test WhatsApp
```bash
# Send yourself a WhatsApp message with keyword:
# "Urgent payment needed"
# WhatsApp watcher will capture within 30 seconds
ls -lt Needs_Action/whatsapp_* | head -1
```

---

## 🔧 TROUBLESHOOTING COMMANDS

### 27. Check If Python Installed
```bash
python --version
```
**Expected:** Python 3.13.x or higher

### 28. Check If Required Packages Installed
```bash
pip list | grep -E "google|playwright"
```
**Expected:** Shows google-api-*, google-auth-*, playwright

### 29. Check If PM2 Installed
```bash
pm2 --version
```
**Expected:** Shows version number

### 30. Reinstall Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright
```

### 31. Check Gmail Credentials
```bash
ls -la credentials.json
ls -la watchers/.gmail_token.json
```
**Shows:** If authentication files exist

### 32. Check WhatsApp Session
```bash
ls -la session/whatsapp_authenticated.txt
ls -la session/whatsapp/
```
**Shows:** If WhatsApp authenticated and session stored

### 33. Check LinkedIn Session
```bash
ls -la session/linkedin_authenticated.txt
ls -la session/linkedin/
```
**Shows:** If LinkedIn authenticated and session stored

---

## 🎯 COMMON WORKFLOWS

### Scenario 1: Check System Health (60 seconds)
```bash
pm2 list
ls -lah Needs_Action/ | wc -l
pm2 logs -f
# Wait 10 seconds to see activity
# Press Ctrl+C
```

### Scenario 2: Watch One Watcher (Monitor for issues)
```bash
pm2 logs gmail_watcher -f
# Watch for errors or successes
# Press Ctrl+C to stop
```

### Scenario 3: Test Gmail Capture
```bash
# Terminal 1:
pm2 logs gmail_watcher -f

# Terminal 2 (after some time):
ls -lt Needs_Action/gmail_* | head -3
```

### Scenario 4: Restart and Watch Recovery
```bash
pm2 restart whatsapp_watcher
sleep 5
pm2 logs whatsapp_watcher -f
# Watch for: "AUTHENTICATED - Chat area detected!"
```

### Scenario 5: Full System Check
```bash
echo "=== STATUS ===" && pm2 list
echo ""
echo "=== MESSAGE COUNT ===" && ls Needs_Action/ | wc -l
echo ""
echo "=== RECENT MESSAGES ===" && ls -lt Needs_Action/ | head -5
echo ""
echo "=== GMAIL LOGS ===" && pm2 logs gmail_watcher --lines 10 --nostream
echo ""
echo "=== WHATSAPP LOGS ===" && pm2 logs whatsapp_watcher --lines 10 --nostream
echo ""
echo "=== LINKEDIN LOGS ===" && pm2 logs linkedin_watcher --lines 10 --nostream
```

### Scenario 6: Run All Three Manually (Best for Demo)
```bash
# Open 3 terminal windows
# Terminal 1: python watchers/gmail_watcher.py
# Terminal 2: python watchers/whatsapp_persistent.py
# Terminal 3: python watchers/linkedin_persistent.py

# All three will run and show output as messages are captured
```

---

## 💡 USEFUL ONE-LINERS

### Get Quick Status
```bash
pm2 list && echo "" && echo "Messages: $(ls -1 Needs_Action/ | wc -l)"
```

### Stream All Logs
```bash
pm2 logs -f --lines 0
```

### See Only Errors
```bash
pm2 logs -f | grep ERROR
```

### See Only Captured Messages
```bash
pm2 logs -f | grep "OK.*Captured"
```

### Count Errors in Last 100 Lines
```bash
pm2 logs gmail_watcher --lines 100 --nostream | grep -c ERROR
```

### Kill All Python Processes (Nuclear Option)
```bash
taskkill /F /IM python.exe
```
⚠️ **Only if system is broken**

---

## 📋 DEMO SCRIPT (For Teacher)

```bash
# 1. Show status
echo "1. SYSTEM STATUS:"
pm2 list

# 2. Show messages
echo ""
echo "2. CAPTURED MESSAGES:"
ls -lah Needs_Action/

# 3. Count by source
echo ""
echo "3. MESSAGE BREAKDOWN:"
echo "Total: $(ls -1 Needs_Action/gmail_* Needs_Action/linkedin_* Needs_Action/whatsapp_* 2>/dev/null | wc -l)"
echo "Gmail: $(ls -1 Needs_Action/gmail_* 2>/dev/null | wc -l)"
echo "LinkedIn: $(ls -1 Needs_Action/linkedin_* 2>/dev/null | wc -l)"
echo "WhatsApp: $(ls -1 Needs_Action/whatsapp_* 2>/dev/null | wc -l)"

# 4. View sample
echo ""
echo "4. SAMPLE EMAIL:"
cat Needs_Action/gmail_*.md | head -30

# 5. Show live monitoring
echo ""
echo "5. LIVE MONITORING (10 seconds):"
timeout 10 pm2 logs -f || true
```

---

## 🆘 IF SOMETHING BREAKS

### Watcher Offline?
```bash
pm2 logs <name> --lines 50 --nostream
# Check for errors
pm2 restart <name>
```

### Authentication Lost?
```bash
# Gmail
rm watchers/.gmail_token.json
pm2 restart gmail_watcher

# WhatsApp - ENHANCED (Feb 16, 2026)
# Session now persists! No QR needed on normal restart
pm2 restart whatsapp_watcher
# Will auto-restore session from session/whatsapp/ folder
# NO QR code needed!

# Only if session is corrupted:
pm2 stop whatsapp_watcher
rm -rf session/whatsapp*
pm2 start whatsapp_watcher
# Will show QR code for fresh authentication

# LinkedIn
rm -rf session/linkedin*
pm2 restart linkedin_watcher
```

### Python Packages Missing?
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright
playwright install chromium
```

### PM2 Issues?
```bash
pm2 delete all
pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python
pm2 start watchers/whatsapp_persistent.py --name whatsapp_watcher --interpreter python
pm2 start watchers/linkedin_persistent.py --name linkedin_watcher --interpreter python
```

---

## ⚡ QUICK REFERENCE TABLE

| Task | Command |
|------|---------|
| Check status | `pm2 list` |
| View logs | `pm2 logs -f` |
| Restart all | `pm2 restart all` |
| Stop all | `pm2 stop all` |
| Count messages | `ls Needs_Action/ \| wc -l` |
| Run Gmail manually | `python watchers/gmail_watcher.py` |
| Run WhatsApp manually | `python watchers/whatsapp_persistent.py` |
| Run LinkedIn manually | `python watchers/linkedin_persistent.py` |
| Monitor CPU/Memory | `pm2 monit` |
| View errors | `pm2 logs -f \| grep ERROR` |
| Fix broken state | `pm2 delete all && pm2 start watchers/*.py` |

