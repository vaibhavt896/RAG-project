from __future__ import annotations

"""
Citation tracking — this is what separates a toy RAG from a production one.

We:
1. Assign numbered references [1], [2]... to each retrieved chunk
2. Inject them into the LLM prompt
3. Parse the LLM's response to extract which citations it used
4. Verify those citations actually support the claims made
"""
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Citation:
    ref_number: int
    chunk_id: str
    doc_id: str
    source: str
    title: str
    page: Optional[int]
    excerpt: str           # The relevant snippet from the chunk
    used_in_response: bool = False


@dataclass
class CitationMap:
    citations: list[Citation]
    context_text: str      # The formatted context sent to LLM

    def get_by_ref(self, ref_number: int) -> Optional[Citation]:
        for c in self.citations:
            if c.ref_number == ref_number:
                return c
        return None


def build_citation_map(ranked_chunks: list[dict]) -> CitationMap:
    """
    Convert ranked chunks into a numbered citation map.
    Returns both the map and the formatted context for the prompt.
    """
    citations = []
    context_parts = []

    for i, chunk in enumerate(ranked_chunks, start=1):
        meta = chunk.get("metadata", {})
        citation = Citation(
            ref_number=i,
            chunk_id=chunk["chunk_id"],
            doc_id=meta.get("doc_id", ""),
            source=meta.get("source", ""),
            title=meta.get("title", "Unknown"),
            page=meta.get("page_number"),
            excerpt=chunk["content"][:200],  # Short excerpt for display
        )
        citations.append(citation)

        # Format for LLM context
        page_str = f", Page {meta['page_number']}" if meta.get("page_number") else ""
        context_parts.append(
            f"[{i}] Source: {meta.get('title', 'Unknown')}{page_str}\n{chunk['content']}"
        )

    context_text = "\n\n---\n\n".join(context_parts)
    return CitationMap(citations=citations, context_text=context_text)


def extract_citations_from_response(response: str) -> list[int]:
    """Extract all citation numbers like [1], [2,3], [1][4] from LLM response."""
    # Match patterns like [1], [1,2], [1, 2, 3]
    patterns = re.findall(r'\[(\d+(?:,\s*\d+)*)\]', response)
    refs = []
    for match in patterns:
        refs.extend(int(n.strip()) for n in match.split(","))
    return list(set(refs))
