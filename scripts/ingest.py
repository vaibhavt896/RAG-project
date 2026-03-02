#!/usr/bin/env python3
"""
CLI to ingest documents into the RAG system.
Usage:
  python scripts/ingest.py --source data/raw/document.pdf
  python scripts/ingest.py --source data/raw/   # ingest all files in directory
"""
import sys
import os
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.ingestion.loader import load_document
from src.ingestion.chunker import create_chunks
from src.retrieval.hybrid import HybridRetriever


def ingest_file(retriever: HybridRetriever, file_path: str) -> dict:
    """Ingest a single file and return stats."""
    print(f"  Loading: {file_path}")
    doc = load_document(file_path)
    print(f"  Document ID: {doc.doc_id}")
    print(f"  Content length: {len(doc.content)} chars")

    chunks = create_chunks(doc)
    print(f"  Chunks created: {len(chunks)}")

    retriever.add_chunks(chunks)
    print(f"  ✓ Indexed into vector store + BM25")

    return {
        "doc_id": doc.doc_id,
        "source": file_path,
        "chunks": len(chunks),
        "content_length": len(doc.content),
    }


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the RAG system")
    parser.add_argument("--source", required=True, help="File path, URL, or directory to ingest")
    args = parser.parse_args()

    retriever = HybridRetriever()
    source = Path(args.source)
    results = []

    if source.is_dir():
        # Ingest all supported files in directory
        supported = {".pdf", ".docx", ".txt", ".md"}
        files = [f for f in source.iterdir() if f.suffix.lower() in supported]
        if not files:
            print(f"No supported files found in {source}")
            return

        print(f"Found {len(files)} files to ingest:\n")
        for f in sorted(files):
            print(f"--- {f.name} ---")
            try:
                result = ingest_file(retriever, str(f))
                results.append(result)
            except Exception as e:
                print(f"  ✗ Error: {e}")
            print()
    else:
        # Single file or URL
        print(f"--- {source} ---")
        result = ingest_file(retriever, str(source))
        results.append(result)

    # Summary
    print("=" * 50)
    print("INGESTION SUMMARY")
    print("=" * 50)
    total_chunks = sum(r["chunks"] for r in results)
    print(f"  Documents processed: {len(results)}")
    print(f"  Total chunks created: {total_chunks}")
    print(f"  Vector store size: {retriever.vector_store.collection.count()}")
    print(f"  BM25 index size: {len(retriever.bm25_store.chunk_map)}")


if __name__ == "__main__":
    main()
