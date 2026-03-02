"""Lead schemas."""
from pydantic import BaseModel
from datetime import datetime


class LeadCreate(BaseModel):
    company_id: str
    linkedin_url: str
    full_name: str
    first_name: str = ""
    last_name: str = ""
    title: str = ""
    persona_type: str = "unknown"


class LeadUpdate(BaseModel):
    title: str | None = None
    persona_type: str | None = None
    outreach_status: str | None = None
    email: str | None = None


class LeadResponse(BaseModel):
    id: str
    user_id: str
    company_id: str
    linkedin_url: str
    full_name: str
    first_name: str
    last_name: str
    title: str
    headline: str
    location: str
    persona_type: str
    email: str | None
    score: float
    recent_posts: list
    outreach_status: str
    sequence_day: int
    connected: bool
    connected_at: datetime | None
    replied_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadScoreResponse(BaseModel):
    lead_id: str
    score: float
    breakdown: dict
