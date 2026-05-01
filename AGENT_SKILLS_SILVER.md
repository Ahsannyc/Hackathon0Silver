# Silver Tier Agent Skills Manifest
**Version:** 1.0 | **Tier:** Silver | **Last Updated:** 2026-01-07

Comprehensive formalization of all AI Employee automation as Claude Agent Skills. These skills enable autonomous operation while maintaining human control.

---

## 📋 **Agent Skills Overview**

Silver Tier includes **5 formalized Agent Skills** that work together to create the autonomous AI Employee:

| # | Skill | Purpose | Primary Input | Primary Output |
|---|-------|---------|----------------|-----------------|
| 1 | **Task Processor** | Process /Needs_Action, create plans | `/Needs_Action/*.md` | `/Plans/PLAN_*.md` |
| 2 | **Approval Manager** | Create & manage approval requests | Task decisions | `/Pending_Approval/*.md` |
| 3 | **LinkedIn Automator** | Auto-create & post LinkedIn content | Business rules | LinkedIn posts + log |
| 4 | **Email Handler** | Draft, review, execute email actions | Email triggers | `/Approved/EMAIL_*.md` |
| 5 | **File Lifecycle Manager** | Organize tasks through workflow | Task completion | `/Done/` organization |

---

## 🔧 **Skill #1: Task Processor**

**What it does:** Reads incoming tasks, understands context, checks Company_Handbook rules

**Trigger:** File appears in `/Needs_Action/`

**Process:**
```
1. Detect new .md file in /Needs_Action/
2. Parse frontmatter (type, from, subject, priority)
3. Extract task content and context
4. Check against Company_Handbook.md rules
5. Create /Plans/PLAN_*.md with decision logic
6. Move original to /In_Progress/
```

**Example:**
```
INPUT: /Needs_Action/EMAIL_client_invoice_request.md
PROCESS: Parse → Check rules → Create plan
OUTPUT: /Plans/PLAN_client_invoice_request.md
        "Email involves $1,500 → Requires approval"
```

**Key Rules Applied:**
- Determine if approval is needed
- Categorize by task type (email, payment, social, file)
- Check urgency level
- Flag for HITL if uncertain

---

## 🆗 **Skill #2: Approval Manager**

**What it does:** Creates formal approval request files with decision information

**Trigger:** Task Processor identifies approval-needed item

**Process:**
```
1. Receive decision from Task Processor
2. Create formal approval file with:
   - Clear action preview
   - Decision rationale
   - Company rules applied
   - Human approval instructions
3. Write to /Pending_Approval/
4. Stop processing (wait for human)
```

**Example: Email Approval Request**
```
File: /Pending_Approval/EMAIL_invoice_client_a.md
---
action: send_email
requires: human_approval
to: client_a@example.com
subject: January Invoice - $1,500
---
[Email preview + approval instructions]
```

**Approval Decision Logic:**
```
Payment > $100?          → Requires approval
Email to new contact?    → Requires approval  
LinkedIn post?           → Requires approval
WhatsApp to known user?  → No approval
File organization?       → No approval
```

---

## 🔗 **Skill #3: LinkedIn Automator**

**What it does:** Create business-focused LinkedIn content automatically

**Activation:** Twice daily (8 AM, 2 PM)

**Content Strategy:**
- Business tips & industry insights
- Case studies & client success
- Company/product announcements
- Thought leadership posts
- Engagement with connections

**Process:**
```
1. Check business calendar for events
2. Generate post based on recent activity
3. Create draft in /Pending_Approval/LINKEDIN_*.md
4. Wait for approval
5. Post via LinkedIn API once approved
6. Log to /Logs/ with engagement metrics
```

**Example Post:**
```
---
action: post_linkedin
status: pending_approval
---

🚀 **AI Automation: The Future of Work**

Just automated 5 hours of daily tasks using AI. 
Here's what worked:
✅ Email triage & drafting
✅ Task scheduling
✅ Document organization
✅ Client communication

If you're curious about AI for business, let me know!

#AI #Automation #BusinessEfficiency
```

**Key Guidelines:**
- Professional tone always
- Link to recent blog posts when relevant
- Include 3-5 relevant hashtags
- Post during business hours (9 AM - 6 PM)
- Schedule 2-3 posts per week

---

