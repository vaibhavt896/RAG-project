"""
AI Writer Agent — generates personalized outreach messages using Gemini + RAG context.
"""

from app.celery_app import celery_app
from app.core.context_assembler import assemble_context
from app.services.gemini import generate_outreach_messages
from app.config import get_settings
import asyncio

settings = get_settings()


@celery_app.task(name="app.agents.ai_writer_agent.generate_messages")
def generate_messages(lead_id: str, user_id: str):
    """Generate all outreach messages for a lead."""
    asyncio.run(_generate(lead_id, user_id))


async def _generate(lead_id: str, user_id: str):
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.lead import Lead
    from app.models.user import User
    from app.models.company import TargetCompany

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        lead = session.execute(
            select(Lead).where(Lead.id == lead_id)
        ).scalar_one_or_none()
        user = session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

        if not lead or not user:
            return

        company = session.execute(
            select(TargetCompany).where(TargetCompany.id == lead.company_id)
        ).scalar_one_or_none()

        # Assemble full context
        lead_dict = {
            "full_name": lead.full_name,
            "title": lead.title,
            "company_name": company.company_name if company else "",
            "recent_posts": lead.recent_posts or [],
            "target_job_title": user.target_role,
        }

        context = await assemble_context(user_id, lead_dict)

        # Generate messages
        messages = await generate_outreach_messages(
            user_name=user.full_name,
            target_role=user.target_role,
            relevant_resume_chunks=context["relevant_resume_chunks"],
            recipient_name=context["recipient_name"],
            recipient_title=context["recipient_title"],
            company_name=context["company_name"],
            recent_posts=context["recent_posts"],
            company_news=context["company_news"],
            signal_type=context["signal_type"],
            signal_detail=context["signal_detail"],
            job_title=context["job_title"],
        )

        # Store generated messages as pending outreach actions
        from app.models.outreach import OutreachAction

        sequence_map = {
            "connection_note": (6, "send_connection"),
            "message_day9": (9, "send_message"),
            "message_day14": (14, "send_message"),
            "email_body": (21, "send_email"),
        }

        for key, (day, action_type) in sequence_map.items():
            content = messages.get(key, "")
            if content:
                action = OutreachAction(
                    lead_id=lead_id,
                    user_id=user_id,
                    action_type=action_type,
                    sequence_day=day,
                    content=content,
                    outcome="pending",
                )
                session.add(action)

        session.commit()
