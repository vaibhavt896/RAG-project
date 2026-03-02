"""
Celery app with beat schedule for all automated agents.
"""

from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "linkedin_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.agents.signal_agent",
        "app.agents.scraper_agent",
        "app.agents.ai_writer_agent",
        "app.agents.outreach_agent",
        "app.agents.safety_agent",
        "app.agents.analytics_agent",
        "app.agents.learning_agent",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=settings.timezone,
    enable_utc=True,
    worker_max_tasks_per_child=50,
    task_soft_time_limit=300,
    task_time_limit=600,
)

# ── Scheduled Tasks ──────────────────────────────────
celery_app.conf.beat_schedule = {
    # Scan all companies for funding / hiring signals
    "signal-scan": {
        "task": "app.agents.signal_agent.scan_all_companies",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    # Process outreach queues (like, connect, message)
    "outreach-queue": {
        "task": "app.agents.outreach_agent.process_queues",
        "schedule": crontab(minute="*/15"),
    },
    # Check LinkedIn inbox for replies
    "check-inbox": {
        "task": "app.agents.analytics_agent.check_inbox",
        "schedule": crontab(minute="*/30"),
    },
    # Weekly A/B optimization run
    "learning-run": {
        "task": "app.agents.learning_agent.optimize",
        "schedule": crontab(day_of_week="sun", hour=2),
    },
}
