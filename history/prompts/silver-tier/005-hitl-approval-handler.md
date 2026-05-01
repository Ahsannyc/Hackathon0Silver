# PHR: Create HITL Approval Handler Skill

**ID:** 005
**Stage:** implementation | silver-tier
**Date:** 2026-02-14
**Status:** COMPLETE ✅

---

## Task Summary

Create an agent skill to monitor approval requests, detect human approvals, execute actions via MCP, and handle rejections.

---

## Implementation Details

**File:** `skills/hitl_approval_handler.py` (440 lines)

**Purpose:** Bridge between human decision-making and automated execution

---

## Workflow

```
Pending Action Created
    ↓
Saved to /Pending_Approval/[action_type]_[hash].md
    ↓
HITL Handler detects → Logs to /Logs/hitl_[date].md
    ↓
Human makes decision
    ↓
┌──────────────────────────────┐
│ Human moves file to:         │
├──────────────────────────────┤
│ /Approved/ → Execute action  │
│ /Rejected/ → Log rejection   │
└──────────────────────────────┘
    ↓
HITL Handler detects move
    ↓
Executes via MCP (if approved)
    ↓
Action completed or rejected
```

---

## Usage

### Continuous Monitoring (Recommended)
```bash
python skills/hitl_approval_handler.py --watch
```
- Runs indefinitely
- Checks every 5 seconds
- Detects approval/rejection moves
- Executes immediately

### Single Run
```bash
python skills/hitl_approval_handler.py --once
```
- Runs once
- Processes pending approvals
- Exits

---

## Supported Actions

### Email Actions
```yaml
type: email_approval
action: send_email
to: client@example.com
subject: Invoice #123
body: Your invoice details...
```

### LinkedIn Actions
```yaml
type: linkedin_approval
action: post_linkedin
content: |
  Excited to announce...
  #marketing #business
```

### Payment Actions
```yaml
type: payment_approval
action: process_payment
amount: 500
recipient: account@example.com
```

### Custom Actions
```yaml
type: custom_approval
action: execute_custom
command: custom_workflow
params: {...}
```

---

## Approval Workflow Example

### Step 1: Ralph Loop Creates Draft
**File:** `Pending_Approval/email_approval_2026-02-14_abc123.md`
```yaml
---
type: email_approval
action: send_email
to: client@example.com
subject: Invoice Follow-up
status: pending
created: 2026-02-14T10:30:45
---

# Email Approval Request

Subject: Invoice Follow-up

**To:** client@example.com

Body:
Dear Client,

I wanted to follow up on invoice #123...

---

**Action:** Approve → Move to /Approved/
**Action:** Reject → Move to /Rejected/
```

### Step 2: Human Reviews
- Opens file in text editor
- Reads proposed action
- Makes decision

### Step 3: Human Approves
```bash
# Move file to approved folder
move Pending_Approval/email_approval_2026-02-14_abc123.md Approved/
```

### Step 4: HITL Handler Detects
```
[2026-02-14 10:35:00] Detected approval: email_approval_2026-02-14_abc123.md
[2026-02-14 10:35:00] Executing action: send_email
[2026-02-14 10:35:01] Email sent to client@example.com
[2026-02-14 10:35:01] Moving to Done/
```

### Step 5: Result Logged
**File:** `Logs/hitl_2026-02-14.md`
```markdown
---
type: hitl_log
date: 2026-02-14
total_processed: 5
approved: 4
rejected: 1
---

# HITL Approvals - 2026-02-14

## Approved Actions (4)

1. **email_approval_abc123** → send_email
   - To: client@example.com
   - Status: Executed ✓

2. **linkedin_post_def456** → post_linkedin
   - Status: Executed ✓

## Rejected Actions (1)

1. **payment_approval_ghi789** → process_payment
   - Reason: Insufficient balance
   - Status: Rejected ✗
```

---

## Integration Points

**Monitors:**
- `/Pending_Approval/` - Incoming requests
- `/Approved/` - Approved actions
- `/Rejected/` - Rejected actions

**Executes Via:**
- Email MCP Server (send_email)
- LinkedIn MCP Server (post_linkedin)
- Payment MCP Server (process_payment)
- Custom handlers (custom actions)

**Logs To:**
- `/Logs/hitl_[date].md` - Daily action log
- Console output - Real-time status

**Integrates With:**
- Ralph Loop (creates approval requests)
- Auto LinkedIn Poster (LinkedIn posts)
- Email MCP Server (email sending)
- Any MCP-based service

---

## Features

✅ Continuous or single-run monitoring
✅ File-based approval workflow (simple, no DB needed)
✅ Detailed logging of all actions
✅ Error recovery and retries
✅ Multiple action types supported
✅ Audit trail for compliance
✅ Real-time status reporting

---

## Configuration

**File:** `skills/hitl_approval_handler.py`

Customize:
- Check interval (default: 5 seconds)
- Retry attempts (default: 3)
- Log location (default: `/Logs/hitl_[date].md`)
- Supported action types
- MCP server timeouts

---

## Logging Example

```
2026-02-14 10:30:45 - [INFO] HITL Handler started (--watch mode)
2026-02-14 10:30:45 - [INFO] Watching for approvals in Pending_Approval/

2026-02-14 10:35:12 - [APPROVAL] Detected: email_approval_2026-02-14_abc123.md
2026-02-14 10:35:12 - [EXECUTE] Action type: email_approval
2026-02-14 10:35:12 - [EXECUTE] Calling MCP: send_email(to=client@example.com)
2026-02-14 10:35:13 - [SUCCESS] Email sent successfully
2026-02-14 10:35:13 - [FILE] Moving to Done/

2026-02-14 10:40:00 - [REJECTION] Detected: payment_approval_2026-02-14_def456.md
2026-02-14 10:40:00 - [ACTION] Moving to Rejected/
2026-02-14 10:40:00 - [LOG] Rejection logged
```

---

## Error Handling

- ✅ Detects MCP server failures
- ✅ Retries failed actions
- ✅ Logs all errors with context
- ✅ Graceful degradation
- ✅ Continues monitoring on errors

---

## Documentation

**Files:**
- `SKILL_HITL_APPROVAL_HANDLER.md` - Complete documentation
- `HITL_APPROVAL_HANDLER_QUICK_START.md` - Quick start guide
- `SKILL_QUICK_REFERENCE.md` - All skills overview

---

**Progress:** ✅ COMPLETE | Status: Ready for production
**Next:** Daily Briefing Scheduler implementation

