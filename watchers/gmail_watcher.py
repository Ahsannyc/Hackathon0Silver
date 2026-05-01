#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher Script - Silver Tier
Monitors unread important emails with specified keywords
Saves notifications to /Needs_Action as markdown files with YAML metadata

INSTRUCTIONS:
=============

1. SETUP:
   - Place credentials.json in project root (obtain from Google Cloud Console)
   - Install dependencies: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   - First run will prompt for OAuth authorization

2. RUN WITH PM2:
   - pm2 start watchers/gmail_watcher.py --name gmail_watcher --interpreter python3
   - pm2 logs gmail_watcher
   - pm2 delete gmail_watcher

3. TEST:
   - Send test email with subject "URGENT invoice #12345 - Test"
   - Check /Needs_Action for new .md file
   - Verify YAML metadata is populated correctly

4. CONFIGURATION:
   - KEYWORDS: urgent, invoice, payment, sales
   - CHECK_INTERVAL: 120 seconds
   - LOOKBACK: checks last 5 minutes of emails

5. LOGS:
   - Logs written to watchers/logs/gmail_watcher.log
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import hashlib

# Fix UTF-8 encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials
    from google.oauth2.credentials import Credentials as OAuth2Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient import discovery
    HAS_GMAIL_API = True
except ImportError:
    HAS_GMAIL_API = False
    print("WARNING: Google API libraries not installed. Install: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Setup logging
os.makedirs("watchers/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("watchers/logs/gmail_watcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GmailWatcher:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    KEYWORDS = ['urgent', 'invoice', 'payment', 'sales']
    CHECK_INTERVAL = 120  # seconds
    NEEDS_ACTION_DIR = Path("Needs_Action")
    TOKEN_PATH = Path("watchers/.gmail_token.json")
    CREDS_PATH = Path("credentials.json")

    # Connection recovery settings
    BACKOFF_INITIAL = 2  # seconds
    BACKOFF_MAX = 60  # seconds
    CONNECTION_RESET_INTERVAL = 3600  # 60 minutes

    def __init__(self):
        self.service = None
        self.last_check_time = datetime.now() - timedelta(minutes=5)
        self.processed_email_ids = set()
        self.consecutive_errors = 0
        self.last_connection_reset = time.time()
        self.authenticate()

    def authenticate(self):
        """Authenticate with Gmail API"""
        try:
            creds = None

            # Load existing token
            if self.TOKEN_PATH.exists():
                creds = OAuth2Credentials.from_authorized_user_file(str(self.TOKEN_PATH), self.SCOPES)

            # Refresh or create new token
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.CREDS_PATH.exists():
                        logger.error(f"credentials.json not found at {self.CREDS_PATH.absolute()}")
                        raise FileNotFoundError(f"Place credentials.json in project root")

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.CREDS_PATH), self.SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save token for reuse
                with open(self.TOKEN_PATH, 'w') as token:
                    token.write(creds.to_json())

            self.service = discovery.build('gmail', 'v1', credentials=creds)
            logger.info("[OK] Gmail authentication successful")
        except Exception as e:
            logger.error(f"[ERROR] Gmail authentication failed: {e}")
            raise

    def build_query(self) -> str:
        """Build Gmail search query"""
        keyword_query = ' OR '.join([f'"{kw}"' for kw in self.KEYWORDS])
        query = f'is:unread is:important ({keyword_query})'
        return query

    def reset_connection(self):
        """Reset Gmail API connection pool"""
        try:
            logger.info("[CONNECTION] Resetting Gmail API connection...")
            self.service = None
            time.sleep(2)
            # Re-authenticate to get fresh connection
            self.authenticate()
            self.consecutive_errors = 0
            logger.info("[CONNECTION] ✓ Connection reset successful")
            self.last_connection_reset = time.time()
        except Exception as e:
            logger.error(f"[CONNECTION] Error resetting connection: {e}")

    def get_unread_emails(self) -> List[Dict]:
        """Fetch unread important emails with keywords"""
        try:
            # Check if it's time for periodic connection reset
            time_since_reset = time.time() - self.last_connection_reset
            if time_since_reset >= self.CONNECTION_RESET_INTERVAL:
                logger.info(f"[CONNECTION] Periodic reset due ({time_since_reset:.0f}s elapsed)")
                self.reset_connection()

            query = self.build_query()
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            email_data = []

            for msg in messages:
                email_id = msg['id']

                # Skip if already processed
                if email_id in self.processed_email_ids:
                    continue

                # Get full message details
                message = self.service.users().messages().get(
                    userId='me',
                    id=email_id,
                    format='full'
                ).execute()

                headers = message['payload']['headers']
                email_info = {
                    'id': email_id,
                    'from': next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown'),
                    'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)'),
                    'received': next((h['value'] for h in headers if h['name'] == 'Date'), datetime.now().isoformat()),
                }

                # Determine priority based on keywords
                subject_lower = email_info['subject'].lower()
                priority = 'high' if 'urgent' in subject_lower else 'medium'
                email_info['priority'] = priority
                email_info['type'] = 'email'
                email_info['status'] = 'pending'

                email_data.append(email_info)
                self.processed_email_ids.add(email_id)

            if email_data:
                logger.info(f"[OK] Found {len(email_data)} unread important emails with keywords")

            self.consecutive_errors = 0  # Reset error counter on success
            return email_data

        except Exception as e:
            self.consecutive_errors += 1
            logger.error(f"[ERROR] Error fetching emails ({self.consecutive_errors}): {e}")

            # Exponential backoff + connection reset
            if self.consecutive_errors >= 3:
                logger.warning(f"[CONNECTION] {self.consecutive_errors} consecutive errors - attempting connection reset")
                self.reset_connection()

            return []

    def save_to_markdown(self, email: Dict) -> Path:
        """Save email as markdown file with YAML metadata"""
        try:
            self.NEEDS_ACTION_DIR.mkdir(exist_ok=True)

            # Create filename from subject and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            email_hash = hashlib.md5(email['id'].encode()).hexdigest()[:6]
            safe_subject = "".join(c for c in email['subject'] if c.isalnum() or c in ' -_')[:30]
            filename = f"gmail_{timestamp}_{email_hash}_{safe_subject}.md"
            filepath = self.NEEDS_ACTION_DIR / filename

            # Create markdown with YAML frontmatter
            content = f"""---
type: {email.get('type', 'email')}
from: {email.get('from', 'Unknown')}
subject: {email.get('subject', '(No Subject)')}
received: {email.get('received', datetime.now().isoformat())}
priority: {email.get('priority', 'medium')}
status: {email.get('status', 'pending')}
source: gmail
created_at: {datetime.now().isoformat()}
---

# Gmail: {email.get('subject', '(No Subject)')}

**From:** {email.get('from', 'Unknown')}

**Priority:** {email.get('priority', 'medium').upper()}

**Received:** {email.get('received', 'Unknown')}

---

## Action Required

Review this email and take appropriate action.

- [ ] Read email
- [ ] Respond
- [ ] Archive
- [ ] Mark as done
"""

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"[OK] Saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"[ERROR] Error saving markdown: {e}")
            return None

    def run(self):
        """Main watcher loop"""
        logger.info(f"Starting Gmail Watcher - Check interval: {self.CHECK_INTERVAL}s, Connection reset: {self.CONNECTION_RESET_INTERVAL}s")

        try:
            cycle_count = 0
            while True:
                cycle_count += 1
                try:
                    logger.debug(f"[CYCLE {cycle_count}] Fetching emails...")
                    emails = self.get_unread_emails()
                    for email in emails:
                        self.save_to_markdown(email)

                    # Normal wait on success
                    wait_time = self.CHECK_INTERVAL
                    logger.debug(f"[CYCLE {cycle_count}] Waiting {wait_time}s until next check...")
                    time.sleep(wait_time)

                except Exception as e:
                    logger.error(f"[ERROR] Cycle {cycle_count} error: {e}")
                    # Exponential backoff: start with 2s, max 60s, multiply by 1.5 each time
                    backoff = min(self.BACKOFF_INITIAL * (1.5 ** self.consecutive_errors), self.BACKOFF_MAX)
                    logger.warning(f"[BACKOFF] Waiting {backoff:.1f}s before retry...")
                    time.sleep(backoff)

        except KeyboardInterrupt:
            logger.info("Gmail Watcher stopped by user")

if __name__ == "__main__":
    if not HAS_GMAIL_API:
        print("\n[ERROR] Required libraries not installed!")
        print("Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        exit(1)

    watcher = GmailWatcher()
    watcher.run()
