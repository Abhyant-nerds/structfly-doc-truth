from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.classification.pipeline import run_email_classification


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def evaluate_samples(path: str | Path) -> dict[str, Any]:
    records = load_jsonl(path)
    results = []
    correct = 0
    candidate_hits = 0

    for record in records:
        result = run_email_classification(record.get("subject", ""), record["body"])
        candidate_ids = {candidate.category_id for candidate in result.candidates}
        expected = record["expected_category_id"]
        final_match = result.final_category_id == expected
        candidate_hit = expected in candidate_ids
        correct += int(final_match)
        candidate_hits += int(candidate_hit)
        results.append(
            {
                "email_id": record.get("email_id"),
                "expected_category_id": expected,
                "final_category_id": result.final_category_id,
                "final_match": final_match,
                "candidate_hit": candidate_hit,
                "needs_review": result.needs_review,
            }
        )

    total = len(records)
    return {
        "total": total,
        "final_accuracy": correct / total if total else 0.0,
        "candidate_recall": candidate_hits / total if total else 0.0,
        "results": results,
    }
