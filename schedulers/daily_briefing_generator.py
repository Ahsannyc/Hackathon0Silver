#!/usr/bin/env python3
"""
Daily Briefing Generator - Silver Tier Scheduler
Generates daily briefing from /Done files and writes to /Logs/daily_briefing_[date].md

This script is called by daily_scheduler.sh (Mac/Linux) or daily_scheduler.ps1 (Windows)
at 8AM each day via cron or Task Scheduler.

Usage:
  python3 schedulers/daily_briefing_generator.py

Cron Setup (Linux/Mac):
  0 8 * * * /path/to/daily_scheduler.sh

Windows Task Scheduler:
  Create task to run: powershell -ExecutionPolicy Bypass -File C:\path\to\daily_scheduler.ps1

FEATURES:
=========
- Scans /Done for completed tasks from yesterday
- Counts completed actions
- Generates briefing with metrics
- Saves to /Logs/daily_briefing_[date].md
- Logs errors to /Logs/scheduler.log
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

# Setup logging
os.makedirs("Logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("Logs/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyBriefingGenerator:
    """Generates daily briefing from completed tasks"""

    def __init__(self):
        self.done_dir = Path("Done")
        self.logs_dir = Path("Logs")
        self.today = datetime.now()
        self.yesterday = self.today - timedelta(days=1)

        # Ensure directories exist
        self.done_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    def scan_completed_tasks(self) -> List[Tuple[Path, Dict]]:
        """Scan /Done for completed tasks"""
        try:
            if not self.done_dir.exists():
                logger.warning(f"⚠ {self.done_dir} does not exist")
                return []

            tasks = []
            markdown_files = sorted(self.done_dir.glob("*.md"))

            for filepath in markdown_files:
                try:
                    metadata, _ = self._parse_markdown_yaml(filepath)

                    # Check file modification time (approximate completion time)
                    file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime)

                    # Include if modified in last 24 hours
                    if self._is_recent(file_mtime):
                        tasks.append((filepath, metadata))
                except Exception as e:
                    logger.warning(f"⚠ Error parsing {filepath.name}: {e}")

            logger.info(f"✓ Found {len(tasks)} completed tasks")
            return tasks
        except Exception as e:
            logger.error(f"✗ Error scanning completed tasks: {e}")
            return []

    def _parse_markdown_yaml(self, filepath: Path) -> Tuple[Dict, str]:
        """Parse markdown file with YAML frontmatter"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    body = parts[2].strip()

                    try:
                        metadata = yaml.safe_load(yaml_content) or {}
                        return metadata, body
                    except Exception as e:
                        logger.warning(f"⚠ YAML parse error: {e}")
                        return {}, content
            return {}, content
        except Exception as e:
            logger.error(f"✗ Error parsing {filepath.name}: {e}")
            return {}, ""

    def _is_recent(self, file_time: datetime) -> bool:
        """Check if file was modified in last 24 hours"""
        time_diff = self.today - file_time
        return timedelta(hours=0) <= time_diff <= timedelta(hours=24)

    def categorize_tasks(self, tasks: List[Tuple[Path, Dict]]) -> Dict[str, List]:
        """Categorize tasks by type"""
        categories = {
            'emails': [],
            'linkedin_posts': [],
            'approvals': [],
            'plans': [],
            'other': []
        }

        for filepath, metadata in tasks:
            task_type = metadata.get('type', 'unknown').lower()

            if 'email' in task_type:
                categories['emails'].append((filepath, metadata))
            elif 'linkedin' in task_type or 'post' in task_type:
                categories['linkedin_posts'].append((filepath, metadata))
            elif 'approval' in task_type or 'hitl' in task_type:
                categories['approvals'].append((filepath, metadata))
            elif 'plan' in task_type:
                categories['plans'].append((filepath, metadata))
            else:
                categories['other'].append((filepath, metadata))

        return categories

    def generate_briefing(self) -> str:
        """Generate daily briefing markdown"""
        try:
            logger.info("📊 Generating daily briefing...")

            # Get current date in local timezone
            date_str = datetime.now().strftime("%Y-%m-%d")
            title_date = datetime.now().strftime("%A, %B %d, %Y")

            # Scan completed tasks
            tasks = self.scan_completed_tasks()
            categories = self.categorize_tasks(tasks)

            # Count totals
            total_completed = len(tasks)
            email_count = len(categories['emails'])
            linkedin_count = len(categories['linkedin_posts'])
            approval_count = len(categories['approvals'])
            plan_count = len(categories['plans'])

            # Generate markdown
            briefing = f"""---
type: daily_briefing
date: {date_str}
generated: {datetime.now().isoformat()}
total_completed: {total_completed}
---

# Daily Briefing - {title_date}

**Generated:** {datetime.now().strftime('%H:%M:%S')}

---

## 📈 Metrics

| Metric | Count |
|--------|-------|
| **Total Completed** | {total_completed} |
| Emails Sent | {email_count} |
| LinkedIn Posts | {linkedin_count} |
| Approvals Processed | {approval_count} |
| Plans Created | {plan_count} |
| Other | {len(categories['other'])} |

---

## 📧 Emails ({email_count})

"""

            # Add email briefing
            if categories['emails']:
                for filepath, metadata in categories['emails']:
                    to = metadata.get('to', 'Unknown')
                    subject = metadata.get('subject', '(No Subject)')
                    briefing += f"- **{subject}** → {to}\n"
            else:
                briefing += "- No emails sent today\n"

            briefing += f"\n## 📱 LinkedIn Posts ({linkedin_count})\n\n"

            # Add LinkedIn briefing
            if categories['linkedin_posts']:
                for filepath, metadata in categories['linkedin_posts']:
                    content = metadata.get('content', 'No content')[:80]
                    briefing += f"- {content}...\n"
            else:
                briefing += "- No LinkedIn posts today\n"

            briefing += f"\n## ✅ Approvals Processed ({approval_count})\n\n"

            # Add approval briefing
            if categories['approvals']:
                for filepath, metadata in categories['approvals']:
                    action = metadata.get('action', 'Unknown')
                    status = metadata.get('status', 'Unknown')
                    briefing += f"- {action}: {status}\n"
            else:
                briefing += "- No approvals processed today\n"

            briefing += f"\n## 📋 Plans Created ({plan_count})\n\n"

            # Add plan briefing
            if categories['plans']:
                for filepath, metadata in categories['plans']:
                    task_type = metadata.get('task_type', 'Unknown')
                    priority = metadata.get('priority', 'medium')
                    briefing += f"- {task_type} ({priority} priority)\n"
            else:
                briefing += "- No plans created today\n"

            # Add insights
            briefing += "\n---\n\n## 💡 Insights\n\n"

            if total_completed > 0:
                insights = []
                if email_count > 3:
                    insights.append(f"📧 High email volume today ({email_count} emails)")
                if linkedin_count > 0:
                    insights.append(f"📱 Successfully posted {linkedin_count} LinkedIn post(s)")
                if approval_count > 0:
                    insights.append(f"✅ Processed {approval_count} approval(s) with HITL")

                if insights:
                    for insight in insights:
                        briefing += f"- {insight}\n"
                else:
                    briefing += "- Daily operations completed successfully\n"
            else:
                briefing += "- No tasks completed today\n"

            briefing += "\n---\n\n"
            briefing += "**Summary Generated by Daily Scheduler**\n"
            briefing += f"*Next briefing: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d at 08:00 AM')}*\n"

            return briefing
        except Exception as e:
            logger.error(f"✗ Error generating briefing: {e}")
            return f"Error generating briefing: {e}"

    def save_briefing(self, briefing: str) -> bool:
        """Save briefing to file"""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            briefing_file = self.logs_dir / f"daily_briefing_{date_str}.md"

            with open(briefing_file, 'w', encoding='utf-8') as f:
                f.write(briefing)

            logger.info(f"✓ Briefing saved: {briefing_file}")
            return True
        except Exception as e:
            logger.error(f"✗ Error saving briefing: {e}")
            return False

    def run(self) -> bool:
        """Generate and save daily briefing"""
        try:
            logger.info("=" * 70)
            logger.info("DAILY BRIEFING GENERATOR")
            logger.info("=" * 70)

            briefing = self.generate_briefing()
            success = self.save_briefing(briefing)

            logger.info("=" * 70)

            return success
        except Exception as e:
            logger.error(f"✗ Fatal error: {e}")
            return False

def main():
    """Main entry point"""
    generator = DailyBriefingGenerator()
    success = generator.run()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
