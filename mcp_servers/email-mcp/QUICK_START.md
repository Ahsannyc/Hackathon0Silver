# Email MCP Server - Quick Start (5 Minutes)

## 1. Installation (2 min)

```bash
# Navigate to server directory
cd mcp_servers/email-mcp

# Install dependencies
npm install

# Verify installation
node index.js --verbose
# Should show: [✓] Email MCP Server running
# Press Ctrl+C to stop
```

## 2. Setup Gmail OAuth (1 min)

**Get credentials.json:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project (if needed)
3. Enable Gmail API
4. Create OAuth 2.0 Desktop credentials
5. Download JSON file
6. Save as `/credentials.json` in project root

**First run will save token:**
```bash
node index.js
# Token saved to: mcp_servers/email-mcp/.gmail_token.json
```

## 3. Test Draft Email (1 min)

```bash
# Terminal 1: Start server
cd mcp_servers/email-mcp
node index.js

# Terminal 2: Create test draft
cat > Needs_Action/test_email.md << 'EOF'
---
type: email_request
to: test@example.com
subject: Test Email
priority: high
---

Please draft and send a test email to test@example.com
EOF

# Terminal 2: Tell Claude to draft it
# (In Claude Code)
# "Draft an email to test@example.com with subject 'Test Email' and body 'Hello, this is a test'"

# Check results
ls -la Plans/email_draft_*.md
cat Plans/email_draft_*.md
```

## 4. Test Approval + Send (1 min)

```bash
# Step 1: Approve the draft
mv Pending_Approval/email_approval_*.md Approved/

# Step 2: Tell Claude to send it
# (In Claude Code)
# "Send the approved email"

# Step 3: Verify sent
cat Logs/email_send_*.json
ls Done/sent_email_approval_*.md
```

## Quick Commands

### Start Server
```bash
node mcp_servers/email-mcp/index.js
```

### Verbose Mode (Debug)
```bash
node mcp_servers/email-mcp/index.js --verbose
```

### Check Pending Approvals
```bash
ls Pending_Approval/email_approval_*.md
cat Pending_Approval/email_approval_*.md
```

### Approve All Pending
```bash
find Pending_Approval -name "email_approval_*.md" -exec mv {} Approved/ \;
```

### View Send Log
```bash
cat Logs/email_send_*.json
```

### Clear Test Files
```bash
rm -f Plans/email_draft_*.md
rm -f Pending_Approval/email_approval_*.md
rm -f Logs/email_send_*.json
```

## How It Works (30 seconds)

```
1. Claude calls: draft_email(to, subject, body)
   ↓
2. Server creates:
   - /Plans/email_draft_*.md (what it will send)
   - /Pending_Approval/email_approval_*.md (approval request)
   ↓
3. You review and move approval to /Approved/
   ↓
4. Claude calls: send_email(...)
   ↓
5. Server detects /Approved/ file
   ↓
6. Gmail API sends email
   ↓
7. Logged to /Logs/email_send_*.json
```

## Common Use Cases

### Use Case 1: Draft Invoice Email
```
Claude: "Draft invoice email to client@example.com"
↓
Creates draft in /Plans/
↓
You: Move to /Approved/
↓
Claude: "Send the invoice email"
↓
Gmail sends invoice
```

### Use Case 2: Auto Reply
```
Watcher detects "urgent" email
↓
Ralph Loop triggers
↓
Claude drafts reply
↓
Email MCP saves draft
↓
You approve
↓
Claude sends reply
```

### Use Case 3: Notification
```
Business event triggers
↓
Claude needs to notify stakeholders
↓
Draft email via MCP
↓
You verify recipients
↓
Claude sends notification
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "credentials.json not found" | Download from Google Cloud Console, save to project root |
| "Gmail auth failed" | Delete `.gmail_token.json`, restart, re-authenticate |
| "Approval not found" | Check file is in `/Approved/` (not `/Pending_Approval/`) |
| "Email not sending" | Check Gmail API enabled, verify OAuth scopes |
| Server won't start | Run `npm install`, check Node version (18+) |

## Next Steps

1. ✅ Install server
2. ✅ Setup Gmail OAuth
3. ✅ Test draft
4. ✅ Test send
5. 📍 Integrate with Ralph Loop (optional)
6. 📍 Add to PM2 for always-on (optional)

## Always-On Setup (Optional)

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start mcp_servers/email-mcp/index.js --name email-mcp

# Check logs
pm2 logs email-mcp

# Auto-restart on reboot
pm2 save
pm2 startup
```

---

**Ready to go!** 🚀
Start the server and begin drafting emails with Claude.
