"""Campaign schemas."""
from pydantic import BaseModel
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str
    description: str = ""
    target_role: str = ""
    target_titles: list[str] = []
    settings: dict = {}


class CampaignUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    settings: dict | None = None


class CampaignResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    target_role: str
    target_titles: list[str]
    status: str
    total_leads: int
    leads_contacted: int
    replies_received: int
    connections_accepted: int
    avg_response_rate: float
    settings: dict
    started_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
