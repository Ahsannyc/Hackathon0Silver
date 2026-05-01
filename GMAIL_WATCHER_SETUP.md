# Gmail Watcher Setup Guide

**Status:** ✅ Fixed and Ready
**Issue Resolved:** Unicode encoding errors on Windows
**Remaining:** OAuth2 credentials file setup

---

## Quick Summary

The `gmail_watcher.py` script monitors your Gmail account for important emails with specific keywords (urgent, invoice, payment, sales) and saves them to `/Needs_Action/` for further processing.

**What was fixed:**
- ✅ Missing Google API library imports (installed google-auth-oauthlib)
- ✅ Unicode encoding errors on Windows (UTF-8 support added)
- ✅ Incorrect import statement (googleapiclient vs google.api_python_client)

**What's needed:**
- ⏳ OAuth2 credentials.json file from Google Cloud Console

---

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a Project"** → **"NEW PROJECT"**
3. Enter project name: `Hackathon0Silver`
4. Click **Create**
5. Wait for project creation (~1 minute)

---

## Step 2: Enable Gmail API

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for **"Gmail API"**
3. Click **Gmail API** → Click **Enable**
4. Wait for it to enable

---

## Step 3: Create OAuth2 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. You'll see a warning: **"To create an OAuth client ID, you must first create an OAuth consent screen"**
4. Click **"CREATE CONSENT SCREEN"**

### Configure Consent Screen:

1. Select **User Type:** `External`
2. Click **Create**
3. Fill in the form:
   - **App name:** `Hackathon0Silver`
   - **User support email:** (your email)
   - **Developer contact:** (your email)
4. Click **Save and Continue**
5. Skip optional scopes (click **Save and Continue**)
6. **⚠️ IMPORTANT - Add Test Users:**
   - On the "Test users" page, click **"+ Add Users"**
   - Enter your Gmail address: `14loansllc@gmail.com` (or your actual email)
   - Click **Add**
   - Click **Save and Continue**
7. Click **Back to Dashboard**

**Why test users are required:** Without adding your email as a test user, you'll get a 403 access_denied error when running the watcher. Google blocks unverified apps unless the user is explicitly added to the test list.

---

## Step 4: Download Credentials File

1. Go back to **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Select **Application type:** `Desktop app`
4. Click **Create**
5. Click **Download** (JSON icon)
6. This downloads `client_secret_*.json`

---

## Step 5: Place credentials.json in Project Root

1. Rename the downloaded file to: `credentials.json`
2. Move it to your project root:
   ```
   C:\Users\[YourName]\Desktop\Hackathon0Silver\credentials.json
   ```

**Verify:**
```powershell
# Windows PowerShell
Test-Path ".\credentials.json"
# Should show: True
```

---

## Step 6: Test Gmail Watcher

### Test 1: Run directly to authenticate

```bash
cd C:\Users\[YourName]\Desktop\Hackathon0Silver
python watchers/gmail_watcher.py
```

**First run:** Will open a browser for OAuth2 authorization
- Google will ask: "Hackathon0Silver wants access to your Google Account"
- Click **Allow**
- Browser will show success message
- Script will save token: `.gmail_token.json`

**Expected Output:**
```
2026-02-14 14:52:28,331 - __main__ - INFO - [OK] Gmail authentication successful
2026-02-14 14:52:28,500 - __main__ - INFO - [OK] Found 0 unread important emails with keywords
```

### Test 2: Run with PM2

```powershell
# Start watcher
pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python

# Check status
pm2 list

# View logs
pm2 logs gmail_watcher

# Stop watcher
pm2 stop gmail_watcher

# Delete watcher
pm2 delete gmail_watcher
```

### Test 3: Check /Needs_Action/ folder

After sending a test email with keywords (urgent, invoice, payment, sales):

```powershell
# Should have new .md file
dir Needs_Action\
```

