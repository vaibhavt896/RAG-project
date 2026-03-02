"""
Analytics Agent — CRM, reply detection, funnel tracking.
Checks LinkedIn inbox for replies every 30 minutes.
"""

from app.celery_app import celery_app
from app.core.health_scorer import increment_stat
from app.config import get_settings
import asyncio
from datetime import datetime

settings = get_settings()


@celery_app.task(name="app.agents.analytics_agent.check_inbox")
def check_inbox():
    """Check all user inboxes for new replies. Runs every 30 minutes."""
    asyncio.run(_check_all_inboxes())


async def _check_all_inboxes():
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.user import User

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        users = session.execute(select(User)).scalars().all()
        for user in users:
            if user.linkedin_cookie:
                try:
                    await _check_user_inbox(user.id, session)
                except Exception as e:
                    print(f"Inbox check failed for {user.id}: {e}")


async def _check_user_inbox(user_id: str, session):
    """
    Check a user's LinkedIn messaging inbox for new replies from tracked leads.
    Uses LinkedInActionExecutor to scan the actual inbox.
    """
    from sqlalchemy import select
    from app.models.lead import Lead
    from app.services.linkedin_actions import LinkedInActionExecutor

    # Get all leads we're tracking
    leads = session.execute(
        select(Lead).where(
            Lead.user_id == user_id,
            Lead.outreach_status.in_(["active", "queued"]),
        )
    ).scalars().all()

    if not leads:
        return

    lead_names = [l.full_name for l in leads if l.full_name]
    lead_name_map = {l.full_name.lower(): l for l in leads if l.full_name}

    executor = LinkedInActionExecutor(user_id=user_id)
    replies = await executor.check_inbox_for_replies(lead_names)

    for reply in replies:
        matched_name = reply.get("lead_name", "").lower()
        lead = lead_name_map.get(matched_name)

        if lead and lead.outreach_status != "replied":
            lead.outreach_status = "replied"
            lead.replied_at = datetime.utcnow()
            increment_stat(user_id, "messages_replied_30d")
            print(
                f"Reply detected from {reply['lead_name']}: "
                f"{reply.get('snippet', '')[:80]}"
            )

    if replies:
        session.commit()


@celery_app.task(name="app.agents.analytics_agent.record_reply")
def record_reply(lead_id: str, user_id: str):
    """Record when a lead replies — immediately pause automation."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.lead import Lead

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        lead = session.execute(
            select(Lead).where(Lead.id == lead_id)
        ).scalar_one_or_none()

        if lead:
            lead.outreach_status = "replied"
            lead.replied_at = datetime.utcnow()
            session.commit()

            # Update health metrics
            increment_stat(user_id, "messages_replied_30d")


@celery_app.task(name="app.agents.analytics_agent.get_funnel_metrics")
def get_funnel_metrics(user_id: str) -> dict:
    """Get funnel metrics for the analytics dashboard."""
    from sqlalchemy import create_engine, select, func
    from sqlalchemy.orm import Session
    from app.models.lead import Lead
    from app.models.outreach import OutreachAction

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        total_leads = session.execute(
            select(func.count()).where(Lead.user_id == user_id)
        ).scalar() or 0

        contacted = session.execute(
            select(func.count()).where(
                Lead.user_id == user_id,
                Lead.outreach_status.in_(["active", "replied", "completed"]),
            )
        ).scalar() or 0

        connected = session.execute(
            select(func.count()).where(
                Lead.user_id == user_id, Lead.connected == True
            )
        ).scalar() or 0

        replied = session.execute(
            select(func.count()).where(
                Lead.user_id == user_id, Lead.outreach_status == "replied"
            )
        ).scalar() or 0

        actions_sent = session.execute(
            select(func.count()).where(
                OutreachAction.user_id == user_id,
                OutreachAction.outcome == "sent",
            )
        ).scalar() or 0

        return {
            "total_leads": total_leads,
            "contacted": contacted,
            "connected": connected,
            "replied": replied,
            "actions_sent": actions_sent,
            "connection_rate": round(connected / max(contacted, 1) * 100, 1),
            "reply_rate": round(replied / max(contacted, 1) * 100, 1),
        }
