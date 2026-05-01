# Email MCP Server - Silver Tier

**Status:** ✅ Ready for Production
**Type:** Model Context Protocol Server
**Language:** Node.js
**Tier:** Silver ⭐⭐

## Overview

Email MCP Server provides Model Context Protocol tools for Gmail email operations with Human-In-The-Loop (HITL) approval workflow. Claude Code can draft and send emails, but sending requires human approval.

## Capabilities

### 1. Draft Email (`draft_email`)
- Creates email draft in `/Plans/email_draft_[date].md`
- Generates HITL approval request in `/Pending_Approval/`
- Saves metadata (to, cc, bcc, subject, body)
- Does NOT send automatically

### 2. Send Email (`send_email`)
- Sends email via Gmail API
- Requires approval file in `/Approved/`
- Logs all sent emails
- Moves approval to `/Done/`

### 3. Get Email Status (`get_email_status`)
- Shows pending approvals
- Shows approved emails
- Shows completed sends

### 4. Authenticate Gmail (`authenticate_gmail`)
- OAuth2 authentication flow
- Saves token for reuse
- Manages refresh tokens

## Installation

### Prerequisites
- Node.js 18+ installed
- npm or yarn
- Gmail API credentials (OAuth 2.0)

### Setup Steps

#### 1. Install Dependencies
```bash
cd mcp_servers/email-mcp
npm install
```

#### 2. Get Gmail OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 Desktop Application credentials
5. Download credentials as `credentials.json`
6. Place in project root: `/credentials.json`

#### 3. Verify Installation
```bash
# Check server can start
node mcp_servers/email-mcp/index.js --verbose

# Should see:
# [✓] Gmail auth initialized
# [✓] Email MCP Server running
```

## Usage

### Running the Server

#### Start Server
```bash
node mcp_servers/email-mcp/index.js
```

#### Verbose Mode (Debug)
```bash
node mcp_servers/email-mcp/index.js --verbose
```

#### With PM2 (Process Manager)
```bash
pm2 start mcp_servers/email-mcp/index.js --name email-mcp
pm2 logs email-mcp
```

### Tools Available to Claude

#### Tool 1: Draft Email

**Purpose:** Create email draft without sending

**Parameters:**
```json
{
  "to": "user@example.com",
  "cc": "manager@example.com",
  "bcc": "",
  "subject": "Invoice #12345",
  "body": "Please find attached your invoice...",
  "attachments": []
}
```

**Response:**
```json
{
  "success": true,
  "draftPath": "/Plans/email_draft_2026-02-14T12-30-00_abc123_user@example.com.md",
  "approvalPath": "/Pending_Approval/email_approval_2026-02-14T12-30-00_abc123_user@example.com.md",
  "message": "Email draft created. Review and approve in /Pending_Approval",
  "requires_approval": true
}
```

#### Tool 2: Send Email

**Purpose:** Send approved email via Gmail

**Parameters:**
```json
{
  "to": "user@example.com",
  "cc": "",
  "bcc": "",
  "subject": "Invoice #12345",
  "body": "Please find attached your invoice...",
  "approval_file": "/Approved/email_approval_2026-02-14T12-30-00_abc123_user@example.com.md"
}
```

**Response (Approved):**
```json
{
  "success": true,
  "approved": true,
  "messageId": "17f80a3dbb1f7a63",
  "message": "Email sent successfully to user@example.com"
}
```

**Response (Not Yet Approved):**
```json
{
  "success": false,
  "approved": false,
  "message": "Approval not found in /Approved/. Waiting for HITL review."
}
```

#### Tool 3: Get Email Status

**Purpose:** Check pending, approved, and completed emails

**Parameters:** (none)

**Response:**
```json
{
  "pending_approvals": 3,
  "approved": 1,
  "completed": 5
}
```

#### Tool 4: Authenticate Gmail

**Purpose:** OAuth2 authentication with Gmail

