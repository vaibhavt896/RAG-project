from __future__ import annotations

"""
Edge case handlers — what separates a portfolio project from a production system.
Each handler addresses a specific failure mode.
"""
import re
import os
import json
import google.generativeai as genai


def _configure_genai():
    """Lazy Gemini configuration — only runs when actually needed."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def detect_unanswerable(question: str, context_chunks: list[dict]) -> bool:
    """
    Detect when the retrieved context can't answer the question.
    Prevents hallucinated answers on low-confidence retrievals.
    """
    if not context_chunks:
        return True

    # Check if best chunk score is above minimum threshold
    best_score = max(c.get("rerank_score", c.get("score", 0)) for c in context_chunks)
    if best_score < 0.1:
        return True

    return False


def detect_ambiguous_query(question: str) -> dict:
    """
    Detect if a query is too ambiguous to answer well.
    Returns clarification questions if needed.
    """
    _configure_genai()
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""Is this question clear enough to answer from a document store, or does it need clarification?

Question: {question}

Return JSON:
{{
  "is_ambiguous": true/false,
  "ambiguity_reason": "explanation or null",
  "clarification_needed": ["question1", "question2"] or []
}}"""

    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)


def detect_sensitive_query(question: str) -> bool:
    """
    Block queries that should go through human review in financial/legal context.
    """
    sensitive_patterns = [
        r"confidential",
        r"personal.*(data|information)",
        r"(legal|medical) advice",
        r"password|secret|api.?key",
    ]
    question_lower = question.lower()
    return any(re.search(p, question_lower) for p in sensitive_patterns)


def handle_long_document_edge_case(chunks: list[dict], max_context_tokens: int = 4000) -> list[dict]:
    """
    If top-k chunks exceed context window, truncate intelligently
    (keep best-ranked, not first-n).
    """
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")

    selected = []
    total_tokens = 0

    for chunk in chunks:
        chunk_tokens = len(enc.encode(chunk["content"]))
        if total_tokens + chunk_tokens > max_context_tokens:
            # Truncate this chunk if it would fit partially
            remaining = max_context_tokens - total_tokens
            if remaining > 100:  # Only include if meaningful content fits
                tokens = enc.encode(chunk["content"])[:remaining]
                chunk = {**chunk, "content": enc.decode(tokens) + "..."}
                selected.append(chunk)
            break
        selected.append(chunk)
        total_tokens += chunk_tokens

    return selected
