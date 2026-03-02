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
"""
# CrossEncoder is lazy-imported in _load_model() to reduce startup memory


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
