from __future__ import annotations

"""
Load documents from various sources.
Supports: PDF, DOCX, TXT, Markdown, URLs
"""
import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import httpx
import pypdf
import docx2txt
from bs4 import BeautifulSoup


@dataclass
class RawDocument:
    """Represents a loaded document before chunking."""
    doc_id: str           # SHA256 of content — deterministic, dedup-safe
    source: str           # file path or URL
    content: str
    metadata: dict        # title, author, page_count, etc.


def _make_doc_id(content: str, source: str) -> str:
    """Deterministic ID based on content hash."""
    return hashlib.sha256(f"{source}{content}".encode()).hexdigest()[:16]


def load_pdf(path: str) -> RawDocument:
    reader = pypdf.PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append(f"[Page {i+1}]\n{text}")
    content = "\n\n".join(pages)
    metadata = {
        "title": Path(path).stem,
        "source_type": "pdf",
        "page_count": len(reader.pages),
        "file_path": str(path),
    }
    return RawDocument(
        doc_id=_make_doc_id(content, path),
        source=path,
        content=content,
        metadata=metadata,
    )


def load_docx(path: str) -> RawDocument:
    content = docx2txt.process(path)
    metadata = {
        "title": Path(path).stem,
        "source_type": "docx",
        "file_path": str(path),
    }
    return RawDocument(
        doc_id=_make_doc_id(content, path),
        source=path,
        content=content,
        metadata=metadata,
    )


def load_txt(path: str) -> RawDocument:
    content = Path(path).read_text(encoding="utf-8")
    metadata = {"title": Path(path).stem, "source_type": "text", "file_path": str(path)}
    return RawDocument(doc_id=_make_doc_id(content, path), source=path, content=content, metadata=metadata)


def load_url(url: str) -> RawDocument:
    response = httpx.get(url, timeout=30, follow_redirects=True)
    soup = BeautifulSoup(response.text, "html.parser")
    # Remove nav, footer, scripts
    for tag in soup(["nav", "footer", "script", "style", "header"]):
        tag.decompose()
    content = soup.get_text(separator="\n", strip=True)
    title = soup.title.string if soup.title else url
    metadata = {
        "title": title,
        "source_type": "url",
        "url": url,
    }
    return RawDocument(
        doc_id=_make_doc_id(content, url),
        source=url,
        content=content,
        metadata=metadata,
    )


def load_document(source: str) -> RawDocument:
    """Auto-detect and load document from any supported source."""
    if source.startswith("http"):
        return load_url(source)
    path = Path(source)
    loaders = {".pdf": load_pdf, ".docx": load_docx, ".txt": load_txt, ".md": load_txt}
    loader = loaders.get(path.suffix.lower())
    if not loader:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    return loader(source)
