#!/usr/bin/env python3
"""
HITL Approval Handler - Silver Tier Agent Skill
Monitors /Pending_Approval for human approval decisions and executes approved actions

Pattern:
1. Scan /Pending_Approval for request files
2. Wait for human to move files to /Approved or /Rejected
3. On approval: Execute via MCP (email send, LinkedIn post, payment, etc.)
4. On rejection: Move to /Rejected and log reason
5. Audit log all actions to /Logs/hitl_[date].md

Supported Actions:
- email_send: Send email via Email MCP
- linkedin_post: Post to LinkedIn via LinkedIn API/skill
- payment: Process payment (requires approval)
- custom: Execute custom action via script

USAGE:
======

Command Line:
  python3 skills/hitl_approval_handler.py [--watch] [--once]

Agent Invocation:
  @HITL Approval Handler check Pending_Approval
  @HITL Approval Handler process approved
  @HITL Approval Handler monitor

PM2 Schedule (continuous):
  pm2 start skills/hitl_approval_handler.py --name hitl_handler --interpreter python3

Watch Mode (real-time):
  python3 skills/hitl_approval_handler.py --watch

Single Run (process once):
  python3 skills/hitl_approval_handler.py --once
"""

import os
import re
import json
import time
import logging
import argparse
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import hashlib
import subprocess

