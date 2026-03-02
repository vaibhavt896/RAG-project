from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    model: Optional[str] = None


class CitationResponse(BaseModel):
    ref_number: int
    title: str
    source: str
    page: Optional[int]
    excerpt: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: list[CitationResponse]
    faithfulness_score: Optional[float] = None
    latency_ms: int
    model_used: str
    tokens_used: int


class IngestRequest(BaseModel):
    source: str  # file path or URL


class IngestResponse(BaseModel):
    doc_id: str
    chunks_created: int
    source: str
