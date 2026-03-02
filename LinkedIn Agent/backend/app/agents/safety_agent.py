"""
Safety Agent — enforces health scoring and daily budgets.
Called before every action. Score < 50 = emergency pause.
"""

from app.celery_app import celery_app
from app.core.health_scorer import calculate_health_score
from app.core.behavior_engine import HumanBehaviorEngine

behavior = HumanBehaviorEngine()


@celery_app.task(name="app.agents.safety_agent.check_safety")
def check_safety(user_id: str) -> dict:
    """
    Full safety check before any action.
    Returns a dict with pass/fail and details.
    """
    health = calculate_health_score(user_id)

    from app.config import get_settings
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.user import User

    settings = get_settings()
    engine = create_engine(settings.database_url_sync)

    with Session(engine) as session:
        user = session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

        if not user:
            return {"safe": False, "reason": "User not found", "health": 0}

        timezone = user.timezone
        warmup_phase = user.warmup_phase

    # Check working hours
    if not behavior.is_working_hour(timezone):
        return {
            "safe": False,
            "reason": "Outside working hours",
            "health": health,
        }

    # Check offline day
    if behavior.should_take_offline_day():
        return {
            "safe": False,
            "reason": "Random offline day",
            "health": health,
        }

    # Check health score
    if health < 50:
        return {
            "safe": False,
            "reason": f"Health score critical: {health}",
            "health": health,
            "alert": True,
        }

    # Get budget
    budget = behavior.get_daily_budget(warmup_phase, health)

    return {
        "safe": True,
        "health": health,
        "warmup_phase": warmup_phase,
        "daily_budget": budget,
    }


@celery_app.task(name="app.agents.safety_agent.get_health_report")
def get_health_report(user_id: str) -> dict:
    """Generate a full health report for the dashboard."""
    health = calculate_health_score(user_id)

    import redis
    from app.config import get_settings

    settings = get_settings()
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    return {
        "health_score": health,
        "status": (
            "healthy" if health >= 70
            else "caution" if health >= 50
            else "critical"
        ),
        "metrics": {
            "connections_sent_30d": int(r.get(f"stats:{user_id}:connections_sent_30d") or 0),
            "connections_accepted_30d": int(r.get(f"stats:{user_id}:connections_accepted_30d") or 0),
            "messages_sent_30d": int(r.get(f"stats:{user_id}:messages_sent_30d") or 0),
            "messages_replied_30d": int(r.get(f"stats:{user_id}:messages_replied_30d") or 0),
            "days_active_30d": int(r.get(f"stats:{user_id}:days_active_30d") or 0),
        },
    }
