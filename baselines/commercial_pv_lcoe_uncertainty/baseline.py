from __future__ import annotations
from typing import Any
from prototype.evaluators.evaluate_commercial_pv_lcoe_uncertainty import solve_case as _solve_case

def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    return _solve_case(task)
