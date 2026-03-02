"""
Leads API — manage individual leads, scoring, email lookup.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.lead import Lead
from app.models.company import TargetCompany
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadScoreResponse
from app.core.lead_scorer import score_lead

router = APIRouter()


@router.get("/", response_model=list[LeadResponse])
async def list_leads(
    user_id: str,
    company_id: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Lead).where(Lead.user_id == user_id)
    if company_id:
        query = query.where(Lead.company_id == company_id)
    if status:
        query = query.where(Lead.outreach_status == status)
    query = query.order_by(Lead.score.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/", response_model=LeadResponse)
async def create_lead(
    user_id: str, data: LeadCreate, db: AsyncSession = Depends(get_db)
):
    lead = Lead(
        user_id=user_id,
        company_id=data.company_id,
        linkedin_url=data.linkedin_url,
        full_name=data.full_name,
        first_name=data.first_name,
        last_name=data.last_name,
        title=data.title,
        persona_type=data.persona_type,
    )
    db.add(lead)
    await db.flush()
    await db.refresh(lead)
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str, data: LeadUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    await db.flush()
    await db.refresh(lead)
    return lead


@router.post("/{lead_id}/score", response_model=LeadScoreResponse)
async def score_single_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Recalculate a lead's score."""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    company = await db.execute(
        select(TargetCompany).where(TargetCompany.id == lead.company_id)
    )
    company = company.scalar_one_or_none()
    company_signal = company.signal_score if company else 0

    lead_data = {
        "title": lead.title,
        "recent_posts": lead.recent_posts or [],
        "email": lead.email,
    }
    result = score_lead(lead_data, "", company_signal)
    lead.score = result["score"]
    await db.flush()

    return LeadScoreResponse(
        lead_id=lead_id,
        score=result["score"],
        breakdown=result["breakdown"],
    )


@router.post("/{lead_id}/find-email")
async def find_lead_email(lead_id: str, db: AsyncSession = Depends(get_db)):
    """Try to find an email for a lead."""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead.email:
        return {"email": lead.email, "source": "cached"}

    company = await db.execute(
        select(TargetCompany).where(TargetCompany.id == lead.company_id)
    )
    company = company.scalar_one_or_none()
    domain = company.domain if company else ""

    if not domain or not lead.first_name or not lead.last_name:
        return {"email": None, "message": "Missing name or company domain"}

    from app.services.email_finder import find_email
    email = await find_email(lead.first_name, lead.last_name, domain)

    if email:
        lead.email = email
        await db.flush()

    return {"email": email, "source": "lookup"}


@router.delete("/{lead_id}")
async def delete_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    await db.delete(lead)
    return {"message": "Lead deleted"}
