"""Company schemas."""
from pydantic import BaseModel
from datetime import datetime


class CompanyCreate(BaseModel):
    company_name: str
    linkedin_company_url: str = ""
    domain: str = ""
    priority: str = "medium"


class CompanyUpdate(BaseModel):
    company_name: str | None = None
    linkedin_company_url: str | None = None
    domain: str | None = None
    priority: str | None = None
    status: str | None = None


class CompanyResponse(BaseModel):
    id: str
    user_id: str
    company_name: str
    linkedin_company_url: str
    domain: str
    signal_score: float
    signal_type: str | None
    signal_detail: str | None
    employee_count: int | None
    open_roles_count: int
    priority: str
    status: str
    last_scanned_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SignalResponse(BaseModel):
    type: str
    detail: str
    score: float
