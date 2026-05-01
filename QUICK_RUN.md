# Quick Start - Silver Tier System

**For Future Sessions: Start Here**

---

## 🚀 Fastest Way to Get Running (30 seconds)

```bash
# Navigate to project
cd "C:\Users\14loa\Desktop\IT\GIAIC\Q4 spec kit\Hackathon0Silver"

# Start all three watchers
pm2 start all

# Verify they're running
pm2 list
```

**Expected output:**
```
✅ gmail_watcher - online
✅ whatsapp_watcher - online
✅ linkedin_watcher - online
```

---

## 📊 Check Current Status (10 seconds)

```bash
# Quick health check
pm2 list

# Count captured messages
ls Needs_Action/ | wc -l

# See breakdown
echo "Gmail: $(ls -1 Needs_Action/gmail_* 2>/dev/null | wc -l) | LinkedIn: $(ls -1 Needs_Action/linkedin_* 2>/dev/null | wc -l) | WhatsApp: $(ls -1 Needs_Action/whatsapp_* 2>/dev/null | wc -l)"
```

---

## 👀 Watch Live Monitoring (Real-time)

```bash
# Stream all three watchers
pm2 logs -f

# Press Ctrl+C to stop
```

---

## 🔧 Common Tasks

### First Time Setup (Initial Authentication)

```bash
# Gmail: Auto-authenticates via OAuth (first run shows browser)
# LinkedIn: Auto-authenticates via persistent session (first run shows login)
# WhatsApp: Auto-restores from session (first run may show QR if session corrupted)

# If WhatsApp needs QR scan (rare):
pm2 stop whatsapp_watcher
rm -rf session/whatsapp_authenticated.txt
pm2 start whatsapp_watcher
# Then scan QR code when browser appears
```

### Restart All Watchers

```bash
pm2 restart all
# WhatsApp will restore session (NO QR needed)
# Gmail will reconnect
# LinkedIn will reconnect
```

### Stop Everything

```bash
pm2 stop all
# Watchers paused, no new messages captured
```

### Resume Monitoring

```bash
pm2 start all
```

### Restart Single Watcher

```bash
pm2 restart gmail_watcher
pm2 restart whatsapp_watcher
pm2 restart linkedin_watcher
```

---

## 📋 Captured Messages Location

All captured messages stored in: `Needs_Action/` folder

```bash
# View all messages
ls -lah Needs_Action/

# View latest 5
ls -lt Needs_Action/ | head -5

# View sample message
cat Needs_Action/gmail_*.md | head -40
```

---

## 🆘 If Something Breaks

### Watcher Offline?
```bash
# Check logs
pm2 logs <watcher-name> -f

# Restart
pm2 restart <watcher-name>
```

### All Broken?
```bash
# Nuclear restart
pm2 delete all
pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python
pm2 start watchers/whatsapp_persistent.py --name whatsapp_watcher --interpreter python
pm2 start watchers/linkedin_persistent.py --name linkedin_watcher --interpreter python
```

### Missing Dependencies?
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright
playwright install chromium
```

---

## 📚 For More Details

- **MANUAL_COMMANDS_REFERENCE.md** - 33 commands and scenarios
- **SYSTEM_LIVE_STATUS.md** - Current system status
- **DEPLOYMENT_FIXES_APPLIED.md** - Architecture improvements
- **SYSTEM_FAILURE_ANALYSIS.md** - What was fixed and why

---

## ✨ What This System Does

Monitors 3 channels 24/7 (Gmail, WhatsApp, LinkedIn), captures business-critical messages with keyword filtering, and queues them in `Needs_Action/` folder for processing.

**Keywords monitored:**
- Gmail: `urgent`, `invoice`, `payment`, `sales`
- WhatsApp: `urgent`, `invoice`, `payment`, `sales`
- LinkedIn: `sales`, `client`, `project`, `opportunity`, `partnership`, `lead`

---

**Next Phase:** Process captured messages with Ralph Loop (Claude AI reasoning engine)