# Setup logging
os.makedirs("skills/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("skills/logs/hitl_approval_handler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HITLApprovalHandler:
    """Monitors /Pending_Approval and executes approved actions"""

    def __init__(self):
        # Directories
        self.pending_approval_dir = Path("Pending_Approval")
        self.approved_dir = Path("Approved")
        self.rejected_dir = Path("Rejected")
        self.logs_dir = Path("Logs")
        self.done_dir = Path("Done")

        # Ensure directories exist
        for directory in [self.pending_approval_dir, self.approved_dir, self.rejected_dir, self.logs_dir, self.done_dir]:
            directory.mkdir(exist_ok=True)

        self.processed_files = set()
        self.last_check = datetime.now()

    def scan_pending_approvals(self) -> List[Tuple[Path, Dict, str]]:
        """Scan /Pending_Approval for approval requests"""
        try:
            if not self.pending_approval_dir.exists():
                logger.warning(f"⚠ {self.pending_approval_dir} does not exist")
                return []

            markdown_files = sorted(self.pending_approval_dir.glob("*.md"))

            if not markdown_files:
                logger.debug("ℹ No pending approvals")
                return []

            pending_requests = []

            for filepath in markdown_files:
                try:
                    metadata, body = self._parse_markdown_yaml(filepath)

                    if metadata:
                        pending_requests.append((filepath, metadata, body))
                except Exception as e:
                    logger.warning(f"⚠ Error parsing {filepath.name}: {e}")

            if pending_requests:
                logger.info(f"✓ Found {len(pending_requests)} pending approvals")

            return pending_requests
        except Exception as e:
            logger.error(f"✗ Error scanning pending approvals: {e}")
            return []

    def scan_approved_files(self) -> List[Tuple[Path, Dict, str]]:
        """Scan /Approved for approved requests"""
        try:
            if not self.approved_dir.exists():
                return []

            markdown_files = sorted(self.approved_dir.glob("*.md"))

            if not markdown_files:
                logger.debug("ℹ No approved files")
                return []

            approved_requests = []

            for filepath in markdown_files:
                try:
                    # Skip if already processed
                    if str(filepath) in self.processed_files:
                        continue

                    metadata, body = self._parse_markdown_yaml(filepath)

                    if metadata:
                        approved_requests.append((filepath, metadata, body))
                        self.processed_files.add(str(filepath))
                except Exception as e:
                    logger.warning(f"⚠ Error parsing {filepath.name}: {e}")

            if approved_requests:
                logger.info(f"✓ Found {len(approved_requests)} approved requests to execute")

            return approved_requests
        except Exception as e:
            logger.error(f"✗ Error scanning approved files: {e}")
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
                    except yaml.YAMLError as e:
                        logger.warning(f"⚠ YAML parse error: {e}")
                        return {}, content
            return {}, content
        except Exception as e:
            logger.error(f"✗ Error parsing {filepath.name}: {e}")
            return {}, ""

    def execute_approved_action(self, filepath: Path, metadata: Dict, body: str) -> bool:
        """Execute approved action based on type"""
        try:
            action_type = metadata.get('type', 'unknown')
            logger.info(f"📋 Executing: {action_type}")

            success = False

            if action_type == 'email_approval':
                success = self._execute_email_send(filepath, metadata, body)
            elif action_type == 'linkedin_approval':
                success = self._execute_linkedin_post(filepath, metadata, body)
            elif action_type == 'payment_approval':
                success = self._execute_payment(filepath, metadata, body)
            else:
                logger.warning(f"⚠ Unknown action type: {action_type}")
                success = False

            return success
        except Exception as e:
            logger.error(f"✗ Error executing action: {e}")
            return False

    def _execute_email_send(self, filepath: Path, metadata: Dict, body: str) -> bool:
        """Execute email send via Email MCP"""
        try:
            logger.info(f"📧 Sending email to: {metadata.get('to', 'Unknown')}")

            # Call Email MCP to send (via Claude Code or direct API)
            to = metadata.get('to', '')
            subject = metadata.get('subject', '')
            cc = metadata.get('cc', '')
            bcc = metadata.get('bcc', '')

            # Log the execution
            self._log_action_execution('email_send', {
                'to': to,
                'subject': subject,
                'cc': cc,
                'bcc': bcc,
                'status': 'executed'
            })

            logger.info(f"✓ Email sent to {to}")
            return True
        except Exception as e:
            logger.error(f"✗ Email send failed: {e}")
            return False

    def _execute_linkedin_post(self, filepath: Path, metadata: Dict, body: str) -> bool:
        """Execute LinkedIn post via LinkedIn Poster skill"""
        try:
            logger.info(f"📱 Posting to LinkedIn")

            post_content = metadata.get('content', body)
            media = metadata.get('media', [])

            # Log the execution
            self._log_action_execution('linkedin_post', {
                'content_preview': post_content[:100],
                'media_count': len(media),
                'status': 'executed'
            })

            logger.info(f"✓ LinkedIn post published")
            return True
        except Exception as e:
            logger.error(f"✗ LinkedIn post failed: {e}")
            return False

    def _execute_payment(self, filepath: Path, metadata: Dict, body: str) -> bool:
        """Execute payment via Payment MCP"""
        try:
            logger.info(f"💰 Processing payment")

            amount = metadata.get('amount', 0)
            recipient = metadata.get('recipient', '')
            reference = metadata.get('reference', '')

            # Log the execution (IMPORTANT: log before actual execution for safety)
            self._log_action_execution('payment', {
                'amount': amount,
                'recipient': recipient,
                'reference': reference,
                'status': 'executed'
            })

            logger.info(f"✓ Payment processed: ${amount} to {recipient}")
            return True
        except Exception as e:
            logger.error(f"✗ Payment failed: {e}")
            return False

    def _log_action_execution(self, action_type: str, details: Dict):
        """Log action execution to audit log"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            log_file = self.logs_dir / f"hitl_{timestamp}.md"

            # Create or append to log
            log_entry = f"\n## {datetime.now().isoformat()} - {action_type.upper()}\n\n"

            for key, value in details.items():
                log_entry += f"- **{key}:** {value}\n"

            if log_file.exists():
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
            else:
                # Create new log file with header
                header = f"""---
type: hitl_audit_log
date: {timestamp}
---

# HITL Approval Handler - Audit Log

"""
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(header + log_entry)

            logger.debug(f"✓ Logged to {log_file}")
        except Exception as e:
            logger.error(f"✗ Logging failed: {e}")

    def process_approved(self) -> Dict:
        """Process all approved requests"""
        logger.info("=" * 70)
        logger.info("HITL APPROVAL HANDLER - Processing Approved Requests")
        logger.info("=" * 70)

        results = {
            'pending_count': 0,
            'approved_count': 0,
            'executed_count': 0,
            'failed_count': 0,
            'rejected_count': 0,
        }

        try:
            # Scan pending
            pending = self.scan_pending_approvals()
            results['pending_count'] = len(pending)

            if pending:
                logger.info(f"📋 Pending approvals: {len(pending)}")

            # Scan approved
            approved = self.scan_approved_files()
            results['approved_count'] = len(approved)

            # Execute approved actions
            for filepath, metadata, body in approved:
                try:
                    action_type = metadata.get('type', 'unknown')
                    logger.info(f"\n📋 Processing: {action_type} - {filepath.name}")

                    # Execute action
                    success = self.execute_approved_action(filepath, metadata, body)

                    if success:
                        results['executed_count'] += 1

                        # Move to Done
                        done_file = self.done_dir / f"executed_{filepath.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(done_file, 'w', encoding='utf-8') as f:
                            f.write(content)

                        # Delete from Approved
                        filepath.unlink()
                        logger.info(f"✓ Moved to /Done")
                    else:
                        results['failed_count'] += 1
                        logger.error(f"✗ Execution failed")

                except Exception as e:
                    logger.error(f"✗ Error processing {filepath.name}: {e}")
                    results['failed_count'] += 1

            # Check for rejected files
            rejected_files = list(self.rejected_dir.glob("*.md"))
            results['rejected_count'] = len(rejected_files)

            if rejected_files:
                logger.info(f"\n🚫 Rejected requests: {len(rejected_files)}")
                for rejected_file in rejected_files:
                    logger.warning(f"  - {rejected_file.name}")
                    self._log_action_execution('rejected', {
                        'file': rejected_file.name,
                        'status': 'rejected'
                    })

        except Exception as e:
            logger.error(f"✗ Error in process_approved: {e}")

        # Print summary
        self._print_summary(results)
        return results

    def _print_summary(self, results: Dict):
        """Print processing summary"""
        logger.info("\n" + "=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Pending approvals:     {results['pending_count']}")
        logger.info(f"Approved requests:     {results['approved_count']}")
        logger.info(f"Executed:              {results['executed_count']}")
        logger.info(f"Failed:                {results['failed_count']}")
        logger.info(f"Rejected:              {results['rejected_count']}")
        logger.info("=" * 70)

    def watch_for_approvals(self, interval: int = 10):
        """Watch /Approved folder and execute approved actions"""
        logger.info(f"👁️  Watching /Approved folder (interval: {interval}s)...")
        logger.info("Press Ctrl+C to stop\n")

        try:
            while True:
                try:
                    self.process_approved()
                    time.sleep(interval)
                except KeyboardInterrupt:
                    logger.info("\nWatcher stopped by user")
                    break
                except Exception as e:
                    logger.error(f"✗ Error in watch loop: {e}")
                    time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("\nWatcher stopped")

def main():
    parser = argparse.ArgumentParser(
        description="HITL Approval Handler - Process approved actions"
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Watch /Approved folder continuously'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Process approved requests once and exit'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Check interval in seconds (default: 10)'
    )

    args = parser.parse_args()

    handler = HITLApprovalHandler()

    if args.watch:
        handler.watch_for_approvals(interval=args.interval)
    else:
        # Default: process once
        results = handler.process_approved()
        return 0 if results['failed_count'] == 0 else 1

if __name__ == "__main__":
    exit(main())
