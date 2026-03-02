"""
AI API — message preview, generation, and resume upload.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.lead import Lead
from app.models.user import User
from app.models.company import TargetCompany
from app.schemas.ai import MessageGenerateRequest, MessagePreviewResponse, ResumeUploadResponse

router = APIRouter()


@router.post("/generate-messages", response_model=MessagePreviewResponse)
async def generate_messages(
    data: MessageGenerateRequest, db: AsyncSession = Depends(get_db)
):
    """Generate all 5 outreach messages for a lead."""
    result = await db.execute(select(Lead).where(Lead.id == data.lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    user_result = await db.execute(select(User).where(User.id == data.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    company_result = await db.execute(
        select(TargetCompany).where(TargetCompany.id == lead.company_id)
    )
    company = company_result.scalar_one_or_none()

    from app.core.context_assembler import assemble_context
    from app.services.gemini import generate_outreach_messages

    lead_dict = {
        "full_name": lead.full_name,
        "title": lead.title,
        "company_name": company.company_name if company else "",
        "recent_posts": lead.recent_posts or [],
        "target_job_title": user.target_role,
    }

    context = await assemble_context(data.user_id, lead_dict, data.job_description)

    messages = await generate_outreach_messages(
        user_name=user.full_name,
        target_role=user.target_role,
        relevant_resume_chunks=context["relevant_resume_chunks"],
        recipient_name=context["recipient_name"],
        recipient_title=context["recipient_title"],
        company_name=context["company_name"],
        recent_posts=context["recent_posts"],
        company_news=context["company_news"],
        signal_type=context["signal_type"],
        signal_detail=context["signal_detail"],
        job_title=context["job_title"],
    )

    return MessagePreviewResponse(**messages)


@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(
    user_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a resume and store it as embeddings for RAG."""
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    # Split into chunks (~500 chars each)
    chunks = _chunk_text(text, chunk_size=500, overlap=50)

    if not chunks:
        raise HTTPException(status_code=400, detail="Resume appears empty")

    from app.core.vector_store import store_resume_chunks
    store_resume_chunks(user_id, chunks)

    user.resume_uploaded = True
    await db.flush()

    return ResumeUploadResponse(
        user_id=user_id,
        chunks_stored=len(chunks),
        message=f"Resume stored as {len(chunks)} chunks",
    )


@router.post("/queue-messages")
async def queue_messages(data: MessageGenerateRequest):
    """Queue message generation as a background Celery task."""
    from app.agents.ai_writer_agent import generate_messages
    generate_messages.delay(data.lead_id, data.user_id)
    return {"message": "Message generation queued"}


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + chunk_size // 4]  # ~4 chars per word avg
        chunk = " ".join(chunk_words)
        if len(chunk.strip()) > 20:
            chunks.append(chunk.strip())
        i += max(1, len(chunk_words) - overlap // 4)
    return chunks
