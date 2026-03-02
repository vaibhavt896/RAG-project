from __future__ import annotations

"""
Four core RAG metrics (aligned with RAGAS framework):

1. FAITHFULNESS — Does the answer contain only what's in the sources?
   (Detects hallucination)

2. ANSWER RELEVANCE — How relevant is the answer to the question?
   (Detects off-topic answers)

3. CONTEXT RECALL — Were all the important facts retrieved?
   (Measures retrieval quality)

4. CONTEXT PRECISION — Are the retrieved chunks actually useful?
   (Measures retrieval precision — penalizes noise)
"""
import os
import json
import google.generativeai as genai
import numpy as np
from dataclasses import dataclass


def _configure_genai():
    """Lazy Gemini configuration — only runs when actually needed."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


@dataclass
class EvalResult:
    faithfulness: float        # 0.0 to 1.0
    answer_relevance: float    # 0.0 to 1.0
    context_recall: float      # 0.0 to 1.0
    context_precision: float   # 0.0 to 1.0
    hallucination_detected: bool
    issues: list[str]          # Human-readable issues found

    @property
    def overall_score(self) -> float:
        weights = {
            "faithfulness": 0.35,       # Most important for production
            "answer_relevance": 0.25,
            "context_recall": 0.20,
            "context_precision": 0.20,
        }
        return (
            self.faithfulness * weights["faithfulness"] +
            self.answer_relevance * weights["answer_relevance"] +
            self.context_recall * weights["context_recall"] +
            self.context_precision * weights["context_precision"]
        )


def evaluate_faithfulness(answer: str, context_chunks: list[str]) -> dict:
    """
    Decompose answer into claims, check each claim against sources.
    Score = (supported claims) / (total claims)
    """
    _configure_genai()
    context = "\n\n".join(context_chunks)
    prompt = f"""Evaluate whether the ANSWER is fully supported by the SOURCES.

SOURCES:
{context}

ANSWER:
{answer}

Instructions:
1. List each factual claim in the answer
2. For each claim, determine if it's supported by the sources
3. Calculate a faithfulness score

Return JSON:
{{
  "claims": [
    {{"claim": "...", "supported": true/false, "evidence": "quote from source or null"}}
  ],
  "faithfulness_score": 0.0-1.0,
  "unsupported_claims": ["list of unsupported claims"]
}}"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)


def evaluate_answer_relevance(question: str, answer: str) -> float:
    """
    Reverse approach: generate questions that the answer implies,
    check if they match the original question via embedding similarity.
    """
    _configure_genai()
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"""Given this ANSWER, generate 5 questions that this answer would be a response to.

ANSWER: {answer}

Return JSON: {{"questions": ["q1", "q2", ...]}}"""

    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.3,
            response_mime_type="application/json",
        ),
    )
    generated_questions = json.loads(response.text).get("questions", [])

    if not generated_questions:
        return 0.0

    # Embed the original question
    embed_model = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    orig_result = genai.embed_content(
        model=embed_model,
        content=question,
        task_type="retrieval_query",
    )
    orig_embedding = np.array(orig_result["embedding"])

    # Embed generated questions and compare
    similarities = []
    for gq in generated_questions:
        gen_result = genai.embed_content(
            model=embed_model,
            content=gq,
            task_type="retrieval_query",
        )
        gen_embedding = np.array(gen_result["embedding"])
        sim = np.dot(orig_embedding, gen_embedding) / (
            np.linalg.norm(orig_embedding) * np.linalg.norm(gen_embedding)
        )
        similarities.append(float(sim))

    return sum(similarities) / len(similarities)
