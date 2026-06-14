"""Least-effort Volt-VAR curve baseline (reference optimum) for PV inverter tasks.

The evaluator keeps every timestep voltage inside the band and scores a solution
by its total reactive effort ``sum |q_command|`` (less effort scores higher).
This solver returns the monotonic curve that achieves that band feasibility with
the least possible effort, i.e. the true optimum.

Why it is optimal over *all* valid curves, not just this one: the evaluator only
ever reads the curve at the timestep base voltages. Any valid Volt-VAR curve is
monotone non-increasing, so the q_fractions it induces at increasing voltages
form a monotone non-increasing vector inside ``[-1, 1]``; conversely any such
vector is realisable by a curve. The score depends only on that vector, so
minimising the effort over monotone, box-bounded, band-feasible vectors
minimises it over every curve. The minimisation below is exact.
"""

from __future__ import annotations

import math
from typing import Any


def _q_limit(step: dict[str, Any]) -> float:
    kva = float(step["inverter_kva"])
    kw = float(step["pv_kw"])
    return math.sqrt(max(0.0, kva * kva - kw * kw))


def _isotonic_l1_to_zero(weights: list[float], lo: list[float], hi: list[float]) -> list[float]:
    """Minimise ``sum(weights_i * |f_i|)`` subject to ``f`` non-increasing and
    ``f_i in [lo_i, hi_i]``.

    The objective is separable, convex and piecewise-linear with its only kink at
    zero, so an optimum exists with every ``f_i`` drawn from the finite candidate
    set ``{0} u {lo_i} u {hi_i}``. A left-to-right dynamic program over that set,
    enforcing ``f_{i-1} >= f_i``, finds it exactly.
    """
    n = len(weights)
    if n == 0:
        return []
    cands = sorted({0.0, *lo, *hi})
    m = len(cands)
    INF = float("inf")
    eps = 1e-12

    # dp[i][c] = least cost for positions 0..i with f_i = cands[c].
    dp = [[INF] * m for _ in range(n)]
    parent = [[-1] * m for _ in range(n)]
    for c, val in enumerate(cands):
        if lo[0] - eps <= val <= hi[0] + eps:
            dp[0][c] = weights[0] * abs(val)
    for i in range(1, n):
        # suffix_min[c] = (best dp[i-1][c'] for c' >= c, its index): f_{i-1} >= f_i.
        best_cost = INF
        best_idx = -1
        suffix = [(INF, -1)] * m
        for c in range(m - 1, -1, -1):
            if dp[i - 1][c] < best_cost:
                best_cost = dp[i - 1][c]
                best_idx = c
            suffix[c] = (best_cost, best_idx)
        for c, val in enumerate(cands):
            if not (lo[i] - eps <= val <= hi[i] + eps):
                continue
            prev_cost, prev_idx = suffix[c]
            if prev_idx < 0:
                continue
            dp[i][c] = weights[i] * abs(val) + prev_cost
            parent[i][c] = prev_idx

    end = min(range(m), key=lambda c: dp[n - 1][c])
    if dp[n - 1][end] == INF:
        raise ValueError("no feasible monotone Volt-VAR selection exists")
    fracs = [0.0] * n
    c = end
    for i in range(n - 1, -1, -1):
        fracs[i] = cands[c]
        c = parent[i][c]
    return fracs


def solve_case(case: dict[str, Any]) -> dict[str, Any]:
    limits = case.get("voltage_limits_pu", {})
    v_min = float(limits.get("min", 0.95))
    v_max = float(limits.get("max", 1.05))

    # Per-timestep feasibility interval on q_fraction, with its effort weight L.
    nodes: list[tuple[float, float, float, float]] = []  # (voltage, weight, lo, hi)
    for step in case.get("timesteps", []):
        v = float(step["base_voltage_pu"])
        s = float(step["voltage_sensitivity_pu_per_kvar"])
        cap = _q_limit(step)
        if cap <= 0.0:
            # No reactive capability: q_command is fixed at 0, so voltage is fixed.
            if not (v_min <= v <= v_max):
                raise ValueError(f"timestep at {v} pu cannot be corrected (no reactive capability)")
            nodes.append((v, 0.0, -1.0, 1.0))
            continue
        if s <= 0.0:
            raise ValueError("voltage sensitivity must be positive")
        # q_command in [(v_min - v)/s, (v_max - v)/s]; divide by cap for q_fraction.
        lo = max(-1.0, (v_min - v) / s / cap)
        hi = min(1.0, (v_max - v) / s / cap)
        if lo > hi + 1e-12:
            raise ValueError(f"timestep at {v} pu has no feasible q_fraction")
        nodes.append((v, cap, min(lo, hi), hi))

    if not nodes:
        raise ValueError("case has no timesteps")

    # The curve is a function of voltage: merge timesteps sharing a voltage.
    merged: dict[float, tuple[float, float, float]] = {}
    for v, w, lo, hi in nodes:
        key = round(v, 9)
        if key in merged:
            w0, lo0, hi0 = merged[key]
            merged[key] = (w0 + w, max(lo0, lo), min(hi0, hi))
        else:
            merged[key] = (w, lo, hi)
    items = sorted(merged.items())
    for _, (w, lo, hi) in items:
        if lo > hi + 1e-12:
            raise ValueError("conflicting feasibility at a shared voltage")

    voltages = [k for k, _ in items]
    weights = [w for _, (w, lo, hi) in items]
    los = [min(lo, hi) for _, (w, lo, hi) in items]
    his = [hi for _, (w, lo, hi) in items]

    fracs = _isotonic_l1_to_zero(weights, los, his)

    curve = [{"voltage_pu": voltages[i], "q_fraction": fracs[i]} for i in range(len(items))]
    if len(curve) == 1:
        v0 = curve[0]["voltage_pu"]
        q0 = curve[0]["q_fraction"]
        curve = [
            {"voltage_pu": v0 - 0.01, "q_fraction": q0},
            {"voltage_pu": v0 + 0.01, "q_fraction": q0},
        ]
    return {
        "volt_var_curve": curve,
        "rationale": "Least reactive-effort monotonic Volt-VAR curve holding every timestep voltage within the band.",
    }
