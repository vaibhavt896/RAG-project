from __future__ import annotations

"""
Citation validator — checks that the LLM's citations actually support its claims.
This catches a subtle form of hallucination: correct answer, wrong citation.
"""
import google.generativeai as genai
import os
import json


def _configure_genai():
    """Lazy Gemini configuration — only runs when actually needed."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def validate_citation(claim: str, cited_chunk: str) -> dict:
    """
    Use Gemini to verify that cited_chunk supports the claim.
    Returns: {"supported": bool, "confidence": float, "reason": str}
    """
    _configure_genai()
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        f"""Does the SOURCE TEXT support the CLAIM?

CLAIM: {claim}

SOURCE TEXT: {cited_chunk}

Reply in JSON only:
{{"supported": true or false, "confidence": 0.0 to 1.0, "reason": "brief explanation"}}""",
        generation_config=genai.GenerationConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)
