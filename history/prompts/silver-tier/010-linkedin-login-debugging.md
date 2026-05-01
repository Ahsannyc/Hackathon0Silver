# PHR: LinkedIn Watcher Login Detection Debugging

**ID:** 010-DEBUG
**Stage:** silver-tier | debugging
**Date:** 2026-02-15
**Status:** 🔄 IN PROGRESS

---

## Issue Summary

User successfully logged into LinkedIn manually, but script still shows:
```
[WAIT] Waiting for LinkedIn login...
```

**Root Cause:** Script is waiting for LinkedIn feed element to load
- Script looks for: `[data-testid="feed-item-card"]` (LinkedIn feed cards)
- Timeout: 120 seconds (2 minutes)
- Status: Feed element not yet detected by script

---

## What's Happening

1. User logged in manually ✓
2. Browser is on LinkedIn
3. Script waiting for feed page to fully load
4. Waiting for specific element: `[data-testid="feed-item-card"]`

**Possible reasons feed isn't loading:**
- Still loading (wait 30-60 more seconds)
- Security verification prompt (LinkedIn asking "Where are you logging in from?")
- Device verification ("Is this you?")
- 2FA additional confirmation
- Page refresh needed

---

## Debugging Steps

### Step 1: Check Browser Window

Look at the LinkedIn browser window currently open:

- [ ] Can you see the LinkedIn feed (your home timeline)?
- [ ] Or does it still show a login screen?
- [ ] Or does it show a verification prompt?
- [ ] Or is the page blank/loading?

### Step 2: Wait & Watch

The script has a 120-second timeout (2 minutes). It should:
- Keep waiting for the feed to load
- Once feed appears in browser, script should detect it
- Then show: `[OK] LinkedIn authenticated`

**Try waiting 2-3 minutes total** - if page is still loading, script will detect it.

### Step 3: If Still Waiting After 2 Minutes

If the terminal still shows `[WAIT]` after 2+ minutes, the feed element might not be visible. Try:

**Option A: Refresh the page in browser**
- While script is still running, click on browser window
- Press `F5` or `Ctrl+R` to refresh
- This might reload the feed properly

**Option B: Close browser and let script handle it**
- Press `Ctrl+C` to stop script
- Delete the session: `rmdir /s session\linkedin` (on Windows)
- Run again: `python watchers/linkedin_watcher.py`
- Let script open browser fresh and handle login

**Option C: Check for verification prompts**
- LinkedIn sometimes asks "Is this you?" or device verification
- Look for any popup/modal windows in browser
- Complete any verification LinkedIn asks for

---

## What We're Waiting For

The script is looking for this HTML element to appear on the page:
```html
<div data-testid="feed-item-card">...</div>
```

This appears on the LinkedIn feed homepage. Once the script detects this element, it knows login was successful.

---

## Timeline

- `00:37:54` - Script started
- `00:38:11` - Still waiting for feed
- Timeline now: Check current time
- If > 2 minutes elapsed → Feed might not be loading properly

---

## Next Actions Based on What You See

### If you see LinkedIn feed (your home timeline):
- **Wait longer** - Script should detect it within 120 seconds
- Don't do anything, let it run

### If you see a verification prompt:
- **Complete the verification** (click buttons LinkedIn shows)
- Then feed should load
- Script will detect it

### If you see blank page:
- **Refresh browser** with F5
- Wait for feed to load
- Script should then detect it

### If after 3 minutes nothing happens:
- **Stop script** with Ctrl+C
- **Delete session** and retry fresh
- Run: `python watchers/linkedin_watcher.py` again

---

**Status:** 🔄 DEBUGGING
**User Action:** Check browser window and take appropriate action above
**Expected Result:** Feed loads, script detects it, shows "[OK] LinkedIn authenticated"
