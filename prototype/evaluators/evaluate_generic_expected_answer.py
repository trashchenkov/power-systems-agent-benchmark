"""Generic deterministic evaluator for lightweight benchmark task candidates.

This evaluator is intentionally simple: it makes a candidate executable by
checking a structured expected answer exactly enough for harness, packet, and
baseline testing. Domain-specific simulator-backed evaluators can replace it
family-by-family later without changing the benchmark contract.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _compare(expected: Any, actual: Any, path: str, tolerance: float, violations: list[str]) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            violations.append(f"{path}: expected object")
            return
        for key, expected_value in expected.items():
            # Generic public-surrogate tasks score the structured answer. Free-text
            # rationale is allowed for explainability but is not an oracle string.
            if path == "submission" and key == "rationale":
                continue
            if key not in actual:
                violations.append(f"{path}.{key}: missing")
            else:
                _compare(expected_value, actual[key], f"{path}.{key}", tolerance, violations)
        for key in actual:
            if path == "submission" and key == "rationale":
                continue
            if key not in expected:
                violations.append(f"{path}.{key}: unexpected")
        return
    if isinstance(expected, list):
        if not isinstance(actual, list):
            violations.append(f"{path}: expected list")
            return
        if len(expected) != len(actual):
            violations.append(f"{path}: expected list length {len(expected)}, got {len(actual)}")
            return
        for idx, (expected_item, actual_item) in enumerate(zip(expected, actual)):
            _compare(expected_item, actual_item, f"{path}[{idx}]", tolerance, violations)
        return
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        if not isinstance(actual, (int, float)) or isinstance(actual, bool):
            violations.append(f"{path}: expected number")
        elif abs(float(expected) - float(actual)) > tolerance:
            violations.append(f"{path}: expected {expected}, got {actual}")
        return
    if expected != actual:
        violations.append(f"{path}: expected {expected!r}, got {actual!r}")


def evaluate_case(task: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
    expected = task.get("expected_submission")
    if expected is None:
        expected = task.get("baseline_submission")
    violations: list[str] = []
    if expected is None:
        violations.append("task is missing expected_submission/baseline_submission")
    else:
        _compare(expected, submission, "submission", float(task.get("numeric_tolerance", 1e-6)), violations)
    feasible = not violations
    return {
        "task_id": task.get("task_id"),
        "feasible": feasible,
        "score": 1.0 if feasible else 0.0,
        "expected_answer_type": task.get("answer_type", "structured_expected_answer"),
        "violations": violations,
    }


def evaluate_files(task_path: Path, submission_path: Path) -> dict[str, Any]:
    return evaluate_case(load_json(task_path), load_json(submission_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate a generic expected-answer benchmark submission.")
    parser.add_argument("task_json", type=Path)
    parser.add_argument("submission_json", type=Path)
    args = parser.parse_args(argv)
    result = evaluate_files(args.task_json, args.submission_json)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("feasible") else 1


if __name__ == "__main__":
    raise SystemExit(main())
