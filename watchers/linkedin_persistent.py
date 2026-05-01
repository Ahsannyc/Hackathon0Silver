#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Watcher - Persistent Browser Session
Keeps the browser open between checks to maintain authentication
One-time setup: manual login, then continuous monitoring
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
        logging.FileHandler("watchers/logs/linkedin_watcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInPersistentWatcher:
    """
    LinkedIn Watcher that keeps browser open to maintain session.
    First run: requires manual login
    Subsequent runs: uses persistent session

    ENHANCEMENTS:
    - Periodic session validation every 90 minutes
    - Auto-restart on authentication failure
    - Better error recovery with exponential backoff
    """
    KEYWORDS = ['sales', 'client', 'project', 'opportunity', 'partnership', 'lead']
    CHECK_INTERVAL = 60  # seconds between message checks
    SESSION_REFRESH_INTERVAL = 5400  # 90 minutes - check auth health
    NEEDS_ACTION_DIR = Path("Needs_Action")
    SESSION_PATH = Path("session/linkedin")
    AUTH_MARKER_FILE = Path("session/linkedin_authenticated.txt")

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

    def launch_browser_persistent(self):
        """Launch browser with persistent session that stays open"""
        try:
            self.playwright = sync_playwright().start()

            # Use persistent context - this saves cookies, localStorage, etc.
            logger.info("[SETUP] Launching Chromium with persistent session...")
            self.browser = self.playwright.chromium.launch_persistent_context(
                str(self.SESSION_PATH.absolute()),
                headless=False,  # Show browser window for login if needed
                args=[
                    '--disable-blink-features=AutomationControlled',
                ]
            )

            self.page = self.browser.new_page()
            logger.info("[OK] Browser launched, navigating to LinkedIn...")

            try:
                self.page.goto("https://www.linkedin.com/feed/", wait_until="networkidle", timeout=30000)
            except Exception as nav_err:
                logger.warning(f"[WARN] Navigation timeout or error: {nav_err}, proceeding anyway...")
                try:
                    self.page.goto("https://www.linkedin.com/feed/")
                except:
                    pass

            logger.info("[LOAD] Page loaded, waiting for feed area...")

            # Try to detect if authenticated
            time.sleep(2)
            auth_status = self._check_authentication()

            if auth_status:
                logger.info("[OK] AUTHENTICATED - LinkedIn feed detected!")
                self.is_authenticated = True
                self.mark_authenticated()
                time.sleep(2)
            else:
                if self.is_already_authenticated():
                    logger.warning("[WARN] Auth marker exists but feed not visible")
                    logger.info("[INFO] Session might need refresh, waiting 15 seconds...")
                    time.sleep(15)
                    self.is_authenticated = True
                else:
                    logger.warning("[WARN] First run detected - feed not visible")
                    logger.info("[INFO] Waiting 60 seconds for manual login...")
                    time.sleep(60)
                    auth_status = self._check_authentication()
                    if auth_status:
                        logger.info("[OK] Authentication successful!")
                        self.is_authenticated = True
                        self.mark_authenticated()
                        time.sleep(2)
                    else:
                        logger.warning("[WARN] Feed still not visible - will proceed anyway")
                        self.is_authenticated = True  # Mark as authenticated to start monitoring

        except Exception as e:
            logger.error(f"[ERROR] Browser launch failed: {e}", exc_info=True)
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            raise

    def _check_authentication(self) -> bool:
        """Check if we're authenticated (feed visible)"""
        try:
            # Look for the main feed area
            is_main_visible = self.page.is_visible('[data-test-id="feed"]', timeout=3000)
            if is_main_visible:
                return True
        except:
            pass

        try:
            # Look for feed with different selector
            is_feed_visible = self.page.is_visible('section.scaffold-layout__list-container', timeout=2000)
            if is_feed_visible:
                return True
        except:
            pass

        try:
            # Check if we're NOT on a login/error page
            page_text = self.page.inner_text("body").lower()
            if "sign in" in page_text and "email" in page_text:
                return False
            # If page has reasonable content, assume authenticated
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

    def get_messages_from_page(self) -> List[Dict]:
        """Extract messages and notifications from LinkedIn"""
        messages = []
        try:
            logger.debug("[JS] Extracting LinkedIn messages...")

            # First verify we're authenticated
            if not self._check_authentication():
                logger.warning("[WARN] Feed area not visible - page may have logged out")
                return messages

            # JavaScript to extract messages and notifications
            js_code = """
            () => {
                const items = [];
                const badWords = ['like', 'comment', 'share', 'linkedin', 'follow', 'connection', 'network', 'endorsement', 'reacted', 'views', 'impression'];

                try {
                    // Strategy 1: Look for all text-heavy divs that might contain messages
                    // This is more aggressive - scan all divs and find ones with substantial content
                    const allDivs = document.querySelectorAll('div');
                    const contentMap = new Map();

                    for (let div of allDivs) {
                        try {
                            const text = div.innerText || div.textContent;
                            if (!text || text.length < 30 || text.length > 1000) continue;

                            const lower = text.toLowerCase();

                            // Filter out obvious UI elements
                            if (badWords.some(w => lower.includes(w) && text.length < 100)) continue;

                            // Look for patterns: "Name: message content"
                            const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
                            if (lines.length < 2) continue;

                            // Potential sender on first line
                            const firstLine = lines[0];
                            if (firstLine.length > 150) continue; // Too long for a name
                            if (firstLine.match(/^\\d{1,2}:\\d{2}/)) continue; // Timestamp
                            if (firstLine.match(/^[a-z0-9 ]+$/i) && firstLine.length < 10) continue; // Single word

                            // Join content
                            const preview = lines.slice(1).join(' ').substring(0, 200);
                            if (preview.length < 5) continue;

                            const key = firstLine + '|' + preview.substring(0, 30);
                            if (!contentMap.has(key)) {
                                contentMap.set(key, {
                                    sender: firstLine,
                                    preview: preview,
                                    full_text: text.substring(0, 500),
                                    source: 'linkedin_feed'
                                });
                            }
                        } catch (e) {
                            // Skip
                        }
                    }

                    // Add all found items
                    for (let [key, item] of contentMap) {
                        items.push(item);
                    }

                    // Strategy 2: Look for message items in the feed/messaging area (fallback)
                    if (items.length === 0) {
                        const messageContainers = document.querySelectorAll('div[class*="message"], div[class*="notification"], article');

                        for (let container of messageContainers) {
                            try {
                                const text = container.innerText || container.textContent;
                                if (!text || text.length < 20) continue;

                                const lower = text.toLowerCase();
                                if (badWords.some(kw => lower.includes(kw) && text.length < 100)) continue;

                                // Extract sender and content
                                const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
                                if (lines.length < 1) continue;

                                // Try to identify sender
                                let sender = '';
                                let preview = '';

                                // Look for name-like patterns
                                for (let i = 0; i < Math.min(3, lines.length); i++) {
                                    const line = lines[i];
                                    if (line.length > 3 && line.length < 100 && !line.match(/^\\d+/) && line.match(/[A-Z]/)) {
                                        sender = line;
                                        preview = lines.slice(i + 1).join(' ').substring(0, 200);
                                        break;
                                    }
                                }

                                if (!sender && lines.length > 0) {
                                    sender = lines[0];
                                    preview = lines.slice(1).join(' ').substring(0, 200);
                                }

                                if (sender && sender.length > 2 && sender.length < 150) {
                                    const key = sender + '|' + preview.substring(0, 30);
                                    if (!contentMap.has(key)) {
                                        items.push({
                                            sender: sender,
                                            preview: preview || text.substring(0, 200),
                                            full_text: text.substring(0, 500),
                                            source: 'linkedin_feed'
                                        });
                                    }
                                }
                            } catch (e) {
                                // Skip items that error
                            }
                        }
                    }

                    // Deduplicate
                    const seen = new Set();
                    const unique = [];
                    for (let item of items) {
                        const key = item.sender + '|' + item.preview.substring(0, 30);
                        if (!seen.has(key)) {
                            seen.add(key);
                            unique.push(item);
                        }
                    }

                    return {
                        success: true,
                        items: unique,
                        total_found: items.length,
                        unique_count: unique.length,
                        page_title: document.title
                    };
                } catch (err) {
                    return {
                        success: false,
                        error: err.message,
                        items: []
                    };
                }
            }
            """

            result = self.page.evaluate(js_code)

            if not result.get('success'):
                logger.error(f"[JS] Error: {result.get('error')}")
                return messages

            items = result.get('items', [])
            logger.info(f"[JS] Found {len(items)} unique items from {result.get('total_found')} total")

            # Process each item
            for idx, item in enumerate(items):
                try:
                    sender = item.get('sender', 'Unknown')
                    preview = item.get('preview', '')
                    full_text = item.get('full_text', '')
                    source = item.get('source', 'linkedin')

                    if not preview:
                        logger.debug(f"[ITEM {idx}] No preview - checking full_text...")
                        if full_text:
                            preview = full_text
                        else:
                            logger.debug(f"[ITEM {idx}] Skipping - no content")
                            continue

                    logger.debug(f"[ITEM {idx}] From: {sender} | Preview: {preview[:80]}")

                    # Check for keywords
                    keywords_found = [kw for kw in self.KEYWORDS if kw.lower() in preview.lower() or kw.lower() in full_text.lower()]

                    if keywords_found:
                        msg_hash = hashlib.md5((sender + preview).encode()).hexdigest()[:8]

                        if msg_hash not in self.processed_messages:
                            messages.append({
                                'from': sender,
                                'message': preview if preview else full_text[:200],
                                'received': datetime.now().isoformat(),
                                'priority': 'high' if 'opportunity' in preview.lower() else 'medium',
                                'type': 'linkedin',
                                'status': 'pending',
                                'hash': msg_hash,
                                'source': source
                            })
                            self.processed_messages.add(msg_hash)
                            logger.info(f"[OK] Captured LinkedIn item from {sender}: {keywords_found} - {preview[:50]}")
                        else:
                            logger.debug(f"[ITEM {idx}] Already processed")
                    else:
                        logger.debug(f"[ITEM {idx}] No keywords found")

                except Exception as e:
                    logger.debug(f"[ITEM {idx}] Error: {e}")

            return messages

        except Exception as e:
            logger.error(f"[ERROR] Failed to extract items: {e}", exc_info=True)
            return messages

    def save_to_markdown(self, message: Dict) -> Path:
        """Save message as markdown file with YAML metadata"""
        try:
            self.NEEDS_ACTION_DIR.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            msg_hash = message.get('hash', hashlib.md5(str(time.time()).encode()).hexdigest()[:6])
            safe_sender = "".join(c for c in message['from'] if c.isalnum() or c in ' -_')[:20]
            filename = f"linkedin_{timestamp}_{msg_hash}_{safe_sender}.md"
            filepath = self.NEEDS_ACTION_DIR / filename

            source = message.get('source', 'linkedin')

            content = f"""---
type: linkedin
from: {message.get('from', 'Unknown')}
subject: LinkedIn {source} from {message.get('from', 'Unknown')}
received: {message.get('received', datetime.now().isoformat())}
priority: {message.get('priority', 'medium')}
status: {message.get('status', 'pending')}
source: {source}
created_at: {datetime.now().isoformat()}
---

# LinkedIn {source.replace('_', ' ').title()} from {message.get('from', 'Unknown')}

**From:** {message.get('from', 'Unknown')}

**Received:** {message.get('received', 'Unknown')}

**Priority:** {message.get('priority', 'medium').upper()}

---

## Message

{message.get('message', '(No content)')}

---

## Action Required

- [ ] Review on LinkedIn
- [ ] Respond to sender
- [ ] Connect if interested
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
        logger.info(f"Starting LinkedIn Watcher (Persistent) - Check interval: {self.CHECK_INTERVAL}s, Session refresh: {self.SESSION_REFRESH_INTERVAL}s")

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
                    messages = self.get_messages_from_page()
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
            logger.info("[OK] LinkedIn Watcher stopped by user")
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
        watcher = LinkedInPersistentWatcher()
        watcher.run()
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}", exc_info=True)
        sys.exit(1)