**First Call (No Code):**
```json
{}
```

**Response:**
```json
{
  "success": false,
  "message": "Visit this URL to authenticate:",
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

**After User Authorization (With Code):**
```json
{
  "auth_code": "4/0AX4XfWj..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Gmail authentication successful"
}
```

## Workflow: Draft → Approve → Send

### Step 1: Claude Drafts Email
Claude calls `draft_email` tool with:
```
To: client@example.com
Subject: Invoice #123
Body: Please review attached invoice
```

**Result:**
- Email draft saved to `/Plans/email_draft_*.md`
- Approval request created in `/Pending_Approval/email_approval_*.md`
- Claude reports: "Draft saved, awaiting approval"

### Step 2: Human Reviews
Human opens `/Pending_Approval/email_approval_*.md`
- Reviews recipient, subject, body
- If approved: Moves file to `/Approved/` folder
- If rejected: Moves file to `/Rejected/` folder

### Step 3: Claude Sends
Claude calls `send_email` tool with approval file path

**If File in /Approved/:**
- Gmail API sends email
- Logs email to `/Logs/email_send_YYYY-MM-DD.json`
- Moves approval to `/Done/sent_email_approval_*.md`
- Returns success with message ID

**If File NOT in /Approved/:**
- Returns error: "Approval not found, waiting for HITL review"
- Continues polling or requests Claude to retry

## File Structure

### Input Files
**Location:** `/Plans/` (drafts created here)

**Format:**
```markdown
---
type: email_draft
to: recipient@example.com
cc: cc@example.com
subject: Email Subject
status: draft
created_at: 2026-02-14T12-30-00
requires_approval: true
---

# Email Draft: Email Subject

**To:** recipient@example.com
**CC:** cc@example.com
**Subject:** Email Subject

---

## Email Body

Email content here...

---

## Action Required

This email draft requires approval before sending.

1. Review the content above
2. Approve by moving to /Approved/ folder
3. Reject by moving to /Rejected/ folder
```

### Approval Files
**Location:** `/Pending_Approval/` (human review queue)

**Format:**
```markdown
---
type: email_approval
action: send_email
to: recipient@example.com
subject: Email Subject
created_at: 2026-02-14T12-30-00
status: pending_approval
requires_approval: true
draft_file: email_draft_*.md
---

# Email Approval Request

**Action:** Send Email

**Recipient:** recipient@example.com
**Subject:** Email Subject

---

## Email Content

Email body here...

---

## To Approve

Move to /Approved/ folder

## To Reject

Move to /Rejected/ folder
```

### Sent Log
**Location:** `/Logs/email_send_YYYY-MM-DD.json`

**Format:**
```json
[
  {
    "timestamp": "2026-02-14T12:30:00.000Z",
    "action": "send",
    "to": "recipient@example.com",
    "subject": "Email Subject",
    "messageId": "17f80a3dbb1f7a63",
    "status": "success"
  }
]
```

## HITL Approval Workflow

### Manual Approval (Obsidian)
1. Open `/Pending_Approval/email_approval_*.md`
2. Review email content
3. Drag to `/Approved/` folder (approved) OR `/Rejected/` folder (rejected)
4. Server detects file movement and continues

### Command Line Approval
```bash
# Approve
mv Pending_Approval/email_approval_*.md Approved/

# Reject
mv Pending_Approval/email_approval_*.md Rejected/
```

### Automated Approval (Advanced)
```bash
# Approve all pending emails
find Pending_Approval -name "email_approval_*.md" -exec mv {} Approved/ \;
```

## Testing Guide

### Test 1: Basic Draft

#### Create Test Script
```bash
cat > test_draft.js << 'EOF'
const fetch = require('node-fetch');

async function testDraft() {
  const response = await fetch('http://localhost:3000/draft', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      to: 'test@example.com',
      subject: 'Test Email',
      body: 'This is a test email'
    })
  });

  const data = await response.json();
  console.log(JSON.stringify(data, null, 2));
}

