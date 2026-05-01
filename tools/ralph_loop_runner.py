#!/usr/bin/env python3
"""
Ralph Wiggum Loop Runner - Silver Tier
Implements the Claude reasoning loop for autonomous task completion

The Ralph Wiggum Pattern:
1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude tries to exit
4. Stop hook checks: Is task file in /Done?
5. YES → Allow exit (complete)
6. NO → Block exit, re-inject prompt, and allow Claude to see its own previous failed output
7. Repeat until complete or max iterations

USAGE:
======

Command Line:
  python3 tools/ralph_loop_runner.py "Process all files in /Needs_Action" \
    --completion-promise "TASK_COMPLETE" \
    --max-iterations 10

Or via wrapper command:
  ./ralph-loop "Process Needs_Action" --max-iterations 10

COMPLETION STRATEGIES:
=====================

1. Promise-based (simple):
   Claude outputs: <promise>TASK_COMPLETE</promise>

2. File movement (advanced):
   Stop hook detects when task files move to /Done

CONFIG:
=======

Loop prompt: "Process all files in /Needs_Action, analyze with Task Analyzer,
             create detailed Plan.md in /Plans with steps, checkboxes, priorities"

Iterate until: All tasks complete OR max 10 iterations
Move processed: Files to /Done
Handle: Multi-step tasks (e.g., sales lead -> draft post -> HITL)

TESTING:
========

1. Drop file in /Needs_Action
2. Run: python3 tools/ralph_loop_runner.py --process-needs-action
3. Monitor: Check /Plans for generated Plan.md
4. Verify: Files moved to /Done when complete
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import time
import subprocess
import hashlib

# Setup logging
os.makedirs("tools/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tools/logs/ralph_loop_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RalphLoopRunner:
    """Implements the Ralph Wiggum reasoning loop pattern"""

    def __init__(self, max_iterations: int = 10, completion_promise: str = "TASK_COMPLETE"):
        self.max_iterations = max_iterations
        self.completion_promise = completion_promise
        self.current_iteration = 0
        self.task_complete = False

        # Directories
        self.needs_action_dir = Path("Needs_Action")
        self.plans_dir = Path("Plans")
        self.done_dir = Path("Done")
        self.state_dir = Path("tools/state")

        # Ensure directories exist
        self.needs_action_dir.mkdir(exist_ok=True)
        self.plans_dir.mkdir(exist_ok=True)
        self.done_dir.mkdir(exist_ok=True)
        self.state_dir.mkdir(exist_ok=True)

    def create_loop_state_file(self, prompt: str) -> Path:
        """Create state file for loop tracking"""
        try:
            state_file = self.state_dir / f"loop_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            state = {
                'prompt': prompt,
                'created_at': datetime.now().isoformat(),
                'max_iterations': self.max_iterations,
                'completion_promise': self.completion_promise,
                'current_iteration': 0,
                'task_complete': False,
                'iterations': []
            }

            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)

            logger.info(f"✓ Loop state file created: {state_file}")
            return state_file
        except Exception as e:
            logger.error(f"✗ Error creating state file: {e}")
            raise

    def scan_needs_action(self) -> List[Path]:
        """Scan /Needs_Action for files to process"""
        try:
            if not self.needs_action_dir.exists():
                logger.warning(f"⚠ {self.needs_action_dir} does not exist")
                return []

            files = sorted(self.needs_action_dir.glob("*.md"))
            if files:
                logger.info(f"✓ Found {len(files)} files in /Needs_Action")
            else:
                logger.info("ℹ No files in /Needs_Action")

            return files
        except Exception as e:
            logger.error(f"✗ Error scanning /Needs_Action: {e}")
            return []

    def create_plan_from_task(self, task_file: Path) -> Optional[Path]:
        """Create Plan.md from task file using Task Analyzer"""
        try:
            logger.info(f"📋 Analyzing task: {task_file.name}")

            # Read task file
            with open(task_file, 'r', encoding='utf-8') as f:
                task_content = f.read()

            # Extract metadata if YAML frontmatter exists
            metadata = {}
            body = task_content
            if task_content.startswith('---'):
                parts = task_content.split('---', 2)
                if len(parts) >= 3:
                    body = parts[2].strip()

            # Create plan filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_hash = hashlib.md5(task_file.name.encode()).hexdigest()[:6]
            plan_filename = f"plan_{timestamp}_{task_hash}_{task_file.stem}.md"
            plan_filepath = self.plans_dir / plan_filename

            # Create detailed plan with checkboxes and priorities
            plan_content = self._generate_plan(task_file.name, task_content)

            with open(plan_filepath, 'w', encoding='utf-8') as f:
                f.write(plan_content)

            logger.info(f"✓ Plan created: {plan_filepath.name}")
            return plan_filepath
        except Exception as e:
            logger.error(f"✗ Error creating plan: {e}")
            return None

    def _generate_plan(self, task_name: str, task_content: str) -> str:
        """Generate detailed Plan.md with steps and checkboxes"""
        timestamp = datetime.now().isoformat()

        # Determine task type and priority
        task_lower = task_content.lower()

        if 'sales' in task_lower or 'client' in task_lower or 'project' in task_lower:
            task_type = "sales_lead"
            priority = "high"
            steps = [
                "Analyze business opportunity in task",
                "Draft LinkedIn post with template",
                "Move draft to /Pending_Approval for HITL",
                "Process approval and move to /Approved",
                "Publish to LinkedIn (manual step)"
            ]
        elif 'invoice' in task_lower or 'payment' in task_lower:
            task_type = "financial"
            priority = "high"
            steps = [
                "Extract invoice/payment details",
                "Generate invoice PDF if needed",
                "Create approval request",
                "Wait for HITL approval in /Pending_Approval",
                "Process approved action",
                "Log transaction"
            ]
        elif 'email' in task_lower or 'whatsapp' in task_lower or 'message' in task_lower:
            task_type = "communication"
            priority = "medium"
            steps = [
                "Extract message/email details",
                "Determine required response",
                "Draft reply (if needed)",
                "Create approval request if sensitive",
                "Send approved response",
                "Archive original"
            ]
        else:
            task_type = "general"
            priority = "medium"
            steps = [
                "Read and understand task",
                "Break down into sub-tasks",
                "Create action items",
                "Request approvals if needed",
                "Execute approved actions",
                "Mark complete"
            ]

        plan = f"""---
