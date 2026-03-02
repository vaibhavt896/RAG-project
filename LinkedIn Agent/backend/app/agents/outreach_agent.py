"""
Outreach Agent — executes LinkedIn actions via Playwright.
ONLY logs in for actions (like, follow, connect, message).
Runs every 15 minutes via Celery Beat.

21-DAY SEQUENCE:
  Day 0  → like_post
  Day 2  → follow_company
  Day 4  → comment_post
  Day 6  → send_connection (no note — higher acceptance)
  Day 9  → send_message (only if connected)
  Day 14 → send_message (only if no reply)
  Day 21 → send_email (only if email found + no reply)
"""

from app.celery_app import celery_app
from app.core.behavior_engine import HumanBehaviorEngine
from app.core.health_scorer import (
    calculate_health_score,
    get_daily_action_count,
    record_daily_action,
)
from app.config import get_settings
import asyncio

settings = get_settings()
behavior = HumanBehaviorEngine()


@celery_app.task(name="app.agents.outreach_agent.process_queues")
def process_queues():
    """Process all pending outreach actions across all users."""
    asyncio.run(_process())


async def _process():
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.user import User
    from app.models.lead import Lead
    from app.models.outreach import OutreachAction
    from datetime import datetime

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        users = session.execute(select(User)).scalars().all()

        for user in users:
            # — Safety checks —
            if not behavior.is_working_hour(user.timezone):
                continue

            if behavior.should_take_offline_day():
                continue

            health = calculate_health_score(user.id)
            if health < 50:
                print(f"Health too low ({health}) for user {user.id}. Skipping.")
                continue

            budget = behavior.get_daily_budget(user.warmup_phase, health)

            # Get pending actions sorted by sequence day
            actions = session.execute(
                select(OutreachAction)
                .where(OutreachAction.user_id == user.id)
                .where(OutreachAction.outcome == "pending")
                .order_by(OutreachAction.sequence_day)
            ).scalars().all()

            for action in actions:
                # Check lead hasn't already replied
                lead = session.execute(
                    select(Lead).where(Lead.id == action.lead_id)
                ).scalar_one_or_none()

                if not lead or lead.outreach_status == "replied":
                    action.outcome = "skipped"
                    continue

                # Check budget
                action_budget_key = _action_to_budget_key(action.action_type)
                if action_budget_key:
                    daily_count = get_daily_action_count(user.id, action_budget_key)
                    max_budget = budget.get(action_budget_key, 0)
                    if daily_count >= max_budget:
                        continue

                # Execute with human-like delay
                await behavior.wait(action.action_type)

                try:
                    success = await _execute_action(action, lead, user)
                    if success:
                        action.outcome = "sent"
                        action.executed_at = datetime.utcnow()
                        if action_budget_key:
                            record_daily_action(user.id, action_budget_key)

                        # Update lead sequence day
                        lead.sequence_day = action.sequence_day
                        if action.action_type == "send_connection":
                            lead.outreach_status = "active"
                    else:
                        action.outcome = "failed"
                        action.error_message = "Execution returned False"

                except Exception as e:
                    action.outcome = "failed"
                    action.error_message = str(e)[:500]

                    # Emergency stop on CAPTCHA
                    if "captcha" in str(e).lower() or "challenge" in str(e).lower():
                        print(f"CAPTCHA detected for user {user.id}. Emergency stop.")
                        break

            session.commit()


async def _execute_action(action, lead, user) -> bool:
    """
    Execute a single LinkedIn action via Playwright.
    Routes to the correct action handler.
    Returns True on success.
    """
    from app.services.linkedin_actions import LinkedInActionExecutor
    from app.services.gmail_sender import send_outreach_email

    # ── Email goes through Gmail SMTP, not Playwright ──
    if action.action_type == "send_email":
        if not lead.email:
            return False
        return send_outreach_email(
            to_email=lead.email,
            subject=action.content[:55] if action.content else "Quick note",
            body=action.content or "",
            from_name=user.full_name,
        )

    # ── All LinkedIn actions go through Playwright ──
    executor = LinkedInActionExecutor(user_id=user.id)

    if action.action_type == "like_post":
        return await executor.like_post(lead.linkedin_url)

    elif action.action_type == "follow_company":
        # Get the company URL from the lead's company record
        from sqlalchemy import create_engine, select
        from sqlalchemy.orm import Session
        from app.models.company import TargetCompany

        engine = create_engine(settings.database_url_sync)
        with Session(engine) as s:
            company = s.execute(
                select(TargetCompany).where(TargetCompany.id == lead.company_id)
            ).scalar_one_or_none()
        if company and company.linkedin_company_url:
            return await executor.follow_company(company.linkedin_company_url)
        return False

    elif action.action_type == "comment_post":
        comment_text = action.content or "Great insight — thanks for sharing this."
        return await executor.comment_on_post(lead.linkedin_url, comment_text)

    elif action.action_type == "send_connection":
        # No note by default = higher acceptance rate
        return await executor.send_connection_request(lead.linkedin_url, note=None)

    elif action.action_type == "send_message":
        if not action.content:
            return False
        return await executor.send_message(lead.linkedin_url, action.content)

    else:
        print(f"Unknown action type: {action.action_type}")
        return False


def _action_to_budget_key(action_type: str) -> str | None:
    """Map action types to budget keys."""
    mapping = {
        "send_connection": "connections",
        "send_message": "messages",
        "profile_view": "profile_views",
        "like_post": "profile_views",
        "follow_company": "profile_views",
        "comment_post": "profile_views",
    }
    return mapping.get(action_type)
