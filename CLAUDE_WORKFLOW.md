# Claude Reasoning Loop Workflow
**Silver Tier Automation Pattern**

This document formalizes how Claude Code processes tasks and creates the automation workflow that makes the AI Employee function.

---

## 🔄 **Core Loop: Read → Think → Plan → Write → Request Approval**

When Orchestrator detects a new task in `/Needs_Action/`, Claude follows this exact sequence:

### **Phase 1: READ** (Understand the Task)
```
Action: Claude reads the task file from /Needs_Action/
Input: *.md file with frontmatter (type, from, subject, priority, etc.)
Output: Task understanding + context

Example:
---
type: email
from: client@example.com
subject: Invoice Request
priority: high
---

Client asks for January 2026 invoice.
```

**Claude's Job:**
- Extract key information (who, what, when, why)
- Identify urgency level (high/medium/low)
- Check against Company_Handbook.md for applicable rules
- Flag if manual review needed

---

### **Phase 2: THINK** (Reason About the Task)
```
Claude internally reasons:
- Is this within my automation scope?
- What does Company_Handbook.md say about this?
- What are the decision rules?
- Do I need human approval?
- What are the failure cases?
```

**Decision Tree:**
```
Does task require approval?
├─ YES → Go to Phase 3 (Create Plan)
└─ NO → Can I execute directly?
    ├─ YES (e.g., email reply) → Execute + log
    └─ NO → Create Plan for approval
```

---

### **Phase 3: PLAN** (Create Action Plan)

**Output File:** `/Plans/PLAN_<task_id>.md`

```markdown
---
created: 2026-01-07T10:30:00Z
task_id: EMAIL_invoice_client_a
status: pending_approval
steps: 3
---

## Objective
Generate and send January 2026 invoice to Client A

## Decision Logic
- Task type: Email with attachment
- Approval required: YES (involves payment/financial document)
- Rule: All invoice sends require approval
- Source: Company_Handbook.md → Financial Thresholds

## Proposed Steps
1. Identify invoice amount from /Accounting/Client_A.md
2. Generate invoice attachment (PDF ready)
3. Draft email with professional tone
4. Create approval request

## Risks
- Incorrect invoice amount
- Outdated client email address
- Missing attachment

## Expected Outcome
Invoice sent → Logged → Moved to /Done
```

**When to Create Plan (vs. Direct Action):**
- ✅ Create plan if: Involves money, sensitive content, new contact, or > 100 decision complexity
- ⚠️ Create plan if: Uncertain about rule interpretation
- ❌ Skip plan if: Routine WhatsApp reply, standard email, no approval needed

---

### **Phase 4: WRITE** (Generate Approval Request)

If approval is needed, create file in `/Pending_Approval/`

**Format for Email Actions:**
```markdown
---
action: send_email
task_id: EMAIL_invoice_client_a
to: client_a@example.com
subject: January 2026 Invoice - $1,500
status: pending_human_approval
created: 2026-01-07T10:35:00Z
expires: 2026-01-08T10:35:00Z
---

## Email Preview

**To:** client_a@example.com
**Subject:** January 2026 Invoice - $1,500

---

Dear Client A,

Please find attached your invoice for services provided in January 2026.

**Invoice Details:**
- Amount: $1,500.00
- Period: January 1-31, 2026
- Due Date: February 7, 2026

Please let me know if you have any questions.

Best regards,
[Your Name]

---

## Action Required
1. Review email content above
2. Move this file to `/Approved` to send
3. Move to `/Rejected` if changes needed
```

**Format for LinkedIn Actions:**
```markdown
---
action: post_linkedin
task_id: LINKEDIN_business_tip_20260107
content_type: business_post
status: pending_human_approval
created: 2026-01-07T10:40:00Z
---

## Proposed Post

🚀 **How to Scale Your Business with AI**

Just deployed a new AI automation system that's handling:
✅ Email triage and replies
✅ Social media scheduling  
✅ Task management
✅ Lead tracking

The result? 4 hours of saved time per day.

If you're curious about AI for business automation, let me know! 🤖

---

## Approval Instructions
- ✅ Approve: Move to `/Approved`
- ❌ Reject: Move to `/Rejected`
```

**Format for Payment Actions:**
```markdown
---
action: execute_payment
task_id: PAYMENT_vendor_invoice_20260107
recipient: Vendor Inc
amount: 250.00
status: pending_human_approval
---

## Payment Details
- Recipient: Vendor Inc (first-time payment)
- Amount: $250.00
- Reason: Software subscription (Jan 2026)
- Due: 2026-01-10
- Approval Required: YES (new vendor + high amount)

## Approval Checklist
- [ ] Verify recipient is legitimate
- [ ] Confirm amount matches invoice
- [ ] Check due date is reasonable
- [ ] Review company handbook payment rules

Move to `/Approved` to proceed.
```

---

### **Phase 5: REQUEST APPROVAL** (Human Decision Point)

Claude writes the approval file and then **stops processing**. 

**What Claude Does NOT Do:**
- ❌ Send email before approval
- ❌ Execute payment
- ❌ Post to social media
- ❌ Delete files

**What Happens Next:**
1. Human reviews the approval file in Obsidian
2. Human either:
   - **Approves:** Move file to `/Approved/`
   - **Rejects:** Move file to `/Rejected/` with feedback
