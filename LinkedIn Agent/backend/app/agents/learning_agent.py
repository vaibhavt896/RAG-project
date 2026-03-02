"""
Learning Agent — weekly A/B optimization using ChromaDB message outcomes.
Runs every Sunday at 2AM via Celery Beat.
"""

from app.celery_app import celery_app
from app.core.vector_store import get_similar_winning_messages, store_message_outcome
from app.config import get_settings

settings = get_settings()


@celery_app.task(name="app.agents.learning_agent.optimize")
def optimize():
    """Weekly optimization run — analyzes what messages worked best."""
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.outreach import OutreachAction
    from app.models.lead import Lead

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        # Get all sent messages from the past week
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)

        actions = session.execute(
            select(OutreachAction).where(
                OutreachAction.outcome == "sent",
                OutreachAction.executed_at >= week_ago,
                OutreachAction.action_type == "send_message",
            )
        ).scalars().all()

        for action in actions:
            if not action.content:
                continue

            # Check if the lead replied
            lead = session.execute(
                select(Lead).where(Lead.id == action.lead_id)
            ).scalar_one_or_none()

            got_reply = lead is not None and lead.outreach_status == "replied"

            # Store the outcome in ChromaDB for future similarity matching
            store_message_outcome(
                message_id=action.id,
                message_text=action.content,
                got_reply=got_reply,
            )

        print(f"Learning agent processed {len(actions)} messages")


@celery_app.task(name="app.agents.learning_agent.get_winning_patterns")
def get_winning_patterns(sample_message: str) -> dict:
    """Find similar messages that got replies — for message improvement."""
    winners = get_similar_winning_messages(sample_message, top_k=5)
    return {
        "similar_winners": winners,
        "count": len(winners),
    }
