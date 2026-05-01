# Ralph Wiggum Loop - Quick Start Guide

**Status:** ✅ Ready to Use
**Files:** `tools/ralph_loop_runner.py`, `tools/ralph-loop`, `tools/ralph-loop.bat`

## One-Minute Setup

Ralph Wiggum Loop is already implemented! Here's how to use it:

## Commands

### Process all files in /Needs_Action (Recommended)
```bash
# Linux/Mac
python3 tools/ralph_loop_runner.py --process-needs-action

# Or use shortcut
./ralph-loop --process-needs-action

# Windows
python3 tools/ralph_loop_runner.py --process-needs-action
# Or
ralph-loop.bat --process-needs-action
```

### With custom max iterations
```bash
python3 tools/ralph_loop_runner.py --process-needs-action --max-iterations 20
```

### With custom prompt
```bash
python3 tools/ralph_loop_runner.py "Your prompt here" --max-iterations 10
```

## How to Test (5 minutes)

### Step 1: Create test file
```bash
cat > Needs_Action/test_sales_lead.md << 'EOF'
---
type: linkedin
from: John Business
subject: Sales opportunity - enterprise project interested
priority: high
source: linkedin
---

We have a major enterprise client interested in a long-term project collaboration.
This is a significant sales opportunity.
EOF
```

### Step 2: Run the loop
```bash
python3 tools/ralph_loop_runner.py --process-needs-action
```

### Step 3: Watch it work
- Ralph loop scans /Needs_Action
- Creates Plan.md in /Plans with multi-step workflow
- Shows HITL approval points
- Moves processed files to /Done

### Step 4: Check results
```bash
# See the generated plan
cat Plans/plan_*test*.md

# Verify file moved to Done
ls Done/

# Check logs
tail -20 tools/logs/ralph_loop_runner.log
```

## What Happens

```
Input: Needs_Action/test_sales_lead.md
  ↓
Ralph Loop reads file
  ↓
Analyzes: sales + client + project keywords detected
  ↓
Creates detailed Plan.md with:
  ✓ Objective
  ✓ Multi-phase workflow
  ✓ Step-by-step checkboxes
  ✓ Priority levels
  ✓ HITL approval points
  ↓
Saves to: Plans/plan_[date]_[hash]_[name].md
  ↓
Awaits human approval in /Pending_Approval
  ↓
Moves processed file: Needs_Action/ → Done/
  ↓
Output: <promise>TASK_COMPLETE</promise>
```

## Files Generated

### Plan.md Structure
When you run the loop, it creates:
```
/Plans/plan_20260214_123456_abc123_test_sales_lead.md

---
type: plan
task_type: sales_lead
priority: high
status: pending
requires_hitl: true
---

# Plan: test_sales_lead.md

## Objective
Process task from test_sales_lead.md...

## Multi-Step Workflow

### Phase 1: Analysis
- [ ] Read source file completely
- [ ] Extract key information
- [ ] Identify required actions
- [ ] Determine priority level

### Phase 2: Planning
- [ ] Break task into sub-steps
- [ ] Identify HITL approval points
- [ ] Create approval requests
- [ ] Document dependencies

### Phase 3: Execution
- [ ] Execute approved actions
- [ ] Create supporting artifacts
- [ ] Request human approval
- [ ] Wait for approval in /Pending_Approval

### Phase 4: Completion
- [ ] Verify all steps completed
- [ ] Move source file to /Done
- [ ] Move plan to /Done
- [ ] Update Dashboard.md

...plus 5 detailed steps for multi-step workflow
```

## Understanding the Loop

### The Pattern (Ralph Wiggum Style)

The loop keeps trying until done:

```
Iteration 1:
  Check /Needs_Action for files
  Found: test_sales_lead.md
  Create Plan.md
  Wait for approvals? YES
  → Iteration continues

Iteration 2:
  Check /Needs_Action for files
  Found: (empty, file was moved to /Done)
  All done? YES
  → Stop loop, success!
```

