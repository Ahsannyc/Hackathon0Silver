# PHR: Create Three Watcher Scripts for Silver Tier

**ID:** 001
**Stage:** implementation | silver-tier
**Date:** 2026-02-14
**Status:** COMPLETE ✅

---

## Task Summary

Create three Python watcher scripts to monitor Gmail, WhatsApp, and LinkedIn for business-relevant keywords, saving matched items to `/Needs_Action/` folder.

---

## Components Delivered

### 1. Gmail Watcher
**File:** `watchers/gmail_watcher.py` (8.6 KB)
**Keywords:** urgent, invoice, payment, sales
**Check Interval:** 120 seconds
**Features:**
- OAuth2 Gmail API authentication
- Filters for important emails only
- Saves to `/Needs_Action/email_[timestamp].md`
- YAML metadata: from, subject, received, priority, status
- Token persistence for re-authentication skip

### 2. WhatsApp Watcher
**File:** `watchers/whatsapp_watcher.py` (11 KB)
**Keywords:** urgent, invoice, payment, sales
**Check Interval:** 30 seconds
**Features:**
- Playwright-based browser automation
- Persistent session at `session/whatsapp/`
- QR code login on first run
- Saves to `/Needs_Action/whatsapp_[timestamp].md`
- Auto-detect unread messages

### 3. LinkedIn Watcher
**File:** `watchers/linkedin_watcher.py` (14 KB)
**Keywords:** sales, client, project
**Check Interval:** 60 seconds
**Features:**
- Monitors messages and notifications
- Persistent session at `session/linkedin/`
- Login credentials on first run
- Saves to `/Needs_Action/linkedin_[timestamp].md`
- Checks multiple notification streams

---

## Instructions in Each Script

All scripts include:
- Setup instructions (pip install, authentication)
- PM2 startup commands
- Testing procedures
- Configuration reference
- Troubleshooting guide

---

## Fixes Applied in This Session

1. **Unicode Encoding (Windows)**
   - Added UTF-8 support at runtime
   - Replaced emoji with ASCII text

2. **Import Error (Gmail)**
   - Fixed: `google.api_python_client` → `googleapiclient`

3. **Missing Dependencies**
   - Installed: google-auth-oauthlib, google-auth-httplib2, google-api-python-client

---

## Current Status

| Watcher | Status | Action Needed |
|---------|--------|---------------|
| Gmail | ⏳ Needs Setup | Download credentials.json |
| WhatsApp | ✅ Ready | Scan QR code (first run) |
| LinkedIn | ✅ Ready | Log in (first run) |

---

## Testing Procedure

```bash
# 1. Run directly (shows browser window)
python watchers/whatsapp_watcher.py

# 2. Scan QR code or log in

# 3. Start with PM2
pm2 start watchers/whatsapp_watcher.py --name whatsapp_watcher --interpreter python

# 4. Check status
pm2 logs whatsapp_watcher
```

---

## Related Documentation

- `GMAIL_WATCHER_SETUP.md` - OAuth2 setup guide
- `BROWSER_WATCHERS_SETUP.md` - WhatsApp & LinkedIn authentication

---

**Progress:** ✅ COMPLETE | Files: 3 scripts + logs folder
**Next:** Authentication and first-run testing