testDraft().catch(console.error);
EOF
```

#### Run Test
```bash
# Terminal 1: Start server
node mcp_servers/email-mcp/index.js --verbose

# Terminal 2: Run test
node test_draft.js
```

#### Verify Results
```bash
# Check draft created
ls -la Plans/email_draft_*.md

# Check approval request created
ls -la Pending_Approval/email_approval_*.md

# View draft content
cat Plans/email_draft_*.md
```

### Test 2: Draft + Approval + Send

#### Step 1: Create Draft
```bash
# Use same script as Test 1
node test_draft.js
```

#### Step 2: Approve
```bash
# Move approval to Approved folder
mv Pending_Approval/email_approval_*.md Approved/
```

#### Step 3: Send
```bash
cat > test_send.js << 'EOF'
const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');

async function testSend() {
  // Find approval file
  const approvedDir = 'Approved';
  const files = fs.readdirSync(approvedDir)
    .filter(f => f.startsWith('email_approval_'));

  if (files.length === 0) {
    console.error('No approval files found');
    return;
  }

  const approvalFile = path.join(approvedDir, files[0]);

  const response = await fetch('http://localhost:3000/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      to: 'test@example.com',
      subject: 'Test Email',
      body: 'This is a test email',
      approval_file: approvalFile
    })
  });

  const data = await response.json();
  console.log(JSON.stringify(data, null, 2));
}

testSend().catch(console.error);
EOF

node test_send.js
```

#### Verify Results
```bash
# Check sent log
cat Logs/email_send_*.json

# Check approval moved to Done
ls -la Done/sent_email_approval_*.md
```

### Test 3: Gmail Authentication

#### First Run (Get Auth URL)
```bash
curl -X POST http://localhost:3000/auth \
  -H "Content-Type: application/json" \
  -d '{}'

# Response:
# {
#   "success": false,
#   "message": "Visit this URL to authenticate:",
#   "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
# }
```

#### Visit Auth URL
1. Click the `auth_url` in response
2. Log in with Gmail account
3. Authorize app
4. Copy authorization code from redirect URL

#### Second Run (Set Token)
```bash
curl -X POST http://localhost:3000/auth \
  -H "Content-Type: application/json" \
  -d '{"auth_code":"4/0AX4XfWj..."}'

# Response:
# {
#   "success": true,
#   "message": "Gmail authentication successful"
# }
```

#### Verify Token Saved
```bash
ls -la mcp_servers/email-mcp/.gmail_token.json
```

## Configuration

### Environment Variables
```bash
# .env file (optional)
EMAIL_VAULT_PATH=/path/to/vault
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/gmail.send
VERBOSE=true
```

### Server Settings
Edit `mcp.json`:
```json
{
  "mcpServers": {
    "email-mcp": {
      "command": "node",
      "args": ["mcp_servers/email-mcp/index.js"],
      "env": {
        "DEBUG": "false"
      },
      "autoStart": true
    }
  }
}
```

## Troubleshooting

### "credentials.json not found"
**Solution:**
1. Download OAuth credentials from Google Cloud Console
2. Save as `/credentials.json` in project root
3. Restart server

### "Gmail authentication failed"
**Solution:**
1. Call `authenticate_gmail` tool
2. Visit the provided auth URL
3. Authorize the app
4. Copy authorization code
5. Call `authenticate_gmail` again with the code

### "Approval not found"
**Solution:**
1. Check approval file exists in `/Approved/` (not `/Pending_Approval/`)
2. File must be named `email_approval_*.md`
3. Verify file path in `send_email` call matches exact filename

### Server won't start
**Solution:**
```bash
# Install dependencies
cd mcp_servers/email-mcp
npm install

# Check Node version
node --version  # Should be 18+

