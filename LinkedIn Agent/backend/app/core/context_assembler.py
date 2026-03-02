"""
Context Assembler — gathers all relevant context for AI message generation.
Combines resume RAG results, company signals, and lead data.
"""

from app.core.vector_store import search_resume
from app.services.funding_signals import get_company_signals


async def assemble_context(
    user_id: str, lead: dict, job_description: str = ""
) -> dict:
    """
    Build a complete context package for Gemini message generation.
    Pulls from:
      - User's resume embeddings (RAG)
      - Company funding/hiring signals
      - Lead's recent posts and profile data
    """
    search_query = job_description or f"{lead.get('title', '')} {lead.get('company_name', '')}"
    resume_chunks = search_resume(user_id, search_query, top_k=3)
    recent_posts = lead.get("recent_posts", [])
    signal = await get_company_signals(lead.get("company_name", ""))

    return {
        "relevant_resume_chunks": resume_chunks,
        "recipient_name": lead.get("full_name", "").split()[0] if lead.get("full_name") else "",
        "recipient_title": lead.get("title", ""),
        "company_name": lead.get("company_name", ""),
        "recent_posts": recent_posts,
        "company_news": signal.get("detail", ""),
        "signal_type": signal.get("type", "general interest"),
        "signal_detail": signal.get("detail", ""),
        "job_title": lead.get("target_job_title", ""),
    }
