#!/usr/bin/env python3
"""
Auto LinkedIn Poster Agent Skill - Silver Tier
Scans /Needs_Action for sales/business leads and drafts LinkedIn posts
Implements HITL (Human In The Loop) approval workflow

SKILL USAGE:
============

Command Line:
  python3 skills/auto_linkedin_poster.py [--process] [--dry-run]

Agent Invocation:
  @Auto LinkedIn Poster process sales lead
  @Auto LinkedIn Poster scan

PM2 Schedule:
  pm2 start skills/auto_linkedin_poster.py --name auto_linkedin_poster --interpreter python3 --cron "0 * * * *"

WORKFLOW:
=========
1. Scan /Needs_Action for files with keywords: sales, client, project
2. Extract YAML metadata and message content
3. Reference Company_Handbook.md for tone/language guidelines
4. Draft LinkedIn post with template: "Excited to offer [service] for [benefit]! DM for more."
5. Save draft to /Plans/linkedin_post_[date]_[hash].md with YAML metadata
6. HITL: Move to /Pending_Approval for human review and approval
7. Once approved, ready for publishing

TESTING:
========
1. Create test file in /Needs_Action with keywords
2. Run: python3 schedulers/auto_linkedin_poster.py --dry-run
3. Check /Plans for draft files
4. Review YAML metadata and content
5. Move approved posts to /Approved folder
"""

import os
import re
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import hashlib
import yaml
import argparse

