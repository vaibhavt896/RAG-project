"""Outreach action schemas."""
from pydantic import BaseModel
from datetime import datetime


class OutreachActionResponse(BaseModel):
    id: str
    lead_id: str
    user_id: str
    campaign_id: str | None
    action_type: str
    sequence_day: int
    content: str | None
    outcome: str
    error_message: str | None
    scheduled_at: datetime | None
    executed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
