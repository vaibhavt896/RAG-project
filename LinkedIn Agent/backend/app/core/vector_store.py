"""
ChromaDB vector store — local persistent storage.
Same concept as Pinecone but runs entirely on your laptop. Zero cost.
"""

import chromadb
from app.core.embedder import embed_text, embed_batch

# Persistent — data survives restarts
_client = chromadb.PersistentClient(path="./chroma_data")


def get_or_create_collection(name: str):
    """Get or create a ChromaDB collection with cosine similarity."""
    return _client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


# ── Resume Storage ───────────────────────────────────


def store_resume_chunks(user_id: str, chunks: list[str]) -> None:
    """Store resume text chunks as embeddings for RAG retrieval."""
    collection = get_or_create_collection(f"resume_{user_id}")
    embeddings = embed_batch(chunks)
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )


def search_resume(user_id: str, query: str, top_k: int = 3) -> list[str]:
    """Find the most relevant resume chunks for a job/company context."""
    collection = get_or_create_collection(f"resume_{user_id}")
    if collection.count() == 0:
        return []
    query_embedding = embed_text(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )
    return results["documents"][0] if results["documents"] else []


# ── Lead Profile Storage ─────────────────────────────


def store_lead_profile(lead_id: str, profile_text: str) -> None:
    """Store a lead's profile text for similarity search."""
    collection = get_or_create_collection("lead_profiles")
    embedding = embed_text(profile_text)
    collection.upsert(
        documents=[profile_text],
        embeddings=[embedding],
        ids=[lead_id],
    )


# ── Message Outcome Storage ──────────────────────────


def store_message_outcome(
    message_id: str, message_text: str, got_reply: bool
) -> None:
    """Store a sent message with its outcome for learning."""
    collection = get_or_create_collection("message_outcomes")
    embedding = embed_text(message_text)
    collection.upsert(
        documents=[message_text],
        embeddings=[embedding],
        ids=[message_id],
        metadatas=[{"got_reply": got_reply}],
    )


def get_similar_winning_messages(
    message_text: str, top_k: int = 3
) -> list[str]:
    """Find messages similar to the current one that got replies."""
    collection = get_or_create_collection("message_outcomes")
    if collection.count() == 0:
        return []
    query_embedding = embed_text(message_text)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        where={"got_reply": True},
    )
    return results["documents"][0] if results["documents"] else []
