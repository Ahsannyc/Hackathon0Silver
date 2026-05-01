# Agent Skill: HITL Approval Handler

**Tier:** Silver
**Status:** Active
**Type:** Approval Workflow Manager
**Skill ID:** `@HITL Approval Handler`

## Overview

HITL Approval Handler is a critical Silver Tier skill that:
- Monitors `/Pending_Approval` for approval requests
- Detects when humans move files to `/Approved`
- Executes approved actions via MCP servers
- Logs rejections to `/Rejected`
- Maintains audit trail in `/Logs/hitl_[date].md`

This enables safe, human-supervised automation of sensitive actions (emails, social posts, payments).

## How It Works

### The HITL Pattern

```
Action Triggered
  ↓
Agent creates approval request in /Pending_Approval/
  ↓
Approval Request: [action_type]_[date].md
  with YAML metadata (type, to, subject, amount, etc.)
  ↓
HUMAN REVIEW
  (in Obsidian or command line)
  ↓
APPROVAL DECISION:
  ✓ Move to /Approved/ → Skill executes
  ✗ Move to /Rejected/ → Logged, not executed
  ↓
Skill detects approval
  ↓
Executes action via MCP
  ↓
Logs result to /Logs/hitl_[date].md
  ↓
Moves to /Done/
```

## Capabilities

### Supported Actions

| Action Type | Triggered By | MCP Used | Example |
|-------------|-------------|----------|---------|
| `email_send` | Email MCP | Email MCP | Send invoice via Gmail |
| `linkedin_post` | Auto LinkedIn Poster | LinkedIn API | Post business update |
| `payment` | Payment MCP (future) | Payment MCP | Process payment |
| `custom` | Custom scripts | Script execution | Run custom command |

### File Structure

**Approval Request:**
```
/Pending_Approval/email_approval_2026-02-14_abc123_user@example.com.md
/Pending_Approval/linkedin_approval_2026-02-14_abc123_marketing.md
/Pending_Approval/payment_approval_2026-02-14_abc123_vendor.md
```

**YAML Metadata:**
```yaml
---
type: email_approval | linkedin_approval | payment_approval
action: send_email | post_linkedin | process_payment
status: pending_approval | approved | rejected
created_at: ISO timestamp
---
```

## Usage

### Command Line

#### Process Approved Requests (Once)
```bash
python3 skills/hitl_approval_handler.py --once
```

#### Watch /Approved Folder (Continuous)
```bash
python3 skills/hitl_approval_handler.py --watch
```

#### Custom Check Interval
```bash
python3 skills/hitl_approval_handler.py --watch --interval 30
```

### Agent Invocation

#### Check Pending Approvals
```
@HITL Approval Handler check Pending_Approval
```

#### Process Approved Actions
```
@HITL Approval Handler process approved
```

#### Watch for Approvals (Real-Time)
```
@HITL Approval Handler monitor
```

### PM2 Scheduling

#### Always-On Monitoring
```bash
pm2 start skills/hitl_approval_handler.py \
  --name hitl_handler \
  --interpreter python3 \
  --watch
```

#### Check Every 30 Seconds
```bash
pm2 start skills/hitl_approval_handler.py \
  --name hitl_handler \
  --interpreter python3 \
  -- --watch --interval 30
```

#### Cron Schedule (Hourly)
```bash
pm2 start skills/hitl_approval_handler.py \
  --name hitl_handler \
  --interpreter python3 \
  --cron "0 * * * *"
```

## Workflow Examples

### Example 1: Email Send Approval

**Step 1: Action Triggered**
```
Claude (Email MCP): "Draft email to client@example.com"
  ↓
Email MCP creates:
  - /Plans/email_draft_[date]_[hash]_client@example.com.md
  - /Pending_Approval/email_approval_[date]_[hash]_client@example.com.md
```

**Step 2: Human Review**
```
/Pending_Approval/email_approval_2026-02-14_abc123_client@example.com.md

---
type: email_approval
action: send_email
to: client@example.com
subject: Invoice #12345
status: pending_approval
---

Recipient: client@example.com
Subject: Invoice #12345
Body: ...

[Human reviews and decides]
```