type: plan
task_type: {task_type}
priority: {priority}
status: pending
requires_hitl: true
created_at: {timestamp}
source_file: {task_name}
---

# Plan: {task_name}

**Type:** {task_type.replace('_', ' ').title()}
**Priority:** {priority.upper()}
**Status:** Pending
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Objective

Process task from {task_name} and complete all necessary steps.

---

## Multi-Step Workflow

### Phase 1: Analysis
- [ ] Read source file completely
- [ ] Extract key information (from, subject, content)
- [ ] Identify required actions
- [ ] Determine priority level

### Phase 2: Planning
- [ ] Break task into sub-steps
- [ ] Identify HITL approval points
- [ ] Create approval requests if needed
- [ ] Document dependencies

### Phase 3: Execution
- [ ] Execute approved actions
- [ ] Create supporting artifacts
- [ ] Request human approval for sensitive actions
- [ ] Wait for approval in /Pending_Approval

### Phase 4: Completion
- [ ] Verify all steps completed
- [ ] Move source file to /Done
- [ ] Move plan to /Done
- [ ] Update Dashboard.md

---

## Detailed Steps

"""

        for i, step in enumerate(steps, 1):
            plan += f"{i}. [ ] {step}\n"

        plan += f"""
---

## HITL Checkpoints

**Human approval required for:**
- Any payment/financial transactions
- External communications (email, WhatsApp)
- Social media posts
- Data modifications

**Approval Workflow:**
1. Create approval request in /Pending_Approval/
2. Wait for human review
3. If approved → move to /Approved/
4. If rejected → move to /Rejected/
5. Execute approved actions only

---

## Success Criteria

- [ ] All steps completed
- [ ] Source file moved to /Done
- [ ] Plan file moved to /Done
- [ ] All approvals obtained
- [ ] All actions executed
- [ ] Task logged in audit trail

---

## Completion Promise

When all steps are complete, output:

```
<promise>TASK_COMPLETE</promise>
```

---

## Notes

This plan was automatically generated by Ralph Loop Runner.
Review each step and provide approvals as needed in /Pending_Approval.

