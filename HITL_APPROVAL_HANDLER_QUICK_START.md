# HITL Approval Handler - Quick Start

**Status:** ✅ Ready
**Skill ID:** `@HITL Approval Handler`
**Location:** `skills/hitl_approval_handler.py`

## 30-Second Overview

```
Agent creates approval request
  ↓
File moves to /Pending_Approval/
  ↓
YOU REVIEW & DECIDE
  ↓
Move to /Approved/ → Executes
Move to /Rejected/ → Logged, not executed
  ↓
HITL Handler detects approval
  ↓
Executes action via MCP
  ↓
Logs to /Logs/hitl_[date].md
```

## Quick Commands

### Run Once (Process Approved)
```bash
python3 skills/hitl_approval_handler.py --once
```

### Watch Continuously (Real-Time)
```bash
python3 skills/hitl_approval_handler.py --watch
```

### Custom Interval (e.g., 30 seconds)
```bash
python3 skills/hitl_approval_handler.py --watch --interval 30
```

### With PM2 (Always-On)
```bash
pm2 start skills/hitl_approval_handler.py --name hitl_handler --interpreter python3
pm2 logs hitl_handler
pm2 delete hitl_handler
```

## Approval Workflow

### Step 1: Approval Request Created
```
/Pending_Approval/email_approval_2026-02-14_abc123_user@example.com.md

---
type: email_approval
action: send_email
to: user@example.com
subject: Invoice #123
status: pending_approval
---

Recipient: user@example.com
Subject: Invoice #123
Body: ...
```

### Step 2: You Decide
```bash
# APPROVE
mv Pending_Approval/email_approval_*.md Approved/

# OR REJECT
mv Pending_Approval/email_approval_*.md Rejected/
```

### Step 3: Handler Executes
```
HITL Approval Handler detects file in /Approved/
  ↓
Executes: Send email via Email MCP
  ↓
Logs: /Logs/hitl_2026-02-14.md
  ↓
Archives: /Done/executed_email_approval_*.md
```

## Agent Commands

```
@HITL Approval Handler check Pending_Approval
@HITL Approval Handler process approved
@HITL Approval Handler monitor
```

## Supported Actions

| Type | What | Where |
|------|------|-------|
| `email_approval` | Send email | /Approved/ → Email MCP |
| `linkedin_approval` | Post to LinkedIn | /Approved/ → LinkedIn API |
| `payment_approval` | Process payment | /Approved/ → Payment MCP |

## Folder Structure

```
/Pending_Approval/   ← Waiting for you
/Approved/           ← You approved (handler executes)
/Rejected/           ← You rejected (logged only)
/Done/               ← Completed (archived)
/Logs/               ← Audit trail (hitl_[date].md)
```

## Examples

### Email Approval
```bash
# Email MCP creates draft
# ↓ Creates approval request in /Pending_Approval/

# You review
cat Pending_Approval/email_approval_*.md

# You approve
mv Pending_Approval/email_approval_*.md Approved/

# Handler detects and executes
# (Watch logs in real-time)
tail -f skills/logs/hitl_approval_handler.log
```

### LinkedIn Post Approval
```bash
# Auto LinkedIn Poster creates draft
# ↓ Creates approval in /Pending_Approval/

# You review
cat Pending_Approval/linkedin_approval_*.md

# You approve
mv Pending_Approval/linkedin_approval_*.md Approved/

# Handler posts to LinkedIn
```

## Monitoring

### Check Pending
```bash
ls Pending_Approval/
```

### Check Approved (Waiting Execution)
```bash
ls Approved/
```

### View Audit Log
```bash
cat Logs/hitl_$(date +%Y-%m-%d).md

# Or watch in real-time
tail -f Logs/hitl_*.md
```

### Check Completed
```bash
ls Done/
```

## Testing

### Create Test Approval
```bash
cat > Pending_Approval/test_approval_$(date +%Y%m%d_%H%M%S)_demo.md << 'EOF'
---
type: email_approval
action: send_email
to: test@example.com
subject: Test Email
status: pending_approval
---

# Test Email Approval

To: test@example.com
Subject: Test Email

This is a test approval request.
EOF
```

