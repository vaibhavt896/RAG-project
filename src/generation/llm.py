from __future__ import annotations

"""
LLM interface using Google Gemini with retry logic and token counting.
"""
import os
import time
import json
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from .prompts import RAG_SYSTEM_PROMPT, RAG_USER_TEMPLATE, QUERY_EXPANSION_PROMPT


def _configure_genai():
    """Lazy Gemini configuration — only runs when actually needed."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_answer(
    question: str,
    context: str,
    model: str = None,
    temperature: float = 0.1,  # Low temp for factual accuracy
) -> dict:
    """
    Generate an answer with citations using Gemini.
    Returns: {"answer": str, "model": str, "tokens_used": int, "latency_ms": int}
    """
    _configure_genai()
    model_name = model or os.getenv("LLM_MODEL", "gemini-2.0-flash")
    gemini_model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=RAG_SYSTEM_PROMPT,
    )

    user_message = RAG_USER_TEMPLATE.format(context=context, question=question)

    start = time.time()
    response = gemini_model.generate_content(
        user_message,
        generation_config=genai.GenerationConfig(temperature=temperature),
    )
    latency_ms = int((time.time() - start) * 1000)

    return {
        "answer": response.text,
        "model": model_name,
        "tokens_used": response.usage_metadata.total_token_count,
        "prompt_tokens": response.usage_metadata.prompt_token_count,
        "completion_tokens": response.usage_metadata.candidates_token_count,
        "latency_ms": latency_ms,
    }


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
def expand_query(query: str) -> list[str]:
    """Generate query variations to improve retrieval recall."""
    _configure_genai()
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    response = gemini_model.generate_content(
        QUERY_EXPANSION_PROMPT.format(query=query),
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            response_mime_type="application/json",
        ),
    )
    try:
        result = json.loads(response.text)
        # Handle both {"queries": [...]} and plain list
        if isinstance(result, list):
            return result
        return list(result.values())[0] if result else []
    except Exception:
        return []
