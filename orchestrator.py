#!/usr/bin/env python3
"""
Orchestrator.py - Master Process for Silver Tier AI Employee
Watches folders, triggers Claude, executes approvals, manages lifecycle.
Core automation engine that ties all components together.
"""

import os
import time
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
import shutil

# ============================================================================
# CONFIGURATION
# ============================================================================

VAULT_PATH = Path.home() / "AI_Employee_Vault"  # Update to your vault path
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
PLANS = VAULT_PATH / "Plans"
APPROVED = VAULT_PATH / "Approved"
REJECTED = VAULT_PATH / "Rejected"
DONE = VAULT_PATH / "Done"
IN_PROGRESS = VAULT_PATH / "In_Progress"
LOGS = VAULT_PATH / "Logs"
DASHBOARD = VAULT_PATH / "Dashboard.md"
COMPANY_HANDBOOK = VAULT_PATH / "Company_Handbook.md"

# Ensure directories exist
for directory in [NEEDS_ACTION, PLANS, APPROVED, REJECTED, DONE, IN_PROGRESS, LOGS]:
    directory.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_FILE = LOGS / f"{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# CORE ORCHESTRATION ENGINE
# ============================================================================

class TaskOrchestrator:
    """Master orchestrator that manages the AI Employee workflow."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.processed_items = set()
        logger.info("🚀 Orchestrator initialized")

    def load_company_handbook(self) -> Dict:
        """Load business rules from Company_Handbook.md"""
        try:
            with open(COMPANY_HANDBOOK, 'r') as f:
                content = f.read()
            # Parse YAML-like format
            rules = {}
            for line in content.split('\n'):
                if line.startswith('- '):
                    rule = line.replace('- ', '').strip()
                    rules[rule] = True
            return rules
        except FileNotFoundError:
            logger.warning("Company_Handbook.md not found")
            return {}

    def trigger_claude_for_task(self, task_file: Path) -> bool:
        """Trigger Claude Code to process a task file.

        In production, this would call Claude API or use subprocess to invoke
        claude command. For now, logs the intent.
        """
        try:
            task_content = task_file.read_text()
            logger.info(f"📋 Triggering Claude for: {task_file.name}")
            logger.info(f"Content preview: {task_content[:200]}")

            # TODO: Integrate with Claude API or command-line invocation
            # For hackathon, Claude is invoked separately via CLI

            return True
        except Exception as e:
            logger.error(f"Error triggering Claude: {e}")
            return False

    def watch_needs_action(self):
        """Watch /Needs_Action folder for new items."""
        logger.info("👀 Watching /Needs_Action folder...")

        while True:
            try:
                for item in NEEDS_ACTION.iterdir():
                    if item.is_file() and item.suffix == '.md':
                        item_id = item.stem

                        if item_id not in self.processed_items:
                            logger.info(f"✨ New task detected: {item.name}")
                            self.processed_items.add(item_id)

                            # Move to In_Progress
                            in_progress_file = IN_PROGRESS / item.name
                            shutil.move(str(item), str(in_progress_file))
                            logger.info(f"📌 Moved to In_Progress: {item.name}")

                            # Trigger Claude
                            self.trigger_claude_for_task(in_progress_file)

                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error watching Needs_Action: {e}")
                time.sleep(10)

    def watch_approved_folder(self):
        """Watch /Approved folder and execute approved actions."""
        logger.info("✅ Watching /Approved folder for executions...")

        while True:
            try:
                for item in APPROVED.iterdir():
                    if item.is_file() and item.suffix == '.md':
                        logger.info(f"✅ Executing approved action: {item.name}")

                        # Parse action from file
                        content = item.read_text()

                        # Execute based on action type
                        if 'action: send_email' in content.lower():
                            self.execute_email_action(item)
                        elif 'action: post_linkedin' in content.lower():
                            self.execute_linkedin_action(item)
                        elif 'action: send_whatsapp' in content.lower():
                            self.execute_whatsapp_action(item)

                        # Move to Done
                        done_file = DONE / item.name
                        shutil.move(str(item), str(done_file))
                        logger.info(f"✓ Completed and moved to Done: {item.name}")

                time.sleep(5)
            except Exception as e:
                logger.error(f"Error watching Approved: {e}")
                time.sleep(10)

    def execute_email_action(self, task_file: Path):
        """Execute email sending action."""
        try:
            content = task_file.read_text()
            logger.info(f"📧 Executing email action from {task_file.name}")

            # Extract email details from frontmatter
            # Format: to:, subject:, body:
            lines = content.split('\n')
            action_data = {}
            for line in lines:
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    action_data[key.strip()] = value.strip()

            # Log the action (in real implementation, would call MCP)
            self.log_action({
                'type': 'email_send',
                'to': action_data.get('to'),
                'subject': action_data.get('subject'),
                'status': 'executed',
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error executing email action: {e}")

    def execute_linkedin_action(self, task_file: Path):
        """Execute LinkedIn posting action."""
        try:
            content = task_file.read_text()
            logger.info(f"🔗 Executing LinkedIn post from {task_file.name}")

            self.log_action({
                'type': 'linkedin_post',
                'status': 'executed',
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error executing LinkedIn action: {e}")

    def execute_whatsapp_action(self, task_file: Path):
        """Execute WhatsApp sending action."""
        try:
            content = task_file.read_text()
            logger.info(f"💬 Executing WhatsApp action from {task_file.name}")

            self.log_action({
                'type': 'whatsapp_send',
                'status': 'executed',
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error executing WhatsApp action: {e}")

    def update_dashboard(self):
        """Update Dashboard.md with current system status."""
        try:
            pending_count = len(list(NEEDS_ACTION.glob('*.md')))
            in_progress_count = len(list(IN_PROGRESS.glob('*.md')))
            approved_count = len(list(APPROVED.glob('*.md')))
            done_today = len([f for f in DONE.glob('*.md')
                             if f.stat().st_mtime > time.time() - 86400])

            # Count pending approvals
            pending_approvals = list(NEEDS_ACTION.glob('*APPROVAL*'))

            dashboard_content = f"""# Dashboard - Last Updated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Status
