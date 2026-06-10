"""Public baseline for N-1 contingency screening."""

from __future__ import annotations

from typing import Any

from prototype.evaluators.evaluate_contingency_screening import _contingency_result


def solve_case(case: dict[str, Any]) -> dict[str, Any]:
    """Rank contingencies by surrogate severity and flag islanding outages."""
    results = {
        contingency["id"]: _contingency_result(case, contingency)
        for contingency in case.get("contingencies", [])
    }
    ranking = sorted(
        results,
        key=lambda cid: (results[cid]["critical"], results[cid]["max_loading_pct"]),
        reverse=True,
    )
    islanding_flags = {cid: result["islanding"] for cid, result in results.items() if result["islanding"]}
    return {
        "ranking": ranking,
        "islanding_flags": islanding_flags,
        "rationale": "Rank by public surrogate severity: islanding/overload criticality and maximum post-contingency loading.",
    }
