from __future__ import annotations

"""Golden dataset management utilities."""
import json
from pathlib import Path
from .harness import EvalCase


def load_testset(path: str = "./data/eval/golden_dataset.json") -> list[EvalCase]:
    """Load a golden test set from JSON."""
    data = json.loads(Path(path).read_text())
    return [EvalCase(**case) for case in data]


def save_testset(cases: list[EvalCase], path: str = "./data/eval/golden_dataset.json"):
    """Save a golden test set to JSON."""
    data = [{"question": c.question, "ground_truth_answer": c.ground_truth_answer, "relevant_doc_ids": c.relevant_doc_ids} for c in cases]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2))
