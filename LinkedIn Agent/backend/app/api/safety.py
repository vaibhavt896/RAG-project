"""
Safety API — health score, daily budget, warmup status.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health/{user_id}")
async def get_health_score(user_id: str):
    """Get current account health score and metrics."""
    from app.agents.safety_agent import get_health_report
    report = get_health_report(user_id)
    return report


@router.get("/check/{user_id}")
async def check_safety(user_id: str):
    """Run a full safety check (used before actions)."""
    from app.agents.safety_agent import check_safety
    result = check_safety(user_id)
    return result


@router.get("/budget/{user_id}")
async def get_daily_budget(user_id: str):
    """Get today's remaining action budget."""
    from app.core.behavior_engine import HumanBehaviorEngine
    from app.core.health_scorer import calculate_health_score, get_daily_action_count
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
            return {"error": "User not found"}

        behavior = HumanBehaviorEngine()
        health = calculate_health_score(user_id)
        budget = behavior.get_daily_budget(user.warmup_phase, health)

        # Calculate remaining
        remaining = {}
        for action_type, limit in budget.items():
            used = get_daily_action_count(user_id, action_type)
            remaining[action_type] = {
                "limit": limit,
                "used": used,
                "remaining": max(0, limit - used),
            }

        return {
            "warmup_phase": user.warmup_phase,
            "health_score": health,
            "budget": remaining,
        }
