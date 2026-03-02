"""
Analytics API — funnel metrics, rates, recent activity feed.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.lead import Lead
from app.models.outreach import OutreachAction
from app.models.company import TargetCompany
from app.schemas.outreach import OutreachActionResponse

router = APIRouter()


@router.get("/funnel/{user_id}")
async def get_funnel(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get the full outreach funnel metrics."""
    total = await db.execute(
        select(func.count()).select_from(Lead).where(Lead.user_id == user_id)
    )
    total_leads = total.scalar() or 0

    contacted = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.user_id == user_id,
            Lead.outreach_status.in_(["active", "replied", "completed"]),
        )
    )
    contacted_count = contacted.scalar() or 0

    connected = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.user_id == user_id, Lead.connected == True
        )
    )
    connected_count = connected.scalar() or 0

    replied = await db.execute(
        select(func.count()).select_from(Lead).where(
            Lead.user_id == user_id, Lead.outreach_status == "replied"
        )
    )
    replied_count = replied.scalar() or 0

    return {
        "total_leads": total_leads,
        "contacted": contacted_count,
        "connected": connected_count,
        "replied": replied_count,
        "connection_rate": round(
            connected_count / max(contacted_count, 1) * 100, 1
        ),
        "reply_rate": round(
            replied_count / max(contacted_count, 1) * 100, 1
        ),
    }


@router.get("/activity/{user_id}", response_model=list[OutreachActionResponse])
async def get_recent_activity(
    user_id: str, limit: int = 20, db: AsyncSession = Depends(get_db)
):
    """Get recent outreach actions for the activity feed."""
    result = await db.execute(
        select(OutreachAction)
        .where(OutreachAction.user_id == user_id)
        .order_by(desc(OutreachAction.created_at))
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/company-stats/{user_id}")
async def get_company_stats(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get lead/signal stats per company."""
    companies = await db.execute(
        select(TargetCompany).where(TargetCompany.user_id == user_id)
    )
    stats = []
    for company in companies.scalars().all():
        lead_count = await db.execute(
            select(func.count()).select_from(Lead).where(
                Lead.company_id == company.id
            )
        )
        replied_count = await db.execute(
            select(func.count()).select_from(Lead).where(
                Lead.company_id == company.id,
                Lead.outreach_status == "replied",
            )
        )
        stats.append({
            "company_id": company.id,
            "company_name": company.company_name,
            "signal_score": company.signal_score,
            "signal_type": company.signal_type,
            "total_leads": lead_count.scalar() or 0,
            "replies": replied_count.scalar() or 0,
            "priority": company.priority,
        })

    return sorted(stats, key=lambda x: x["signal_score"], reverse=True)