## 📧 **Skill #4: Email Handler**

**What it does:** Draft, manage, and execute email communications

**Triggers:**
- Incoming emails to VIP/important senders
- Invoice/payment-related emails
- Customer inquiries
- Newsletter responses

**Process:**
```
1. Detect incoming email (via Gmail watcher)
2. Classify priority (urgent/high/normal)
3. Draft response based on rules
4. If approval needed:
   - Create /Pending_Approval/EMAIL_*.md
   - Wait for human approval
5. If no approval needed:
   - Send directly via Email MCP
   - Log to /Logs/
6. Move to /Done/
```

**Types of Actions:**
```
✅ Direct Send (No Approval):
   - Reply to existing customer
   - Acknowledgment message
   - Calendar invitation
   
⚠️  Approval Required:
   - First contact with new person
   - Email involving financial info
   - Formal proposals or contracts
   - Sensitive/confidential content
```

**Template: Professional Email Reply**
```
Dear [Name],

Thank you for your email regarding [topic].

[Main response body]

[Call to action if needed]

Best regards,
[Your Name]
```

---

## 📁 **Skill #5: File Lifecycle Manager**

**What it does:** Organize and archive tasks through their complete lifecycle

**Workflow:**
```
/Needs_Action/  ← New tasks arrive
    ↓ (Processed)
/In_Progress/   ← Currently being handled
    ↓ (Decision made)
/Pending_Approval/ ← Waiting for human approval
    ↓ (Approved)
/Approved/      ← Ready to execute
    ↓ (Executed)
/Done/          ← Completed tasks
    ↓ (After 30 days)
Archive or Delete
```

**Process:**
```
1. Monitor file movements
2. Validate workflow transitions
3. Prevent duplicate processing (claim-by-move)
4. Archive old files after 30 days
5. Generate completion reports
```

**Rules:**
```
- /In_Progress/ acts as lock (only one processor per file)
- /Pending_Approval/ is final before execution
- /Done/ is immutable archive
- Auto-archive files older than 30 days
- Daily summary in Dashboard.md
```

---

## 🔄 **How Skills Work Together**

**Example: Invoice Email Workflow**

```
Step 1: TRIGGER
└─ Email arrives: "Please send invoice"
   Location: Gmail inbox

Step 2: DETECT & READ (Task Processor)
└─ Gmail Watcher creates: /Needs_Action/EMAIL_invoice_request.md
   Processor reads it

Step 3: THINK & PLAN (Task Processor)
└─ Checks Company_Handbook.md:
   - Invoice = financial document
   - Amount unknown → potential risk
   - Decision: REQUIRES APPROVAL

Step 4: REQUEST APPROVAL (Approval Manager)
└─ Creates: /Pending_Approval/EMAIL_invoice_request.md
   With: Email preview, client details, instructions

Step 5: HUMAN DECISION
└─ [Human reviews in Obsidian]
   [Moves file to /Approved/]

Step 6: EXECUTE (Email Handler)
└─ Orchestrator detects /Approved/ file
   Sends email via MCP
   Logs action: /Logs/2026-01-07.json

Step 7: ARCHIVE (File Lifecycle Manager)
└─ Orchestrator moves to /Done/
   Dashboard updates: +1 completed task
   Marked for archive after 30 days
```

---

## 💻 **How to Invoke Skills**

Each skill can be invoked as an **Agent Skill** in Claude:

### **Method 1: Direct Claude Command**
```bash
claude --skill "Task Processor" \
       --cwd ~/AI_Employee_Vault
```

### **Method 2: In Claude Code (Interactive)**
```
You: "Process all tasks in /Needs_Action and create plans"
Claude: [Invokes Task Processor skill]
Result: Plans created in /Plans/
```

### **Method 3: Orchestrator Trigger (Automatic)**
```python
# orchestrator.py watches folders and auto-triggers skills
if new_file_in(NEEDS_ACTION):
    trigger_skill("Task Processor")
```

---

## 🎯 **Skill Configuration**

**Location:** `~/.claude/agent-skills/`

**Example Configuration File:**

