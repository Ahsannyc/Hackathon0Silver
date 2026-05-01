# Bronze Tier Agent Skills Manifest

## Overview
Two custom Agent Skills for the Bronze Tier AI Employee Project, enabling automated file handling and task analysis workflows.

---

## Skill 1: Basic File Handler

**Purpose:** Read and process markdown files from Needs_Action, create action plans, and move completed work to Done.

**Capabilities:**
- ✓ Read all .md files from `/Needs_Action` folder
- ✓ Summarize file contents and extract key sections
- ✓ Verify Company_Handbook.md rules before processing
- ✓ Create structured Plan.md with task checkboxes
- ✓ Move completed files to `/Done` folder
- ✓ Output full file paths for all operations

**Key Features:**
- Automatic handbook rule validation
- Simple checkbox-based action plans
- Batch file processing
- Detailed logging with full paths

**Location:** `.specify/skills/basic_file_handler.py`

**Usage:**
```bash
# From project root:
python .specify/skills/basic_file_handler.py

# Or invoke as:
@Basic File Handler
```

**Output:**
- Plan created in `/Plans/Plan.md`
- Success summary with file counts
- Full paths for all processed files
- Handbook compliance check: ✓

**Example Output:**
```
============================================================
BASIC FILE HANDLER - Bronze Tier Skill
============================================================

📋 CHECKING COMPANY HANDBOOK:
# Company Handbook
Rules:
- Always be polite in replies.
- Flag payments > $500 for approval.

📂 SCANNING /Needs_Action:
✓ Found 2 file(s)

📝 SUMMARIZING FILES:
  • request_001.md (3 sections)
  • feedback_002.md (2 sections)

✍️  CREATING ACTION PLAN:
✓ Plan created: C:\...\Plans\Plan.md

============================================================
✅ EXECUTION COMPLETE
============================================================
Files processed: 2
Plan location: C:\...\Plans\Plan.md
Handbook rules applied: ✓
```

---

## Skill 2: Task Analyzer

**Purpose:** Analyze task types, identify approval needs, and create categorized action plans with support for complex multi-step workflows.

**Capabilities:**
- ✓ Detect task types (payment, approval, file_drop, action, info)
- ✓ Identify tasks requiring approval (>$500 payments, sensitive data)
- ✓ Count task steps and complexity
- ✓ Create detailed analysis plans
- ✓ Write approval queue to `/Pending_Approval`
- ✓ Flag multi-step tasks using Ralph Wiggum Loop

**Key Features:**
- Intelligent task type detection
- Approval rule enforcement ($500+ threshold)
- Multi-step task framework (Ralph Wiggum Loop)
- Categorized task breakdown
- Approval queue management

**Location:** `.specify/skills/task_analyzer.py`

**Ralph Wiggum Loop** (for multi-step tasks):
```
Step 1: I'm helping (identify the issue)
Step 2: Let's solve this (break into steps)
Step 3: I'm doing my best (execute)
Step 4: It's working! (verify completion)
```

**Usage:**
```bash
# From project root:
python .specify/skills/task_analyzer.py

# Or invoke as:
@Task Analyzer
```

**Output:**
- Task Analysis Plan in `/Plans/Task_Analysis_Plan.md`
- Approval queue in `/Pending_Approval/approval_queue.md`
- Task categorization summary
- Multi-step task guidance

**Example Output:**
```
============================================================
TASK ANALYZER - Bronze Tier Skill
============================================================

🔍 ANALYZING FILES IN /Needs_Action:
✓ Analyzed 3 task(s)

📊 TASK CATEGORIZATION:
  • payment_request.md        | Type: payment     | Steps: 2 | 🚫 APPROVAL NEEDED
  • status_update.md          | Type: info        | Steps: 1 | ✓ OK
  • feature_request.md        | Type: action      | Steps: 4 | 🎯 RALPH WIGGUM LOOP

⚠️  APPROVAL REQUIRED FOR 1 TASK(S):
  • payment_request.md
    • High Payment (>$500)

✍️  CREATING ANALYSIS PLAN:
✓ Plan created: C:\...\Plans\Task_Analysis_Plan.md

📋 WRITING APPROVAL QUEUE:
✓ Approval queue: C:\...\Pending_Approval\approval_queue.md

🎯 RALPH WIGGUM LOOP (for multi-step tasks):
   Detected 1 multi-step task(s)
   - Step 1: I'm helping (identify issue)
   - Step 2: Let's solve this (break into steps)
   - Step 3: I'm doing my best (execute)
   - Step 4: It's working! (verify)

============================================================
✅ ANALYSIS COMPLETE
============================================================
Tasks analyzed: 3
Approval needed: 1
Analysis plan: C:\...\Plans\Task_Analysis_Plan.md
```

---

## Quick Reference

| Skill | Purpose | Input Folder | Output Folder(s) | Key Rule |
|-------|---------|--------------|------------------|----------|
| Basic File Handler | Process files & create plans | `/Needs_Action` | `/Plans`, `/Done` | Always check handbook |
| Task Analyzer | Analyze & categorize tasks | `/Needs_Action` | `/Plans`, `/Pending_Approval` | Flag payments >$500 |

---

## Integration Notes

- Both skills respect `/Company_Handbook.md` rules
- Automatic creation of output folders (mkdir -p)
- Full absolute paths logged for all operations
- Python 3.6+ required
- Cross-platform compatible (Windows, Mac, Linux)

---

## Next Steps

1. Place markdown files in `/Needs_Action`
2. Run `@Basic File Handler` to process and create plans
3. Run `@Task Analyzer` to categorize and check approvals
4. Review output in `/Plans` and `/Pending_Approval`
5. Move completed tasks from `/Needs_Action` to `/Done`