### Approve It
```bash
mv Pending_Approval/test_approval_*.md Approved/
```

### Process
```bash
python3 skills/hitl_approval_handler.py --once
```

### Check Log
```bash
tail Logs/hitl_*.md
```

## Workflow in Action

### Scenario: Client Invoice Email

**1. Claude (via Email MCP):**
```
Draft invoice email to client@example.com
```

**2. Email MCP creates:**
```
/Plans/email_draft_2026-02-14_abc123_client@example.com.md
/Pending_Approval/email_approval_2026-02-14_abc123_client@example.com.md
```

**3. You review:**
```bash
cat Pending_Approval/email_approval_*.md

# Check:
# - Recipient: client@example.com ✓
# - Subject: Invoice #123 ✓
# - Body: Correct ✓
```

**4. You approve:**
```bash
mv Pending_Approval/email_approval_*.md Approved/
```

**5. HITL Handler:**
```
Detects approval file
  ↓
Calls Email MCP: send_email()
  ↓
Gmail sends email
  ↓
Logs: /Logs/hitl_2026-02-14.md
  ↓
Archives: /Done/executed_email_approval_*.md
```

**6. Result:**
```markdown
## 2026-02-14T10:30:00 - EMAIL_SEND

- **action:** send_email
- **to:** client@example.com
- **subject:** Invoice #123
- **status:** executed
```

## Integration

### With Email MCP
```
Email MCP creates approval
  ↓
HITL Handler executes send_email
```

### With Auto LinkedIn Poster
```
LinkedIn Poster creates approval
  ↓
HITL Handler executes post_linkedin
```

### With Ralph Wiggum Loop
```
Ralph Loop orchestrates
  ↓
Claude creates approval via MCP
  ↓
Ralph Loop waits
  ↓
HITL Handler processes
  ↓
Ralph Loop continues
```

## Status Check

### One-Time Check
```bash
python3 skills/hitl_approval_handler.py --once

# Output:
# ✓ Found 3 pending approvals
# ✓ Found 1 approved requests to execute
# ✓ Email sent to user@example.com
# ✓ Moved to /Done
#
# SUMMARY
# =========================
# Pending approvals:     3
# Approved requests:     1
# Executed:              1
# Failed:                0
# Rejected:              0
```

### Continuous Watch
```bash
python3 skills/hitl_approval_handler.py --watch

# Runs forever, checks every 10 seconds
# Processes new approvals automatically
# Press Ctrl+C to stop
```

## Tips & Tricks

### Bulk Approve
```bash
# Approve all pending (use with caution!)
find Pending_Approval -name "*.md" -exec mv {} Approved/ \;
```

### Bulk Reject
```bash
# Reject all pending
find Pending_Approval -name "*.md" -exec mv {} Rejected/ \;
```

### Monitor Like a Pro
```bash
# Terminal 1: Run handler in watch mode
python3 skills/hitl_approval_handler.py --watch

# Terminal 2: Watch logs in real-time
tail -f skills/logs/hitl_approval_handler.log

# Terminal 3: Check folders
watch -n 1 'ls Pending_Approval Approved Done'
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Files not executing | Verify they're in /Approved/ (not /Pending_Approval/) |
| No logs created | Check /Logs/ folder exists and has permissions |
| Action type unknown | Ensure YAML `type:` field is valid |
| Approval not detected | Restart handler, check file names |

## Next Steps

1. ✅ Start handler: `python3 skills/hitl_approval_handler.py --watch`
2. ✅ Create approval request in /Pending_Approval/
3. ✅ Approve by moving to /Approved/
4. ✅ Watch it execute
5. ✅ Check audit log

## Documentation

**Full Guide:** `skills/SKILL_HITL_APPROVAL_HANDLER.md`
**Implementation:** `skills/hitl_approval_handler.py`

---

**Ready to go!** 🚀
Start monitoring approvals and executing them safely.