**Step 3: Human Approval**
```bash
# Approve: Move to /Approved/
mv Pending_Approval/email_approval_*.md Approved/

# Or Reject: Move to /Rejected/
mv Pending_Approval/email_approval_*.md Rejected/
```

**Step 4: Skill Executes**
```
HITL Approval Handler detects approval
  ↓
Reads: /Approved/email_approval_*.md
  ↓
Executes: Email MCP send_email()
  ↓
Logs: /Logs/hitl_2026-02-14.md
  ↓
Archives: /Done/executed_email_approval_*.md
```

**Audit Log Entry:**
```markdown
## 2026-02-14T12:30:45 - EMAIL_SEND

- **action:** send_email
- **to:** client@example.com
- **subject:** Invoice #12345
- **status:** executed
```

### Example 2: LinkedIn Post Approval

**Step 1: Auto LinkedIn Poster Creates Request**
```
/Pending_Approval/linkedin_approval_2026-02-14_xyz789_marketing.md

---
type: linkedin_approval
action: post_linkedin
content: "Excited to announce our new product..."
status: pending_approval
---
```

**Step 2: Human Approves**
```bash
mv Pending_Approval/linkedin_approval_*.md Approved/
```

**Step 3: Skill Executes**
```
Detects approval
  ↓
Calls LinkedIn API
  ↓
Post published
  ↓
Logged to /Logs/hitl_2026-02-14.md
```

### Example 3: Payment Approval (Future)

**Step 1: Payment Request Created**
```
/Pending_Approval/payment_approval_2026-02-14_pay123_vendor.md

---
type: payment_approval
action: process_payment
amount: 500.00
recipient: vendor@example.com
reference: Invoice #789
status: pending_approval
---
```

**Step 2: Human Reviews**
- Amount: $500.00
- Recipient: vendor@example.com
- Reference: Invoice #789

**Step 3: Approval/Rejection**
```bash
# Approve
mv Pending_Approval/payment_approval_*.md Approved/

# Reject
mv Pending_Approval/payment_approval_*.md Rejected/
```

**Step 4: Execution**
```
If approved:
  - Process payment via Payment MCP
  - Log to /Logs/

If rejected:
  - Log rejection reason
  - Move to /Rejected/
```

## Integration with Other Skills

### With Email MCP
```
Email MCP (drafts email)
  ↓
Creates: /Pending_Approval/email_approval_*.md
  ↓
HITL Approval Handler (monitors)
  ↓
Human approves
  ↓
HITL Approval Handler (executes send_email)
  ↓
Email sent via Gmail API
```

### With Auto LinkedIn Poster
```
Auto LinkedIn Poster (drafts post)
  ↓
Creates: /Pending_Approval/linkedin_approval_*.md
  ↓
HITL Approval Handler (monitors)
  ↓
Human approves
  ↓
HITL Approval Handler (executes post)
  ↓
Post published to LinkedIn
```

### With Ralph Wiggum Loop
```
Ralph Loop (orchestrates)
  ↓
Claude calls Email MCP: draft_email()
  ↓
Email MCP creates approval request
  ↓
Ralph Loop continues (waiting)
  ↓
HITL Approval Handler detects approval
  ↓
Executes action
  ↓
Ralph Loop continues with next task
```

## Audit Logging

### Log Location
```
/Logs/hitl_YYYY-MM-DD.md
```

### Log Format
```markdown
---
type: hitl_audit_log
date: 2026-02-14
---

# HITL Approval Handler - Audit Log

## 2026-02-14T08:00:00 - EMAIL_SEND

- **action:** send_email
- **to:** client@example.com
- **subject:** Invoice #123
- **status:** executed

## 2026-02-14T08:15:00 - LINKEDIN_POST

- **action:** post_linkedin
- **content_preview:** Excited to announce...
- **status:** executed

## 2026-02-14T08:30:00 - REJECTED

- **file:** payment_approval_2026-02-14_pay123_vendor.md
- **status:** rejected
```

## File Lifecycle

### Pending Approval
```
/Pending_Approval/[action]_approval_[date]_[hash]_[recipient].md
├─ Type: Awaiting human decision
├─ Status: pending_approval
└─ Action: Waiting
```

### Approved (Execution)
```
/Approved/[action]_approval_[date]_[hash]_[recipient].md
├─ Type: Ready for execution
├─ Status: approved
└─ Action: HITL Handler executes
```