### Key Features

✅ **Autonomous Processing**
- Automatically analyzes files
- Generates detailed plans
- Handles multi-step workflows

✅ **Human Approval (HITL)**
- Sensitive actions marked for approval
- Creates approval requests
- Waits for human review

✅ **Safe Iteration**
- Max 10 iterations (prevents infinite loops)
- Checks for completion after each iteration
- Detailed logging

✅ **Multi-Step Task Handling**
Example: Sales Lead → Draft Post → HITL Approval → Publish
- Each step tracked with checkboxes
- Clear workflow phases
- Approval required before sensitive actions

## Output Locations

| Item | Location |
|------|----------|
| Input files | `/Needs_Action/*.md` |
| Generated plans | `/Plans/plan_*.md` |
| Approval queue | `/Pending_Approval/*.md` |
| Approved items | `/Approved/*.md` |
| Completed tasks | `/Done/processed_*.md` |
| Logs | `tools/logs/ralph_loop_runner.log` |

## Test Results

After running `python3 tools/ralph_loop_runner.py --process-needs-action`, you should see:

```
========================================================================
RALPH WIGGUM LOOP - Starting
========================================================================
Prompt: Process all files in /Needs_Action, analyze with Task Analyzer...
Max iterations: 10
Completion promise: TASK_COMPLETE
========================================================================

🔄 ITERATION 1/10
----------------------------------------------------------------------

📄 Processing: test_sales_lead.md

📋 Analyzing task: test_sales_lead.md

✓ Plan created: plan_20260214_123456_abc123_test_sales_lead.md
✓ Plan created: /full/path/to/Plans/plan_*.md

⏸️  AWAITING HUMAN APPROVAL
   Review plan in: plan_20260214_*.md
   Location: Plans/plan_*.md

   After approving actions, move required files to /Pending_Approval

========================================================================
RALPH WIGGUM LOOP - SUMMARY
========================================================================
Iterations completed: 1/10
Task complete: true
State file: tools/state/loop_state_*.json
========================================================================

✅ SUCCESS: All tasks completed!

<promise>TASK_COMPLETE</promise>
```

## Troubleshooting

### "No files in /Needs_Action"
→ Create a test file first (see Step 1 above)

### "Plan not generated"
→ Check the file has proper YAML frontmatter:
```markdown
---
type: [type]
from: [sender]
subject: [subject]
---
```

### Loop doesn't move to iteration 2
→ Check logs: `tail tools/logs/ralph_loop_runner.log`

### Permission denied error
→ Make script executable: `chmod +x tools/ralph-loop`

## Integration with Other Skills

### With Auto LinkedIn Poster
```bash
# 1. Ralph loop analyzes sales leads
python3 tools/ralph_loop_runner.py --process-needs-action

# 2. Ralph creates Plan.md with workflow
# 3. Auto LinkedIn Poster executes posts
# 4. Files flow: Needs_Action → Plans → Pending_Approval → Approved → Done
```

### With Gmail/WhatsApp Watchers
```bash
# Watchers drop files in /Needs_Action
# Ralph loop processes them
# Creates Plans with multi-step workflows
# Handles approvals
# Moves to Done
```

## Next Steps

1. ✅ **Run test:** `python3 tools/ralph_loop_runner.py --process-needs-action`
2. ✅ **Create test file:** Drop file in /Needs_Action
3. ✅ **Check Plan.md:** Review generated plan in /Plans
4. ✅ **Approve actions:** Move approval requests to /Approved
5. ✅ **Verify completion:** Check /Done for processed files

## Documentation

**Full Guide:** `tools/RALPH_LOOP_GUIDE.md`
**Pattern Source:** Hackathon0.md Section 2D
**Implementation:** `tools/ralph_loop_runner.py` (507 lines)

---

**Status:** ✅ Ready for production
**Created:** 2026-02-14
**For:** Silver Tier Implementation
