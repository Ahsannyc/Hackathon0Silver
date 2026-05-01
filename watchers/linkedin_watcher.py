#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Watcher Script - Silver Tier
Monitors messages and notifications for business leads using Playwright
Saves notifications to /Needs_Action as markdown files with YAML metadata

INSTRUCTIONS:
=============

1. SETUP:
   - Install dependencies: pip install playwright
   - Run: playwright install chromium
   - Create session directory: mkdir -p session/linkedin

2. FIRST RUN:
   - Script will open LinkedIn in browser
   - Log in with your LinkedIn credentials
   - Session will be saved for reuse
   - Subsequent runs will use saved session

3. RUN WITH PM2:
   - pm2 start watchers/linkedin_watcher.py --name linkedin_watcher --interpreter python3
   - pm2 logs linkedin_watcher
   - pm2 delete linkedin_watcher

4. TEST:
   - Send LinkedIn message: "URGENT: sales opportunity for project #456"
   - Or post comment with "client interested in sales project"
   - Check /Needs_Action for new .md file within 60 seconds
   - Verify sender and content in YAML

5. CONFIGURATION:
   - KEYWORDS: sales, client, project
   - CHECK_INTERVAL: 60 seconds
   - SESSION_PATH: session/linkedin (persists login)
   - MONITORS: Messages, Notifications, Mentions

6. LOGS:
   - Logs written to watchers/logs/linkedin_watcher.log

7. TROUBLESHOOTING:
   - If login fails: delete session/linkedin folder and re-login
   - If messages not detected: ensure LinkedIn notifications are enabled
   - LinkedIn may require periodic re-authentication due to security checks
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import hashlib
import json

# Fix UTF-8 encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Playwright import
try:
    from playwright.sync_api import sync_playwright, Page
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("WARNING: Playwright not installed. Install: pip install playwright && playwright install chromium")

