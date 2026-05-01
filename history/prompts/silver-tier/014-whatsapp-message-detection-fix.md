# PHR: WhatsApp Message Detection Selectors Update

**ID:** 014
**Stage:** silver-tier | debugging
**Date:** 2026-02-15
**Status:** 🔄 FIXING NOW

---

## Issue Summary

WhatsApp watcher successfully authenticates but **fails to detect/capture messages**.

**Log Evidence:**
```
[OK] WhatsApp Web loaded (network idle)  ← Authentication works ✅
(No messages detected)  ← Message detection broken ❌
(No files created in /Needs_Action/)
```

**Root Cause:** Message detection uses outdated selectors:
- `[data-testid="chat-list-item"]` - no longer exists
- `[data-testid="unread-badge"]` - no longer exists
- `[data-testid="msg-container"]` - no longer exists
- `[data-testid="msg"]` - no longer exists

These selectors were valid in older WhatsApp Web versions but WhatsApp changed their UI structure significantly.

---

## Problem Analysis

**Current Code Issues (lines 159-220):**

```python
def get_unread_messages(self):
    # Line 159: Try to find chat items (outdated selector)
    chat_items = self.page.query_selector_all('[data-testid="chat-list-item"]')

    # Line 168: Look for unread badge (outdated)
    unread_badge = chat_item.query_selector('[data-testid="unread-badge"]')

    # Line 182: Find messages container (outdated)
    messages_container = self.page.query_selector('[data-testid="msg-container"]')

    # Line 184: Find message elements (outdated)
    last_message = self.page.query_selector_all('[data-testid="msg"]')
```

All these selectors fail silently, caught by `except` blocks, returning no messages.

---

## Solution Approaches

### Option A: Simple Workaround (Recommended for Now)
Use more generic CSS selectors that are less likely to break:
- Use `div` elements instead of data-testid
- Use role-based selectors if available
- Fall back to broader XPath queries

### Option B: Alternative Method
Instead of detecting unread messages with selectors, we could:
1. Keep a list of seen conversations
2. Click through recent conversations
3. Get any new messages since last check
4. Compare timestamps

### Option C: Message Polling via Browser Logs
Use Playwright's ability to monitor network requests:
1. Listen for WhatsApp API calls
2. Detect new messages from API responses
3. Extract message content from API data

---

## Immediate Fix (Option A)

**Strategy:** Use more flexible selectors and error handling

**Changes needed in `get_unread_messages()` function:**

```python
def get_unread_messages(self) -> List[Dict]:
    """Fetch unread messages with keywords"""
    try:
        messages = []

        # Method 1: Try new structure (current WhatsApp)
        try:
            # WhatsApp stores conversations in specific containers
            # Try multiple selector approaches
            chat_items = None

            # Try approach 1: div with aria-label
            chat_items = self.page.query_selector_all('div[aria-label*="Chat"]')

            if not chat_items or len(chat_items) == 0:
                # Try approach 2: list items
                chat_items = self.page.query_selector_all('[role="button"]')

            if not chat_items or len(chat_items) == 0:
                # Try approach 3: conversation list divs
                chat_items = self.page.query_selector_all('div[class*="conversation"]')

            if chat_items:
                logger.info(f"Found {len(chat_items)} conversations")

        except Exception as e:
            logger.debug(f"Could not find chat items: {e}")

        # Method 2: If no items found, try alternative approach
        if not chat_items or len(chat_items) == 0:
            logger.debug("No chat items found, trying alternative method")
            # Could implement alternative detection here
            return messages

        # Process found conversations...
        return messages

    except Exception as e:
        logger.error(f"[ERROR] Error fetching messages: {e}")
        return []
```

---

## Why This Happened

WhatsApp Web frequently updates its UI structure and data-testid values. The selectors in the original script were:
- Written for an older version of WhatsApp Web
- Never updated when WhatsApp changed their UI
- Now completely mismatched with current HTML

This is a common problem with web scraping - external websites change without warning.

---

## Testing Challenge

**The real challenge:** We can't easily find the new selectors without inspecting the current WhatsApp Web page in a browser's developer tools.

**What would be needed:**
1. Open WhatsApp Web in a browser
2. Right-click on a conversation → "Inspect"
3. Find the actual HTML structure and class names
4. Update the selectors in the code
5. Test the detection

---

## Temporary Solution Available

**Until we fix selectors, users could:**

**Option 1: Manual Testing Setup**
- Keep WhatsApp watcher running
- Don't depend on it detecting messages for now
- Focus on testing other watchers (Gmail works!)

**Option 2: Try Alternative Approach**
- Switch to testing LinkedIn or Gmail
- Come back to WhatsApp once we understand current selectors
- Both have same issue but need different fixes

**Option 3: Community Solution**
- Check GitHub for updated Playwright WhatsApp examples
- Look for recent WhatsApp Web scraping libraries
- See if they have new selector information

---

## Next Steps

**Immediate (15 minutes):**
1. Try generic selector approach (Option A above)
2. Test if ANY messages are detected

**If that fails (30 minutes):**
1. Inspect WhatsApp Web in browser dev tools
2. Identify new HTML structure
3. Update selectors accordingly

**Alternative (5 minutes):**
1. Test Gmail watcher instead (known working)
2. Come back to WhatsApp/LinkedIn later
3. Get PM2 setup with Gmail watcher running

---

## Recommendation

**Given time constraints:**

**Option A (Recommended):**
Skip WhatsApp/LinkedIn testing for now, focus on:
1. Verify Gmail watcher works with PM2
2. Set up PM2 process management
3. Configure daily briefing scheduler
4. Get the core system running

**Option B:**
Try one more selector fix attempt, if it doesn't work, move to Phase 5 with Gmail

---

**Status:** 🔄 FIXING NOW
**User Action Required:** Test fix or choose alternative approach
**Estimated Fix Time:** 15-30 minutes depending on approach
**Date:** 2026-02-15
