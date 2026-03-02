"""
Scraper Agent — discovers leads at target companies via public LinkedIn scraping.
No login. Triggered on-demand per company.
"""

from app.celery_app import celery_app
from app.services.linkedin_public import LinkedInPublicScraper
from app.services.email_finder import find_email
from app.core.lead_scorer import score_lead
from app.config import get_settings
import asyncio

settings = get_settings()
scraper = LinkedInPublicScraper()


@celery_app.task(name="app.agents.scraper_agent.discover_leads")
def discover_leads(company_id: str, user_id: str):
    """Discover TA/recruiting leads at a target company."""
    asyncio.run(_discover(company_id, user_id))


async def _discover(company_id: str, user_id: str):
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.company import TargetCompany
    from app.models.lead import Lead

    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        company = session.execute(
            select(TargetCompany).where(TargetCompany.id == company_id)
        ).scalar_one_or_none()

        if not company:
            return

        # Scrape employees with TA title keywords
        employees = await scraper.get_company_employees(
            company.linkedin_company_url
        )

        for emp in employees:
            # Skip if lead already exists
            existing = session.execute(
                select(Lead).where(Lead.linkedin_url == emp.get("url", ""))
            ).scalar_one_or_none()

            if existing:
                continue

            # Parse name
            full_name = emp.get("name", "").strip()
            name_parts = full_name.split() if full_name else []
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[-1] if len(name_parts) > 1 else ""

            # Determine persona type
            title_lower = emp.get("title", "").lower()
            if any(kw in title_lower for kw in ["recruiter", "talent", "sourcer"]):
                persona_type = "recruiter"
            elif any(kw in title_lower for kw in ["hr", "people", "hrbp"]):
                persona_type = "hrbp"
            elif any(kw in title_lower for kw in ["manager", "director", "vp", "head"]):
                persona_type = "hiring_mgr"
            else:
                persona_type = "unknown"

            # Try to find email
            email = None
            if first_name and last_name and company.domain:
                try:
                    email = await find_email(first_name, last_name, company.domain)
                except Exception:
                    pass

            # Get recent posts
            posts = []
            if emp.get("url"):
                try:
                    posts = await scraper.get_recent_posts(emp["url"])
                except Exception:
                    pass

            # Score the lead
            lead_data = {
                "title": emp.get("title", ""),
                "recent_posts": posts,
                "email": email,
            }
            score_result = score_lead(
                lead_data, "", company.signal_score
            )

            # Create lead
            lead = Lead(
                user_id=user_id,
                company_id=company_id,
                linkedin_url=emp.get("url", ""),
                full_name=full_name,
                first_name=first_name,
                last_name=last_name,
                title=emp.get("title", ""),
                persona_type=persona_type,
                email=email,
                score=score_result["score"],
                recent_posts=posts,
                outreach_status="queued" if score_result["auto_contact"] else "manual_review",
            )
            session.add(lead)

        session.commit()
