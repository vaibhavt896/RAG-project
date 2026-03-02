from __future__ import annotations

"""
Evaluation harness — runs a complete eval loop over a golden dataset.
"""
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
import pandas as pd
from .metrics import evaluate_faithfulness, evaluate_answer_relevance, EvalResult


@dataclass
class EvalCase:
    """A single test case in the golden dataset."""
    question: str
    ground_truth_answer: str
    relevant_doc_ids: list[str]  # Docs that SHOULD be retrieved


def load_golden_dataset(path: str) -> list[EvalCase]:
    """Load Q&A pairs from JSON file."""
    data = json.loads(Path(path).read_text())
    return [EvalCase(**case) for case in data]


def run_eval_harness(
    pipeline,  # Your full RAG pipeline callable
    golden_dataset: list[EvalCase],
    output_path: str = "./data/eval/results.json",
) -> dict:
    """
    Run complete evaluation.
    Returns summary metrics and saves detailed results.
    """
    results = []
    start_time = time.time()

    for i, case in enumerate(golden_dataset):
        print(f"Evaluating {i+1}/{len(golden_dataset)}: {case.question[:60]}...")

        # Run the full pipeline
        pipeline_output = pipeline(case.question)

        # Get retrieved chunks
        retrieved_chunks = [c["content"] for c in pipeline_output.get("chunks", [])]
        retrieved_ids = [c.get("doc_id", "") for c in pipeline_output.get("chunks", [])]
        answer = pipeline_output.get("answer", "")

        # Compute metrics
        faithfulness_result = evaluate_faithfulness(answer, retrieved_chunks)
        relevance_score = evaluate_answer_relevance(case.question, answer)

        # Context recall: what % of relevant docs were retrieved?
        if case.relevant_doc_ids:
            retrieved_relevant = len(set(retrieved_ids) & set(case.relevant_doc_ids))
            context_recall = retrieved_relevant / len(case.relevant_doc_ids)
        else:
            context_recall = 1.0

        # Context precision: what % of retrieved chunks are actually relevant?
        if retrieved_ids:
            relevant_retrieved = len(set(retrieved_ids) & set(case.relevant_doc_ids))
            context_precision = relevant_retrieved / len(retrieved_ids)
        else:
            context_precision = 0.0

        faithfulness_score = faithfulness_result.get("faithfulness_score", 0.0)
        unsupported = faithfulness_result.get("unsupported_claims", [])

        eval_result = EvalResult(
            faithfulness=faithfulness_score,
            answer_relevance=relevance_score,
            context_recall=context_recall,
            context_precision=context_precision,
            hallucination_detected=len(unsupported) > 0,
            issues=unsupported,
        )

        results.append({
            "question": case.question,
            "answer": answer,
            "ground_truth": case.ground_truth_answer,
            "faithfulness": eval_result.faithfulness,
            "answer_relevance": eval_result.answer_relevance,
            "context_recall": eval_result.context_recall,
            "context_precision": eval_result.context_precision,
            "overall_score": eval_result.overall_score,
            "hallucination_detected": eval_result.hallucination_detected,
            "issues": eval_result.issues,
            "latency_ms": pipeline_output.get("latency_ms", 0),
        })

    total_time = time.time() - start_time

    # Summary statistics
    df = pd.DataFrame(results)
    summary = {
        "total_cases": len(results),
        "avg_faithfulness": df["faithfulness"].mean(),
        "avg_answer_relevance": df["answer_relevance"].mean(),
        "avg_context_recall": df["context_recall"].mean(),
        "avg_context_precision": df["context_precision"].mean(),
        "avg_overall_score": df["overall_score"].mean(),
        "hallucination_rate": df["hallucination_detected"].mean(),
        "avg_latency_ms": df["latency_ms"].mean(),
        "p95_latency_ms": df["latency_ms"].quantile(0.95),
        "total_eval_time_sec": round(total_time, 1),
    }

    output = {"summary": summary, "detailed_results": results}
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(output, indent=2))

    print("\n=== EVALUATION SUMMARY ===")
    for k, v in summary.items():
        print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")

    return summary
