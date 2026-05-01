# PHR: Implement Ralph Wiggum Reasoning Loop

**ID:** 003
**Stage:** implementation | silver-tier
**Date:** 2026-02-14
**Status:** COMPLETE ✅

---

## Task Summary

Implement the Ralph Wiggum iterative reasoning loop pattern for multi-step task completion with HITL checkpoints.

---

## Implementation Details

**Files Created:**
- `tools/ralph_loop_runner.py` (507 lines) - Main implementation
- `ralph-loop` (Bash wrapper for Linux/Mac)
- `ralph-loop.bat` (Batch wrapper for Windows)

---

## Loop Workflow

```
Start
  ↓
Read task from /Needs_Action/
  ↓
Analyze requirements (Task Analyzer)
  ↓
Create multi-step plan in /Plans/Plan.md
  ↓
Execute step (max 10 iterations)
  ↓
Step complete? → [Checkpoint]
  ↓ YES
Check completion promise
  ↓
Completion detected → Move to /Done/
  ↓
Output: <promise>TASK_COMPLETE</promise>
```

---

## Key Features

**Multi-Step Processing:**
- Plans with numbered checkboxes
- Tracks completion progress
- Handles nested dependencies

**HITL Integration:**
- Checkpoint detection
- Waits for human approval
- Logs all interactions

**Safety Guardrails:**
- Max 10 iterations (prevents infinite loops)
- Timeout protection
- Error recovery

**Completion Detection:**
- Looks for promise tag: `<promise>TASK_COMPLETE</promise>`
- Alternative: `[x]` checkboxes all marked done
- Or explicit "Task complete" message

---

## Usage

### Direct Command
```bash
cd C:\Users\[name]\Desktop\Hackathon0Silver
python tools/ralph_loop_runner.py
```

### Convenience Commands
```bash
# Linux/Mac
./ralph-loop

# Windows
ralph-loop.bat
```

### With PM2
```bash
pm2 start tools/ralph_loop_runner.py --name ralph_loop --interpreter python
```

---

## Example Workflow

**Input Task:** `Needs_Action/email_invoice_2026-02-14.md`
```yaml
---
type: email
from: client@example.com
subject: Invoice #123 for project work
content: Need to follow up on pending invoice
---
```

**Generated Plan:** `Plans/Plan.md`
```markdown
---
type: plan
task: Follow up on invoice
max_iterations: 10
current_iteration: 0
---

## Plan: Follow Up Invoice #123

### Steps:
- [ ] Read invoice details
- [ ] Calculate amount due
- [ ] Draft follow-up email
- [ ] Review with HITL
- [ ] Send email
- [ ] Mark as complete

[Iteration 1...]
```

**After Completion:** `Done/email_invoice_2026-02-14.md`
```
Task moved with: <promise>TASK_COMPLETE</promise>
```

---

## Integration Points

**Input:** `/Needs_Action/` folder

**Processing Steps:**
1. Task Analyzer reads and understands task
2. Plan Generator creates `/Plans/Plan.md`
3. Execution Loop iterates (max 10)
4. HITL Checkpoints pause for approval
5. Auto-resume after approval

**Output:**
- `/Done/` - Completed tasks
- `/Logs/ralph_loop_[date].md` - Execution log
- `<promise>TASK_COMPLETE</promise>` - Success indicator

**Integrates With:**
- Auto LinkedIn Poster (for posts)
- HITL Approval Handler (for approvals)
- Email MCP Server (for emails)
- Ralph Loop conveniences (shell wrappers)

---

## Configuration

Edit `tools/ralph_loop_runner.py`:
- `MAX_ITERATIONS = 10` - Change iteration limit
- `WAIT_TIME = 5` - Change checkpoint wait time
- Keywords and task types

---

## Documentation

**Files:**
- `RALPH_LOOP_GUIDE.md` - Complete guide with examples
- `RALPH_LOOP_QUICK_START.md` - 5-minute quick start
- `SKILL_QUICK_REFERENCE.md` - All skills overview

---

**Progress:** ✅ COMPLETE | Status: Ready for production
**Next:** Integrate with HITL Approval Handler

