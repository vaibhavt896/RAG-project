"""
Observability — trace every LLM call with Langfuse.
Tracks: input/output, token usage, latency, evaluation scores.

Use Langfuse free tier: cloud.langfuse.com
"""
from langfuse import Langfuse
import os
from functools import wraps
import time

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)


def trace_rag_query(func):
    """Decorator to trace entire RAG pipeline execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        trace = langfuse.trace(name="rag_query")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            trace.update(
                output=result.get("answer", ""),
                metadata={
                    "latency_ms": int((time.time() - start) * 1000),
                    "tokens_used": result.get("tokens_used", 0),
                    "citations_count": len(result.get("citations", [])),
                }
            )
            return result
        except Exception as e:
            trace.update(output=str(e), metadata={"error": True})
            raise
    return wrapper
