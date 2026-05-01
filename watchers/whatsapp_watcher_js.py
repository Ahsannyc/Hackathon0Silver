#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - JavaScript Evaluation Version
Uses page.evaluate() to extract conversation data directly from the DOM
Bypasses CSS selector issues by using JavaScript
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

class WhatsAppWatcherJS:
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
        """Launch browser with persistent session (restores previous auth)"""
        try:
            self.playwright = sync_playwright().start()
            # Use persistent context to restore previous WhatsApp authentication
            self.browser = self.playwright.chromium.launch_persistent_context(
                str(self.SESSION_PATH),
                headless=False
            )
            logger.info(f"[OK] Persistent session ready: {self.SESSION_PATH}")
            self.page = self.browser.new_page()
            self.page.goto("https://web.whatsapp.com")

            logger.info("[WAIT] Waiting for WhatsApp Web to load...")

            # Try to detect authentication
            try:
                # Wait for chat list container (indicates we're authenticated)
                self.page.wait_for_selector('[role="main"]', timeout=15000)
                logger.info("[OK] WhatsApp Web authenticated - chat area detected")
            except:
                try:
                    # Fallback: Wait for network idle
                    self.page.wait_for_load_state('networkidle', timeout=30000)
                    logger.info("[OK] WhatsApp Web loaded (network idle)")
                except:
                    logger.warning("[WARN] WhatsApp Web loading inconclusive, proceeding...")

            # Ensure page is scrolled to top
            try:
                self.page.evaluate("window.scrollTo(0, 0)")
                time.sleep(1)  # Give page time to render
            except:
                pass

        except Exception as e:
            logger.error(f"[ERROR] Browser launch failed: {e}")
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            raise

    def get_conversations_via_js(self) -> List[Dict]:
        """
        Extract conversation data using JavaScript evaluation
        This bypasses CSS selector issues by querying the DOM directly via JS
        """
        messages = []
        try:
            logger.debug("[JS] Evaluating page to extract conversations...")

            # First, try to ensure chat list is visible (in case we're on login screen)
            try:
                # Check if we can see the sidebar - if not, try reloading
                sidebar_visible = self.page.evaluate("() => !!document.querySelector('[role=\"main\"]')")
                if not sidebar_visible:
                    logger.debug("[JS] Chat area not visible, trying to reload...")
                    self.page.goto("https://web.whatsapp.com")
                    time.sleep(3)
            except:
                pass

            # JavaScript to find all conversation items and extract data
            js_code = """
            () => {
                const conversations = [];
                const badKeywords = ['download', 'scan', 'log in', 'sign up', 'get started', 'terms', 'privacy', 'help', 'windows', 'camera', 'whatsapp', 'account', 'encrypted', 'link', 'phone', 'settings'];

                // First, check if we're in the chat list area or still on login/onboarding
                const mainArea = document.querySelector('[role="main"]');
                const chatList = document.querySelector('[role="list"]');
                let isAuthenticatedView = !!mainArea;

                if (!isAuthenticatedView) {
                    console.log('Not in authenticated view - showing login/onboarding screen');
                }

                let candidates = [];

                // If we're authenticated, look in the sidebar for chat items
                if (mainArea) {
                    // Look for elements that are styled as chat items (usually have unread count, timestamp, etc)
                    const chatItems = mainArea.parentElement.querySelectorAll('[role="button"][tabindex="0"]');

                    for (let item of chatItems) {
                        const text = (item.innerText || item.textContent || '').trim();
                        if (!text || text.length < 3) continue;

                        // Check if this looks like a real conversation (not a menu item)
                        const lowerText = text.toLowerCase();
                        const isMenuKeyword = badKeywords.some(kw => lowerText.includes(kw));

                        if (!isMenuKeyword && text.includes('\\n')) {
                            const lines = text.split('\\n').filter(l => l.trim());
                            if (lines.length >= 1) {
                                candidates.push({
                                    sender: lines[0].trim(),
                                    preview: lines.slice(1).join(' ').trim().substring(0, 200),
                                    lines_count: lines.length,
                                    text_length: text.length
                                });
                            }
                        }
                    }
                }

                // If no results from main area, fallback to general div scan but more restrictive
                if (candidates.length === 0 && !isAuthenticatedView) {
                    console.log('Fallback: scanning all divs (unauthenticated state)');
                    const allDivs = document.querySelectorAll('div[class*="chat"], div[class*="conversation"]');

                    for (let div of allDivs) {
                        const text = (div.innerText || div.textContent || '').trim();
                        if (!text || text.length < 10) continue;

                        const lowerText = text.toLowerCase();
                        if (!badKeywords.some(kw => lowerText.includes(kw))) {
                            const lines = text.split('\\n').filter(l => l.trim());
                            if (lines.length >= 2) {
                                candidates.push({
                                    sender: lines[0].trim(),
                                    preview: lines.slice(1).join(' ').trim().substring(0, 200),
                                    lines_count: lines.length
                                });
                            }
                        }
                    }
                }

                // Deduplicate
                const seen = new Set();
                for (let cand of candidates) {
                    const key = cand.sender + '|' + cand.preview.substring(0, 30);
                    if (!seen.has(key)) {
                        seen.add(key);
                        conversations.push(cand);
                    }
                }

                return {
                    conversations: conversations,
                    candidates_scanned: candidates.length,
                    is_authenticated: isAuthenticatedView,
                    page_title: document.title,
                    url: window.location.href
                };
            }
            """

            result = self.page.evaluate(js_code)
            conversations_data = result.get('conversations', []) if isinstance(result, dict) else result
            candidates = result.get('candidates_scanned', 0) if isinstance(result, dict) else 0
            is_auth = result.get('is_authenticated', False) if isinstance(result, dict) else False

            auth_status = "[AUTH OK]" if is_auth else "[NOT AUTH]"
            logger.info(f"[JS] {auth_status} - Found {len(conversations_data)} conversations from {candidates} candidates")
            if isinstance(result, dict):
                logger.debug(f"[JS] Page: {result.get('page_title')} | URL: {result.get('url')}")

            # Process conversations
            for idx, conv in enumerate(conversations_data):
                try:
                    sender = conv.get('sender', 'Unknown')
                    preview = conv.get('preview', '')

                    logger.debug(f"[CONV {idx}] Sender: {sender}, Preview: {preview[:80]}")

                    if not preview:
                        logger.debug(f"[CONV {idx}] No preview text, skipping")
                        continue

                    # Check for keywords
                    keywords_found = [kw for kw in self.KEYWORDS if kw.lower() in preview.lower()]

                    if keywords_found:
                        msg_hash = hashlib.md5((sender + preview).encode()).hexdigest()[:8]

                        if msg_hash not in self.processed_messages:
                            messages.append({
                                'from': sender,
                                'message': preview,
                                'received': datetime.now().isoformat(),
                                'priority': 'high' if 'urgent' in preview.lower() else 'medium',
                                'type': 'whatsapp',
                                'status': 'pending',
                                'hash': msg_hash
                            })
                            self.processed_messages.add(msg_hash)
                            logger.info(f"[OK] Found message from {sender}: {preview[:60]}")
                        else:
                            logger.debug(f"[CONV {idx}] Already processed")
                    else:
                        logger.debug(f"[CONV {idx}] No keywords found")

                except Exception as e:
                    logger.debug(f"[CONV {idx}] Error: {e}")

            if messages:
                logger.info(f"[OK] Total messages found: {len(messages)}")
            else:
                logger.debug("[JS] No messages with keywords found")

            return messages

        except Exception as e:
            logger.error(f"[ERROR] JavaScript evaluation failed: {e}", exc_info=True)
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
        logger.info(f"Starting WhatsApp Watcher (JavaScript) - Check interval: {self.CHECK_INTERVAL}s")

        try:
            self.launch_browser()
            logger.info("[OK] Browser launched successfully, starting monitoring loop...")

            cycle_count = 0
            while True:
                cycle_count += 1
                try:
                    logger.debug(f"[CYCLE {cycle_count}] Starting message check...")

                    messages = self.get_conversations_via_js()
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
        watcher = WhatsAppWatcherJS()
        watcher.run()
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}", exc_info=True)
        sys.exit(1)
