"""
Companies API — manage target companies + trigger signal scans.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.company import TargetCompany
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter()


@router.get("/", response_model=list[CompanyResponse])
async def list_companies(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TargetCompany)
        .where(TargetCompany.user_id == user_id)
        .order_by(TargetCompany.signal_score.desc())
    )
    return result.scalars().all()


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TargetCompany).where(TargetCompany.id == company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/", response_model=CompanyResponse)
async def create_company(
    user_id: str, data: CompanyCreate, db: AsyncSession = Depends(get_db)
):
    company = TargetCompany(
        user_id=user_id,
        company_name=data.company_name,
        linkedin_company_url=data.linkedin_company_url,
        domain=data.domain,
        priority=data.priority,
    )
    db.add(company)
    await db.flush()
    await db.refresh(company)
    return company


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str, data: CompanyUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TargetCompany).where(TargetCompany.id == company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await db.flush()
    await db.refresh(company)
    return company


@router.post("/{company_id}/scan")
async def scan_company_signals(company_id: str, db: AsyncSession = Depends(get_db)):
    """Trigger an on-demand signal scan for a company."""
    result = await db.execute(
        select(TargetCompany).where(TargetCompany.id == company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    from app.agents.signal_agent import scan_single_company
    scan_single_company.delay(company_id)
    return {"message": f"Signal scan queued for {company.company_name}"}


@router.post("/{company_id}/discover-leads")
async def discover_company_leads(
    company_id: str, user_id: str, db: AsyncSession = Depends(get_db)
):
    """Trigger lead discovery for a company."""
    result = await db.execute(
        select(TargetCompany).where(TargetCompany.id == company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    from app.agents.scraper_agent import discover_leads
    discover_leads.delay(company_id, user_id)
    return {"message": f"Lead discovery queued for {company.company_name}"}


@router.delete("/{company_id}")
async def delete_company(company_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TargetCompany).where(TargetCompany.id == company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    await db.delete(company)
    return {"message": "Company deleted"}
