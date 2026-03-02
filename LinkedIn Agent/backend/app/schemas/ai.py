"""AI message generation schemas."""
from pydantic import BaseModel


class MessageGenerateRequest(BaseModel):
    lead_id: str
    user_id: str
    job_description: str = ""


class MessagePreviewResponse(BaseModel):
    connection_note: str
    message_day9: str
    message_day14: str
    email_subject: str
    email_body: str


class ResumeUploadResponse(BaseModel):
    user_id: str
    chunks_stored: int
    message: str
