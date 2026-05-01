# PHR: Create Email MCP Server for Gmail Integration

**ID:** 004
**Stage:** implementation | silver-tier
**Date:** 2026-02-14
**Status:** COMPLETE ✅

---

## Task Summary

Create a Node.js MCP (Model Context Protocol) server for Gmail integration with draft/send capabilities and HITL approval workflow.

---

## Implementation Details

**Location:** `mcp_servers/email-mcp/`

**Files Created:**
- `index.js` (19 KB) - Core MCP server implementation
- `package.json` - Dependencies configuration
- `README.md` - Full API documentation
- `QUICK_START.md` - Setup guide
- `mcp.json` - Server registration (project root)

---

## Provided Tools

### 1. `draft_email`
**Purpose:** Create email draft for review

**Input:**
```json
{
  "to": "recipient@example.com",
  "subject": "Invoice Follow-up",
  "body": "Email content...",
  "cc": "optional@example.com",
  "bcc": "optional@example.com"
}
```

**Output:**
- Saves to `/Plans/email_draft_[timestamp].md`
- Creates YAML metadata
- Moves to `/Pending_Approval/` for HITL

**Example:**
```markdown
---
type: email_draft
to: client@example.com
subject: Invoice #123 Follow-up
created: 2026-02-14T10:30:45
status: pending
approval_required: true
---

Dear Client,

I wanted to follow up on invoice #123...
```

### 2. `send_email`
**Purpose:** Send email (requires prior approval)

**Requirements:**
- Draft must exist in `/Plans/email_draft_[hash].md`
- Approval file must exist in `/Approved/email_draft_[hash].md`

**Input:**
```json
{
  "draft_id": "[timestamp]_[hash]",
  "approved": true
}
```

**Output:**
- Email sent via Gmail API
- File moved to `/Done/`
- Execution logged

### 3. `get_email_status`
**Purpose:** Check email queue status

**Output:**
```json
{
  "pending_drafts": 3,
  "awaiting_approval": 2,
  "completed": 15
}
```

### 4. `authenticate_gmail`
**Purpose:** OAuth2 authentication flow

**Use Once:** On first run
- Opens browser
- User logs in
- Token saved for future use

---

## Architecture

**MCP Pattern:**
```
Claude (AI)
    ↓
MCP Server (Tools/Handlers)
    ↓
Gmail API (OAuth2)
    ↓
User Gmail Account
```

**File-Based HITL:**
1. Draft → `/Plans/email_draft_[hash].md`
2. Await approval → `/Pending_Approval/`
3. Human moves to → `/Approved/`
4. Server detects → Executes send
5. Complete → `/Done/`

---

## Setup

### Quick Start (2 minutes)

```bash
# 1. Install Node.js dependencies
cd mcp_servers/email-mcp
npm install

# 2. Configure credentials (same as Gmail watcher)
# Copy credentials.json to project root

# 3. Server auto-starts via mcp.json
# Or start manually:
node index.js
```

### Registration

**File:** `mcp.json` (project root)
```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["mcp_servers/email-mcp/index.js"],
      "autoStart": true
    }
  }
}
```

---

## Integration Points

**Reads From:**
- Gmail API (OAuth2)
- `/Plans/` - Email drafts
- `/Approved/` - Approval confirmations

**Writes To:**
- `/Plans/` - Draft files
- `/Pending_Approval/` - For HITL
- `/Done/` - Completed emails
- Google Gmail account - Sent emails

**Integrates With:**
- Ralph Loop (draft creation)
- HITL Approval Handler (approval detection)
- Auto LinkedIn Poster (email sending)

---

## Usage Example

**Ralph Loop wants to send an email:**

1. **Ralph calls MCP:** `draft_email(to, subject, body)`
2. **MCP Server:**
   - Validates inputs
   - Creates `/Plans/email_draft_abc123.md`
   - Moves to `/Pending_Approval/email_draft_abc123.md`
   - Returns success

3. **Human Reviews:**
   - Opens draft in editor
   - Approves/rejects

4. **HITL Handler detects approval:**
   - Finds file in `/Approved/`
   - Calls MCP: `send_email(draft_id)`
   - MCP Server sends via Gmail
   - Moves to `/Done/`

---

## Error Handling

- ✅ Validates email addresses
- ✅ Checks for missing credentials
- ✅ Handles OAuth token refresh
- ✅ Provides detailed error messages
- ✅ Logs all operations

---

## Security

- ✅ OAuth2 authentication (not passwords)
- ✅ Token stored securely
- ✅ HITL approval required for sending
- ✅ File-based audit trail
- ✅ No credentials in code

---

## Documentation

**Files:**
- `mcp_servers/email-mcp/README.md` - Full API reference
- `mcp_servers/email-mcp/QUICK_START.md` - Setup guide
- `EMAIL_MCP_SETUP.md` - Integration guide

---

**Progress:** ✅ COMPLETE | Status: Ready for integration
**Next:** HITL Approval Handler implementation

