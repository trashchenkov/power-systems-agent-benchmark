from __future__ import annotations

from typing import Any

from prototype.evaluators.evaluate_ybus_construction import compute_ybus


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    result = compute_ybus(task)
    return {
        "buses": result["buses"],
        "ybus": result["ybus"],
        "rationale": "Built Ybus by summing series admittances, half line-charging susceptance at terminal buses, and explicit shunts."
    }
