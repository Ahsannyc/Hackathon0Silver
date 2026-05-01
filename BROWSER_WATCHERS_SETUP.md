# WhatsApp & LinkedIn Watchers - Browser Setup Guide

**Status:** ✅ Fixed - Unicode encoding errors resolved
**Current Issue:** Browser windows need manual authentication

---

## Quick Summary

The WhatsApp and LinkedIn watchers use **Playwright to automate browser interactions**. They:
- Launch real Chromium browser windows (not headless)
- Require **first-run manual login/QR scan**
- Save session for reuse in subsequent runs
- Check for messages/notifications every 30-60 seconds

**Fixed Issues:**
- ✅ Unicode encoding errors on Windows
- ✅ Import errors
- ✅ Process crashing

**Current Requirement:**
- ⏳ Manual browser authentication (QR code / login)

---

## Step 1: Ensure Playwright is Installed

```bash
# Check Playwright installation
pip list | grep playwright

# If not installed, install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium

# Verify installation
playwright install --with-deps chromium
```

---

## Step 2: Start WhatsApp Watcher

### Option 1: Run Directly (Recommended for Setup)

```bash
# Run directly to see browser window and QR code
python watchers/whatsapp_watcher.py
```

**What happens:**
1. Chromium browser window opens
2. WhatsApp Web loads (https://web.whatsapp.com)
3. QR code appears on screen
4. Scan with your phone's WhatsApp
5. Session saved for future runs
6. Script starts monitoring (30-second intervals)

**Expected output:**
```
[OK] Session path ready: ...
Starting WhatsApp Watcher - Check interval: 30s
[WAIT] Waiting for WhatsApp Web login...
[Scan QR code in browser window]
[OK] WhatsApp Web authenticated
[OK] Found 0 unread messages with keywords
```

### Option 2: Run with PM2 (Production)

```bash
pm2 start watchers/whatsapp_watcher.py --name whatsapp_watcher --interpreter python
pm2 logs whatsapp_watcher
```

Monitor the logs until you see:
- `[WAIT] Waiting for WhatsApp Web login...`
- Then a browser window should open
- Scan QR code
- Then you should see: `[OK] WhatsApp Web authenticated`

---

## Step 3: Start LinkedIn Watcher

### Option 1: Run Directly (Recommended for Setup)

```bash
# Run directly to see browser window and login prompt
python watchers/linkedin_watcher.py
```

**What happens:**
1. Chromium browser window opens
2. LinkedIn page loads
3. If not logged in: sign-in page appears (enter credentials)
4. Session saved for future runs
5. Script starts monitoring feed (60-second intervals)

**Expected output:**
```
[OK] Session path ready: ...
Starting LinkedIn Watcher - Check interval: 60s
[WAIT] Waiting for LinkedIn login...
[Enter credentials in browser window]
[OK] LinkedIn authenticated
[OK] Found 0 unread messages with keywords
```

### Option 2: Run with PM2 (Production)

```bash
pm2 start watchers/linkedin_watcher.py --name linkedin_watcher --interpreter python
pm2 logs linkedin_watcher
```

---

## Troubleshooting: Browser Windows Not Appearing

### Issue 1: Browser Launches Silently / No Window Visible

**Diagnosis:**
- Logs show `[WAIT] Waiting for LinkedIn login...` or `[WAIT] Waiting for WhatsApp Web login...`
- But no browser window appears

**Solutions:**

**A) Check for Hidden Browser Windows**
```bash
# Check if Chromium process is running
tasklist | findstr chromium

# Should show chromium.exe processes
```

**B) Force Window to Foreground**
- Add this to the watcher script before `self.page.goto()`:
```python
# In launch_browser method, after context creation:
self.page.evaluate("window.focus()")
self.page.evaluate("document.body.focus()")
```

**C) Use Visible Window Mode**
- The scripts already have `headless=False`
- But some systems need explicit window settings

**D) Restart Playwright Installation**
```bash
playwright install --with-deps chromium --force
```

### Issue 2: Browser Opens But Timed Out Before QR Scan

**Diagnosis:**
- Browser window appeared
- But closed because you didn't scan in time

**Solution:**
- Browser waits 120 seconds (2 minutes) for login
- Scan QR code faster or extend timeout in script
- Edit timeout value (line 124 in whatsapp_watcher.py):
```python
# Change from 120000ms to 300000ms (5 minutes)
self.page.wait_for_selector('[data-testid="chat-list-item"]', timeout=300000)
```

### Issue 3: Different Behavior from Classmate

**Why their browser opened but yours didn't:**

