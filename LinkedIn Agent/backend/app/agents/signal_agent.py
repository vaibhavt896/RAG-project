"""
Signal Agent — scans target companies for funding, hiring, and job posting signals.
Runs every 6 hours via Celery Beat.
"""

from app.celery_app import celery_app
from app.services.funding_signals import get_company_signals
from app.config import get_settings
import asyncio

settings = get_settings()


@celery_app.task(name="app.agents.signal_agent.scan_all_companies")
def scan_all_companies():
    """Scan all active target companies for new signals."""
    asyncio.run(_scan_all())


async def _scan_all():
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.company import TargetCompany
    from datetime import datetime

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        companies = session.execute(
            select(TargetCompany).where(TargetCompany.status != "archived")
        ).scalars().all()

        for company in companies:
            try:
                signal = await get_company_signals(company.company_name)
                company.signal_score = signal.get("score", 0)
                company.signal_type = signal.get("type", "none")
                company.signal_detail = signal.get("detail", "")

                # Auto-upgrade priority based on signal
                if signal.get("score", 0) >= 80:
                    company.priority = "high"
                elif signal.get("score", 0) >= 60:
                    company.priority = "medium"

                company.last_scanned_at = datetime.utcnow()
                session.commit()
            except Exception as e:
                print(f"Signal scan failed for {company.company_name}: {e}")
                continue


@celery_app.task(name="app.agents.signal_agent.scan_single_company")
def scan_single_company(company_id: str):
    """Scan a single company for signals (on-demand trigger)."""
    asyncio.run(_scan_single(company_id))


async def _scan_single(company_id: str):
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.company import TargetCompany
    from datetime import datetime

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        company = session.execute(
            select(TargetCompany).where(TargetCompany.id == company_id)
        ).scalar_one_or_none()

        if not company:
            return

        signal = await get_company_signals(company.company_name)
        company.signal_score = signal.get("score", 0)
        company.signal_type = signal.get("type", "none")
        company.signal_detail = signal.get("detail", "")
        company.last_scanned_at = datetime.utcnow()
        session.commit()
