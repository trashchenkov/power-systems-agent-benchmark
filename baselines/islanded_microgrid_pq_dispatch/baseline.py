from __future__ import annotations

from typing import Any

from prototype.evaluators.evaluate_islanded_microgrid_pq_dispatch import solve_case as _solve_case


def solve_case(task: dict[str, Any]) -> dict[str, Any]:
    return _solve_case(task)
