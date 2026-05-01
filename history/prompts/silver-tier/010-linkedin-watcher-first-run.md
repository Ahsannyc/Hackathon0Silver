# PHR: LinkedIn Watcher First Run & Authentication

**ID:** 010
**Stage:** silver-tier | testing
**Date:** 2026-02-15
**Status:** ✅ IN PROGRESS

---

## Task Summary

User initiated LinkedIn watcher first run authentication flow.

**Command Executed:**
```bash
playwright install chromium  # ✅ Success
python watchers/linkedin_watcher.py  # ✅ Script started, awaiting login
```

**Status:** Script running, waiting for user to log in to LinkedIn

---

## Current Output Analysis

```
[OK] Session path ready: C:\Users\14loa\Desktop\IT\GIAIC\Q4 spec kit\Hackathon0Silver\session\linkedin
Starting LinkedIn Watcher - Check interval: 60s
[WAIT] Waiting for LinkedIn login...
[WARN] Feed may not be fully loaded
```

**What This Means:**
- ✅ Playwright installed successfully
- ✅ Browser window should have opened
- ✅ Script is running and monitoring
- ⏳ Waiting for user to log in to LinkedIn
- ⚠️ Feed not fully loaded (normal on first login)

---

## What's Happening

1. **Playwright installed:** Chromium browser downloaded and ready
2. **Session folder created:** `session/linkedin/` ready to store persistent cookies
3. **Browser opened:** Should show LinkedIn login page
4. **Waiting for authentication:** Script is paused until login completes
5. **Feed warning:** Normal - happens when page is still loading

---

## What You Need to Do

The browser window showing LinkedIn login page has opened (check if it's behind other windows).

**Steps:**
1. Find the LinkedIn login browser window (check taskbar if hidden)
2. Enter your LinkedIn email
3. Enter your LinkedIn password
4. Complete any 2FA (two-factor authentication) if prompted
5. Wait for LinkedIn feed to fully load
6. The script will automatically detect successful login and continue

**Expected behavior after login:**
```
[OK] LinkedIn authenticated successfully
[OK] Checking notifications...
[OK] Found 0 unread messages
```

---

## Troubleshooting If Browser Didn't Open

If you don't see a browser window:

**Check 1: Hidden Window**
- Check Windows taskbar for "chromium" or browser window
- Alt+Tab to cycle through windows

**Check 2: Reinstall Playwright**
```bash
pip install playwright --upgrade
playwright install chromium
```

**Check 3: Run with verbose output**
```bash
python -u watchers/linkedin_watcher.py
```

**Check 4: Check for errors in terminal**
- Look for error messages after "[WAIT] Waiting for LinkedIn login..."
- If you see errors, take screenshot and share

---

## Important Notes

- **Don't close the terminal:** Script needs to run continuously
- **2FA is normal:** If LinkedIn asks for code, complete it
- **Timeout is 5 minutes:** Script will timeout if no login after 300 seconds
- **Multiple devices:** If LinkedIn asks about device, click "Trust this device"
- **Session is saved:** After first login, won't need to re-authenticate on restart

---

## Integration Points

Once login is successful:
- Session saved to `session/linkedin/`
- Can be started with PM2
- Can run alongside Gmail and WhatsApp watchers
- Ready for HITL approval handler

---

## Next Steps

**After LinkedIn login completes successfully:**

1. Press `Ctrl+C` to stop the script (or wait for it to run continuously)
2. Verify session was saved: `dir session/linkedin/`
3. Check logs: `cat watchers/logs/linkedin_watcher.log`
4. Run with PM2: `pm2 start watchers/linkedin_watcher.py --name linkedin_watcher --interpreter python`

---

**Status:** ✅ IN PROGRESS
**User Action Required:** Complete LinkedIn login in browser window
**Expected Result:** Successful authentication and session saved
**Date:** 2026-02-15
**Next:** Confirm login complete
