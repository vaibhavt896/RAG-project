"""User schemas."""
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    full_name: str = ""
    target_role: str = ""
    timezone: str = "America/New_York"
    target_locations: dict = {}


class UserUpdate(BaseModel):
    full_name: str | None = None
    target_role: str | None = None
    timezone: str | None = None
    target_locations: dict | None = None
    linkedin_profile_url: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    linkedin_profile_url: str | None
    target_role: str
    target_locations: dict
    timezone: str
    warmup_phase: int
    resume_uploaded: bool
    created_at: datetime

    model_config = {"from_attributes": True}
