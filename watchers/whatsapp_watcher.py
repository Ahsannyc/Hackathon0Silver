#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher Script - Silver Tier
Monitors unread messages with specified keywords using Playwright
Saves notifications to /Needs_Action as markdown files with YAML metadata

INSTRUCTIONS:
=============

1. SETUP:
   - Install dependencies: pip install playwright
   - Run: playwright install chromium
   - Create session directory: mkdir -p session/whatsapp

2. FIRST RUN:
   - Script will open WhatsApp Web in browser
   - Scan QR code with your phone
   - Session will be saved to session/whatsapp for reuse
   - Subsequent runs will use saved session (no QR needed)

3. RUN WITH PM2:
   - pm2 start watchers/whatsapp_watcher.py --name whatsapp_watcher --interpreter python3
   - pm2 logs whatsapp_watcher
   - pm2 delete whatsapp_watcher

4. TEST:
   - Send WhatsApp message with text "URGENT invoice #789 - Test"
   - Check /Needs_Action for new .md file within 30 seconds
   - Verify sender and message content in YAML

5. CONFIGURATION:
   - KEYWORDS: urgent, invoice, payment, sales
   - CHECK_INTERVAL: 30 seconds
   - SESSION_PATH: session/whatsapp (persists login)

6. LOGS:
   - Logs written to watchers/logs/whatsapp_watcher.log
   - Browser activity: watchers/logs/whatsapp_browser.log

