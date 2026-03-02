from __future__ import annotations

"""
Smart chunking — NOT naive fixed-size splitting.
Uses sentence-aware chunking with overlap to preserve context.
"""
import re
from dataclasses import dataclass
from typing import Optional
import tiktoken
from .loader import RawDocument


@dataclass
class Chunk:
    """A chunk ready for embedding and storage."""
    chunk_id: str          # "{doc_id}_chunk_{n}"
    doc_id: str
    content: str
    metadata: dict         # Inherits from RawDocument + chunk-specific info


def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using regex (faster than NLTK for production)."""
    # Handle common abbreviations to avoid false splits
    text = re.sub(r'\b(Dr|Mr|Mrs|Ms|Prof|Sr|Jr|etc|vs|approx)\.\s', r'\1<PERIOD> ', text)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.replace('<PERIOD>', '.') for s in sentences if s.strip()]


def create_chunks(
    doc: RawDocument,
    chunk_size: int = 512,       # tokens
    chunk_overlap: int = 64,     # tokens
) -> list[Chunk]:
    """
    Sentence-aware chunking:
    1. Split into sentences
    2. Accumulate until chunk_size
    3. Overlap by going back chunk_overlap tokens
    """
    sentences = split_into_sentences(doc.content)
    chunks = []
    current_sentences = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        # If a single sentence exceeds chunk_size, split it hard
        if sentence_tokens > chunk_size:
            words = sentence.split()
            sub = []
            sub_tokens = 0
            for word in words:
                wt = count_tokens(word)
                if sub_tokens + wt > chunk_size and sub:
                    _flush_chunk(sub, chunks, doc, len(chunks))
                    sub = [word]
                    sub_tokens = wt
                else:
                    sub.append(word)
                    sub_tokens += wt
            if sub:
                current_sentences.extend(sub)
                current_tokens += sub_tokens
            continue

        if current_tokens + sentence_tokens > chunk_size and current_sentences:
            _flush_chunk(current_sentences, chunks, doc, len(chunks))
            # Overlap: roll back sentences until we have chunk_overlap tokens
            overlap_sentences = []
            overlap_tokens = 0
            for s in reversed(current_sentences):
                st = count_tokens(s)
                if overlap_tokens + st > chunk_overlap:
                    break
                overlap_sentences.insert(0, s)
                overlap_tokens += st
            current_sentences = overlap_sentences
            current_tokens = overlap_tokens

        current_sentences.append(sentence)
        current_tokens += sentence_tokens

    if current_sentences:
        _flush_chunk(current_sentences, chunks, doc, len(chunks))

    return chunks


def _flush_chunk(sentences: list[str], chunks: list, doc: RawDocument, idx: int):
    content = " ".join(sentences).strip()
    if not content:
        return
    chunk_id = f"{doc.doc_id}_chunk_{idx}"
    chunk_meta = {
        **doc.metadata,
        "chunk_index": idx,
        "chunk_id": chunk_id,
        "doc_id": doc.doc_id,
        "source": doc.source,
        "token_count": count_tokens(content),
    }
    chunks.append(Chunk(chunk_id=chunk_id, doc_id=doc.doc_id, content=content, metadata=chunk_meta))
