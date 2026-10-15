"""Summarize repeated agent runs: run-to-run variability and pass@k-style metrics.

Reads `<run>/rep_*/results.jsonl` written by `scripts/run_repeated_agent.py`. For every
case it reports the mean and standard deviation of the score over the n repeats, the
feasible and perfect counts, and the unbiased estimators (Chen et al., 2021)

    pass@k = 1 - C(n - c, k) / C(n, k)      (at least one of k draws succeeds)
    pass^k = C(c, k) / C(n, k)              (all k draws succeed)

where c is the number of successful repeats. Success is a perfect score (score == 1 after
normalization), matching the "perfect" count of the paper; feasible-based variants are
reported as well. Run-level means (one per repeat, over all cases) give the spread of the
aggregate score that a single-run table would hide.
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from math import comb
from pathlib import Path
from typing import Any

PERFECT_EPS = 1e-9


def pass_at_k(n: int, c: int, k: int) -> float:
    if k > n:
        raise ValueError("k must not exceed the number of repeats")
    if n - c < k:
        return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    if k > n:
        raise ValueError("k must not exceed the number of repeats")
    return comb(c, k) / comb(n, k)


def _sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def load_repeats(run_dir: Path) -> dict[str, list[dict[str, Any]]]:
    rows_by_rep: dict[str, list[dict[str, Any]]] = {}
    for rep in sorted(run_dir.glob("rep_*"), key=lambda p: int(p.name.split("_")[1])):
        path = rep / "results.jsonl"
        if path.exists():
            rows_by_rep[rep.name] = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not rows_by_rep:
        raise SystemExit(f"no rep_*/results.jsonl under {run_dir}")
    return rows_by_rep


def summarize(run_dir: Path, ks: list[int]) -> dict[str, Any]:
    rows_by_rep = load_repeats(run_dir)
    n_reps = len(rows_by_rep)
    per_case: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for rows in rows_by_rep.values():
        for row in rows:
            per_case[(row["family"], row["split"], row["case_id"])].append(row)

    cases = []
    for (family, split, case_id), rows in sorted(per_case.items()):
        scores = [float(r["result"].get("score", 0.0)) for r in rows]
        feasible = sum(1 for r in rows if r["result"].get("feasible"))
        perfect = sum(1 for s in scores if s >= 1.0 - PERFECT_EPS)
        n = len(rows)
        entry = {
            "family": family,
            "split": split,
            "case_id": case_id,
            "n": n,
            "mean_score": round(statistics.fmean(scores), 6),
            "sd_score": round(_sd(scores), 6),
            "min_score": round(min(scores), 6),
            "max_score": round(max(scores), 6),
            "feasible": feasible,
            "perfect": perfect,
            "no_submission": sum(1 for r in rows if r.get("selected_attempt") is None),
            "infra_unresolved": sum(1 for r in rows if r["result"].get("infra_unresolved")),
        }
        for k in ks:
            if k <= n:
                entry[f"pass@{k}"] = round(pass_at_k(n, perfect, k), 6)
                entry[f"pass^{k}"] = round(pass_hat_k(n, perfect, k), 6)
        cases.append(entry)

    run_means = {
        rep: round(statistics.fmean(float(r["result"].get("score", 0.0)) for r in rows), 6)
        for rep, rows in rows_by_rep.items()
    }
    means = list(run_means.values())
    overall: dict[str, Any] = {
        "repeats": n_reps,
        "cases": len(cases),
        "run_means": run_means,
        "mean_of_run_means": round(statistics.fmean(means), 6),
        "sd_of_run_means": round(_sd(means), 6),
        "min_run_mean": min(means),
        "max_run_mean": max(means),
        "mean_within_case_sd": round(statistics.fmean(c["sd_score"] for c in cases), 6),
        "cases_with_varying_score": sum(1 for c in cases if c["max_score"] - c["min_score"] > PERFECT_EPS),
    }
    for k in ks:
        vals = [c[f"pass@{k}"] for c in cases if f"pass@{k}" in c]
        hats = [c[f"pass^{k}"] for c in cases if f"pass^{k}" in c]
        if vals:
            overall[f"pass@{k}"] = round(statistics.fmean(vals), 6)
            overall[f"pass^{k}"] = round(statistics.fmean(hats), 6)
    return {"run_dir": str(run_dir), "overall": overall, "cases": cases}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize repeated agent runs.")
    parser.add_argument("run_dirs", type=Path, nargs="+", help="Directories containing rep_*/results.jsonl")
    parser.add_argument("--k", type=int, nargs="+", default=[1, 3, 5])
    parser.add_argument("--out", type=Path, default=None, help="Write JSON summary here (single run dir only)")
    args = parser.parse_args(argv)
    summaries = [summarize(d, args.k) for d in args.run_dirs]
    if args.out:
        if len(summaries) != 1:
            raise SystemExit("--out requires exactly one run directory")
        args.out.write_text(json.dumps(summaries[0], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for s in summaries:
        print(json.dumps({"run_dir": s["run_dir"], **s["overall"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
