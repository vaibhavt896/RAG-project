#!/usr/bin/env python3
"""
CLI to run the evaluation harness.
Usage:
  python scripts/evaluate.py --dataset data/eval/golden_dataset.json
"""
import sys
import os
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.evaluation.harness import load_golden_dataset, run_eval_harness
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.reranker import CrossEncoderReranker
from src.citation.tracker import build_citation_map, extract_citations_from_response
from src.generation.llm import generate_answer
from src.retrieval.edge_cases import handle_long_document_edge_case


def create_pipeline():
    """Create a callable RAG pipeline for evaluation."""
    retriever = HybridRetriever()
    reranker = CrossEncoderReranker()

    def pipeline(question: str) -> dict:
        import time
        start = time.time()

        # Retrieve
        results = retriever.search(question, top_k=20)

        # Re-rank
        reranked = reranker.rerank(question, results, top_k=5)

        # Context length check
        reranked = handle_long_document_edge_case(reranked)

        # Build citations
        citation_map = build_citation_map(reranked)

        # Generate
        gen_result = generate_answer(
            question=question,
            context=citation_map.context_text,
        )

        return {
            "answer": gen_result["answer"],
            "chunks": [{"content": c["content"], "doc_id": c.get("metadata", {}).get("doc_id", "")} for c in reranked],
            "latency_ms": int((time.time() - start) * 1000),
            "tokens_used": gen_result["tokens_used"],
        }

    return pipeline


def main():
    parser = argparse.ArgumentParser(description="Run RAG evaluation harness")
    parser.add_argument("--dataset", default="./data/eval/golden_dataset.json", help="Path to golden dataset")
    parser.add_argument("--output", default="./data/eval/results.json", help="Path to save results")
    args = parser.parse_args()

    print("Loading golden dataset...")
    dataset = load_golden_dataset(args.dataset)
    print(f"Loaded {len(dataset)} test cases\n")

    print("Creating pipeline...")
    pipeline = create_pipeline()

    print("Running evaluation...\n")
    summary = run_eval_harness(pipeline, dataset, output_path=args.output)

    print(f"\nDetailed results saved to: {args.output}")


if __name__ == "__main__":
    main()
