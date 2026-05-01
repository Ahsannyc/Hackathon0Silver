# Ralph Wiggum Loop - Silver Tier Implementation

**Status:** ✅ Active
**Tier:** Silver
**Type:** Autonomous Reasoning Loop

## Overview

The Ralph Wiggum Loop is an autonomous reasoning pattern that keeps Claude working iteratively until a task is complete. Named after the character from The Simpsons who "keeps on trying," it implements persistent task execution with human approval checkpoints.

## How It Works

```
Iteration 1:
  1. Orchestrator creates state file with prompt
  2. Claude reads /Needs_Action files
  3. Claude analyzes tasks with Task Analyzer
  4. Claude creates detailed Plan.md in /Plans
  5. Claude requests approval for sensitive actions

  ↓ (Check: Task complete?)

Iteration 2 (if tasks remain):
  - Claude continues processing remaining files
  - Iterates until /Needs_Action is empty

Iteration 10 (max):
  - Loop stops (safeguard)
  - Reports: "Max iterations reached, some tasks pending"

Completion:
  - All files moved to /Done
  - Output: <promise>TASK_COMPLETE</promise>
```

## Command Usage

### Quick Start

**Process all files in /Needs_Action:**
```bash
python3 tools/ralph_loop_runner.py --process-needs-action
```

**Or using convenience command (Linux/Mac):**
```bash
./ralph-loop --process-needs-action
```

**Windows:**
```bash
ralph-loop.bat --process-needs-action
```

### Custom Prompt

**Run with custom prompt:**
```bash
python3 tools/ralph_loop_runner.py "Your custom prompt here" \
  --completion-promise "DONE" \
  --max-iterations 10
```

### Examples

**Example 1: Process single batch**
```bash
python3 tools/ralph_loop_runner.py --process-needs-action
```

**Example 2: Custom max iterations**
```bash
python3 tools/ralph_loop_runner.py --process-needs-action --max-iterations 20
```

**Example 3: Custom completion marker**
```bash
python3 tools/ralph_loop_runner.py \
  "Process sales leads and draft LinkedIn posts" \
  --completion-promise "MARKETING_READY" \
  --max-iterations 10
```

## Understanding the Loop

### The Problem: Lazy Agents

Claude Code runs in interactive mode - after processing a prompt, it waits for more input. Without the Ralph loop, it won't keep working until tasks are truly complete.

### The Solution: The Stop Hook Pattern

1. **Iteration starts** with prompt
2. **Claude works** on tasks
3. **Claude tries to exit**
4. **Stop hook intercepts** and checks: "Is /Needs_Action empty?"
5. **If NO** → Reject exit, re-inject prompt, loop continues
6. **If YES** → Allow exit, task is complete

### Two Completion Strategies

#### 1. Promise-Based (Simple)
Claude outputs the completion marker:
```
<promise>TASK_COMPLETE</promise>
```
Loop detects this and stops.

#### 2. File Movement (Advanced)
Loop watches for files moving from /Needs_Action to /Done.
When /Needs_Action is empty → task complete.

## Silver Tier Configuration

### Loop Prompt
```
Process all files in /Needs_Action:
1. Analyze each file with Task Analyzer
2. Create detailed Plan.md in /Plans with:
   - Clear steps with [ ] checkboxes
   - Priority levels (high/medium/low)
   - Multi-step workflow phases
   - HITL approval checkpoints
3. Handle multi-step tasks (e.g., sales lead -> draft -> approve -> publish)
4. Move processed files to /Done when complete
5. Output <promise>TASK_COMPLETE</promise> when all done
```

### Max Iterations
Default: **10 iterations**
(Prevents infinite loops; use --max-iterations to override)

### Completion Promise
Default: **TASK_COMPLETE**
(Marker Claude outputs when done)

## Workflow Stages

### Stage 1: Scan & Analyze
- Ralph loop scans /Needs_Action for files
- Task Analyzer examines each file
- Determines task type, priority, required actions

### Stage 2: Plan Generation
- Creates Plan.md for each task with:
  - Multi-step workflow breakdown
  - Checkboxes for tracking
  - Priority indicators
  - HITL approval points

### Stage 3: Multi-Step Execution
Example: **Sales Lead → LinkedIn Post**

```
Input: /Needs_Action/sales_lead_from_linkedin.md
  ↓
Analysis: Detects "sales", "client", "project" keywords
  ↓
Plan.md: Multi-phase workflow
  Phase 1: Analyze lead
  Phase 2: Draft post (moves to /Plans/)
  Phase 3: HITL approval (moves to /Pending_Approval/)
  Phase 4: Publish (moves to /Approved/)
  ↓
Output: /Done/processed_sales_lead_*.md
```

