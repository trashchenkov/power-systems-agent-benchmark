"""Prepare portable task packets for arbitrary coding/tool agents."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

from scripts.evaluate_submission import discover_executable_cases, load_json

INSTRUCTIONS_TEMPLATE = """# Agent task packet

You are solving one executable power-systems benchmark task.

## Goal

Read `task.json` in this directory. Use the public inputs/specification to compute the answer. Write exactly one JSON file named `submission.json` in this same directory.

## Rules

- Treat this as an executable agent task, not a copy task: derive the answer from `public_inputs`, `objective`, `hard_constraints`, and `submission_schema`.
- Do not modify `task.json`.
- Do not inspect files outside this packet directory. The packet intentionally omits hidden expected answers and evaluator internals.
- Do not search for benchmark evaluator code, baseline submissions, sample submissions, or hidden answers.
- You may create and run a short helper script/scratch calculation inside this packet directory if useful.
- Output must be valid JSON, not Markdown.
- Include only fields compatible with the task's `submission_schema`; optional `rationale` is free text and is not required to match any hidden string.
- After writing `submission.json`, stop.

## Expected output path

`{packet_submission_path}`
"""

HIDDEN_INSTRUCTIONS_TEMPLATE = """# Agent task packet

You are solving one sealed executable power-systems benchmark task.

## Goal

Read `task.json` in this directory. Write exactly one JSON file named `submission.json` in this same directory.

## Rules

- Do not modify `task.json`.
- Use only the inputs, objective, hard constraints, and submission schema in `task.json`.
- Do not inspect files outside this packet directory.
- Do not search for benchmark evaluator code, baseline submissions, sample submissions, or hidden answers.
- You may create and run a short helper script/scratch calculation inside this packet directory if useful.
- Output must be valid JSON, not Markdown.
- Include only fields compatible with the task's `submission_schema`; optional `rationale` is free text and is not required to match any hidden string.
- After writing `submission.json`, stop.

## Expected output path

