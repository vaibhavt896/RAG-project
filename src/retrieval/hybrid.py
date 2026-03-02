from __future__ import annotations

"""
Reciprocal Rank Fusion (RRF) — the correct way to merge ranked lists.

Why RRF and not simple score averaging?
- Vector and BM25 scores live in different spaces (not comparable)
- RRF uses rank position, not raw scores — more robust
- Proven in information retrieval research (Cormack et al., 2009)

Formula: RRF(d) = Σ 1 / (k + rank(d))  where k=60 (empirically best)
"""
from collections import defaultdict
from .vector_store import VectorStore
from .bm25_store import BM25Store


def reciprocal_rank_fusion(
    result_lists: list[list[dict]],
    k: int = 60,
) -> list[dict]:
    """
    Merge multiple ranked result lists using RRF.
    Returns deduplicated results sorted by RRF score (descending).
    """
    scores: dict[str, float] = defaultdict(float)
    chunk_data: dict[str, dict] = {}

    for result_list in result_lists:
        for rank, result in enumerate(result_list, start=1):
            chunk_id = result["chunk_id"]
            scores[chunk_id] += 1.0 / (k + rank)
            if chunk_id not in chunk_data:
                chunk_data[chunk_id] = result

    # Sort by RRF score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {**chunk_data[chunk_id], "rrf_score": rrf_score, "score": rrf_score}
        for chunk_id, rrf_score in ranked
    ]


class HybridRetriever:
    def __init__(self):
        self.vector_store = VectorStore()
        self.bm25_store = BM25Store()

    def add_chunks(self, chunks) -> None:
        self.vector_store.add_chunks(chunks)
        self.bm25_store.add_chunks(chunks)

    def search(
        self,
        query: str,
        top_k: int = 20,
        vector_weight: float = 0.6,  # Tunable per domain
        keyword_weight: float = 0.4,
    ) -> list[dict]:
        # Run both searches
        vector_results = self.vector_store.search(query, top_k=top_k)
        keyword_results = self.bm25_store.search(query, top_k=top_k)

        # Fuse with RRF
        fused = reciprocal_rank_fusion([vector_results, keyword_results])
        return fused[:top_k]
