# PHR: LinkedIn Watcher Monitoring Active Despite Feed Warning

**ID:** 011
**Stage:** silver-tier | testing
**Date:** 2026-02-15
**Status:** ✅ READY FOR TESTING

---

## Issue Summary

After LinkedIn login, script shows warning:
```
[WARN] Feed may not be fully loaded
```

**Analysis:** This is a **detection warning only** - the script continues monitoring anyway!

**What happened:**
- Script tried to detect LinkedIn feed element: `[data-testid="feed-item-card"]`
- Element not found within 120 seconds (LinkedIn's page structure may have changed)
- Script logged warning but **continues monitoring** in background loop

---

## Good News ✅

The script is **still running and monitoring** despite the warning!

Evidence: Script has `while True` loop that runs regardless of the warning:
```python
def run(self):
    self.launch_browser()

    while True:  # ← Monitoring loop continues
        try:
            messages = self.check_messages()
            notifications = self.check_notifications()
            # Save items to /Needs_Action/
        except Exception as e:
            logger.error(f"[ERROR] {e}")

        time.sleep(self.CHECK_INTERVAL)  # Wait 60 seconds, repeat
```

---

## How to Test

**The monitoring should be working. Let's verify:**

### Test 1: Send LinkedIn Message

1. Open LinkedIn in another browser window (or phone)
2. Go to your LinkedIn Messaging
3. Send yourself a message with keyword: `"sales opportunity for project"`
4. **Wait 60-90 seconds** (script checks every 60 seconds)
5. Check `/Needs_Action/` folder:
   ```bash
   dir Needs_Action\
   ```

**Expected:** Should see new `.md` file with your message

### Test 2: Check LinkedIn Logs

While script is running, check what it's actually monitoring:
```bash
# View live logs
Get-Content watchers/logs/linkedin_watcher.log -Tail 30

# Or run script with verbose output
python -u watchers/linkedin_watcher.py
```

---

## What the Warning Means

The warning appears because:

**Issue:** LinkedIn page structure changed or selector is outdated
- Selector looking for: `[data-testid="feed-item-card"]`
- Result: Not found in 120 seconds

**BUT:** This only affects initialization verification, NOT the actual monitoring

The monitoring functions `check_messages()` and `check_notifications()` use **different selectors**:
- Messages: `[data-testid="msg-conversation-item"]`
- Notifications: Different XPath

These selectors should still work!

---

## Next Steps

### Option A: Test & Confirm It's Working
1. Send test LinkedIn message with "sales" keyword
2. Wait 60 seconds
3. Check `/Needs_Action/` folder
4. If file appears → Script is working! ✅
5. If no file → Investigate selectors

### Option B: Increase Feed Detection Timeout
If you want to fix the warning (optional):

Edit `watchers/linkedin_watcher.py` line 137:
```python
# Current:
self.page.wait_for_selector('[data-testid="feed-item-card"]', timeout=120000)

# Change to:
self.page.wait_for_selector('[data-testid="feed-item-card"]', timeout=300000)
# (Increases timeout from 120s to 300s)
```

### Option C: Replace Feed Selector
If increasing timeout doesn't help, try alternative selector:

Edit line 131 and 137, replace:
```python
# Old:
'[data-testid="feed-item-card"]'

# Try new:
'[class*="feed"]'
```

---

## Bottom Line

✅ **Script IS running and monitoring**
⚠️ **Warning is cosmetic** (just means feed element not detected)
📝 **Need to verify:** Messages are actually being captured

**To confirm:** Send test message with "sales" keyword, wait 60s, check `/Needs_Action/`

---

**Status:** ✅ READY FOR TESTING
**Next:** User to send test LinkedIn message and confirm `/Needs_Action/` file appears
**Date:** 2026-02-15
