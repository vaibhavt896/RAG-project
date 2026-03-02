"""
Application configuration — loads from .env file.
All services use free tiers only.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────
    app_name: str = "LinkedIn Intelligence Agent"
    debug: bool = True
    timezone: str = "America/New_York"

    # ── Database ─────────────────────────────────
    database_url: str = "postgresql+asyncpg://liagent:liagent@localhost:5432/liagent"
    database_url_sync: str = "postgresql://liagent:liagent@localhost:5432/liagent"

    # ── Redis ────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── AI ───────────────────────────────────────
    gemini_api_key: str = ""

    # ── LinkedIn (actions only) ──────────────────
    linkedin_email: str = ""
    linkedin_password: str = ""

    # ── Email Finders (free tiers) ───────────────
    apollo_api_key: str = ""
    hunter_api_key: str = ""
    skrapp_api_key: str = ""

    # ── Gmail SMTP ───────────────────────────────
    gmail_address: str = ""
    gmail_app_password: str = ""

    # ── Security ─────────────────────────────────
    encryption_key: str = ""

    # ── Clerk (optional) ─────────────────────────
    clerk_secret_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
