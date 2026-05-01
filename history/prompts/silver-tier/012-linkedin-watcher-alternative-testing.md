# PHR: LinkedIn Watcher Alternative Testing Methods

**ID:** 012
**Stage:** silver-tier | debugging
**Date:** 2026-02-15
**Status:** 🔄 TROUBLESHOOTING

---

## Issue Summary

LinkedIn watcher script runs but shows warning and may not be capturing messages correctly.

**User Question:** "How else can I check if it works besides sending a test message?"

**Answer:** Multiple debugging methods available without sending test messages.

---

## Testing Method 1: Check Logs File ✅

LinkedIn watcher writes detailed logs to a file:

```powershell
# View the logs file
Get-Content watchers/logs/linkedin_watcher.log -Tail 50

# Or in continuous mode (live tail):
Get-Content -Path watchers/logs/linkedin_watcher.log -Wait
```

**What to look for:**
- `[OK] Found X unread messages` - Messages detected
- `[ERROR]` - Something failed
- `[OK] Checking notifications` - Monitoring loop running
- Any errors about selectors or navigation

---

## Testing Method 2: Check Session Folder 📁

Verify that session/cookies are being saved:

```powershell
# List session files
dir session\linkedin\

# If files exist → Session saved ✅
# If empty → Session not saving (login didn't work properly)
```

**Expected:** Should have multiple `.dat` files or `user_data` folder

---

## Testing Method 3: Check Script Output in Real-Time 🔍

Run with verbose output to see what's happening:

```powershell
# Run with unbuffered output to see logs immediately
python -u watchers/linkedin_watcher.py 2>&1

# Keep terminal visible and watch for messages like:
# [OK] Found X unread messages
# [OK] Checking notifications
# [ERROR] (if something fails)
```

---

## Testing Method 4: Try WhatsApp Watcher Instead ↔️

**Recommendation:** LinkedIn appears to have selector issues. Try WhatsApp watcher instead, which is simpler:

```powershell
# Stop current script: Ctrl+C

# Run WhatsApp watcher
python watchers/whatsapp_watcher.py

# Scan QR code on first run
# Then send yourself WhatsApp message with keyword "sales"
# Check /Needs_Action/ folder
```

WhatsApp is simpler and more reliable because:
- ✅ Uses QR code (same as browser login)
- ✅ More stable selectors
- ✅ Less likely to have structural changes
- ✅ Works better with Playwright

---

## Testing Method 5: Check Browser Window Manually 🌐

While script is running:

```powershell
# Check if Chromium process is running
tasklist | findstr chromium

# Should show: chrome.exe (Playwright uses Chromium)
```

If process is running:
- ✅ Browser is open
- ✅ Script loaded LinkedIn
- ⚠️ But selectors might not match page structure

---

## Testing Method 6: Run Gmail Watcher for Comparison ✅

**What we know works:** Gmail watcher (you confirmed it runs successfully)

Compare:
```powershell
# Stop LinkedIn: Ctrl+C

# Try Gmail watcher (we know this works)
python watchers/gmail_watcher.py

# If Gmail works but LinkedIn doesn't → LinkedIn has selector issues
```

---

## Testing Method 7: Check /Needs_Action/ Folder

Even without sending messages:

```powershell
# List all files
dir Needs_Action\

# Check if any LinkedIn files exist:
dir Needs_Action\linkedin*

# View file contents
type Needs_Action\linkedin_*.md
```

If files exist → Script IS capturing messages!

---

## Likely Issue with LinkedIn

**Based on symptoms:**
- Login warning appears
- Feed element not detected
- Selectors may be outdated

**LinkedIn likely changed their HTML selectors** because:
- LinkedIn frequently updates UI
- `data-testid="feed-item-card"` may no longer exist
- `data-testid="msg-conversation-item"` may have changed

---

## Recommended Action Plan

**Option A: Quick Fix - Increase Timeout & Continue Testing**

```powershell
# Stop script: Ctrl+C

# Keep running in background, send test message:
python watchers/linkedin_watcher.py

# Wait 2-3 minutes, then:
dir Needs_Action\

# If file appears → Just ignore the warning, it works
```

**Option B: Try WhatsApp First**

```powershell
# Stop LinkedIn: Ctrl+C

# Try WhatsApp (simpler, more reliable)
python watchers/whatsapp_watcher.py
```

**Option C: Advanced - Update Selectors**

If you want to fix LinkedIn properly:
- Need to inspect LinkedIn page in browser
- Find actual HTML selectors
- Update lines 131, 137, 164, etc. in linkedin_watcher.py

---

## Quick Diagnostic Command

Run this to get all info at once:

```powershell
# Check session exists
Write-Host "=== Checking LinkedIn Session ==="
dir session\linkedin\

# Check logs exist
Write-Host "=== Checking Logs ==="
Get-Content watchers/logs/linkedin_watcher.log -Tail 20

# Check Needs_Action folder
Write-Host "=== Checking Needs_Action ==="
dir Needs_Action\linkedin*
```

---

## Summary

**Without sending test message, you can check:**

1. ✅ Logs file: `watchers/logs/linkedin_watcher.log`
2. ✅ Session folder: `session/linkedin/` (should have files)
3. ✅ Process: `tasklist | findstr chromium`
4. ✅ Needs_Action folder: Any LinkedIn files exist?
5. ✅ Compare with Gmail watcher (known working)
6. ✅ Try WhatsApp watcher (simpler, more reliable)

**My Recommendation:**

Given the warning, I suggest:

**Option 1 (Fast):** Try WhatsApp watcher - simpler, more reliable
**Option 2 (Wait & See):** Keep LinkedIn running, wait for actual messages, check logs

---

**Status:** 🔄 TROUBLESHOOTING
**Options:** Multiple testing methods available
**Next:** Choose testing approach and run diagnostics
**Date:** 2026-02-15
