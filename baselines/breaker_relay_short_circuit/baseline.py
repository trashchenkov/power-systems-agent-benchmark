from __future__ import annotations

from typing import Any

from prototype.evaluators.evaluate_breaker_relay_short_circuit import solve_nominal_selection


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    return solve_nominal_selection(task)