### Rejected (Not Executed)
```
/Rejected/[action]_approval_[date]_[hash]_[recipient].md
├─ Type: User rejected
├─ Status: rejected
└─ Action: None (logged only)
```

### Done (Archived)
```
/Done/executed_[action]_approval_[date]_[hash]_[recipient].md
├─ Type: Completed
├─ Status: executed or rejected
└─ Archive: For audit trail
```

## Configuration

### Environment Variables
```bash
# .env (optional)
HITL_CHECK_INTERVAL=10          # Check /Approved every 10 seconds
HITL_WATCH_MODE=true            # Enable continuous watching
HITL_LOG_LEVEL=info             # Log level (debug, info, warn, error)
```

### Logging
```
Location: skills/logs/hitl_approval_handler.log
Format: [timestamp] [level] [message]
```

## API Reference

### Process Approved Requests
```python
handler = HITLApprovalHandler()
results = handler.process_approved()

# Results:
# {
#   'pending_count': 3,
#   'approved_count': 1,
#   'executed_count': 1,
#   'failed_count': 0,
#   'rejected_count': 2
# }
```

### Watch for Approvals
```python
handler = HITLApprovalHandler()
handler.watch_for_approvals(interval=10)  # Check every 10 seconds
```

### Execute Single Action
```python
handler = HITLApprovalHandler()
success = handler.execute_approved_action(
    filepath,
    metadata,
    body
)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No pending approvals" | Check /Pending_Approval folder for files |
| "Files not executing" | Verify files are in /Approved/ (not /Pending_Approval/) |
| "Logs not created" | Check /Logs/ directory permissions |
| "Approval not detected" | Ensure YAML metadata is valid (use `yaml` library check) |
| "Action type unknown" | Check `type:` field in YAML matches supported types |

### Debug Mode
```bash
# Enable verbose logging
python3 skills/hitl_approval_handler.py --watch --verbose

# Check audit logs
tail -f Logs/hitl_*.md

# List pending approvals
ls -la Pending_Approval/

# List approved (waiting execution)
ls -la Approved/
```

## Security Considerations

✅ **HITL Safeguard**: No automatic execution without human approval
✅ **Audit Trail**: All actions logged to /Logs/
✅ **Rejection Support**: Ability to reject sensitive actions
✅ **MCP Integration**: Uses secure MCP servers for actual execution
✅ **Approval Detection**: File-based (no API key exposure)

## Performance

- **Pending scan:** <100ms
- **Approved scan:** <100ms
- **Action execution:** Depends on MCP (1-3 seconds typical)
- **Watch interval:** Configurable (default 10 seconds)
- **Concurrent actions:** Sequential (one at a time)

## Monitoring

### Check Status
```bash
# Show pending and approved counts
python3 skills/hitl_approval_handler.py --once

# Watch continuously
python3 skills/hitl_approval_handler.py --watch
```

### View Audit Trail
```bash
# Today's actions
cat Logs/hitl_$(date +%Y-%m-%d).md

# All actions
cat Logs/hitl_*.md

# Monitor in real-time
tail -f Logs/hitl_*.md
```

## Next Steps

1. ✅ Integrate with Email MCP (email_send approvals)
2. ✅ Integrate with Auto LinkedIn Poster (linkedin_post approvals)
3. 📋 Add payment approval support (when Payment MCP available)
4. 📋 Add custom action support
5. 📋 Create web dashboard for approvals (optional)

## Examples

### Quick Test
```bash
# Create test approval request
cat > Pending_Approval/test_approval_$(date +%Y%m%d_%H%M%S)_test.md << 'EOF'
---
type: email_approval
action: send_email
to: test@example.com
subject: Test Email
status: pending_approval
---

# Test Approval Request

To: test@example.com
Subject: Test Email

Test email content
EOF

# Approve it
mv Pending_Approval/test_approval_*.md Approved/

# Process
python3 skills/hitl_approval_handler.py --once

# Check results
tail Logs/hitl_*.md
ls Done/executed_*
```

---

**Created:** 2026-02-14
**Skill Type:** Approval Workflow Manager
**Tier:** Silver ⭐⭐
**Status:** ✅ Active