### Stage 4: HITL Checkpoints
For sensitive actions:
1. Claude creates approval request in /Pending_Approval
2. Human reviews and approves/rejects
3. If approved → moves to /Approved
4. Claude continues with approved actions

### Stage 5: Completion & Cleanup
- All source files moved to /Done
- All plan files moved to /Done
- Dashboard updated
- Loop outputs completion promise

## File Structure

### Input
**Location:** `/Needs_Action/*.md`

Structure:
```markdown
---
type: email/whatsapp/linkedin
from: Contact Name
subject: Message Subject
priority: high/medium/low
---

Message content here...
```

### Output: Plans
**Location:** `/Plans/plan_[date]_[hash]_[name].md`

Structure:
```markdown
---
type: plan
task_type: sales_lead|financial|communication|general
priority: high|medium|low
status: pending
requires_hitl: true
---

# Plan: [Original Task Name]

## Objective
...

## Multi-Step Workflow
### Phase 1: Analysis
- [ ] Step 1
- [ ] Step 2
...
```

### Output: Done
**Location:** `/Done/processed_[name]_[timestamp].md`

Archive of completed tasks with metadata.

## HITL Approval Workflow

### For Multi-Step Tasks

**Step 1: Claude creates Plan.md**
```
/Plans/plan_sales_lead.md
```

**Step 2: Claude creates approval request**
```
/Pending_Approval/approval_linkedin_post_draft.md
```

**Step 3: Human reviews and approves**
```
Move: /Pending_Approval/approval_* → /Approved/approval_*
```

**Step 4: Claude detects approval and continues**
```
Executes approved action
Moves file to /Done
```

## Testing the Loop

### Test 1: Basic Functionality

**1. Create test file:**
```bash
cat > Needs_Action/test_task.md << 'EOF'
---
type: email
from: Test User
subject: Test task for Ralph loop
priority: high
---

This is a test task for the Ralph Wiggum loop.
Please create a plan with detailed steps.
EOF
```

**2. Run loop:**
```bash
python3 tools/ralph_loop_runner.py --process-needs-action
```

**3. Check results:**
```bash
# Should see:
# - Plan created in /Plans/
# - File moved to /Done/
# - Log entries in tools/logs/ralph_loop_runner.log

ls -la Plans/
ls -la Done/
tail -f tools/logs/ralph_loop_runner.log
```

### Test 2: Multi-Step Task

**1. Create sales lead file:**
```bash
cat > Needs_Action/sales_opportunity.md << 'EOF'
---
type: linkedin
from: John Sales Manager
subject: Sales opportunity - enterprise client interested in project
priority: high
source: linkedin
---

We have a major client interested in a project collaboration.
This is a great sales opportunity that could lead to a significant deal.
EOF
```

**2. Run loop:**
```bash
python3 tools/ralph_loop_runner.py --process-needs-action --max-iterations 5
```

**3. Verify plan generation:**
```bash
# Check that multi-phase plan was created
cat Plans/plan_*sales*.md

# Should see:
# - Phase 1: Analysis
# - Phase 2: Draft LinkedIn post
# - Phase 3: HITL Approval
# - Phase 4: Publish (manual step)
```

### Test 3: Max Iterations Safety

**1. Create 5 files in /Needs_Action**

**2. Run with low iteration limit:**
```bash
python3 tools/ralph_loop_runner.py --process-needs-action --max-iterations 2
```

**3. Verify loop stops:**
```bash
# Should see:
# - Max iterations (2) reached
# - Remaining files still in /Needs_Action
# - Warning in logs
```

## Logs & Debugging

### Log Location
```
tools/logs/ralph_loop_runner.log
```

### View Logs
```bash
# Real-time monitoring
tail -f tools/logs/ralph_loop_runner.log

# View complete log
cat tools/logs/ralph_loop_runner.log

# Search for errors
grep "✗" tools/logs/ralph_loop_runner.log
```

### Log Format
```
2026-02-14 12:34:56,789 - ralph_loop_runner - INFO - ✓ Loop state file created: ...
2026-02-14 12:34:57,123 - ralph_loop_runner - INFO - 🔄 ITERATION 1/10
2026-02-14 12:34:58,456 - ralph_loop_runner - INFO - ✓ Found 3 files in /Needs_Action
...
```