---

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| `credentials.json` | `project_root/` | OAuth2 credentials (DO NOT COMMIT) |
| `.gmail_token.json` | `watchers/` | OAuth2 token (auto-generated, DO NOT COMMIT) |
| `gmail_watcher.py` | `watchers/` | Watcher script |
| `gmail_watcher.log` | `watchers/logs/` | Execution logs |
| Saved emails | `Needs_Action/` | Emails matching keywords |

---

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `credentials.json` to Git
- Never commit `.gmail_token.json` to Git
- Add to `.gitignore`:
  ```
  credentials.json
  .gmail_token.json
  client_secret_*.json
  ```

---

## Troubleshooting

### Issue: "credentials.json not found"

**Solution:** Verify file exists in project root
```powershell
Test-Path ".\credentials.json"
```

If false, download again from Google Cloud Console.

### Issue: "AuthenticationError" or "Invalid credentials"

**Solution:** Delete the token and re-authenticate
```powershell
# Delete token
Remove-Item "watchers\.gmail_token.json"

# Run script to re-authenticate
python watchers/gmail_watcher.py
```

### Issue: Gmail API not enabled

**Solution:** Go to Google Cloud Console → APIs & Services → Enable Gmail API

### Issue: "Access blocked: Hackathon0 has not completed the Google verification process" (Error 403)

**Root Cause:** Your email is not added as a test user to the OAuth consent screen

**Solution:**
1. Go back to Google Cloud Console
2. Select project "Hackathon0Silver"
3. Go to **APIs & Services** → **OAuth consent screen**
4. In the left sidebar, click **"Audience"** (NOT "Overview")
   ```
   Left sidebar menu:
   ├── Overview
   ├── Branding
   ├── Audience  ← CLICK HERE
   ├── Clients
   ├── Data Access
   ├── Verification Center
   └── Settings
   ```
5. Click **"+ Add Users"**
6. Enter your email: `14loansllc@gmail.com`
7. Click **"Add"**
8. Re-run: `python watchers/gmail_watcher.py`

**Tip:** The "Add Users" button is in the Audience section, not the Overview section. Many users miss this because the Overview page shows metrics but no user management.

### Issue: Script hangs after printing "Found X emails"

**Solution:** Check file permissions in /Needs_Action/
```powershell
# Verify folder exists and is writable
New-Item -ItemType Directory -Path "Needs_Action" -Force
```

---

## Monitoring

### Check Execution Status

```powershell
# View real-time logs
pm2 logs gmail_watcher

# Check if running
pm2 list

# View saved emails
dir Needs_Action\
```

### Check Saved Emails Format

```powershell
# View a saved email
Get-Content Needs_Action\email_*.md | head -30
```

Should contain YAML frontmatter with:
```yaml
---
type: email
from: sender@example.com
subject: URGENT invoice #123
received: 2026-02-14T14:52:28
priority: high
status: pending
---
```

---

## Configuration

Edit `watchers/gmail_watcher.py` to customize:

| Parameter | Line | Default | Purpose |
|-----------|------|---------|---------|
| `KEYWORDS` | 77 | `['urgent', 'invoice', 'payment', 'sales']` | Email keywords to monitor |
| `CHECK_INTERVAL` | 78 | `120` | Check every N seconds |
| `SCOPES` | 76 | `gmail.readonly` | Gmail API permissions |

---

## Next Steps

1. ✅ Create Google Cloud Project
2. ✅ Enable Gmail API
3. ✅ Download credentials.json
4. ✅ Place in project root
5. ✅ Run script to authenticate
6. ✅ Start with PM2
7. ✅ Monitor /Needs_Action/ folder

Once complete, your Gmail watcher will automatically:
- Check Gmail every 2 minutes
- Find important emails with keywords
- Save to /Needs_Action/ for processing
- Run continuously via PM2

---

**Status:** Ready for OAuth2 setup
**Created:** 2026-02-14
**Next:** Download credentials.json and place in project root

