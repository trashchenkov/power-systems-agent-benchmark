"""Public surrogate evaluator for false-data injection detection.

This v0 evaluator scores attack-label detection and corrected-state accuracy. The
public case exposes deterministic residuals and ground truth; hidden variants can
compute residuals from a DC state estimator and synthetic attack generator while
keeping the same submission contract.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _metrics(truth: set[str], predicted: set[str]) -> tuple[float, float, float]:
    tp = len(truth & predicted)
    fp = len(predicted - truth)
    fn = len(truth - predicted)
    precision = tp / (tp + fp) if tp + fp else (1.0 if not truth else 0.0)
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def evaluate_case(case: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    measurements = case.get("measurements", [])
    known = {m["id"] for m in measurements}
    truth = {m["id"] for m in measurements if bool(m.get("ground_truth_attack", False))}
    attacked = submission.get("attacked_measurements", [])
    corrected_state = submission.get("corrected_state", {})
    violations: list[str] = []

    if not isinstance(attacked, list):
        violations.append("attacked_measurements must be a list")
        attacked = []
    if not isinstance(corrected_state, dict):
        violations.append("corrected_state must be an object")
        corrected_state = {}

    predicted = set(str(mid) for mid in attacked)
    for mid in sorted(predicted - known):
        violations.append(f"unknown measurement id: {mid}")
    for mid in sorted(truth - predicted):
        violations.append(f"missed attacked measurement: {mid}")
    for mid in sorted(predicted - truth - (predicted - known)):
        violations.append(f"false attack alarm: {mid}")

    state_truth = case.get("ground_truth_state", {})
    state_errors: dict[str, float] = {}
    max_state_error = 0.0
    for key, true_value in state_truth.items():
        if key not in corrected_state:
            violations.append(f"corrected_state missing {key}")
            continue
        try:
            error = abs(float(corrected_state[key]) - float(true_value))
        except (TypeError, ValueError):
            violations.append(f"corrected_state.{key} must be numeric")
            continue
        state_errors[key] = round(error, 6)
        max_state_error = max(max_state_error, error)
    state_threshold = float(case.get("state_error_threshold", 0.05))
    if max_state_error > state_threshold:
        violations.append(f"max_state_error above threshold {state_threshold:.6f}")

    precision, recall, f1 = _metrics(truth, predicted & known)
    feasible = not violations
    score = round(f1, 6) if feasible else 0.0
    return {
        "task_id": case.get("task_id"),
        "feasible": feasible,
        "score": score,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "truth_attacked_measurements": sorted(truth),
        "predicted_attacked_measurements": sorted(predicted),
        "max_state_error": round(max_state_error, 6),
        "state_errors": state_errors,
        "violations": violations,
    }


def evaluate_files(case_path: str | Path, submission_path: str | Path) -> dict[str, Any]:
    return evaluate_case(_load_json(case_path), _load_json(submission_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate an FDI state-estimation detection submission.")
    parser.add_argument("case", help="Path to public/hidden case JSON")
    parser.add_argument("submission", help="Path to submission JSON")
    args = parser.parse_args()
    print(json.dumps(evaluate_files(args.case, args.submission), ensure_ascii=False, indent=2))
