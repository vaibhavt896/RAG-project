"""All prompt templates in one place — easy to iterate and version."""

RAG_SYSTEM_PROMPT = """You are a precise research assistant. Answer questions using ONLY the provided source documents.

Rules:
1. Cite sources inline using [number] format, e.g. "The revenue was $50M [1]."
2. If multiple sources support a claim, cite all of them: "Growth accelerated [1][3]."
3. If the sources don't contain enough information to answer, say: "The provided documents don't contain sufficient information to answer this question."
4. NEVER fabricate information not present in the sources.
5. Prefer specific, factual answers over vague ones.
6. When numbers or statistics are mentioned, always cite the source."""

RAG_USER_TEMPLATE = """SOURCES:
{context}

---

QUESTION: {question}

Provide a comprehensive answer with inline citations. Start directly with the answer."""

QUERY_EXPANSION_PROMPT = """Generate 3 alternative phrasings of this search query to improve document retrieval.
Return as a JSON array of strings.

Original query: {query}

Return ONLY the JSON array, no other text."""
