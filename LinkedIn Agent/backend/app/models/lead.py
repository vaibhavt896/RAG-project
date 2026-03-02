"""
Lead model — individual contacts discovered at target companies.
"""

from sqlalchemy import String, Float, Integer, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid

from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    linkedin_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), default="")
    last_name: Mapped[str] = mapped_column(String(100), default="")
    title: Mapped[str] = mapped_column(String(300), default="")
    headline: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    persona_type: Mapped[str] = mapped_column(
        String(30), default="unknown"
    )  # recruiter / hiring_mgr / hrbp / exec
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    recent_posts: Mapped[list] = mapped_column(JSON, default=list)
    outreach_status: Mapped[str] = mapped_column(
        String(30), default="queued"
    )  # queued / active / paused / replied / completed
    sequence_day: Mapped[int] = mapped_column(Integer, default=0)
    connected: Mapped[bool] = mapped_column(default=False)
    connected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    replied_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