# Setup logging
os.makedirs("skills/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("skills/logs/auto_linkedin_poster.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoLinkedInPoster:
    KEYWORDS = ['sales', 'client', 'project']
    NEEDS_ACTION_DIR = Path("Needs_Action")
    PLANS_DIR = Path("Plans")
    PENDING_APPROVAL_DIR = Path("Pending_Approval")
    APPROVED_DIR = Path("Approved")
    HANDBOOK_PATH = Path("Company_Handbook.md")

    # LinkedIn post templates
    POST_TEMPLATES = [
        "Excited to offer {service} for {benefit}! DM for more.",
        "Looking to help with {service}? {benefit} is our specialty. Let's connect!",
        "We specialize in {service}. {benefit} guaranteed. Reach out!",
    ]

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.handbook_guidelines = self.load_handbook()
        self.processed_files = set()
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.NEEDS_ACTION_DIR, self.PLANS_DIR, self.PENDING_APPROVAL_DIR, self.APPROVED_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info("✓ Directories verified")

    def load_handbook(self) -> str:
        """Load Company Handbook guidelines"""
        try:
            if self.HANDBOOK_PATH.exists():
                with open(self.HANDBOOK_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info("✓ Loaded Company_Handbook.md")
                return content
            else:
                logger.warning("⚠ Company_Handbook.md not found")
                return "Default: Be polite and professional."
        except Exception as e:
            logger.error(f"✗ Error loading handbook: {e}")
            return "Default: Be polite and professional."

    def parse_markdown_yaml(self, filepath: Path) -> Tuple[Dict, str]:
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
                        logger.warning(f"⚠ YAML parse error in {filepath.name}: {e}")
                        return {}, content
            return {}, content
        except Exception as e:
            logger.error(f"✗ Error parsing {filepath.name}: {e}")
            return {}, ""

    def extract_lead_info(self, metadata: Dict, body: str) -> Optional[Dict]:
        """Extract lead information from parsed markdown"""
        try:
            # Check if content matches keywords
            combined_text = f"{metadata.get('subject', '')} {body}".lower()
            has_keyword = any(kw in combined_text for kw in self.KEYWORDS)

            if not has_keyword:
                return None

            lead_info = {
                'from': metadata.get('from', 'Unknown Contact'),
                'subject': metadata.get('subject', '(No Subject)'),
                'priority': metadata.get('priority', 'medium'),
                'type': metadata.get('type', 'unknown'),
                'content': body,
                'source': metadata.get('source', 'unknown'),
                'received': metadata.get('received', datetime.now().isoformat()),
            }

            return lead_info
        except Exception as e:
            logger.error(f"✗ Error extracting lead info: {e}")
            return None

    def scan_needs_action(self) -> List[Tuple[Path, Dict, str]]:
        """Scan /Needs_Action for sales/business leads"""
        leads = []
        try:
            if not self.NEEDS_ACTION_DIR.exists():
                logger.warning(f"⚠ {self.NEEDS_ACTION_DIR} does not exist")
                return leads

            markdown_files = sorted(self.NEEDS_ACTION_DIR.glob("*.md"))

            if not markdown_files:
                logger.info("ℹ No files found in /Needs_Action")
                return leads

            for filepath in markdown_files:
                try:
                    metadata, body = self.parse_markdown_yaml(filepath)
                    lead_info = self.extract_lead_info(metadata, body)

                    if lead_info:
                        leads.append((filepath, lead_info, body))
                except Exception as e:
                    logger.warning(f"⚠ Error processing {filepath.name}: {e}")

            if leads:
                logger.info(f"✓ Found {len(leads)} sales/business leads")

            return leads
        except Exception as e:
            logger.error(f"✗ Error scanning /Needs_Action: {e}")
            return []

    def draft_post(self, lead: Dict) -> str:
        """Draft LinkedIn post from lead information"""
        try:
            # Extract service and benefit from lead content
            content_lower = lead['content'].lower()

            # Simple extraction - can be enhanced
            service = "our services"
            benefit = "professional support"

            # Try to extract from source
            if lead['source'] in ['gmail', 'whatsapp', 'linkedin']:
                if 'invoice' in content_lower:
                    service = "invoice management solutions"
                    benefit = "streamlined financial processes"
                elif 'payment' in content_lower:
                    service = "payment solutions"
                    benefit = "seamless transactions"
                elif 'sales' in content_lower:
                    service = "sales enablement"
                    benefit = "increased revenue"
                elif 'project' in content_lower:
                    service = "project management expertise"
                    benefit = "on-time delivery"

            # Use template
            template = self.POST_TEMPLATES[0]
            post = template.format(service=service, benefit=benefit)

            # Ensure polite tone (from handbook)
            post = self.ensure_polite_tone(post)

            return post
        except Exception as e:
            logger.error(f"✗ Error drafting post: {e}")
            return "Excited to connect on business opportunities! DM for more."

    def ensure_polite_tone(self, text: str) -> str:
        """Ensure text follows Company Handbook guidelines"""
        # Handbook says: Always be polite in replies
        polite_replacements = {
            'need': 'would appreciate',
            'must': 'should',
            'can\'t': 'unable to',
            'don\'t': 'do not',
        }

        for word, replacement in polite_replacements.items():
            text = re.sub(rf'\b{word}\b', replacement, text, flags=re.IGNORECASE)

        return text

    def save_draft(self, lead: Dict, post: str, source_file: Path) -> Optional[Path]:
        """Save draft post to /Plans with YAML metadata"""
        try:
            self.PLANS_DIR.mkdir(exist_ok=True)

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            lead_hash = hashlib.md5(post.encode()).hexdigest()[:6]
            safe_from = "".join(c for c in lead['from'] if c.isalnum() or c in ' -_')[:20]
            filename = f"linkedin_post_{timestamp}_{lead_hash}_{safe_from}.md"
            filepath = self.PLANS_DIR / filename

            # Create markdown with YAML frontmatter
            content = f"""---
type: linkedin_post
from: {lead['from']}
subject: LinkedIn Post Draft
source_lead: {source_file.name}
priority: {lead['priority']}
status: draft
requires_approval: true
created_at: {datetime.now().isoformat()}
keywords: {', '.join(self.KEYWORDS)}
---

# LinkedIn Post Draft

**From Lead:** {lead['from']}

**Source:** {lead['source'].upper()} ({source_file.name})

**Priority:** {lead['priority'].upper()}

**Status:** Awaiting Approval

---

## Post Content

{post}

---

## Lead Context

**Original Subject:** {lead['subject']}

**Received:** {lead['received']}

---

## Action Required

This post draft is ready for review and approval.

- [ ] Review post content
- [ ] Verify tone (per Company_Handbook.md)
- [ ] Approve draft
- [ ] Move to /Approved
- [ ] Publish to LinkedIn

**Next Step:** Move this file to /Pending_Approval for HITL review.
"""

            if not self.dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✓ Draft saved: {filepath}")
            else:
                logger.info(f"[DRY-RUN] Would save: {filepath}")

            return filepath
        except Exception as e:
            logger.error(f"✗ Error saving draft: {e}")
            return None

    def move_to_pending_approval(self, draft_file: Path, source_file: Path) -> bool:
        """Move draft to /Pending_Approval for HITL review"""
        try:
            self.PENDING_APPROVAL_DIR.mkdir(exist_ok=True)

            target_file = self.PENDING_APPROVAL_DIR / draft_file.name

            if not self.dry_run:
                # Copy draft to pending approval
                with open(draft_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Update status in metadata
                with open(target_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Update status field
                content = content.replace('status: draft', 'status: pending_approval')

                with open(target_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f"✓ Moved to approval: {target_file.name}")
            else:
                logger.info(f"[DRY-RUN] Would move to: {target_file}")

            return True
        except Exception as e:
            logger.error(f"✗ Error moving to approval: {e}")
            return False

    def process_leads(self) -> Dict:
        """Process all identified sales leads"""
        logger.info("=" * 60)
        logger.info("AUTO LINKEDIN POSTER - Processing Leads")
        logger.info("=" * 60)

        results = {
            'scanned': 0,
            'leads_found': 0,
            'posts_drafted': 0,
            'pending_approval': 0,
            'errors': 0,
        }

        try:
            leads = self.scan_needs_action()
            results['scanned'] = len(list(self.NEEDS_ACTION_DIR.glob("*.md"))) if self.NEEDS_ACTION_DIR.exists() else 0
            results['leads_found'] = len(leads)

            for source_file, lead_info, body in leads:
                try:
                    # Draft post
                    post = self.draft_post(lead_info)
                    logger.info(f"✓ Drafted post for: {lead_info['from']}")

                    # Save draft
                    draft_file = self.save_draft(lead_info, post, source_file)
                    if draft_file:
                        results['posts_drafted'] += 1

                        # Move to pending approval (HITL)
                        if self.move_to_pending_approval(draft_file, source_file):
                            results['pending_approval'] += 1
                            logger.info(f"✓ Post moved to /Pending_Approval for approval")
                except Exception as e:
                    logger.error(f"✗ Error processing lead: {e}")
                    results['errors'] += 1

        except Exception as e:
            logger.error(f"✗ Error in process_leads: {e}")
            results['errors'] += 1

        # Print summary
        self.print_summary(results)
        return results

    def print_summary(self, results: Dict):
        """Print processing summary"""
        logger.info("=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Files scanned:         {results['scanned']}")
        logger.info(f"Sales leads found:     {results['leads_found']}")
        logger.info(f"Posts drafted:         {results['posts_drafted']}")
        logger.info(f"Pending approval:      {results['pending_approval']}")
        logger.info(f"Errors:                {results['errors']}")
        logger.info("=" * 60)

        if results['pending_approval'] > 0:
            logger.info(f"\n📋 HITL REQUIRED: {results['pending_approval']} post(s) awaiting approval")
            logger.info(f"📂 Location: {self.PENDING_APPROVAL_DIR.absolute()}")

def main():
    parser = argparse.ArgumentParser(
        description="Auto LinkedIn Poster - Agent Skill for Silver Tier"
    )
    parser.add_argument('--process', action='store_true', help='Process leads and draft posts')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no files created)')
    args = parser.parse_args()

    # If no args, default to process
    if not args.process and not args.dry_run:
        args.process = True

    dry_run = args.dry_run
    if dry_run:
        logger.info("[DRY-RUN MODE] No files will be created")

    poster = AutoLinkedInPoster(dry_run=dry_run)
    results = poster.process_leads()

    return 0 if results['errors'] == 0 else 1

if __name__ == "__main__":
    exit(main())
