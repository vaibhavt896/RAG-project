"""
Health Scorer — Redis-backed account safety scoring.
Monitors connection acceptance, reply rates, engagement ratio, and activity.
Score < 50 triggers emergency pause across all agents.
"""

import redis
from app.config import get_settings

settings = get_settings()


def _get_redis():
    return redis.Redis.from_url(settings.redis_url, decode_responses=True)


def calculate_health_score(user_id: str) -> float:
    """
    Calculates an account health score from 0-100.
    Components:
      - Connection acceptance rate (30 pts)
      - Message reply rate (25 pts)
      - Engagement ratio (20 pts)
      - Days active in last 30 (15 pts)
      - Baseline (10 pts)
    """
    r = _get_redis()
    score = 0.0

    # 1. Connection acceptance rate (30 pts)
    sent = int(r.get(f"stats:{user_id}:connections_sent_30d") or 0)
    accepted = int(r.get(f"stats:{user_id}:connections_accepted_30d") or 0)
    if sent > 0:
        rate = accepted / sent
        if rate >= 0.30:
            score += 30
        elif rate >= 0.20:
            score += 20
        elif rate >= 0.15:
            score += 10

    # 2. Message reply rate (25 pts)
    msgs_sent = int(r.get(f"stats:{user_id}:messages_sent_30d") or 0)
    msgs_replied = int(r.get(f"stats:{user_id}:messages_replied_30d") or 0)
    if msgs_sent > 0:
        rate = msgs_replied / msgs_sent
        if rate >= 0.10:
            score += 25
        elif rate >= 0.05:
            score += 15
        elif rate >= 0.03:
            score += 8

    # 3. Engagement ratio (20 pts)
    engagements = int(r.get(f"stats:{user_id}:engagements_7d") or 0)
    connections = int(r.get(f"stats:{user_id}:connections_sent_7d") or 1)
    ratio = engagements / connections
    if ratio >= 0.5:
        score += 20
    elif ratio >= 0.3:
        score += 13
    elif ratio >= 0.1:
        score += 6

    # 4. Days active in last 30 (15 pts)
    days_active = int(r.get(f"stats:{user_id}:days_active_30d") or 0)
    if days_active >= 18:
        score += 15
    elif days_active >= 12:
        score += 10
    elif days_active >= 8:
        score += 5

    # 5. Baseline (10 pts)
    score += 10

    return round(min(100.0, score), 1)


def increment_stat(user_id: str, stat_key: str, amount: int = 1) -> None:
    """Increment a health stat counter."""
    r = _get_redis()
    key = f"stats:{user_id}:{stat_key}"
    r.incrby(key, amount)
    # Auto-expire stats after 35 days
    r.expire(key, 35 * 86400)


def get_daily_action_count(user_id: str, action_type: str) -> int:
    """Get how many of a specific action have been taken today."""
    r = _get_redis()
    key = f"daily:{user_id}:{action_type}:{_today_key()}"
    return int(r.get(key) or 0)


def record_daily_action(user_id: str, action_type: str) -> None:
    """Record an action for today's budget tracking."""
    r = _get_redis()
    key = f"daily:{user_id}:{action_type}:{_today_key()}"
    r.incr(key)
    r.expire(key, 86400 * 2)  # Expire after 2 days


def _today_key() -> str:
    from datetime import date
    return date.today().isoformat()