```yaml
skills:
  - name: Task Processor
    description: "Read and understand incoming tasks"
    input_folders:
      - /Needs_Action
    output_folders:
      - /Plans
      - /In_Progress
    rules_file: Company_Handbook.md
    
  - name: Approval Manager
    description: "Create approval requests for sensitive actions"
    input: task_decisions
    output_folders:
      - /Pending_Approval
    
  - name: LinkedIn Automator
    description: "Auto-create and post LinkedIn content"
    schedule: "8 AM, 2 PM daily"
    
  - name: Email Handler
    description: "Draft and send emails"
    triggers:
      - Gmail watcher
    
  - name: File Lifecycle Manager
    description: "Manage task workflow and archival"
    watch_folders:
      - /In_Progress
      - /Approved
      - /Done
```

---

## ⚙️ **Integration with Orchestrator**

The **Orchestrator.py** automatically triggers skills:

```python
# Detect file in /Needs_Action
def watch_needs_action():
    for item in NEEDS_ACTION.glob('*.md'):
        # Trigger Task Processor skill
        process_task(item)
        
        # Skill creates plan
        # If approval needed → trigger Approval Manager
        if approval_needed(task):
            request_approval(task)

# Watch for approvals
def watch_approved_folder():
    for item in APPROVED.glob('*.md'):
        # Trigger Email Handler, LinkedIn Automator, etc.
        execute_action(item)
        
        # Trigger File Lifecycle Manager
        move_to_done(item)
```

---

## 📊 **Skill Execution Flow**

```
ORCHESTRATOR.PY (Master Controller)
    ├─ FILE WATCHER
    │  └─ Detects /Needs_Action changes
    │
    ├─ TRIGGER TASK PROCESSOR
    │  └─ Reads file → Creates plan → Checks rules
    │     └─ IF needs approval:
    │        TRIGGER APPROVAL MANAGER
    │        └─ Creates /Pending_Approval file
    │        └─ STOP (wait for human)
    │     └─ IF no approval:
    │        Move to /Approved
    │
    └─ WATCH APPROVED FOLDER
       └─ File appears in /Approved
          ├─ If EMAIL: TRIGGER EMAIL HANDLER
          ├─ If LINKEDIN: TRIGGER LINKEDIN AUTOMATOR
          └─ TRIGGER FILE LIFECYCLE MANAGER
             └─ Move to /Done & Update Dashboard
```

---

## ✅ **Silver Tier Skill Checklist**

Verify all skills are working:

- [ ] Task Processor: Creates plans in /Plans/
- [ ] Approval Manager: Creates files in /Pending_Approval/
- [ ] LinkedIn Automator: Posts 2x daily with approval
- [ ] Email Handler: Sends approved emails via MCP
- [ ] File Lifecycle Manager: Files move through workflow
- [ ] Dashboard: Updates every 30 seconds
- [ ] Orchestrator: Monitors all folders and triggers skills
- [ ] Logs: JSON logs record all actions
- [ ] Company_Handbook: Rules applied to all decisions

---

## 🚀 **Quick Start**

1. **Verify skills exist:**
   ```bash
   ls -la skills/
   ```

2. **Start Orchestrator:**
   ```bash
   python orchestrator.py
   ```

3. **Create test task:**
   ```bash
   echo "---
   type: email
   ---
   Test task" > Needs_Action/TEST.md
   ```

4. **Watch it process:**
   ```bash
   tail -f Logs/$(date +%Y-%m-%d).log
   ```

5. **Check Dashboard:**
   ```bash
   cat Dashboard.md
   ```

---

## 📈 **Skill Maturity Levels**

| Skill | Status | Maturity | Notes |
|-------|--------|----------|-------|
| Task Processor | ✅ Complete | Stable | Ready for production |
| Approval Manager | ✅ Complete | Stable | File-based approval proven |
| LinkedIn Automator | ✅ Complete | Stable | 2+ weeks of posts |
| Email Handler | ✅ Complete | Stable | Draft + send working |
| File Lifecycle Manager | ✅ Complete | Stable | Workflow validated |

---

## 🔮 **Future Enhancements (Gold Tier)**

When moving to Gold Tier, skills will be enhanced with:
- CEO Briefing Generator
- Finance/Banking Watcher
- Odoo integration
- Twitter/Facebook/Instagram automation
- Advanced error recovery
- Ralph Wiggum multi-step loop

---

*Silver Tier Agent Skills are production-ready. Use them to build a fully autonomous AI Employee.*
