"""
LinkedIn Public Scraper — reads public profiles WITHOUT logging in.
No account session = zero risk.
"""

import asyncio
import random
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async


class LinkedInPublicScraper:
    """
    Scrapes public LinkedIn pages without any login.
    This is equivalent to any regular browser visiting a public page.
    """

    BASE_URL = "https://www.linkedin.com"

    # Title keywords for identifying TA / recruiting contacts
    TA_TITLE_KEYWORDS = [
        "recruiter", "talent acquisition", "talent partner",
        "sourcer", "recruiting", "people operations", "hr partner",
    ]

    async def get_profile(self, linkedin_url: str) -> dict:
        """Fetch public profile data — no login required."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent=self._random_useragent(),
                viewport={"width": 1366, "height": 768},
                locale="en-US",
            )
            page = await context.new_page()
            await stealth_async(page)

            # Human-like delay before navigation
            await asyncio.sleep(random.uniform(2, 5))
            await page.goto(linkedin_url, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(3, 7))

            data = await page.evaluate("""() => {
                return {
                    name: document.querySelector('h1')?.innerText || '',
                    headline: document.querySelector('.text-body-medium')?.innerText || '',
                    location: document.querySelector('.text-body-small.inline')?.innerText || '',
                    about: document.querySelector('#about + div')?.innerText || '',
                }
            }""")

            await browser.close()
            return data

    async def get_company_employees(
        self,
        company_linkedin_url: str,
        title_keywords: list[str] | None = None,
    ) -> list[dict]:
        """
        Search LinkedIn for employees at a company by title keywords.
        Uses public search — no login needed.
        """
        if title_keywords is None:
            title_keywords = self.TA_TITLE_KEYWORDS

        results = []
        for keyword in title_keywords:
            company_slug = company_linkedin_url.rstrip("/").split("/")[-1]
            search_url = (
                f"{self.BASE_URL}/search/results/people/"
                f"?keywords={keyword}"
                f"&facetCurrentCompany={company_slug}"
            )
            profiles = await self._scrape_search_results(search_url)
            results.extend(profiles)
            await asyncio.sleep(random.uniform(5, 12))

        # Deduplicate by URL
        seen = set()
        unique = []
        for profile in results:
            url = profile.get("url", "")
            if url and url not in seen:
                seen.add(url)
                unique.append(profile)
        return unique

    async def get_recent_posts(self, profile_url: str) -> list[str]:
        """Fetch recent public posts from a profile."""
        posts_url = f"{profile_url.rstrip('/')}/recent-activity/all/"
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self._random_useragent()
            )
            page = await context.new_page()
            await stealth_async(page)
            await page.goto(posts_url, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(4, 8))

            posts = await page.evaluate("""() => {
                const items = document.querySelectorAll('.feed-shared-text');
                return Array.from(items).slice(0, 5).map(el => el.innerText);
            }""")

            await browser.close()
            return [p for p in posts if p and len(p) > 20]

    def _random_useragent(self) -> str:
        agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
        ]
        return random.choice(agents)

    async def _scrape_search_results(self, url: str) -> list[dict]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self._random_useragent()
            )
            page = await context.new_page()
            await stealth_async(page)
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(3, 6))

            results = await page.evaluate("""() => {
                const cards = document.querySelectorAll('.reusable-search__result-container');
                return Array.from(cards).slice(0, 10).map(card => ({
                    name: card.querySelector('.entity-result__title-text')?.innerText?.trim() || '',
                    title: card.querySelector('.entity-result__primary-subtitle')?.innerText?.trim() || '',
                    url: card.querySelector('a.app-aware-link')?.href || '',
                }));
            }""")

            await browser.close()
            return results