3. Orchestrator detects change and executes or logs rejection
4. Claude moves completed task to `/Done/`

---

## 📋 **When to Bypass Approval (Direct Execution)**

Claude can execute DIRECTLY (no approval needed) for:

| Task | Reason | Rules |
|------|--------|-------|
| WhatsApp reply to known contact | Routine | < 100 characters, friendly tone |
| Email reply to existing customer | Standard | Doesn't reference payment/contracts |
| Archive/organize files | Admin | Moving completed tasks to /Done |
| LinkedIn like/comment | Engagement | Generic positive feedback only |
| Sync logs | System | Maintenance operation |

**Example: Direct Execution (No Approval)**
```
📲 WhatsApp Incoming: "Hey, when's our meeting?"

Claude's Response:
1. Identify sender: Known contact ✓
2. Check handbook: WhatsApp replies don't need approval ✓
3. Execute directly:
   - Write reply: "Hi! It's at 3 PM today."
   - Send via WhatsApp MCP
   - Log action
   - Move to /Done

[No approval file created]
```

---

## 🔄 **Error Handling in Workflow**

If Claude encounters an error:

```
Stage 1 (Read): File is corrupted
├─ Action: Log error
├─ Create: /Needs_Action/ERROR_<task_id>.md
└─ Alert: Human to review file

Stage 2 (Think): Rule ambiguity
├─ Action: Ask in /Pending_Approval with question
├─ Wait: Human clarification
└─ Result: Human adds rule to Company_Handbook.md

Stage 3 (Plan): Unclear context
├─ Action: Create plan with "CLARIFICATION NEEDED" section
├─ Request: Human to provide missing information
└─ Resume: Once clarified

Stage 4 (Write): Content inappropriate
├─ Action: Log concern
├─ Create: /Pending_Approval with "REVIEW REQUIRED"
└─ Alert: Human to validate before proceeding

Stage 5 (Approval): Human doesn't respond
├─ Timeout: 24 hours
├─ Action: Create escalation alert
└─ Pause: No further action on this task
```

---

## 🎯 **Real-World Examples**

### **Example 1: Invoice Email (Requires Approval)**

```
Trigger: /Needs_Action/EMAIL_invoice_client_a.md detected

PHASE 1 - READ:
✓ Task: Send invoice to Client A
✓ Type: Email with attachment
✓ Priority: High
✓ Amount: $1,500

PHASE 2 - THINK:
✓ Is this automated? Check handbook...
✓ Financial threshold rule: Invoices require approval
✓ Decision: CREATE PLAN

PHASE 3 - PLAN:
→ Create /Plans/PLAN_invoice_client_a.md
  - Objective: Send invoice
  - Decision logic: Approval required
  - Steps: 3 steps identified
  - Status: pending_approval

PHASE 4 - WRITE:
→ Create /Pending_Approval/EMAIL_invoice_client_a.md
  - Email preview shown
  - Action: Move to /Approved to send

PHASE 5 - REQUEST APPROVAL:
⏸️  WAITING: Human reviews Pending_Approval folder

[Human moves file to /Approved]

PHASE 5B - EXECUTE:
→ Orchestrator detects approval
→ Email sent via MCP
→ Log action to /Logs/
→ Move to /Done/EMAIL_invoice_client_a.md

✅ COMPLETE
```

### **Example 2: WhatsApp Reply (Direct Execution)**

```
Trigger: /Needs_Action/WHATSAPP_john_doe.md detected

PHASE 1 - READ:
✓ From: John Doe (known contact)
✓ Message: "Are we still on for 3 PM?"
✓ Type: WhatsApp

PHASE 2 - THINK:
✓ Is approval needed? Check handbook...
✓ WhatsApp: No approval needed for routine replies
✓ Decision: EXECUTE DIRECTLY

PHASE 4 - WRITE (Skip plan, go direct):
→ Draft reply: "Yes, 3 PM works. See you then!"

PHASE 5 - REQUEST APPROVAL:
❌ Skip: No approval for routine WhatsApp

EXECUTE:
→ Send via WhatsApp MCP
→ Log action to /Logs/
→ Move to /Done/WHATSAPP_john_doe.md

✅ COMPLETE (No approval needed)
```

---

## ✅ **Checklist for Claude Before Taking Action**

Before executing ANY action, Claude should verify:

- [ ] Task file is properly formatted
- [ ] All required fields present
- [ ] No conflicts with existing tasks
- [ ] Company_Handbook.md rules checked
- [ ] Approval requirements determined
- [ ] No sensitive data being exposed
- [ ] Appropriate file destinations confirmed
- [ ] Logging plan in place
- [ ] Fallback plan if action fails

---

## 📝 **Summary**

**Short Version:**
1. Read task from `/Needs_Action/`
2. Check Company_Handbook.md rules
3. Create `/Plans/` file with logic
4. If approval needed → create `/Pending_Approval/` file and STOP
5. If no approval needed → execute directly and log
6. Move to `/Done/` when complete

**Golden Rule:**
> When in doubt, create an approval file. Better to ask the human than execute wrong action.

---

*This workflow is designed for autonomous operation while maintaining human control. Follow it exactly for reliability.*
