#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Simplified Version
Uses preview text from chat list instead of opening each chat
"""

import os
import sys
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from playwright.sync_api import sync_playwright

# UTF-8 encoding support for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Create logs directory
Path("watchers/logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("watchers/logs/whatsapp_watcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhatsAppWatcherSimplified:
    KEYWORDS = ['urgent', 'invoice', 'payment', 'sales']
    CHECK_INTERVAL = 30  # seconds
    NEEDS_ACTION_DIR = Path("Needs_Action")
    SESSION_PATH = Path("session/whatsapp")

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.processed_messages = set()

    def launch_browser(self):
        """Launch browser with saved session"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch_persistent_context(
                str(self.SESSION_PATH),
                headless=False
            )
            logger.info("[OK] Session path ready: " + str(self.SESSION_PATH))
            self.page = self.browser.new_page()
            self.page.goto("https://web.whatsapp.com")

            logger.info("[WAIT] Waiting for WhatsApp Web login...")

            # Try multiple methods to detect successful login
            try:
                self.page.wait_for_selector('[role="button"][tabindex="0"]', timeout=10000)
                logger.info("[OK] WhatsApp Web authenticated (method 1)")
            except:
                try:
                    self.page.wait_for_load_state('networkidle', timeout=30000)
                    logger.info("[OK] WhatsApp Web loaded (network idle)")
                except:
                    logger.warning("[WARN] WhatsApp authentication detection inconclusive, proceeding anyway...")
                    time.sleep(5)

        except Exception as e:
            logger.error(f"[ERROR] Browser launch failed: {e}")
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            raise

    def get_recent_chats_with_preview(self) -> List[Dict]:
        """Get recent chats with their preview text"""
        messages = []
        try:
            # Try to find chat items
            chat_items = None

            # Method 1: role-based
            try:
                chat_items = self.page.query_selector_all('[role="button"][tabindex="0"]')
                if chat_items and len(chat_items) > 0:
                    logger.info(f"[OK] Found {len(chat_items)} chats using role-based selector")
            except Exception as e:
                logger.debug(f"Method 1 failed: {e}")

            # Method 2: Generic div
            if not chat_items or len(chat_items) == 0:
                try:
                    chat_items = self.page.query_selector_all('div[class*="chat"]')
                    if chat_items and len(chat_items) > 0:
                        logger.info(f"[OK] Found {len(chat_items)} chats using div selector")
                except Exception as e:
                    logger.debug(f"Method 2 failed: {e}")

            if not chat_items or len(chat_items) == 0:
                logger.warning("[WARN] Could not find any chat items!")
                return messages

            # Process each chat item - extract preview text directly
            for idx, chat_item in enumerate(chat_items[:10]):
                try:
                    # Get all text from this chat item
                    full_text = chat_item.text_content().strip()
                    if not full_text:
                        logger.debug(f"[CHAT {idx}] Empty chat item, skipping")
                        continue

                    text_lines = full_text.split('\n')

                    # First line is usually contact name
                    contact = text_lines[0][:50] if len(text_lines) > 0 else "Unknown"

                    # Remaining lines are the preview
                    preview = '\n'.join(text_lines[1:]).strip()

                    if not preview:
                        logger.debug(f"[CHAT {idx}] No preview text for {contact}")
                        continue

                    logger.debug(f"[CHAT {idx}] Contact: {contact}, Preview: {preview[:80]}")

                    # Check for keywords in preview
                    keywords_found = [kw for kw in self.KEYWORDS if kw.lower() in preview.lower()]

                    if keywords_found:
                        msg_hash = hashlib.md5((contact + preview).encode()).hexdigest()[:8]

                        if msg_hash not in self.processed_messages:
                            messages.append({
                                'from': contact,
                                'message': preview,
                                'received': datetime.now().isoformat(),
                                'priority': 'high' if 'urgent' in preview.lower() else 'medium',
                                'type': 'whatsapp',
                                'status': 'pending',
                                'hash': msg_hash
                            })
                            self.processed_messages.add(msg_hash)
                            logger.info(f"[OK] Found message from {contact}: {preview[:60]}")
                        else:
                            logger.debug(f"[CHAT {idx}] Already processed message from {contact}")
                    else:
                        logger.debug(f"[CHAT {idx}] No keywords in preview")

                except Exception as e:
                    logger.debug(f"[CHAT {idx}] Error processing chat: {e}")

            if messages:
                logger.info(f"[OK] Found {len(messages)} messages with keywords")

            return messages

        except Exception as e:
            logger.error(f"[ERROR] Error fetching messages: {e}", exc_info=True)
            return []

    def save_to_markdown(self, message: Dict) -> Path:
        """Save message as markdown file with YAML metadata"""
        try:
            self.NEEDS_ACTION_DIR.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            msg_hash = message.get('hash', hashlib.md5(str(time.time()).encode()).hexdigest()[:6])
            safe_sender = "".join(c for c in message['from'] if c.isalnum() or c in ' -_')[:20]
            filename = f"whatsapp_{timestamp}_{msg_hash}_{safe_sender}.md"
            filepath = self.NEEDS_ACTION_DIR / filename

            content = f"""---
type: whatsapp
from: {message.get('from', 'Unknown')}
subject: WhatsApp message from {message.get('from', 'Unknown')}
received: {message.get('received', datetime.now().isoformat())}
priority: {message.get('priority', 'medium')}
status: {message.get('status', 'pending')}
source: whatsapp
created_at: {datetime.now().isoformat()}
---

# WhatsApp Message from {message.get('from', 'Unknown')}

**From:** {message.get('from', 'Unknown')}

**Received:** {message.get('received', 'Unknown')}

**Priority:** {message.get('priority', 'medium').upper()}

---

## Message

{message.get('message', '(No content)')}

---

## Action Required

This appears to be a business-related message with a keyword match.

- [ ] Review full message on WhatsApp
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
        logger.info(f"Starting WhatsApp Watcher (Simplified) - Check interval: {self.CHECK_INTERVAL}s")

        try:
            self.launch_browser()
            logger.info("[OK] Browser launched successfully, starting monitoring loop...")

            cycle_count = 0
            while True:
                cycle_count += 1
                try:
                    logger.debug(f"[CYCLE {cycle_count}] Starting message check...")

                    messages = self.get_recent_chats_with_preview()
                    logger.debug(f"[CYCLE {cycle_count}] Found {len(messages)} messages")

                    for message in messages:
                        try:
                            filepath = self.save_to_markdown(message)
                            if filepath:
                                logger.info(f"[OK] Message saved: {filepath}")
                        except Exception as save_err:
                            logger.error(f"[ERROR] Failed to save message: {save_err}", exc_info=True)

                    if len(messages) == 0:
                        logger.debug(f"[CYCLE {cycle_count}] No messages with keywords found")

                    logger.debug(f"[CYCLE {cycle_count}] Waiting {self.CHECK_INTERVAL}s before next check...")
                    time.sleep(self.CHECK_INTERVAL)

                except Exception as e:
                    logger.error(f"[ERROR] Cycle {cycle_count} exception: {type(e).__name__}: {e}", exc_info=True)
                    logger.debug(f"[ERROR] Full traceback: {e}")
                    try:
                        time.sleep(self.CHECK_INTERVAL)
                    except:
                        pass

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
    try:
        watcher = WhatsAppWatcherSimplified()
        watcher.run()
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}", exc_info=True)
        sys.exit(1)
