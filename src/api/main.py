"""
Production-ready FastAPI application.
"""
import time
import os
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .schemas import QueryRequest, QueryResponse, IngestRequest, IngestResponse, CitationResponse
from ..ingestion.loader import load_document
from ..ingestion.chunker import create_chunks
from ..retrieval.hybrid import HybridRetriever
from ..retrieval.reranker import get_reranker
from ..citation.tracker import build_citation_map, extract_citations_from_response
from ..generation.llm import generate_answer, expand_query
from ..retrieval.edge_cases import detect_unanswerable, detect_sensitive_query, handle_long_document_edge_case


# Global instances (initialized once at startup)
retriever = None
reranker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever, reranker
    retriever = HybridRetriever()
    reranker = get_reranker()
    yield
    # Cleanup on shutdown


app = FastAPI(
    title="Production RAG API",
    description="Hybrid search RAG with citation tracking and evaluation — powered by Google Gemini",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest):
    """Ingest a document from file path or URL."""
    try:
        doc = load_document(request.source)
        chunks = create_chunks(doc)
        retriever.add_chunks(chunks)
        return IngestResponse(
            doc_id=doc.doc_id,
            chunks_created=len(chunks),
            source=request.source,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system and get a cited answer."""
    try:
        start_time = time.time()

        # Edge case: sensitive query
        if detect_sensitive_query(request.question):
            raise HTTPException(
                status_code=400,
                detail="This query has been flagged for human review."
            )

        # Query expansion for better recall
        expanded_queries = await _expand_queries(request.question)

        # Hybrid retrieval (search with original + expanded queries)
        all_results = retriever.search(request.question, top_k=20)
        for eq in expanded_queries[:2]:  # Use top 2 expansions
            eq_results = retriever.search(eq, top_k=10)
            all_results.extend(eq_results)

        # Deduplicate
        seen_ids = set()
        deduped = []
        for r in all_results:
            if r["chunk_id"] not in seen_ids:
                seen_ids.add(r["chunk_id"])
                deduped.append(r)

        # Re-rank
        reranked = reranker.rerank(request.question, deduped, top_k=request.top_k)

        # Edge case: unanswerable
        if detect_unanswerable(request.question, reranked):
            return QueryResponse(
                question=request.question,
                answer="I couldn't find relevant information in the documents to answer this question. Please check if the relevant documents have been ingested.",
                citations=[],
                latency_ms=int((time.time() - start_time) * 1000),
                model_used="none",
                tokens_used=0,
            )

        # Handle context length edge case
        reranked = handle_long_document_edge_case(reranked)

        # Build citation map
        citation_map = build_citation_map(reranked)

        # Generate answer
        gen_result = generate_answer(
            question=request.question,
            context=citation_map.context_text,
            model=request.model,
        )

        # Extract which citations were used
        used_refs = extract_citations_from_response(gen_result["answer"])
        for citation in citation_map.citations:
            citation.used_in_response = citation.ref_number in used_refs

        # Build response citations (only used ones)
        response_citations = [
            CitationResponse(
                ref_number=c.ref_number,
                title=c.title,
                source=c.source,
                page=c.page,
                excerpt=c.excerpt,
            )
            for c in citation_map.citations
            if c.used_in_response
        ]

        return QueryResponse(
            question=request.question,
            answer=gen_result["answer"],
            citations=response_citations,
            latency_ms=int((time.time() - start_time) * 1000),
            model_used=gen_result["model"],
            tokens_used=gen_result["tokens_used"],
        )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}\n\nTraceback:\n{error_details}")


async def _expand_queries(question: str) -> list[str]:
    try:
        return expand_query(question)
    except Exception:
        return []


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/stats")
async def stats():
    return {
        "vector_store_size": retriever.vector_store.collection.count(),
        "bm25_index_size": len(retriever.bm25_store.chunk_map),
    }