1. **Chromium Cache** - Already installed on their system
   - Solution: Run `playwright install chromium` on your system

2. **System Permissions** - Windows blocking browser
   - Solution: Allow python.exe to launch applications (Windows Defender)

3. **Display/GPU Issues** - Your system using different graphics
   - Solution: Test with: `python watchers/whatsapp_watcher.py` directly first

4. **Python Environment** - Different Python versions
   - Check: `python --version` (should be 3.10+)

---

## First Run Checklist

- [ ] Installed Playwright: `pip install playwright`
- [ ] Installed Chromium: `playwright install chromium`
- [ ] Run WhatsApp watcher directly: `python watchers/whatsapp_watcher.py`
- [ ] Browser window opened (wait up to 2 min)
- [ ] Scanned QR code with phone
- [ ] Saw: `[OK] WhatsApp Web authenticated`
- [ ] Session saved (can't scan again on next run)
- [ ] Run LinkedIn watcher directly: `python watchers/linkedin_watcher.py`
- [ ] Logged into LinkedIn (enter email/password)
- [ ] Saw: `[OK] LinkedIn authenticated`
- [ ] Both scripts running with PM2

---

## How Sessions Work

### First Run:
```
Start watcher
  ↓
Browser opens
  ↓
Manual authentication (QR/Login)
  ↓
Session saved to session/whatsapp or session/linkedin
  ↓
Watcher monitoring (no login needed again)
```

### Subsequent Runs:
```
Start watcher
  ↓
Browser opens with saved session
  ↓
Already authenticated (no QR/Login needed)
  ↓
Immediate monitoring starts
```

### Session Files:
```
session/whatsapp/    - WhatsApp session data
session/linkedin/    - LinkedIn session data
```

**To reset and re-authenticate:**
```bash
# Delete session folder
rm -r session/whatsapp        # Linux/Mac
rmdir /s session\whatsapp     # Windows

# Next run will require new authentication
```

---

## Why Your Classmate's Worked Immediately

They likely had:
1. ✅ Playwright already installed
2. ✅ Chromium browser already downloaded
3. ✅ Sessions already authenticated
4. ✅ Same Python version

---

## Testing Messages

### WhatsApp Test:
1. Open WhatsApp on your phone
2. Find the bot/account being monitored
3. Send message: "URGENT invoice #123"
4. Wait 30 seconds
5. Check `/Needs_Action/` folder for new .md file

### LinkedIn Test:
1. Visit LinkedIn.com
2. Send DM or post comment with: "sales opportunity client project"
3. Wait 60 seconds
4. Check `/Needs_Action/` folder for new .md file

---

## Current PM2 Status

```
WhatsApp: online (31.6 MB)
LinkedIn: online (34.3 MB)
Gmail: errored (needs credentials.json)
```

### Monitor Live:
```bash
# Watch logs in real-time
pm2 logs whatsapp_watcher -f
pm2 logs linkedin_watcher -f

# Check process list
pm2 list

# Restart if needed
pm2 restart whatsapp_watcher
pm2 restart linkedin_watcher
```

---

## Expected File Outputs

When messages are detected with keywords, files are saved to `/Needs_Action/`:

**WhatsApp Example:**
```
Needs_Action/
├── whatsapp_urgent_2026-02-14_143052.md
├── whatsapp_invoice_2026-02-14_144123.md
└── whatsapp_payment_2026-02-14_145234.md
```

**LinkedIn Example:**
```
Needs_Action/
├── linkedin_sales_2026-02-14_143052.md
├── linkedin_client_2026-02-14_144123.md
└── linkedin_project_2026-02-14_145234.md
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `watchers/whatsapp_watcher.py` | WhatsApp monitoring script |
| `watchers/linkedin_watcher.py` | LinkedIn monitoring script |
| `session/whatsapp/` | WhatsApp session (persistent login) |
| `session/linkedin/` | LinkedIn session (persistent login) |
| `Needs_Action/` | Saved messages with keywords |

---

## Next Steps

1. ✅ Run: `playwright install chromium`
2. ✅ Run: `python watchers/whatsapp_watcher.py`
3. ✅ Scan QR code (browser window)
4. ✅ Wait for: `[OK] WhatsApp Web authenticated`
5. ✅ Ctrl+C to stop script
6. ✅ Run with PM2: `pm2 start watchers/whatsapp_watcher.py --name whatsapp_watcher --interpreter python`
7. ✅ Repeat for LinkedIn watcher
8. ✅ Verify with: `pm2 list`

---

**Status:** ✅ Ready for manual authentication
**Created:** 2026-02-14
**Next:** Scan QR codes and set up sessions

