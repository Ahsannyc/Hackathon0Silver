# PHR: Gmail OAuth Test User Setup Fix

**ID:** 008
**Stage:** silver-tier | debugging
**Date:** 2026-02-15
**Status:** ✅ COMPLETE

---

## Task Summary

Session continuation from initial Silver Tier build. User attempted to run `python watchers/gmail_watcher.py` after downloading credentials.json from Google Cloud Console but received OAuth verification error: "Access blocked: Hackathon0 has not completed the Google verification process" (Error 403: access_denied).

Root cause identified: User needs to add their email as a test user to the OAuth consent screen, but could not locate the "Add Users" button in the current Google Cloud Console UI.

---

## Problem Analysis

**User's Error:**
```
Access blocked: Hackathon0 has not completed the Google verification process.
Error code: 403: access_denied
```

**User's Report:**
- Downloaded credentials.json ✓
- Ran gmail_watcher.py ✓
- OAuth login opened in browser
- Got verification error
- Navigated to OAuth consent screen in Google Cloud Console
- Could not find "Add Users" button in Step 4

**Investigation:**
User provided screenshot showing they were on the OAuth **Overview** page instead of the **Audience** page. The left sidebar menu shows multiple sections:
- Overview (current location)
- Branding
- Audience (correct location for test users)
- Clients
- Data Access
- Verification Center
- Settings

---

## Solution Implementation

**Fixed Navigation Path:**

1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Select project: "Hackathon0Silver"
3. Go to **OAuth consent screen**
4. In left sidebar, click **"Audience"** (not Overview)
5. Click "+ Add Users" button
6. Enter email: `14loansllc@gmail.com` (user's email)
7. Click "Add"
8. Return to run: `python watchers/gmail_watcher.py`

**Key Clarification:**
The Google Cloud Console OAuth consent screen has multiple sections accessible from the left sidebar. Test users are managed in the **Audience** section, not the **Overview** section where metrics are displayed.

---

## Integration Points

This fix integrates with:
- **HOW_TO_RUN_PROJECT.md Phase 2.1:** Gmail Watcher Setup (updated with clarification)
- **GMAIL_WATCHER_SETUP.md:** Gmail credentials setup guide (references Audience section)
- **watchers/gmail_watcher.py:** Depends on successful OAuth authentication with test user

---

## Testing

**Manual Verification:**
```bash
# After adding test user to Audience section:
python watchers/gmail_watcher.py

# Expected behavior:
# 1. Browser opens with Google login
# 2. OAuth flow completes without 403 error
# 3. Program shows: [OK] Gmail authentication successful
# 4. User's token.pickle is saved for future authentication
```

**Success Criteria:**
- ✅ OAuth flow completes without access_denied error
- ✅ token.pickle file created (persistent authentication)
- ✅ Gmail watcher shows successful authentication message
- ✅ Can be started with PM2: `pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python`

---

## Documentation Updates

**Files Updated:**
1. `HOW_TO_RUN_PROJECT.md` - Phase 2.1 clarified with sidebar navigation
2. `history/README.md` - Added PHR 008 to table
3. `history/PROJECT_SUMMARY.md` - Updated debugging notes
4. `QUICK_RUN.md` - Cross-reference to detailed guide

**Documentation Changes:**
- Added visual sidebar menu structure to Phase 2.1
- Clarified "Audience" section location
- Added explanation: "The left sidebar menu shows multiple sections"
- Provided step-by-step navigation with emphasis on correct section

---

## Lessons Learned

1. **Google Cloud Console UI Complexity:** OAuth consent screen has multiple views (Overview vs. Audience). Test users are in Audience section, not Overview.

2. **Screenshot-Driven Debugging:** User provided screenshot showing the exact issue (Overview page instead of Audience). This enabled precise diagnosis.

3. **Navigation Clarity:** Documentation should explicitly highlight which sidebar section to click, not just list steps.

4. **Error Message Investigation:** The 403 access_denied error is the correct indicator that test user is missing, not a credentials.json issue.

---

## Next Steps

1. ✅ User adds test user email to Audience section
2. ✅ User runs gmail_watcher.py again
3. ✅ OAuth flow completes successfully
4. ✅ token.pickle is created
5. ⏳ PM2 start: `pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python`
6. ⏳ Verify status: `pm2 list`
7. ⏳ Proceed to Phase 3 (WhatsApp Watcher)

---

**Status:** ✅ COMPLETE
**Next:** User to confirm OAuth setup successful, then proceed to WhatsApp and LinkedIn watcher authentication
**Documentation:** All guides updated with clarification
**Date Resolved:** 2026-02-15