## Integration with Silver Tier Skills

### With Auto LinkedIn Poster
```bash
# 1. Run ralph loop to analyze leads
python3 tools/ralph_loop_runner.py --process-needs-action

# 2. Loop creates Plan.md with multi-step workflow
# 3. Auto LinkedIn Poster skill executes approved posts
# 4. HITL approval happens in /Pending_Approval

# Result: Sales leads → Plans → Posts → Approval → LinkedIn
```

### With Task Analyzer
```
Ralph Loop → Task Analyzer → Plan.md with:
  - Detailed steps
  - Checkboxes
  - Priorities
  - HITL checkpoints
```

## Performance Considerations

### Iteration Time
- First iteration: ~10-30 seconds per file (planning)
- Subsequent iterations: ~5-10 seconds (execution)

### File Limits
- Recommended: 1-5 files per run
- Max tested: ~20 files (some may timeout)

### Max Iterations
- Default: 10 (safe)
- Typical for 5 files: 3-5 iterations
- Use `--max-iterations 20` for complex workflows

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "No files in /Needs_Action" | Empty input folder | Drop files to test, then run loop |
| "Max iterations reached" | Too many files or complex tasks | Increase `--max-iterations` or reduce file count |
| "Loop state file error" | Permission issue | Check `tools/` directory permissions |
| File not moved to /Done | YAML parse error | Verify markdown frontmatter syntax |

## State Management

### State File
Location: `tools/state/loop_state_[timestamp].json`

Contains:
```json
{
  "prompt": "Process all files...",
  "created_at": "2026-02-14T12:30:00",
  "max_iterations": 10,
  "completion_promise": "TASK_COMPLETE",
  "current_iteration": 3,
  "task_complete": false,
  "iterations": [...]
}
```

### Cleanup
State files auto-expire after 7 days (manual cleanup recommended):
```bash
find tools/state/ -name "*.json" -mtime +7 -delete
```

## Advanced Usage

### Custom Loop Logic

Extend `ralph_loop_runner.py` for custom behavior:

```python
class CustomRalphLoop(RalphLoopRunner):
    def _generate_plan(self, task_name, task_content):
        # Custom plan generation logic
        pass

    def check_task_completion(self):
        # Custom completion detection
        pass
```

### Scheduled Execution

**Run every hour with PM2:**
```bash
pm2 start tools/ralph_loop_runner.py \
  --name ralph_loop \
  --interpreter python3 \
  --cron "0 * * * *"
```

**Or with cron (Linux/Mac):**
```bash
0 * * * * cd /path/to/project && python3 tools/ralph_loop_runner.py --process-needs-action
```

### Monitoring Dashboard

Create a monitoring script:
```bash
#!/bin/bash
while true; do
  clear
  echo "=== Ralph Loop Status ==="
  echo "Files in /Needs_Action: $(ls Needs_Action/ | wc -l)"
  echo "Plans in /Plans: $(ls Plans/ | wc -l)"
  echo "Recent logs:"
  tail -5 tools/logs/ralph_loop_runner.log
  sleep 5
done
```

## Troubleshooting

### Loop won't start
```bash
# Check Python installed
python3 --version

# Check logs
cat tools/logs/ralph_loop_runner.log

# Verify directories exist
ls -la Needs_Action Plans Done
```

### Files not processed
```bash
# Check file format (must be .md)
ls -la Needs_Action/

# Check file content (must have proper YAML)
cat Needs_Action/test.md

# Run with verbose output
python3 tools/ralph_loop_runner.py --process-needs-action 2>&1 | tee debug.log
```

### Plans not generated
```bash
# Check Plans directory exists
mkdir -p Plans

# Check permissions
ls -ld Plans/
chmod 755 Plans/
```

## Next Steps

1. **Setup:** Create `tools/` directory and scripts
2. **Test:** Drop test file in /Needs_Action and run loop
3. **Monitor:** Watch loop iterate and process files
4. **Approve:** Review and approve actions in /Pending_Approval
5. **Verify:** Check /Done for completed tasks
6. **Schedule:** Use PM2 or cron for automated runs

---

## Reference

**Documentation:**
- Section D of Hackathon0.md: Ralph Wiggum Loop pattern
- Ralph Loop reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

**Related Skills:**
- Task Analyzer: Analyzes files and creates detailed plans
- Auto LinkedIn Poster: Executes multi-step posting workflows

**Status:** ✅ Ready for Silver Tier implementation
**Last Updated:** 2026-02-14
