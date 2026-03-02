"""
LinkedIn Action Executor — Playwright-based action execution.
This module handles the actual browser interactions for LinkedIn:
  - Login + session management
  - Liking posts
  - Following companies
  - Commenting on posts
  - Sending connection requests
  - Sending messages
  - Checking inbox for replies

ONLY used for actions. NEVER for data collection.
Data collection uses the public scraper (no login).
"""

import asyncio
import random
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext
from playwright_stealth import stealth_async

from app.core.behavior_engine import HumanBehaviorEngine
from app.config import get_settings

settings = get_settings()
behavior = HumanBehaviorEngine()

# Session storage path — persist cookies between runs
SESSION_DIR = Path("./sessions")
SESSION_DIR.mkdir(exist_ok=True)


class LinkedInActionExecutor:
    """
    Executes LinkedIn actions via Playwright with full human simulation.
    Maintains a persistent login session via stored cookies.
    """

    BASE_URL = "https://www.linkedin.com"

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.session_path = SESSION_DIR / f"{user_id}_session.json"

    # ── Session Management ───────────────────────────────────────

    async def _get_context(self, playwright) -> BrowserContext:
        """
        Launch browser and restore session cookies if available.
        """
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        context = await browser.new_context(
            user_agent=self._random_ua(),
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id=settings.timezone,
        )

        # Restore saved cookies
        if self.session_path.exists():
            try:
                cookies = json.loads(self.session_path.read_text())
                await context.add_cookies(cookies)
            except Exception:
                pass

        return context

    async def _save_session(self, context: BrowserContext) -> None:
        """Persist cookies for next session."""
        cookies = await context.cookies()
        self.session_path.write_text(json.dumps(cookies, default=str))

    async def _ensure_logged_in(self, page: Page) -> bool:
        """
        Navigate to LinkedIn and verify login. If not logged in, perform login.
        Returns True if successfully logged in.
        """
        await page.goto(f"{self.BASE_URL}/feed/", wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(2, 4))

        # Check if we're on the feed (logged in) or login page
        current_url = page.url
        if "/feed" in current_url:
            return True

        if "/login" in current_url or "/checkpoint" in current_url:
            return await self._perform_login(page)

        # Unknown state — try navigating to feed again
        await page.goto(f"{self.BASE_URL}/feed/", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        return "/feed" in page.url

    async def _perform_login(self, page: Page) -> bool:
        """
        Log into LinkedIn with human-like typing and timing.
        """
        if not settings.linkedin_email or not settings.linkedin_password:
            print("LinkedIn credentials not configured")
            return False

        try:
            # Wait for email field
            email_field = await page.wait_for_selector(
                'input[name="session_key"], #username', timeout=10000
            )
            if not email_field:
                return False

            # Human-like typing with random delays between keys
            await email_field.click()
            await asyncio.sleep(random.uniform(0.3, 0.8))
            for char in settings.linkedin_email:
                await email_field.type(char, delay=random.randint(50, 150))
            await asyncio.sleep(random.uniform(0.5, 1.2))

            # Password field
            pw_field = await page.wait_for_selector(
                'input[name="session_password"], #password', timeout=5000
            )
            if not pw_field:
                return False

            await pw_field.click()
            await asyncio.sleep(random.uniform(0.3, 0.6))
            for char in settings.linkedin_password:
                await pw_field.type(char, delay=random.randint(40, 130))
            await asyncio.sleep(random.uniform(0.5, 1.5))

            # Click sign in
            submit = await page.query_selector(
                'button[type="submit"], .login__form_action_container button'
            )
            if submit:
                await submit.click()
            else:
                await page.keyboard.press("Enter")

            await asyncio.sleep(random.uniform(3, 6))

            # Check for CAPTCHA or challenge
            current_url = page.url
            if "challenge" in current_url or "checkpoint" in current_url:
                raise Exception("CAPTCHA/security challenge detected — manual intervention required")

            return "/feed" in page.url

        except Exception as e:
            print(f"Login failed: {e}")
            raise

    # ── Action Implementations ───────────────────────────────────

    async def like_post(self, profile_url: str) -> bool:
        """
        Navigate to a lead's recent activity and like their most recent post.
        """
        async with async_playwright() as p:
            context = await self._get_context(p)
            page = await context.new_page()
            await stealth_async(page)

            try:
                if not await self._ensure_logged_in(page):
                    return False

                # Go to their recent posts
                activity_url = f"{profile_url.rstrip('/')}/recent-activity/all/"
                await behavior.wait("profile_view")
                await page.goto(activity_url, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(3, 6))

                # Simulate reading
                await behavior.simulate_reading_page(page)

                # Find the first like button that isn't already liked
                like_buttons = await page.query_selector_all(
                    'button[aria-label*="Like"], button.react-button__trigger'
                )
                for btn in like_buttons:
                    aria = await btn.get_attribute("aria-pressed") or "false"
                    if aria.lower() == "false":
                        await behavior.random_micro_delay()
                        await btn.click()
                        await asyncio.sleep(random.uniform(1, 3))
                        await self._save_session(context)
                        return True

                # No unliked posts found — still a success (nothing to like)
                return True

            except Exception as e:
                print(f"Like post failed: {e}")
                return self._check_captcha(e)
            finally:
                await context.browser.close()

    async def follow_company(self, company_url: str) -> bool:
        """
        Navigate to a company page and click Follow.
        """
        async with async_playwright() as p:
            context = await self._get_context(p)
            page = await context.new_page()
            await stealth_async(page)

            try:
                if not await self._ensure_logged_in(page):
                    return False

                await behavior.wait("profile_view")
                await page.goto(company_url, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(3, 6))
                await behavior.simulate_reading_page(page)

                # Click Follow button
                follow_btn = await page.query_selector(
                    'button:has-text("Follow"), button[aria-label*="Follow"]'
                )
                if follow_btn:
                    text = await follow_btn.inner_text()
                    if "follow" in text.lower() and "following" not in text.lower():
                        await behavior.random_micro_delay()
                        await follow_btn.click()
                        await asyncio.sleep(random.uniform(1, 3))

                await self._save_session(context)
                return True

            except Exception as e:
                print(f"Follow company failed: {e}")
                return self._check_captcha(e)
            finally:
                await context.browser.close()

    async def comment_on_post(self, profile_url: str, comment_text: str) -> bool:
        """
        Navigate to a lead's posts and leave a comment on the most recent one.
        """
        async with async_playwright() as p:
            context = await self._get_context(p)
            page = await context.new_page()
            await stealth_async(page)

            try:
                if not await self._ensure_logged_in(page):
                    return False

                activity_url = f"{profile_url.rstrip('/')}/recent-activity/all/"
                await behavior.wait("profile_view")
                await page.goto(activity_url, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(3, 6))
                await behavior.simulate_reading_page(page)

                # Find the first comment button
                comment_btns = await page.query_selector_all(
                    'button[aria-label*="Comment"], button.comment-button'
                )
                if not comment_btns:
                    return False

                await comment_btns[0].click()
                await asyncio.sleep(random.uniform(1.5, 3))

                # Find and focus the comment input
                comment_box = await page.wait_for_selector(
                    'div.ql-editor, div[contenteditable="true"][role="textbox"]',
                    timeout=5000,
                )
                if not comment_box:
                    return False

                await comment_box.click()
                await asyncio.sleep(random.uniform(0.5, 1))

                # Type comment with human-like speed
                for char in comment_text:
                    await page.keyboard.type(char, delay=random.randint(30, 100))
                await asyncio.sleep(random.uniform(1, 2.5))

                # Submit
                submit_btn = await page.query_selector(
                    'button.comments-comment-box__submit-button, button[aria-label*="Post"]'
                )
                if submit_btn:
                    await submit_btn.click()
                    await asyncio.sleep(random.uniform(2, 4))

                await self._save_session(context)
                return True

            except Exception as e:
                print(f"Comment failed: {e}")
                return self._check_captcha(e)
            finally:
                await context.browser.close()

    async def send_connection_request(
        self, profile_url: str, note: str | None = None
    ) -> bool:
        """
        Send a connection request. By default, no note (higher acceptance rate).
        If note is provided, it must be ≤ 290 characters.
        """
        async with async_playwright() as p:
            context = await self._get_context(p)
            page = await context.new_page()
            await stealth_async(page)

            try:
                if not await self._ensure_logged_in(page):
                    return False

                await behavior.wait("connection_request")
                await page.goto(profile_url, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(3, 6))
                await behavior.simulate_reading_page(page)

                # Look for Connect button
                connect_btn = await page.query_selector(
                    'button:has-text("Connect"), '
                    'button[aria-label*="connect" i]'
                )

                # Sometimes Connect is in "More" dropdown
                if not connect_btn:
                    more_btn = await page.query_selector(
                        'button[aria-label*="More actions"], '
                        'button.artdeco-dropdown__trigger'
                    )
                    if more_btn:
                        await more_btn.click()
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        connect_btn = await page.query_selector(
                            'span:has-text("Connect"), '
                            'div[aria-label*="connect" i]'
                        )

                if not connect_btn:
                    print("Connect button not found — may already be connected")
                    return False

                await behavior.random_micro_delay()
                await connect_btn.click()
                await asyncio.sleep(random.uniform(1, 3))

                # Handle the connection dialog
                if note and len(note) <= 290:
                    add_note_btn = await page.query_selector(
                        'button:has-text("Add a note"), button[aria-label*="Add a note"]'
                    )
                    if add_note_btn:
                        await add_note_btn.click()
                        await asyncio.sleep(random.uniform(0.5, 1.5))

                        note_field = await page.wait_for_selector(
                            'textarea[name="message"], textarea#custom-message',
                            timeout=3000,
                        )
                        if note_field:
                            for char in note:
                                await page.keyboard.type(char, delay=random.randint(20, 80))
                            await asyncio.sleep(random.uniform(0.5, 1))

                # Click "Send" / "Send without a note"
                send_btn = await page.query_selector(
                    'button:has-text("Send"), '
                    'button[aria-label*="Send"]'
                )
                if send_btn:
                    await send_btn.click()
                    await asyncio.sleep(random.uniform(2, 4))

                await self._save_session(context)
                return True

            except Exception as e:
                print(f"Connection request failed: {e}")
                return self._check_captcha(e)
            finally:
                await context.browser.close()

    async def send_message(self, profile_url: str, message_text: str) -> bool:
        """
        Send a message to a 1st-degree connection via their profile message button.
        """
        async with async_playwright() as p:
            context = await self._get_context(p)
            page = await context.new_page()
            await stealth_async(page)

            try:
                if not await self._ensure_logged_in(page):
                    return False

                await behavior.wait("send_message")
                await page.goto(profile_url, wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(3, 6))
                await behavior.simulate_reading_page(page)

                # Click Message button
                msg_btn = await page.query_selector(
                    'button:has-text("Message"), '
                    'a:has-text("Message"), '
                    'button[aria-label*="message" i]'
                )
                if not msg_btn:
                    print("Message button not found — may not be connected")
                    return False

                await msg_btn.click()
                await asyncio.sleep(random.uniform(2, 4))

                # Wait for message compose box
                compose_box = await page.wait_for_selector(
                    'div.msg-form__contenteditable, '
                    'div[contenteditable="true"][role="textbox"]',
                    timeout=8000,
                )
                if not compose_box:
                    return False

                await compose_box.click()
                await asyncio.sleep(random.uniform(0.5, 1))

                # Type message with human-like speed
                for char in message_text:
                    await page.keyboard.type(char, delay=random.randint(20, 80))

                await asyncio.sleep(random.uniform(1, 3))

                # Click Send
                send_btn = await page.query_selector(
                    'button.msg-form__send-button, '
                    'button[type="submit"]:has-text("Send"), '
                    'button[aria-label="Send"]'
                )
                if send_btn:
                    await send_btn.click()
                    await asyncio.sleep(random.uniform(2, 4))

                await self._save_session(context)
                return True

            except Exception as e:
                print(f"Send message failed: {e}")
                return self._check_captcha(e)
            finally:
                await context.browser.close()

    async def check_inbox_for_replies(self, known_lead_names: list[str]) -> list[dict]:
        """
        Open LinkedIn messaging and scan for new replies from tracked leads.
        Returns list of {lead_name, snippet} for leads that have replied.
        """
        replies = []
        async with async_playwright() as p:
            context = await self._get_context(p)
            page = await context.new_page()
            await stealth_async(page)

            try:
                if not await self._ensure_logged_in(page):
                    return replies

                await page.goto(
                    f"{self.BASE_URL}/messaging/", wait_until="domcontentloaded"
                )
                await asyncio.sleep(random.uniform(3, 6))

                # Get conversation list items
                convos = await page.query_selector_all(
                    'li.msg-conversation-listitem, '
                    'div.msg-conversation-card'
                )

                for convo in convos[:20]:  # Check top 20 conversations
                    try:
                        # Get sender name
                        name_el = await convo.query_selector(
                            'span.msg-conversation-card__participant-names, '
                            '.msg-conversation-listitem__participant-names'
                        )
                        if not name_el:
                            continue
                        sender_name = (await name_el.inner_text()).strip()

                        # Check if sender is a tracked lead
                        matched_lead = None
                        for lead_name in known_lead_names:
                            if lead_name.lower() in sender_name.lower():
                                matched_lead = lead_name
                                break

                        if not matched_lead:
                            continue

                        # Check for unread indicator
                        unread = await convo.query_selector(
                            '.msg-conversation-card__unread-count, '
                            '.notification-badge'
                        )

                        # Get snippet
                        snippet_el = await convo.query_selector(
                            'p.msg-conversation-card__message-snippet, '
                            '.msg-conversation-card__message-snippet-body'
                        )
                        snippet = ""
                        if snippet_el:
                            snippet = (await snippet_el.inner_text()).strip()

                        if unread or snippet:
                            replies.append({
                                "lead_name": matched_lead,
                                "sender_display": sender_name,
                                "snippet": snippet[:200],
                                "has_unread": unread is not None,
                            })

                    except Exception:
                        continue

                await self._save_session(context)

            except Exception as e:
                print(f"Inbox check failed: {e}")
            finally:
                await context.browser.close()

        return replies

    # ── Utilities ────────────────────────────────────────────────

    def _check_captcha(self, error: Exception) -> bool:
        """If CAPTCHA detected, raise to trigger emergency stop."""
        err_str = str(error).lower()
        if "captcha" in err_str or "challenge" in err_str or "security" in err_str:
            raise Exception(f"CAPTCHA/security challenge detected: {error}")
        return False

    def _random_ua(self) -> str:
        agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        ]
        return random.choice(agents)