- **Status**: 🟢 Running
- **Last Update**: {datetime.now().isoformat()}

## Task Queue
- **Pending Tasks**: {pending_count}
- **In Progress**: {in_progress_count}
- **Awaiting Approval**: {approved_count}
- **Completed Today**: {done_today}

## Pending Approvals
{self._format_pending_approvals(pending_approvals)}

## Recent Activity
{self._format_recent_activity()}

## Next Scheduled Tasks
- Daily Briefing: 8:00 AM
- LinkedIn Auto-Post: Every 2 hours
- Email Check: Every 5 minutes

---
*Auto-generated by Orchestrator.py*
"""

            with open(DASHBOARD, 'w') as f:
                f.write(dashboard_content)

            logger.info("📊 Dashboard updated")

        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

    def _format_pending_approvals(self, approvals: List[Path]) -> str:
        """Format pending approvals for dashboard."""
        if not approvals:
            return "- None"
        return '\n'.join([f"- {a.name}" for a in approvals[:5]])

    def _format_recent_activity(self) -> str:
        """Format recent completed tasks."""
        try:
            recent = sorted(DONE.glob('*.md'),
                          key=lambda x: x.stat().st_mtime,
                          reverse=True)[:5]
            if not recent:
                return "- None"
            return '\n'.join([f"- {f.name}" for f in recent])
        except:
            return "- Unable to load"

    def log_action(self, action: Dict):
        """Log action to JSON log file."""
        try:
            log_file = LOGS / f"{datetime.now().strftime('%Y-%m-%d')}.json"

            # Append to log file
            logs = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)

            logs.append(action)

            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)

            logger.info(f"📝 Action logged: {action['type']}")

        except Exception as e:
            logger.error(f"Error logging action: {e}")

    def run(self):
        """Start the orchestrator main loop."""
        logger.info("=" * 60)
        logger.info("ORCHESTRATOR STARTED")
        logger.info("=" * 60)
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Watching: {NEEDS_ACTION}")
        logger.info("=" * 60)

        # Start dashboard update loop in background
        import threading
        dashboard_thread = threading.Thread(target=self._dashboard_loop, daemon=True)
        dashboard_thread.start()

        # Main loop: watch folders
        try:
            # Note: In production, use proper observer pattern
            # For now, use simple polling
            self.watch_needs_action()
        except KeyboardInterrupt:
            logger.info("Orchestrator stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in orchestrator: {e}")

    def _dashboard_loop(self):
        """Background thread to update dashboard every 30 seconds."""
        while True:
            try:
                self.update_dashboard()
                time.sleep(30)
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                time.sleep(30)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Verify vault exists
    if not VAULT_PATH.exists():
        print(f"❌ Vault not found at {VAULT_PATH}")
        print(f"   Update VAULT_PATH in orchestrator.py")
        exit(1)

    orchestrator = TaskOrchestrator(VAULT_PATH)
    orchestrator.run()