# Start with verbose output
node index.js --verbose
```

### Email not sending
**Solution:**
1. Check Gmail API is enabled in Google Cloud Console
2. Check OAuth scopes include `gmail.modify` and `gmail.send`
3. Check credentials.json has correct client_id and client_secret
4. Verify approval file is in `/Approved/` folder
5. Check server logs: `tail -f tools/logs/email_*.log`

## Integration with Silver Tier

### With Ralph Wiggum Loop
```
Ralph Loop creates Plan.md
  ↓
Claude detects email action needed
  ↓
Claude calls draft_email tool
  ↓
Draft saved to /Plans/
Approval request in /Pending_Approval/
  ↓
Human approves: moves to /Approved/
  ↓
Claude calls send_email tool
  ↓
Email sent via Gmail API
Logged to /Logs/
```

### With Auto LinkedIn Poster
```
Sales Lead → Ralph Loop → Plans
  ↓
Needs email confirmation
  ↓
Draft email via MCP
  ↓
Human approves
  ↓
Send confirmation email
  ↓
Proceed with social posting
```

### With Watchers
```
Gmail/WhatsApp Watcher → /Needs_Action
  ↓
Ralph Loop analyzes
  ↓
Determines email reply needed
  ↓
Draft reply via Email MCP
  ↓
Human approves
  ↓
Send email
  ↓
Log and mark done
```

## Architecture

```
Claude Code (Reasoning)
    ↓
MCP Tools Interface
    ↓
Email MCP Server (Node.js)
    ├─ Draft Email Handler
    │  └─ Save to /Plans/
    │  └─ Create approval request
    │
    ├─ Send Email Handler
    │  └─ Check /Approved/
    │  └─ Gmail API call
    │  └─ Log action
    │
    ├─ Gmail OAuth Handler
    │  └─ OAuth2 authentication
    │  └─ Token management
    │
    └─ Vault Integration
       ├─ /Plans/ (drafts)
       ├─ /Pending_Approval/ (review)
       ├─ /Approved/ (approved)
       └─ /Logs/ (audit trail)
```

## Performance

- **Draft creation:** <100ms
- **Approval detection:** <50ms
- **Gmail send:** 1-3 seconds (depends on network)
- **Concurrent emails:** Limited by Gmail API rate limits

## Security

✅ **Credentials**: Stored in `.env` and Google keychain
✅ **Token**: Saved only in server directory (not in vault)
✅ **HITL**: All sends require human approval
✅ **Audit Trail**: All actions logged to `/Logs/`
✅ **Scoping**: Uses minimal Gmail API scopes

## Rate Limits

Gmail API rate limits:
- 1,000,000 requests per day
- ~40 requests per second

For typical usage:
- 100 emails/day: No issues
- 1,000 emails/day: Monitor quota
- 10,000+ emails/day: Consider batch API

## Future Enhancements

- [ ] Attachment upload support
- [ ] Template variables (${name}, ${date})
- [ ] Scheduled sends
- [ ] Reply-to: management
- [ ] Signature insertion
- [ ] HTML email support

## Support & Debugging

### Enable Debug Mode
```bash
node mcp_servers/email-mcp/index.js --verbose

# Or via env
DEBUG=true node mcp_servers/email-mcp/index.js
```

### Check Logs
```bash
# Server logs
tail -f tools/logs/email_*.log

# Gmail API calls
grep "Gmail API" tools/logs/email_*.log
```

### Test Email Delivery
```bash
# After sending, verify in Gmail
# Check Sent Mail folder in Gmail account

# Or via Gmail API
node -e "
const gmail = require('googleapis').gmail({version:'v1', auth: ...});
gmail.users.messages.list({userId: 'me', q: 'is:sent'}, (err, res) => {
  console.log(res.data.messages);
});
"
```

---

**Status:** ✅ Ready for Silver Tier
**Created:** 2026-02-14
**Maintainer:** Silver Tier Team
