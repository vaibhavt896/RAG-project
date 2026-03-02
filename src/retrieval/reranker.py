from __future__ import annotations

"""
Cross-encoder re-ranking.

Why re-rank after retrieval?
Bi-encoders (embedding models) encode query and document SEPARATELY.
This is fast but loses fine-grained interaction between query terms and document.

Cross-encoders process (query, document) TOGETHER — much more accurate
but too slow to run on the entire corpus. So we:
1. Retrieve top-20 candidates cheaply with hybrid search
2. Re-rank top-20 accurately with cross-encoder
3. Take top-5 for generation

In memory-constrained environments (e.g. Render free tier, 512MB),
set ENABLE_RERANKER=false to use a lightweight keyword-overlap fallback
that requires no PyTorch or model loading.
"""
import os


class LightweightReranker:
    """
    Fallback reranker using keyword overlap scoring.
    No PyTorch, no model download — fits any memory budget.
    Still provides meaningful re-ranking via term-frequency scoring.
    """

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        if not candidates:
            return []

        candidates = [dict(c) for c in candidates]
        query_terms = set(query.lower().split())

        for candidate in candidates:
            content_lower = candidate["content"].lower()
            # Score = fraction of query terms found in the chunk
            matches = sum(1 for t in query_terms if t in content_lower)
            candidate["rerank_score"] = matches / max(len(query_terms), 1)

        reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

        for i, chunk in enumerate(reranked):
            chunk["final_rank"] = i + 1

        return reranked[:top_k]


class CrossEncoderReranker:
    _instance = None  # Singleton — model loading is expensive

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = None  # Lazy load to save startup memory
        return cls._instance

    def _load_model(self):
        """Lazy load the model on first use — keeps startup memory low."""
        if self.model is None:
            from sentence_transformers import CrossEncoder
            # This model is ~80MB, fast on CPU, production-ready
            self.model = CrossEncoder(
                "cross-encoder/ms-marco-MiniLM-L-6-v2",
                max_length=512,
            )

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        self._load_model()

        if not candidates:
            return []

        # Create copies to avoid mutating input dicts
        candidates = [dict(c) for c in candidates]

        # Score all (query, chunk) pairs
        pairs = [(query, c["content"]) for c in candidates]
        scores = self.model.predict(pairs)

        # Attach scores and sort
        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)

        reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

        # Add rank metadata for debugging/evaluation
        for i, chunk in enumerate(reranked):
            chunk["final_rank"] = i + 1

        return reranked[:top_k]


def get_reranker():
    """Factory: returns CrossEncoderReranker if enabled, else LightweightReranker."""
    enable = os.environ.get("ENABLE_RERANKER", "true").lower()
    if enable in ("false", "0", "no"):
        return LightweightReranker()
    return CrossEncoderReranker()