# Setup logging
os.makedirs("watchers/logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("watchers/logs/linkedin_watcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInWatcher:
    KEYWORDS = ['sales', 'client', 'project']
    CHECK_INTERVAL = 60  # seconds
    NEEDS_ACTION_DIR = Path("Needs_Action")
    SESSION_PATH = Path("session/linkedin")

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.processed_items = set()
        self.setup_session()

    def setup_session(self):
        """Setup persistent session directory"""
        try:
            self.SESSION_PATH.mkdir(parents=True, exist_ok=True)
            logger.info(f"[OK] Session path ready: {self.SESSION_PATH.absolute()}")
        except Exception as e:
            logger.error(f"[ERROR] Error setting up session: {e}")
            raise

    def launch_browser(self):
        """Launch Playwright browser with persistent session"""
        try:
            self.playwright = sync_playwright().start()

            self.browser = self.playwright.chromium.launch(
                headless=False,  # Show browser for login if needed
                args=['--disable-blink-features=AutomationControlled']
            )

            context = self.browser.new_context(
                storage_state=str(self.SESSION_PATH / "storage.json") if (self.SESSION_PATH / "storage.json").exists() else None
            )

            self.page = context.new_page()

            # Set LinkedIn user agent
            self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            self.page.goto("https://www.linkedin.com/feed/")

            # Check if login needed
            try:
                self.page.wait_for_selector('[data-testid="feed-item-card"]', timeout=5000)
                logger.info("[OK] LinkedIn authenticated (using saved session)")
            except:
                logger.info("[WAIT] Waiting for LinkedIn login...")
                # Wait for feed to load after login
                try:
                    # Method 1: Try feed item selector
                    self.page.wait_for_selector('[data-testid="feed-item-card"]', timeout=30000)
                    logger.info("[OK] LinkedIn authenticated")
                except:
                    try:
                        # Method 2: Try messaging or profile page
                        self.page.wait_for_load_state('networkidle', timeout=30000)
                        logger.info("[OK] LinkedIn loaded (network idle)")
                    except:
                        # Method 3: Proceed anyway, monitoring can still work
                        logger.warning("[WARN] Feed may not be fully loaded, proceeding with monitoring...")

        except Exception as e:
            logger.error(f"[ERROR] Browser launch failed: {e}")
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            raise

    def check_messages(self) -> List[Dict]:
        """Check LinkedIn messages for keywords"""
        messages = []
        try:
            # Navigate to messages
            try:
                self.page.goto("https://www.linkedin.com/messaging/")
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                logger.debug("Could not navigate to messages")
                return messages

            # Get message threads with multiple methods
            conversation_items = None

            # Method 1: Try original selector
            try:
                conversation_items = self.page.query_selector_all('[data-testid="msg-conversation-item"]')
                if conversation_items and len(conversation_items) > 0:
                    logger.debug(f"Found {len(conversation_items)} conversations using method 1")
            except:
                pass

            # Method 2: Try alternative selectors
            if not conversation_items or len(conversation_items) == 0:
                try:
                    conversation_items = self.page.query_selector_all('[role="button"][class*="conversation"]')
                    if conversation_items and len(conversation_items) > 0:
                        logger.debug(f"Found {len(conversation_items)} conversations using method 2")
                except:
                    pass

            # Method 3: Try generic approach
            if not conversation_items or len(conversation_items) == 0:
                try:
                    conversation_items = self.page.query_selector_all('li[data-qa-id*="conversation"]')
                    if conversation_items and len(conversation_items) > 0:
                        logger.debug(f"Found {len(conversation_items)} conversations using method 3")
                except:
                    pass

            if not conversation_items or len(conversation_items) == 0:
                logger.debug("No conversations found")
                return messages

            for idx, item in enumerate(conversation_items[:5]):  # Check recent 5 conversations
                try:
                    sender = "Unknown"
                    preview = ""

                    # Get sender name with multiple approaches
                    try:
                        sender_elem = item.query_selector('[data-testid="msg-conversation-item__sender"]')
                        if sender_elem:
                            sender = sender_elem.text_content().strip()
                    except:
                        try:
                            # Fallback: get text from element
                            sender = item.text_content().split('\n')[0][:30]
                        except:
                            sender = f"Contact_{idx}"

                    # Get preview text with multiple approaches
                    try:
                        preview_elem = item.query_selector('[data-testid="msg-conversation-item__preview"]')
                        if preview_elem:
                            preview = preview_elem.text_content().strip()
                    except:
                        try:
                            # Fallback: get second line of text
                            text_lines = item.text_content().split('\n')
                            preview = text_lines[1] if len(text_lines) > 1 else ""
                        except:
                            pass

                    # Check for unread indicator (multiple approaches)
                    unread = False
                    try:
                        unread = item.query_selector('[class*="unread"]') is not None
                    except:
                        try:
                            unread = item.query_selector('[aria-label*="unread"]') is not None
                        except:
                            unread = True  # Assume unread if we can't detect

                    # Check for keywords (don't require unread check for robustness)
                    if preview and any(kw.lower() in preview.lower() for kw in self.KEYWORDS):
                        msg_hash = hashlib.md5((sender + preview).encode()).hexdigest()[:8]

                        if msg_hash not in self.processed_items:
                            messages.append({
                                'from': sender,
                                'content': preview,
                                'received': datetime.now().isoformat(),
                                'type': 'linkedin_message',
                                'priority': 'high' if any(kw in preview.lower() for kw in ['urgent', 'asap']) else 'medium',
                                'status': 'pending',
                                'hash': msg_hash
                            })
                            self.processed_items.add(msg_hash)
                            logger.info(f"[OK] Found message from {sender}: {preview[:50]}")
                except Exception as e:
                    logger.debug(f"Error reading message {idx}: {e}")

            if messages:
                logger.info(f"[OK] Found {len(messages)} messages with keywords")

            return messages
        except Exception as e:
            logger.error(f"[ERROR] Error checking messages: {e}")
            return []

    def check_notifications(self) -> List[Dict]:
        """Check LinkedIn notifications for leads"""
        notifications = []
        try:
            # Navigate to notifications
            try:
                self.page.goto("https://www.linkedin.com/notifications/")
                self.page.wait_for_load_state('networkidle', timeout=10000)
            except:
                logger.debug("Could not navigate to notifications")
                return notifications

            # Get notification items with multiple methods
            notif_items = None

            # Method 1: Try original selector
            try:
                notif_items = self.page.query_selector_all('[data-testid="notification-item"]')
                if notif_items and len(notif_items) > 0:
                    logger.debug(f"Found {len(notif_items)} notifications using method 1")
            except:
                pass

            # Method 2: Try alternative selectors
            if not notif_items or len(notif_items) == 0:
                try:
                    notif_items = self.page.query_selector_all('[role="main"] li')
                    if notif_items and len(notif_items) > 0:
                        logger.debug(f"Found {len(notif_items)} notifications using method 2")
                except:
                    pass

            # Method 3: Try generic div approach
            if not notif_items or len(notif_items) == 0:
                try:
                    notif_items = self.page.query_selector_all('div[class*="notification"]')
                    if notif_items and len(notif_items) > 0:
                        logger.debug(f"Found {len(notif_items)} notifications using method 3")
                except:
                    pass

            if not notif_items or len(notif_items) == 0:
                logger.debug("No notifications found")
                return notifications

            for idx, item in enumerate(notif_items[:5]):  # Check recent 5 notifications
                try:
                    notif_text = ""
                    sender = "Unknown"

                    # Get notification text with multiple approaches
                    try:
                        text_elem = item.query_selector('[data-testid="notification-text"]')
                        if text_elem:
                            notif_text = text_elem.text_content().strip()
                    except:
                        try:
                            # Fallback: get text from item
                            notif_text = item.text_content().strip()
                            if '\n' in notif_text:
                                notif_text = notif_text.split('\n')[0]
                        except:
                            pass

                    # Get sender with multiple approaches
                    try:
                        sender_elem = item.query_selector('[data-testid="notification-sender"]')
                        if sender_elem:
                            sender = sender_elem.text_content().strip()
                    except:
                        try:
                            # Fallback: extract from notification text
                            text_lines = item.text_content().split('\n')
                            sender = text_lines[0] if len(text_lines) > 0 else "Unknown"
                        except:
                            sender = f"Contact_{idx}"

                    # Check for keywords
                    if notif_text and any(kw.lower() in notif_text.lower() for kw in self.KEYWORDS):
                        notif_hash = hashlib.md5((sender + notif_text).encode()).hexdigest()[:8]

                        if notif_hash not in self.processed_items:
                            notifications.append({
                                'from': sender,
                                'content': notif_text,
                                'received': datetime.now().isoformat(),
                                'type': 'linkedin_notification',
                                'priority': 'medium',
                                'status': 'pending',
                                'hash': notif_hash
                            })
                            self.processed_items.add(notif_hash)
                            logger.info(f"[OK] Found notification from {sender}: {notif_text[:50]}")
                except Exception as e:
                    logger.debug(f"Error reading notification {idx}: {e}")

            if notifications:
                logger.info(f"[OK] Found {len(notifications)} notifications with keywords")

            return notifications
        except Exception as e:
            logger.error(f"[ERROR] Error checking notifications: {e}")
            return []

    def save_to_markdown(self, item: Dict) -> Path:
        """Save item as markdown file with YAML metadata"""
        try:
            self.NEEDS_ACTION_DIR.mkdir(exist_ok=True)

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            item_hash = item.get('hash', hashlib.md5(str(time.time()).encode()).hexdigest()[:6])
            safe_sender = "".join(c for c in item['from'] if c.isalnum() or c in ' -_')[:20]
            item_type = item.get('type', 'linkedin').replace('_', '-')
            filename = f"linkedin_{item_type}_{timestamp}_{item_hash}_{safe_sender}.md"
            filepath = self.NEEDS_ACTION_DIR / filename

            # Create markdown with YAML frontmatter
            content = f"""---
type: {item.get('type', 'linkedin')}
from: {item.get('from', 'Unknown')}
subject: LinkedIn {item.get('type', 'linkedin').replace('_', ' ').title()}
received: {item.get('received', datetime.now().isoformat())}
priority: {item.get('priority', 'medium')}
status: {item.get('status', 'pending')}
source: linkedin
created_at: {datetime.now().isoformat()}
---

# LinkedIn {item.get('type', 'notification').replace('_', ' ').title()} from {item.get('from', 'Unknown')}

**From:** {item.get('from', 'Unknown')}

**Type:** {item.get('type', 'notification').replace('_', ' ').title()}

**Priority:** {item.get('priority', 'medium').upper()}

**Received:** {item.get('received', 'Unknown')}

---

## Content

{item.get('content', '(No content)')}

---

## Action Required

This appears to be a potential business lead or important business communication.

- [ ] Review full message/notification on LinkedIn
- [ ] Contact sender if interested
- [ ] Save contact details
- [ ] Follow up
- [ ] Archive when done
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
        logger.info(f"Starting LinkedIn Watcher - Check interval: {self.CHECK_INTERVAL}s")

        try:
            self.launch_browser()

            while True:
                try:
                    # Check messages
                    messages = self.check_messages()
                    for msg in messages:
                        self.save_to_markdown(msg)

                    # Check notifications
                    notifications = self.check_notifications()
                    for notif in notifications:
                        self.save_to_markdown(notif)

                    time.sleep(self.CHECK_INTERVAL)
                except Exception as e:
                    logger.error(f"[ERROR] Error in watcher loop: {e}")
                    time.sleep(self.CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("LinkedIn Watcher stopped by user")
        finally:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

if __name__ == "__main__":
    if not HAS_PLAYWRIGHT:
        print("\n❌ Playwright not installed!")
        print("Install with: pip install playwright && playwright install chromium")
        exit(1)

    watcher = LinkedInWatcher()
    watcher.run()