`{packet_submission_path}`
"""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


GENERIC_SCALAR_TYPES = {
    "breaker_relay_values",
    "cct_s",
    "ampacity_a",
    "capacity_kw",
    "control_steps",
    "faulted_section",
    "reliability_indices",
    "fault_current_profile",
    "min_share_pct",
    "operator_actions",
    "sensitivity_ranking",
    "fault_current_ka",
    "forecast_mw",
}

GENERIC_PLAN_TYPES = {
    "response_plan",
    "switching_plan",
    "dispatch_mw",
    "charging_schedule",
    "ev_reactive_dispatch",
    "commitment_plan",
    "pq_dispatch",
    "economic_dispatch",
    "rolling_dispatch",
    "scuc_schedule",
}


def _candidate_plan(answer: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(answer, dict):
        return {}
    low = {k: v - 2 for k, v in answer.items() if isinstance(v, (int, float))}
    high = {k: v + 2 for k, v in answer.items() if isinstance(v, (int, float))}
    return {
        "type": "choose_min_cost_feasible_schedule",
        "decision_variables": list(answer.keys()),
        "candidates": [
            {"name": "under_supply", "values": low, "feasible": False, "cost": 0},
            {"name": "balanced", "values": answer, "feasible": True, "cost": 10},
            {"name": "over_supply", "values": high, "feasible": True, "cost": 15},
        ],
        "rule": "Select the feasible candidate with minimum cost and return its values as answer.",
    }


def _generic_calculation_spec(task: dict[str, Any]) -> dict[str, Any] | None:
    """Add public, executable instructions for lightweight generic cases.

    The source task keeps evaluator-only expected answers for deterministic
    scoring, but agent packets must expose a derivation problem instead of the
    answer itself. These specs are intentionally simple public surrogates; they
    are for harness/agent smoke tests until simulator-backed hidden cases replace
    them.
    """
    answer_type = task.get("answer_type")
    expected = task.get("expected_submission") or task.get("baseline_submission") or {}
    answer = expected.get("answer") if isinstance(expected, dict) else None
    if answer_type in GENERIC_SCALAR_TYPES:
        return {
            "type": "scalar_formula",
            "formula": "answer = base - index / 4",
            "rounding": "Use normal decimal arithmetic; numeric tolerance is 1e-6.",
            "inputs": "public_inputs.surrogate_parameters.index/base/limit",
        }
    if answer_type in GENERIC_PLAN_TYPES and isinstance(answer, dict):
        return _candidate_plan(answer)
    if answer_type in {"compliance_decision", "handover_decision", "event_class", "stability_label"}:
        return {
            "type": "threshold_classification",
            "rule": "Return 'compliant' when index < limit, otherwise return 'non_compliant'.",
            "inputs": "public_inputs.surrogate_parameters.index/limit",
        }
    if answer_type in {"lcoe_quantiles", "prediction_interval"}:
        return {
            "type": "quantile_interval_formula",
            "formula": {"p10": "base - 2", "p50": "base + 4", "p90": "base + 11"},
            "inputs": "public_inputs.surrogate_parameters.base",
        }
    if answer_type in {"selected_locations", "protected_meters"}:
        return {
            "type": "coverage_selection",
            "candidate_locations": [
                {"id": "n1", "covers": ["f1"], "priority_score": 2},
                {"id": "n2", "covers": ["f1", "f2", "f3"], "priority_score": 8},
                {"id": "n3", "covers": ["f2"], "priority_score": 3},
                {"id": "n5", "covers": ["f4", "f5", "f6"], "priority_score": 7},
            ],
            "budget": 2,
            "required_coverage": ["f1", "f2", "f3", "f4", "f5", "f6"],
            "rule": "Choose up to budget locations that cover every required item; break ties by total priority_score, then lexicographic id order.",
        }
    if answer_type == "sequence_currents":
        return {
            "type": "sequence_current_formula",
            "formula": {"i1_ka": "(base - 6) / 10", "i2_ka": "(index - 17) / 10", "i0_ka": "(limit - 119) / 10"},
            "inputs": "public_inputs.surrogate_parameters.index/base/limit",
        }
    if answer_type == "zones":
        return {
            "type": "distance_zone_formula",
            "line_ohm": 23.0,
            "formula": {"zone1_ohm": "0.8 * line_ohm", "zone2_ohm": "1.291304347826087 * line_ohm", "zone3_ohm": "1.921739130434783 * line_ohm"},
            "rounding": "Round each zone to one decimal place.",
        }
    if answer_type == "ybus_matrix":
        return {
            "type": "two_bus_ybus",
            "series_admittance_pu": 5.0,
            "shunt_admittance_per_bus_pu": 5.0,
            "rule": "For a two-bus line, off-diagonal entries are -series_admittance; diagonal entries are series_admittance + shunt_admittance_per_bus.",
        }
    return None


def redacted_task_for_agent(task: dict[str, Any], split: str) -> dict[str, Any]:
    """Return the task payload visible to an agent packet.

    Agent-facing packets must not disclose evaluator-only answers, even for the
    public split. Public packets get public executable surrogate specs instead.
    """
    visible = json.loads(json.dumps(task))
    for key in (
        "expected_submission",
        "baseline_submission",
        "sample_submission",
        "evaluator_only",
        "ground_truth_state",
    ):
        visible.pop(key, None)
    for measurement in visible.get("measurements", []):
        if isinstance(measurement, dict):
            measurement.pop("ground_truth_attack", None)
    spec = _generic_calculation_spec(task)
    if spec is not None:
        public_inputs = visible.setdefault("public_inputs", {})
        public_inputs["calculation_spec"] = spec
        visible["agent_task_design"] = "public executable surrogate: derive answer from calculation_spec; hidden evaluator retains the oracle"
    return visible


def prepare_agent_tasks(root: Path, out_dir: Path, splits: tuple[str, ...] = ("public",)) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for case in discover_executable_cases(root, splits=splits):
        packet_name = f"{case.family}__{case.split}__{case.case_id}"
        packet_dir = out_dir / packet_name
        packet_dir.mkdir(parents=True, exist_ok=True)
        task = load_json(case.task_path)
        packet_task = redacted_task_for_agent(task, case.split)
        _write_json(packet_dir / "task.json", packet_task)
        template = HIDDEN_INSTRUCTIONS_TEMPLATE if case.split == "hidden" else INSTRUCTIONS_TEMPLATE
        instructions = template.format(
            task_path=case.task_path,
            packet_submission_path=packet_dir / "submission.json",
        )
        (packet_dir / "instructions.md").write_text(instructions, encoding="utf-8")
        manifest.append(
            {
                "family": case.family,
                "split": case.split,
                "case_id": case.case_id,
                "task_id": task.get("task_id"),
                "packet_dir": str(packet_dir),
                "task_path": str(packet_dir / "task.json"),
                "expected_submission_path": str(packet_dir / "submission.json"),
            }
        )
    summary = {"case_count": len(manifest), "packets": manifest}
    _write_json(out_dir / "manifest.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create agent-agnostic public task packets.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Benchmark repository root")
    parser.add_argument("--out", type=Path, required=True, help="Output directory for task packets")
    parser.add_argument(
        "--split",
        action="append",
        choices=("public", "hidden"),
        default=None,
        help="Task split to include. Repeat for multiple splits. Defaults to public.",
    )
    args = parser.parse_args(argv)
    summary = prepare_agent_tasks(args.root, args.out, splits=tuple(args.split or ["public"]))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
