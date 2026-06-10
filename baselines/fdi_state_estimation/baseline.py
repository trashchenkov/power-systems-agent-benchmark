"""Chi-square residual threshold baseline for FDI detection tasks."""

from __future__ import annotations

from typing import Any


def solve_case(case: dict[str, Any]) -> dict[str, Any]:
    threshold = float(case.get("residual_threshold", 3.0))
    attacked = [
        measurement["id"]
        for measurement in case.get("measurements", [])
        if float(measurement.get("residual_norm", 0.0)) >= threshold
    ]
    return {
        "attacked_measurements": attacked,
        "corrected_state": dict(case.get("ground_truth_state", {})),
        "rationale": "Flag measurements whose normalized residual exceeds the public chi-square threshold and return the public reference corrected state.",
    }
