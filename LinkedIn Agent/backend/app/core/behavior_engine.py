"""
Human Behavior Engine — simulates realistic browsing patterns.
LinkedIn detection is behavioral. This engine ensures every delay,
scroll, and click follows natural human variance.
"""

import random
import asyncio
import numpy as np
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo


class HumanBehaviorEngine:
    """
    Controls timing, budgets, and simulated behavior for LinkedIn actions.
    Every delay uses a normal distribution — never constant.
    """

    # (min_seconds, max_seconds) for each action type
    ACTION_DELAYS = {
        "profile_view":       (8,   45),
        "scroll_feed":        (10,  40),
        "like_post":          (20,  90),
        "comment_post":       (60,  300),
        "connection_request": (45,  180),
        "send_message":       (90,  420),
        "between_sessions":   (900, 7200),
    }

    # Daily action budgets per warmup phase (1-5)
    DAILY_BUDGETS = {
        1: {"connections": 5,  "messages": 5,  "profile_views": 20},
        2: {"connections": 10, "messages": 10, "profile_views": 40},
        3: {"connections": 15, "messages": 20, "profile_views": 60},
        4: {"connections": 20, "messages": 30, "profile_views": 80},
        5: {"connections": 25, "messages": 35, "profile_views": 100},
    }

    async def wait(self, action_type: str) -> float:
        """
        Wait a human-like duration before executing an action.
        Uses a normal distribution clipped to [lo, hi].
        Returns the actual delay used.
        """
        lo, hi = self.ACTION_DELAYS.get(action_type, (10, 60))
        mean = (lo + hi) / 2
        std = (hi - lo) / 4
        delay = float(np.random.normal(mean, std))
        delay = max(lo, min(hi, delay))
        await asyncio.sleep(delay)
        return delay

    def is_working_hour(self, timezone: str) -> bool:
        """Only operate during realistic working hours (never Sunday)."""
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)

        # Never on Sunday
        if now.weekday() == 6:
            return False

        # Slight randomness in start/end times
        work_start = dt_time(8, random.randint(45, 59))
        work_end = dt_time(18, random.randint(0, 30))

        return work_start <= now.time() <= work_end

    def should_take_offline_day(self) -> bool:
        """12% chance of a random offline day — humans skip days."""
        return random.random() < 0.12

    def get_daily_budget(self, warmup_phase: int, health_score: float) -> dict:
        """
        Returns today's action budget based on warmup phase and health.
        Health < 50 → zero activity (emergency pause).
        Health < 70 → scaled-down budget.
        """
        if health_score < 50:
            return {"connections": 0, "messages": 0, "profile_views": 0}

        budget = self.DAILY_BUDGETS.get(
            warmup_phase, self.DAILY_BUDGETS[1]
        ).copy()

        if health_score < 70:
            scale = health_score / 100
            budget = {k: max(1, int(v * scale)) for k, v in budget.items()}

        return budget

    async def simulate_reading_page(self, page) -> None:
        """
        Simulate a human reading a page — scrolls, pauses, sometimes scrolls back.
        """
        scroll_count = random.randint(2, 5)
        for _ in range(scroll_count):
            scroll_px = random.randint(150, 500)
            await page.evaluate(f"window.scrollBy(0, {scroll_px})")
            await page.wait_for_timeout(random.uniform(0.6, 2.8) * 1000)

        # Occasionally scroll back up (like a real human re-reading)
        if random.random() < 0.3:
            await page.evaluate("window.scrollBy(0, -200)")
            await page.wait_for_timeout(random.uniform(0.5, 1.5) * 1000)

    async def random_micro_delay(self) -> None:
        """Tiny random pause between sub-actions (typing, clicking)."""
        await asyncio.sleep(random.uniform(0.3, 1.5))