**Last Updated:** {timestamp}
"""

        return plan

    def check_task_completion(self) -> bool:
        """Check if all tasks are complete (moved to /Done)"""
        try:
            needs_action_files = list(self.needs_action_dir.glob("*.md"))

            if not needs_action_files:
                logger.info("✓ All files processed - /Needs_Action is empty")
                return True
            else:
                logger.info(f"⏳ Still {len(needs_action_files)} file(s) in /Needs_Action")
                return False
        except Exception as e:
            logger.error(f"✗ Error checking completion: {e}")
            return False

    def move_file_to_done(self, filepath: Path) -> bool:
        """Move processed file to /Done"""
        try:
            self.done_dir.mkdir(exist_ok=True)
            dest = self.done_dir / f"processed_{filepath.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            with open(dest, 'w', encoding='utf-8') as f:
                f.write(content)

            # Delete original
            filepath.unlink()

            logger.info(f"✓ Moved to /Done: {filepath.name}")
            return True
        except Exception as e:
            logger.error(f"✗ Error moving file: {e}")
            return False

    def run_loop(self, prompt: str) -> bool:
        """Run the Ralph Wiggum reasoning loop"""
        logger.info("=" * 70)
        logger.info("RALPH WIGGUM LOOP - Starting")
        logger.info("=" * 70)
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Max iterations: {self.max_iterations}")
        logger.info(f"Completion promise: {self.completion_promise}")
        logger.info("=" * 70)

        state_file = self.create_loop_state_file(prompt)

        for iteration in range(1, self.max_iterations + 1):
            self.current_iteration = iteration
            logger.info(f"\n🔄 ITERATION {iteration}/{self.max_iterations}")
            logger.info("-" * 70)

            try:
                # Step 1: Scan for tasks
                tasks = self.scan_needs_action()

                if not tasks:
                    logger.info("✓ No tasks in /Needs_Action - LOOP COMPLETE")
                    self.task_complete = True
                    break

                # Step 2: Process each task
                for task_file in tasks:
                    logger.info(f"\n📄 Processing: {task_file.name}")

                    # Create plan
                    plan_file = self.create_plan_from_task(task_file)

                    if plan_file:
                        logger.info(f"✓ Plan created: {plan_file.name}")
                        logger.info(f"📍 Location: {plan_file.absolute()}")
                        logger.info("\n⏸️  AWAITING HUMAN APPROVAL")
                        logger.info(f"   Review plan in: {plan_file}")
                        logger.info(f"   Location: Plans/{plan_file.name}")
                        logger.info("\n   After approving actions, move required files to /Pending_Approval")

                # Step 3: Check for completion
                if self.check_task_completion():
                    logger.info("\n✅ TASK COMPLETION DETECTED")
                    logger.info("All files processed and moved to /Done")
                    self.task_complete = True
                    break
                else:
                    logger.info(f"\n⏳ Iteration {iteration} complete - tasks remaining")
                    logger.info("Claude should continue in next iteration...")

            except Exception as e:
                logger.error(f"✗ Error in iteration {iteration}: {e}")
                continue

        # Final summary
        logger.info("\n" + "=" * 70)
        logger.info("RALPH WIGGUM LOOP - SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Iterations completed: {self.current_iteration}/{self.max_iterations}")
        logger.info(f"Task complete: {self.task_complete}")
        logger.info(f"State file: {state_file}")
        logger.info("=" * 70)

        if self.task_complete:
            logger.info("\n✅ SUCCESS: All tasks completed!")
            logger.info(f"\n<promise>{self.completion_promise}</promise>")
            return True
        else:
            logger.warning(f"\n⚠️  Max iterations ({self.max_iterations}) reached")
            logger.warning("Some tasks may still be pending human approval")
            return False

    def run_process_needs_action(self):
        """Convenience method to process /Needs_Action folder"""
        prompt = """Process all files in /Needs_Action:
1. Analyze each file with Task Analyzer
2. Create detailed Plan.md in /Plans with:
   - Clear steps with [ ] checkboxes
   - Priority levels (high/medium/low)
   - Multi-step workflow phases
   - HITL approval checkpoints
3. Handle multi-step tasks (e.g., sales lead -> draft -> approve -> publish)
4. Move processed files to /Done when complete
5. Output <promise>TASK_COMPLETE</promise> when all done
"""
        return self.run_loop(prompt)

def main():
    parser = argparse.ArgumentParser(
        description="Ralph Wiggum Loop Runner - Autonomous task completion with Claude reasoning"
    )

    parser.add_argument(
        'prompt',
        nargs='?',
        help='Task prompt for Claude to process'
    )
    parser.add_argument(
        '--completion-promise',
        default='TASK_COMPLETE',
        help='Completion promise marker (default: TASK_COMPLETE)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum loop iterations (default: 10)'
    )
    parser.add_argument(
        '--process-needs-action',
        action='store_true',
        help='Process all files in /Needs_Action (convenience mode)'
    )

    args = parser.parse_args()

    runner = RalphLoopRunner(
        max_iterations=args.max_iterations,
        completion_promise=args.completion_promise
    )

    if args.process_needs_action:
        success = runner.run_process_needs_action()
    elif args.prompt:
        success = runner.run_loop(args.prompt)
    else:
        parser.print_help()
        return 1

    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
