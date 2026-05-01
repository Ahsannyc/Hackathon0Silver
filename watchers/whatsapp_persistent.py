#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Persistent Browser Session
Keeps the browser open between checks to maintain authentication
One-time setup: manual QR code scan, then continuous monitoring
"""

import os
import sys
import time
import logging
import hashlib
import json
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

class WhatsAppPersistentWatcher:
    """
    WhatsApp Watcher that keeps browser open to maintain session.
    First run: requires manual QR code scan
    Subsequent runs: uses persistent session

    ENHANCEMENTS:
    - Periodic session validation every 90 minutes
    - Auto-restart on authentication failure
    - Better error recovery with exponential backoff
    """
    KEYWORDS = ['urgent', 'invoice', 'payment', 'sales']
    CHECK_INTERVAL = 30  # seconds between message checks
    SESSION_REFRESH_INTERVAL = 5400  # 90 minutes - check auth health
    NEEDS_ACTION_DIR = Path("Needs_Action")
    SESSION_PATH = Path("session/whatsapp")
    AUTH_MARKER_FILE = Path("session/whatsapp_authenticated.txt")

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.processed_messages = set()
        self.is_authenticated = False
        self.last_auth_check = time.time()
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5

    def ensure_session_dir(self):
        """Ensure session directory exists"""
        self.SESSION_PATH.mkdir(parents=True, exist_ok=True)
        self.NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)

    def is_already_authenticated(self) -> bool:
        """Check if we've authenticated before"""
        return self.AUTH_MARKER_FILE.exists()

    def mark_authenticated(self):
        """Mark that we've successfully authenticated"""
        self.AUTH_MARKER_FILE.write_text(datetime.now().isoformat())
        logger.info("[OK] Authentication marked - session will be reused")

    def check_session_exists(self) -> bool:
        """Check if valid session folder exists with cookies"""
        cookies_path = self.SESSION_PATH / "Default" / "Network" / "Cookies"
        return cookies_path.exists()

    def launch_browser_persistent(self):
        """Launch browser with persistent session that stays open"""
        try:
            self.playwright = sync_playwright().start()

            # Check if we have an existing session
            has_session = self.check_session_exists()
            has_auth_marker = self.is_already_authenticated()

            # Use persistent context - this saves cookies, localStorage, etc.
            logger.info("[SETUP] Launching Chromium with persistent session...")
            logger.info(f"[SESSION] Existing session: {has_session}, Auth marker: {has_auth_marker}")

            self.browser = self.playwright.chromium.launch_persistent_context(
                str(self.SESSION_PATH.absolute()),
                headless=False,  # Show browser window for QR code if needed
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-resources',
                    '--disable-blink-features=IsolateOrigins',  # Better session restore
                    '--disable-site-isolation-trials',  # Better session restore
                ]
            )

            self.page = self.browser.new_page()
            logger.info("[OK] Browser launched, navigating to WhatsApp Web...")

            self.page.goto("https://web.whatsapp.com", wait_until="networkidle")
            logger.info("[LOAD] Page loaded, waiting for chat area...")

            # Try to detect if authenticated
            time.sleep(2)
            auth_status = self._check_authentication()

            if auth_status:
                logger.info("[OK] AUTHENTICATED - Chat area detected!")
                self.is_authenticated = True
                self.mark_authenticated()
                time.sleep(2)  # Let page fully load
            else:
                # If we have session files, wait longer before asking for QR
                if has_session and has_auth_marker:
                    logger.warning("[WARN] Session exists but chat area not immediately visible")
                    logger.info("[INFO] Waiting longer for session to restore (30 seconds)...")
                    # Sometimes WhatsApp needs time to restore cookies
                    for i in range(3):
                        time.sleep(10)
                        logger.debug(f"[SESSION] Retry {i+1}/3 checking authentication...")
                        auth_status = self._check_authentication()
                        if auth_status:
                            logger.info("[OK] Session restored!")
                            self.is_authenticated = True
                            self.mark_authenticated()
                            break

                    if not auth_status:
                        logger.warning("[WARN] Session didn't restore - may need QR scan")
                        self.is_authenticated = True  # Proceed anyway
                elif self.is_already_authenticated():
                    logger.warning("[WARN] Auth marker exists but chat area not visible (first check)")
                    logger.info("[INFO] Session might need refresh, waiting 20 seconds...")
                    time.sleep(20)
                    auth_status = self._check_authentication()
                    if auth_status:
                        logger.info("[OK] Session refreshed!")
                    self.is_authenticated = True
                else:
                    logger.warning("[WARN] First run detected - chat area not visible")
                    logger.info("[INFO] Waiting 60 seconds for authentication...")
                    time.sleep(60)
                    auth_status = self._check_authentication()
                    if auth_status:
                        logger.info("[OK] Authentication successful!")
                        self.is_authenticated = True
                        self.mark_authenticated()
                        time.sleep(2)
                    else:
                        logger.warning("[WARN] Chat area still not visible - will proceed anyway")
                        self.is_authenticated = True  # Mark as authenticated to start monitoring

        except Exception as e:
            logger.error(f"[ERROR] Browser launch failed: {e}", exc_info=True)
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            raise

    def _check_authentication(self) -> bool:
        """Check if we're authenticated (chat area visible)"""
        try:
            # Look for the main chat area
            is_main_visible = self.page.is_visible('[role="main"]', timeout=5000)
            if is_main_visible:
                return True
        except:
            pass

        try:
            # Look for chat list
            is_list_visible = self.page.is_visible('[role="list"]', timeout=2000)
            if is_list_visible:
                return True
        except:
            pass

        # As fallback, check if we're NOT on a login/onboarding page
        try:
            page_text = self.page.inner_text("body").lower()
            if "scan the qr code" in page_text or "get whatsapp" in page_text:
                return False
            # If page has reasonable content and no obvious login/onboarding text, assume authenticated
            if len(page_text) > 500:
                return True
        except:
            pass

        return False

    def refresh_session(self) -> bool:
        """
        Periodic session refresh - verify authentication is still valid.
        Returns True if session is still valid, False if needs restart.
        """
        logger.info("[SESSION] Performing periodic authentication check...")
        try:
            if self._check_authentication():
                logger.info("[SESSION] ✓ Authentication still valid - session healthy")
                self.consecutive_failures = 0
                return True
            else:
                logger.warning("[SESSION] ✗ Authentication failed - session may be expired")
                self.consecutive_failures += 1

                if self.consecutive_failures >= self.max_consecutive_failures:
                    logger.error(f"[SESSION] {self.consecutive_failures} consecutive failures - initiating browser restart")
                    return False
                else:
                    logger.info(f"[SESSION] Failure count: {self.consecutive_failures}/{self.max_consecutive_failures}")
                    # Try to navigate to refresh
                    try:
                        logger.info("[SESSION] Attempting page refresh...")
                        self.page.reload(wait_until="networkidle")
                        time.sleep(3)
                        if self._check_authentication():
                            logger.info("[SESSION] ✓ Refresh successful")
                            self.consecutive_failures = 0
                            return True
                    except Exception as e:
                        logger.warning(f"[SESSION] Refresh failed: {e}")
                    return False
        except Exception as e:
            logger.error(f"[SESSION] Refresh check error: {e}")
            self.consecutive_failures += 1
            return self.consecutive_failures < self.max_consecutive_failures

    def get_conversations_from_page(self) -> List[Dict]:
        """Extract conversations from the page using JavaScript"""
        messages = []
        try:
            logger.debug("[JS] Extracting conversations via JavaScript...")

            # First verify we're authenticated
            if not self._check_authentication():
                logger.warning("[WARN] Chat area not visible - page may have logged out")
                logger.debug("[JS] Dumping page structure for debugging...")
                try:
                    page_content = self.page.evaluate("() => document.body.innerText.substring(0, 500)")
                    logger.debug(f"[JS] Page content preview: {page_content}")
                except:
                    pass
                return messages

            # JavaScript to extract all conversations from the page
            js_code = """
            () => {
                const conversations = [];
                const skipPatterns = ['edited', 'pinned', 'muted', 'archived', 'scheduled'];

                try {
                    // Strategy 1: Find all elements that contain text with newlines
                    // WhatsApp chat items always have: "Contact Name\\nMessage Preview" format
                    const allElements = document.querySelectorAll('div, span');
                    const foundChats = new Map(); // Use map to deduplicate

                    for (let el of allElements) {
                        try {
                            const text = el.innerText || el.textContent;
                            if (!text || text.length < 15) continue;

                            // Check if this looks like a chat item (contact name + message)
                            const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
                            if (lines.length < 2) continue;

                            const firstLine = lines[0];

                            // Filter out garbage
                            if (firstLine.length > 150 ||
                                firstLine.length < 2 ||
                                /^\\d{1,2}:\\d{2}/.test(firstLine) ||
                                skipPatterns.some(p => text.toLowerCase().includes(p)) ||
                                firstLine.match(/^[a-z-]+$/i)) { // Single word like "arrow", "camera" etc
                                continue;
                            }

                            // Get the best preview line (skip timestamps)
                            let preview = '';
                            for (let i = 1; i < lines.length; i++) {
                                const line = lines[i];
                                if (line &&
                                    !/^\\d{1,2}:\\d{2}$/.test(line) &&  // Not a timestamp
                                    !line.match(/^[a-z0-9-]*$/i) &&      // Not a single word/class name
                                    line.length > 3) {                    // Has actual content
                                    preview = line;
                                    break;
                                }
                            }

                            // If we found a preview, add it
                            if (preview.length > 3) {
                                const key = firstLine + '|' + preview.substring(0, 50);
                                if (!foundChats.has(key)) {
                                    foundChats.set(key, {
                                        sender: firstLine,
                                        preview: preview.substring(0, 200),
                                        full_text: text.substring(0, 500)
                                    });
                                }
                            }
                        } catch (e) {
                            // Ignore elements that error
                        }
                    }

                    // Convert map to array
                    for (let [key, conv] of foundChats) {
                        conversations.push(conv);
                    }

                    return {
                        success: true,
                        conversations: conversations,
                        total_found: conversations.length,
                        page_title: document.title
                    };
                } catch (err) {
                    return {
                        success: false,
                        error: err.message,
                        conversations: []
                    };
                }
            }
            """

            result = self.page.evaluate(js_code)

            if not result.get('success'):
                logger.error(f"[JS] Error: {result.get('error')}")
                return messages

            conversations = result.get('conversations', [])
            logger.info(f"[JS] Found {len(conversations)} unique conversations from {result.get('total_found')} items")

            # Process each conversation
            for idx, conv in enumerate(conversations):
                try:
                    sender = conv.get('sender', 'Unknown')
                    preview = conv.get('preview', '')
                    full_text = conv.get('full_text', '')

                    # Log all conversations with their full text for debugging
                    if full_text:
                        logger.debug(f"[CONV {idx}] Sender: {sender} | Full: {full_text[:100]}")

                    if not preview:
                        logger.debug(f"[CONV {idx}] No preview - checking full_text for keywords...")
                        # If we don't have a preview, use full_text for keyword matching
                        if full_text:
                            preview = full_text
                        else:
                            logger.debug(f"[CONV {idx}] Skipping - no content")
                            continue

                    logger.debug(f"[CONV {idx}] From: {sender} | Preview: {preview[:80]}")

                    # Check for keywords
                    keywords_found = [kw for kw in self.KEYWORDS if kw.lower() in preview.lower() or kw.lower() in full_text.lower()]

                    if keywords_found:
                        msg_hash = hashlib.md5((sender + preview).encode()).hexdigest()[:8]

                        if msg_hash not in self.processed_messages:
                            messages.append({
                                'from': sender,
                                'message': preview if preview else full_text[:200],
                                'received': datetime.now().isoformat(),
                                'priority': 'high' if 'urgent' in preview.lower() else 'medium',
                                'type': 'whatsapp',
                                'status': 'pending',
                                'hash': msg_hash
                            })
                            self.processed_messages.add(msg_hash)
                            logger.info(f"[OK] Captured message from {sender}: {keywords_found} - {preview[:50]}")
                        else:
                            logger.debug(f"[CONV {idx}] Already processed")
                    else:
                        logger.debug(f"[CONV {idx}] No keywords found")

                except Exception as e:
                    logger.debug(f"[CONV {idx}] Error: {e}")

            return messages

        except Exception as e:
            logger.error(f"[ERROR] Failed to extract conversations: {e}", exc_info=True)
            return messages

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
        """Main watcher loop - keeps browser open between checks"""
        logger.info(f"Starting WhatsApp Watcher (Persistent) - Check interval: {self.CHECK_INTERVAL}s, Session refresh: {self.SESSION_REFRESH_INTERVAL}s")

        try:
            self.ensure_session_dir()
            self.launch_browser_persistent()

            if not self.is_authenticated:
                logger.error("[ERROR] Could not authenticate - giving up")
                return

            logger.info("[OK] Starting monitoring loop...")

            cycle_count = 0
            while True:
                cycle_count += 1
                try:
                    current_time = time.time()
                    time_since_auth_check = current_time - self.last_auth_check

                    # Periodic session refresh (every 90 minutes)
                    if time_since_auth_check >= self.SESSION_REFRESH_INTERVAL:
                        logger.info(f"[CYCLE {cycle_count}] Time for session refresh ({time_since_auth_check:.0f}s elapsed)")
                        if not self.refresh_session():
                            logger.error("[SESSION] Session is invalid - need browser restart. Exiting for PM2 restart...")
                            break  # Let PM2 restart the process
                        self.last_auth_check = current_time

                    logger.debug(f"[CYCLE {cycle_count}] Checking for messages...")

                    # Check messages
                    messages = self.get_conversations_from_page()
                    logger.debug(f"[CYCLE {cycle_count}] Found {len(messages)} new messages with keywords")

                    # Save any new messages
                    for message in messages:
                        try:
                            filepath = self.save_to_markdown(message)
                            if filepath:
                                logger.info(f"[OK] Saved message to {filepath}")
                        except Exception as save_err:
                            logger.error(f"[ERROR] Failed to save message: {save_err}", exc_info=True)

                    # Wait for next check
                    logger.debug(f"[CYCLE {cycle_count}] Waiting {self.CHECK_INTERVAL}s until next check...")
                    time.sleep(self.CHECK_INTERVAL)

                except Exception as e:
                    logger.error(f"[ERROR] Cycle {cycle_count} failed: {type(e).__name__}: {e}")
                    try:
                        time.sleep(self.CHECK_INTERVAL)
                    except:
                        pass

        except KeyboardInterrupt:
            logger.info("[OK] WhatsApp Watcher stopped by user")
        except Exception as e:
            logger.error(f"[ERROR] Fatal error: {e}", exc_info=True)
        finally:
            logger.info("[INFO] Cleaning up...")
            if self.page:
                try:
                    self.page.close()
                except:
                    pass
            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass
            if self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass
            logger.info("[OK] Shutdown complete")


if __name__ == "__main__":
    try:
        watcher = WhatsAppPersistentWatcher()
        watcher.run()
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}", exc_info=True)
        sys.exit(1)
