from __future__ import annotations

"""
BM25 keyword search.
BM25 excels where vector search fails:
- Exact product codes, names, IDs
- Technical jargon not in embedding training data
- Numeric data matching
"""
import json
import pickle
from pathlib import Path
import bm25s
import numpy as np
from ..ingestion.chunker import Chunk


class BM25Store:
    def __init__(self, index_path: str = "./data/bm25_index"):
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.retriever = None
        self.chunk_map: dict[int, dict] = {}  # position → chunk info
        self._load_if_exists()

    def _load_if_exists(self):
        index_file = self.index_path / "index.pkl"
        map_file = self.index_path / "chunk_map.json"
        if index_file.exists() and map_file.exists():
            with open(index_file, "rb") as f:
                self.retriever = pickle.load(f)
            with open(map_file, "r") as f:
                self.chunk_map = {int(k): v for k, v in json.load(f).items()}

    def _save(self):
        with open(self.index_path / "index.pkl", "wb") as f:
            pickle.dump(self.retriever, f)
        with open(self.index_path / "chunk_map.json", "w") as f:
            json.dump(self.chunk_map, f)

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Rebuild index with new chunks (BM25 requires full rebuild on add)."""
        existing_count = len(self.chunk_map)
        for i, chunk in enumerate(chunks):
            pos = existing_count + i
            self.chunk_map[pos] = {
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "metadata": chunk.metadata,
            }

        all_docs = [self.chunk_map[i]["content"] for i in range(len(self.chunk_map))]
        corpus_tokens = bm25s.tokenize(all_docs)
        self.retriever = bm25s.BM25()
        self.retriever.index(corpus_tokens)
        self._save()

    def search(self, query: str, top_k: int = 20) -> list[dict]:
        if self.retriever is None or not self.chunk_map:
            return []

        query_tokens = bm25s.tokenize([query])
        results, scores = self.retriever.retrieve(query_tokens, k=min(top_k, len(self.chunk_map)))

        output = []
        for i, score in zip(results[0], scores[0]):
            chunk_info = self.chunk_map[int(i)]
            # Normalize BM25 score to [0,1] range
            normalized_score = float(score) / (float(score) + 10)
            output.append({
                "chunk_id": chunk_info["chunk_id"],
                "content": chunk_info["content"],
                "metadata": chunk_info["metadata"],
                "score": normalized_score,
                "search_type": "keyword",
            })
        return output
