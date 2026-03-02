"""
LinkedIn Intelligence Agent — FastAPI Application
Signal-first LinkedIn automation with 7 specialized AI agents.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import campaigns, companies, leads, ai, safety, analytics

app = FastAPI(
    title="LinkedIn Intelligence Agent",
    description="Signal-first LinkedIn automation with 7 AI agents, "
                "Gemini personalization, and ChromaDB vector storage.",
    version="2.0.0",
)

# ── CORS ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(leads.router,     prefix="/api/leads",     tags=["Leads"])
app.include_router(ai.router,        prefix="/api/ai",        tags=["AI"])
app.include_router(safety.router,    prefix="/api/safety",    tags=["Safety"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "LinkedIn Intelligence Agent"}
