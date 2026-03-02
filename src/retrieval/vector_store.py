from __future__ import annotations

"""
Vector store interface using ChromaDB with Gemini embeddings.
Swap to pgvector in production by changing this file only.
"""
import google.generativeai as genai
import chromadb
import chromadb.utils.embedding_functions as ef
import os
from ..ingestion.chunker import Chunk


def _configure_genai():
    """Lazy Gemini configuration — only runs when actually needed."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiEmbeddingFunction(ef.EmbeddingFunction):
    """Custom Gemini embedding function for ChromaDB."""

    def __call__(self, input: list[str]) -> list[list[float]]:
        _configure_genai()
        embeddings = []
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
        # Batch in groups of 10 to stay within rate limits
        for i in range(0, len(input), 10):
            batch = input[i:i + 10]
            for text in batch:
                result = genai.embed_content(
                    model=model,
                    content=text,
                    task_type="retrieval_document",
                )
                embeddings.append(result["embedding"])
        return embeddings


class VectorStore:
    def __init__(self, collection_name: str = "rag_docs"):
        self.client = chromadb.PersistentClient(path="./data/chromadb")
        self.embedding_fn = GeminiEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},  # cosine for semantic similarity
        )

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Add chunks with deduplication via chunk_id."""
        # Filter out already-existing chunks
        existing_ids = set(self.collection.get(ids=[c.chunk_id for c in chunks])["ids"])
        new_chunks = [c for c in chunks if c.chunk_id not in existing_ids]
        if not new_chunks:
            return

        self.collection.add(
            ids=[c.chunk_id for c in new_chunks],
            documents=[c.content for c in new_chunks],
            metadatas=[c.metadata for c in new_chunks],
        )

    def search(self, query: str, top_k: int = 20) -> list[dict]:
        """Returns ranked results with similarity scores."""
        count = self.collection.count()
        if count == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, count),
            include=["documents", "metadatas", "distances"],
        )
        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "chunk_id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i],  # cosine similarity
                "search_type": "vector",
            })
        return output
