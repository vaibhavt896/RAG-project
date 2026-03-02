"""
Local embeddings using sentence-transformers.
No API calls. No cost. Runs entirely on your machine.
Model: all-MiniLM-L6-v2 (~80MB, downloads once).
"""

import numpy as np
from sentence_transformers import SentenceTransformer

_model = None


def get_model() -> SentenceTransformer:
    """Lazy-load the embedding model (downloads on first use)."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text: str) -> list[float]:
    """Embed a single text string. Returns a normalized vector."""
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns normalized vectors."""
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
    return embeddings.tolist()


def similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Cosine similarity between two normalized vectors.
    Since vectors are normalized, dot product = cosine similarity.
    """
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b))
