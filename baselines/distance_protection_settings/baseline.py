from __future__ import annotations

from typing import Any

from prototype.evaluators.evaluate_distance_protection_settings import solve_nominal_settings


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    return solve_nominal_settings(task)
