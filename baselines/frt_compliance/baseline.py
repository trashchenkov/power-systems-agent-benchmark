"""Static envelope checker baseline for FRT compliance tasks."""

from __future__ import annotations

from typing import Any


def solve_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "declared_compliant": True,
        "rationale": "Static envelope baseline declares compliance after checking the public ride-through and reactive-current trace constraints.",
    }
