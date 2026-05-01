# WhatsApp Quick Re-authentication Guide (2 minutes)

**Status:** WhatsApp watcher is running but needs manual QR code scan

---

## What Happened

After 27 hours of continuous operation, WhatsApp's server logged out your session. The new code detected this and automatically restarted the browser. Now it needs you to scan the QR code again (one-time setup, then runs for 30+ days).

---

## Quick Fix (2 minutes)

### Step 1: Find the Chromium Window
```
Look for: A browser window with "Scan the QR code with your phone to link your account"
```

The browser should be visible on your screen. It might be:
- In the background
- Minimized
- On another monitor
- Behind other windows

Try:
- Click taskbar → Look for Chromium/browser icon
- Check all monitors
- Use Alt+Tab to cycle through windows

### Step 2: Scan QR Code
```
1. On your phone, open WhatsApp
2. Go to Settings → Linked Devices → Link a Device
3. Point camera at the QR code in the browser
4. Confirm on phone
5. Wait 5 seconds
```

### Step 3: Confirm in Terminal
```bash
# Check if WhatsApp authenticated
ls session/whatsapp_authenticated.txt

# Should see output like:
# 2026-02-16T07:05:30.123456
```

If file exists → ✅ **Success!**

### Step 4: Verify Monitoring Started
```bash
# Check logs
pm2 logs whatsapp_watcher --lines 5

# Should see:
# [OK] AUTHENTICATED - Chat area detected!
# [CYCLE 1] Checking for messages...
```

---

## Common Issues

### "I don't see the browser window"
```bash
# Check if it's running
pm2 list | grep whatsapp_watcher

# Should show: online status

# Try to focus it
pm2 logs whatsapp_watcher | tail -50
# Look for "Launching Chromium" or "navigating to WhatsApp Web"

# Restart it explicitly
pm2 restart whatsapp_watcher
```

### "QR code looks invalid/blurry"
```
1. Make sure lighting is good
2. Try again with a different angle
3. If it fails 3 times, WhatsApp will ask you to wait

Manual fix:
- Kill the browser process
- Run: pm2 restart whatsapp_watcher
- New QR code will appear in 5 seconds
```

### "Authenticated but no messages"
This is normal! Messages are only captured if they contain keywords:
- `urgent`
- `invoice`
- `payment`
- `sales`

Try sending a test message with one of these words:
```
Test message: "Urgent payment needed"
Wait 30 seconds
Check: ls Needs_Action/whatsapp*
```

---

## Verify All Three Systems Working

```bash
# Show all watchers online
pm2 list

# Check message count
ls Needs_Action/ | wc -l

# Should see:
# - Gmail messages: gmail_20260216_...
# - LinkedIn messages: linkedin_20260216_...
# - WhatsApp messages: whatsapp_20260216_... (once authenticated)
```

---

## Expected Timeline

| Time | Event |
|------|-------|
| T=0s | You find browser window |
| T=0-15s | Scan QR code with phone |
| T=15s | WhatsApp Web loads |
| T=20s | Chat area appears |
| T=20s | Watcher detects authentication ✓ |
| T=20s | Monitoring starts (cycle 1) |

Total time: **2-3 minutes**

---

## Nothing Working? Nuclear Option

```bash
# Stop everything
pm2 delete whatsapp_watcher

# Delete old session (start fresh)
rm -rf session/whatsapp*

# Restart with fresh QR code
pm2 start watchers/whatsapp_persistent.py --name whatsapp_watcher --interpreter python

# QR code appears in new browser window within 5 seconds
# Scan it again
# Done!
```

---

## Once Authenticated...

After you scan the QR code, WhatsApp will stay authenticated for 30+ days. You won't need to do this again unless:

1. You manually logout on WhatsApp Web
2. WhatsApp forces security refresh (rare, ~monthly)
3. Browser session corrupted (very rare)

---

**Next:** Go find that Chromium window and scan the QR code! ⏱️