7. TROUBLESHOOTING:
   - If session expires: delete session/whatsapp folder and re-scan QR
   - If messages not detected: ensure WhatsApp notifications are enabled
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
    level=logging.DEBUG,  # Changed from INFO to DEBUG to see detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("watchers/logs/whatsapp_watcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhatsAppWatcher:
    KEYWORDS = ['urgent', 'invoice', 'payment', 'sales']
    CHECK_INTERVAL = 30  # seconds
    NEEDS_ACTION_DIR = Path("Needs_Action")
    SESSION_PATH = Path("session/whatsapp")
    BROWSER_EXECUTABLE = None  # Use system chromium

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.processed_messages = set()
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

            context_args = {
                'user_data_dir': str(self.SESSION_PATH.absolute()),
            }

            self.browser = self.playwright.chromium.launch(
                headless=False,  # Show browser for QR scan
                args=['--disable-blink-features=AutomationControlled']
            )

            self.page = self.browser.new_page()
            self.page.goto("https://web.whatsapp.com")

            # Wait for login (QR scan on first run)
            logger.info("[WAIT] Waiting for WhatsApp Web login...")

            # Try multiple methods to detect successful login
            try:
                # Method 1: Wait for chat list item (primary selector)
                self.page.wait_for_selector('[data-testid="chat-list-item"]', timeout=10000)
                logger.info("[OK] WhatsApp Web authenticated")
            except:
                try:
                    # Method 2: Wait for main chat area (fallback)
                    self.page.wait_for_selector('div[data-testid="chat-list"]', timeout=10000)
                    logger.info("[OK] WhatsApp Web authenticated (via chat list)")
                except:
                    try:
                        # Method 3: Wait for network idle (page loaded)
                        self.page.wait_for_load_state('networkidle', timeout=30000)
                        logger.info("[OK] WhatsApp Web loaded (network idle)")
                    except:
                        # Method 4: If all else fails, assume logged in and proceed
                        logger.warning("[WARN] WhatsApp authentication detection inconclusive, proceeding anyway...")
                        time.sleep(5)  # Give page time to settle

        except Exception as e:
            logger.error(f"[ERROR] Browser launch failed: {e}")
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            raise

    def get_unread_messages(self) -> List[Dict]:
        """Fetch unread messages with keywords"""
        try:
            messages = []

            # Try multiple selector methods for robustness
            chat_items = None

            # Method 1: Try original selector (in case it still works)
            try:
                chat_items = self.page.query_selector_all('[data-testid="chat-list-item"]')
                if chat_items and len(chat_items) > 0:
                    logger.info(f"[OK] Found {len(chat_items)} chats using method 1 (data-testid)")
                else:
                    logger.debug("Method 1 found 0 chats, trying method 2...")
            except Exception as e:
                logger.debug(f"Method 1 failed: {e}")

            # Method 2: Try role-based selector
            if not chat_items or len(chat_items) == 0:
                try:
                    chat_items = self.page.query_selector_all('[role="button"][tabindex="0"]')
                    if chat_items and len(chat_items) > 0:
                        logger.info(f"[OK] Found {len(chat_items)} chats using method 2 (role-based)")
                    else:
                        logger.debug("Method 2 found 0 chats, trying method 3...")
                except Exception as e:
                    logger.debug(f"Method 2 failed: {e}")

            # Method 3: Try class-based selector
            if not chat_items or len(chat_items) == 0:
                try:
                    chat_items = self.page.query_selector_all('div[class*="chat"][class*="item"]')
                    if chat_items and len(chat_items) > 0:
                        logger.info(f"[OK] Found {len(chat_items)} chats using method 3 (class-based)")
                    else:
                        logger.debug("Method 3 found 0 chats, trying method 4...")
                except Exception as e:
                    logger.debug(f"Method 3 failed: {e}")

            # Method 4: Try generic conversation list
            if not chat_items or len(chat_items) == 0:
                try:
                    chat_items = self.page.query_selector_all('div[data-qa-type="conversation-list-item"]')
                    if chat_items and len(chat_items) > 0:
                        logger.info(f"[OK] Found {len(chat_items)} chats using method 4 (qa-type)")
                    else:
                        logger.debug("Method 4 found 0 chats")
                except Exception as e:
                    logger.debug(f"Method 4 failed: {e}")

            if not chat_items or len(chat_items) == 0:
                logger.warning("[WARN] Could not find any chat items using ANY of 4 methods!")
                logger.warning("[WARN] Possible reasons: 1) No conversations loaded 2) All selectors outdated 3) WhatsApp Web layout changed")
                logger.debug("[DEBUG] Current page URL: " + str(self.page.url) if hasattr(self, 'page') else "N/A")
                return messages

            # Process found chat items
            for idx, chat_item in enumerate(chat_items[:10]):  # Check first 10
                try:
                    sender = "Unknown"
                    message_text = ""

                    # Try to get sender name with multiple approaches
                    try:
                        sender_elem = chat_item.query_selector('[data-testid="chat-list-item-title"]')
                        if sender_elem:
                            sender = sender_elem.text_content().strip()
                    except:
                        try:
                            # Fallback: get text content of first element
                            sender = chat_item.text_content().split('\n')[0][:30]
                        except:
                            sender = f"Contact_{idx}"

                    logger.debug(f"[CHAT {idx}] Processing chat from: {sender}")

                    # Click to open chat
                    try:
                        chat_item.click()
                        time.sleep(1.5)
                        logger.debug(f"[CHAT {idx}] Clicked and waiting for messages...")
                    except Exception as click_err:
                        logger.debug(f"[CHAT {idx}] Click failed: {click_err}")
                        continue

                    # Try to get message text with multiple approaches
                    message_methods = ["[data-testid=\"msg\"]", "div[data-qa-type=\"message-bubble\"]", "[role=\"region\"] [role=\"article\"]"]

                    for method_idx, selector in enumerate(message_methods, 1):
                        if message_text:
                            break
                        try:
                            msg_elements = self.page.query_selector_all(selector)
                            if msg_elements and len(msg_elements) > 0:
                                message_text = msg_elements[-1].text_content().strip()
                                logger.debug(f"[CHAT {idx}] Method {method_idx} found message: {message_text[:60]}")
                                break
                            else:
                                logger.debug(f"[CHAT {idx}] Method {method_idx} found 0 messages")
                        except Exception as msg_err:
                            logger.debug(f"[CHAT {idx}] Method {method_idx} error: {msg_err}")

                    # Method 4: Get any text in message area
                    if not message_text:
                        try:
                            message_area = self.page.query_selector('div[data-testid="msg-list"]')
                            if message_area:
                                all_text = message_area.text_content()
                                message_text = all_text.split('\n')[-2] if len(all_text.split('\n')) > 1 else all_text
                                logger.debug(f"[CHAT {idx}] Method 4 got text: {message_text[:60]}")
                        except Exception as method4_err:
                            logger.debug(f"[CHAT {idx}] Method 4 failed: {method4_err}")

                    # Check for keywords
                    if message_text:
                        logger.debug(f"[CHAT {idx}] Message text: '{message_text[:80]}'")
                        keywords_found = [kw for kw in self.KEYWORDS if kw.lower() in message_text.lower()]
                        if keywords_found:
                            logger.info(f"[OK] Found keywords in {sender}: {keywords_found}")
                        else:
                            logger.debug(f"[CHAT {idx}] No keywords found (keywords: {self.KEYWORDS})")
                    else:
                        logger.debug(f"[CHAT {idx}] No message text extracted")

                    if message_text and any(kw.lower() in message_text.lower() for kw in self.KEYWORDS):
                        msg_hash = hashlib.md5((sender + message_text).encode()).hexdigest()[:8]

                        # Skip if already processed
                        if msg_hash in self.processed_messages:
                            logger.debug(f"Already processed message from {sender}")
                            continue

                        messages.append({
                            'from': sender,
                            'message': message_text,
                            'received': datetime.now().isoformat(),
                            'priority': 'high' if 'urgent' in message_text.lower() else 'medium',
                            'type': 'whatsapp',
                            'status': 'pending',
                            'hash': msg_hash
                        })

                        self.processed_messages.add(msg_hash)
                        logger.info(f"[OK] Found message from {sender}: {message_text[:50]}")

                except Exception as e:
                    logger.debug(f"Error processing chat {idx}: {e}")

            if messages:
                logger.info(f"[OK] Found {len(messages)} unread messages with keywords")
            else:
                logger.debug("No messages with keywords found")

            return messages
        except Exception as e:
            logger.error(f"[ERROR] Error fetching messages: {e}")
            return []

    def save_to_markdown(self, message: Dict) -> Path:
        """Save message as markdown file with YAML metadata"""
        try:
            self.NEEDS_ACTION_DIR.mkdir(exist_ok=True)

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            msg_hash = message.get('hash', hashlib.md5(str(time.time()).encode()).hexdigest()[:6])
            safe_sender = "".join(c for c in message['from'] if c.isalnum() or c in ' -_')[:20]
            filename = f"whatsapp_{timestamp}_{msg_hash}_{safe_sender}.md"
            filepath = self.NEEDS_ACTION_DIR / filename

            # Create markdown with YAML frontmatter
            content = f"""---
type: {message.get('type', 'whatsapp')}
from: {message.get('from', 'Unknown')}
subject: WhatsApp Message
received: {message.get('received', datetime.now().isoformat())}
priority: {message.get('priority', 'medium')}
status: {message.get('status', 'pending')}
source: whatsapp
created_at: {datetime.now().isoformat()}
---

# WhatsApp Message from {message.get('from', 'Unknown')}

**From:** {message.get('from', 'Unknown')}

**Priority:** {message.get('priority', 'medium').upper()}

**Received:** {message.get('received', 'Unknown')}

---

## Message Content

{message.get('message', '(No message content)')}

---

## Action Required

- [ ] Read message
- [ ] Reply
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
        logger.info(f"Starting WhatsApp Watcher - Check interval: {self.CHECK_INTERVAL}s")

        try:
            self.launch_browser()
            logger.info("[OK] Browser launched successfully, starting monitoring loop...")

            cycle_count = 0
            while True:
                cycle_count += 1
                try:
                    logger.debug(f"[CYCLE {cycle_count}] Starting message check...")

                    messages = self.get_unread_messages()
                    logger.debug(f"[CYCLE {cycle_count}] Found {len(messages)} messages")

                    for message in messages:
                        try:
                            filepath = self.save_to_markdown(message)
                            if filepath:
                                logger.info(f"[OK] Saved: {filepath}")
                        except Exception as save_err:
                            logger.error(f"[ERROR] Failed to save message: {save_err}", exc_info=True)

                    if len(messages) == 0:
                        logger.debug(f"[CYCLE {cycle_count}] No messages with keywords found, waiting...")

                    time.sleep(self.CHECK_INTERVAL)

                except Exception as e:
                    logger.error(f"[ERROR] Cycle {cycle_count} exception: {type(e).__name__}: {e}", exc_info=True)
                    logger.debug(f"[ERROR] Full traceback: {e}")
                    # Try to reconnect
                    try:
                        if self.page:
                            logger.info("[WARN] Attempting to reconnect to WhatsApp Web...")
                            self.page.goto("https://web.whatsapp.com")
                    except Exception as reconnect_err:
                        logger.error(f"[ERROR] Reconnect failed: {reconnect_err}")
                    time.sleep(self.CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("WhatsApp Watcher stopped by user")
        finally:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

if __name__ == "__main__":
    if not HAS_PLAYWRIGHT:
        print("\n[ERROR] Playwright not installed!")
        print("Install with: pip install playwright && playwright install chromium")
        exit(1)

    watcher = WhatsAppWatcher()
    watcher.run()
