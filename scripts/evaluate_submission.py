"""Generic evaluator dispatch for public benchmark submissions."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

EVALUATOR_MODULE_BY_FAMILY = {
    "bess_ancillary_response": "prototype.evaluators.evaluate_bess_ancillary_response",
    "breaker_relay_short_circuit": "prototype.evaluators.evaluate_breaker_relay_short_circuit",
    "cable_ampacity_sizing": "prototype.evaluators.evaluate_cable_ampacity_sizing",
    "commercial_pv_lcoe_uncertainty": "prototype.evaluators.evaluate_commercial_pv_lcoe_uncertainty",
    "contingency_screening": "prototype.evaluators.evaluate_contingency_screening",
    "corrective_transmission_switching": "prototype.evaluators.evaluate_corrective_transmission_switching",
    "critical_clearing_time": "prototype.evaluators.evaluate_critical_clearing_time",
    "dispatch_uncertainty": "prototype.evaluators.evaluate_dispatch_uncertainty",
    "distance_protection_settings": "prototype.evaluators.evaluate_distance_protection_settings",
    "dynamic_thermal_rating": "prototype.evaluators.evaluate_dynamic_thermal_rating",
    "earth_fault_calculation": "prototype.evaluators.evaluate_earth_fault_calculation",
    "en50160_voltage_compliance": "prototype.evaluators.evaluate_en50160_voltage_compliance",
    "ev_v2g_outage_schedule": "prototype.evaluators.evaluate_ev_v2g_outage_schedule",
    "ev_v2g_voltage_support": "prototype.evaluators.evaluate_ev_v2g_voltage_support",
    "fault_section_localization": "prototype.evaluators.evaluate_fault_section_localization",
    "fci_placement": "prototype.evaluators.evaluate_fci_placement",
    "fci_saidi_caidi": "prototype.evaluators.evaluate_fci_saidi_caidi",
    "fdi_state_estimation": "prototype.evaluators.evaluate_fdi_state_estimation",
    "flisr_restoration": "prototype.evaluators.evaluate_flisr_restoration",
    "frt_compliance": "prototype.evaluators.evaluate_frt_compliance",
    "harmonic_ieee519_compliance": "prototype.evaluators.evaluate_harmonic_ieee519_compliance",
    "hydro_thermal_storage_uc": "prototype.evaluators.evaluate_hydro_thermal_storage_uc",
    "ibr_short_circuit_frt": "prototype.evaluators.evaluate_ibr_short_circuit_frt",
    "islanded_microgrid_pq_dispatch": "prototype.evaluators.evaluate_islanded_microgrid_pq_dispatch",
    "mas_frequency_handover": "prototype.evaluators.evaluate_mas_frequency_handover",
    "microgrid_economic_dispatch": "prototype.evaluators.evaluate_microgrid_economic_dispatch",
    "min_synchronous_share": "prototype.evaluators.evaluate_min_synchronous_share",
    "operator_breaker_load_actions": "prototype.evaluators.evaluate_operator_breaker_load_actions",
    "overcurrent_protection": "prototype.evaluators.evaluate_overcurrent_protection",
    "pf_voltage_repair": "prototype.evaluators.evaluate_voltage_repair",
    "power_quality_event_classification": "prototype.evaluators.evaluate_power_quality_event_classification",
    "protected_meter_placement": "prototype.evaluators.evaluate_protected_meter_placement",
    "pv_volt_var": "prototype.evaluators.evaluate_pv_volt_var",
    "rolling_microgrid_dispatch": "prototype.evaluators.evaluate_rolling_microgrid_dispatch",
    "n1_generation_commitment": "prototype.evaluators.evaluate_n1_generation_commitment",
    "three_phase_short_circuit": "prototype.evaluators.evaluate_three_phase_short_circuit",
    "transformer_thermal_loading": "prototype.evaluators.evaluate_transformer_thermal_loading",
    "transient_stability_prediction": "prototype.evaluators.evaluate_transient_stability_prediction",
    "wind_power_forecast": "prototype.evaluators.evaluate_wind_power_forecast",
    "wind_prediction_interval": "prototype.evaluators.evaluate_wind_prediction_interval",
    "ybus_construction": "prototype.evaluators.evaluate_ybus_construction",
}

@dataclass(frozen=True)
class PublicCase:
    family: str
    split: str
    case_id: str
    task_path: Path
    sample_submission_path: Path | None


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover_executable_cases(root: Path, splits: tuple[str, ...] = ("public",)) -> list[PublicCase]:
    """Return cases from requested splits whose family has a registered evaluator."""
    cases: list[PublicCase] = []
    for split in splits:
        for task_path in sorted(root.glob(f"tasks/*/{split}/case_*/task.json")):
            family = task_path.parts[-4]
            if family not in EVALUATOR_MODULE_BY_FAMILY:
                continue
            sample = task_path.with_name("sample_submission.json")
            cases.append(
                PublicCase(
                    family=family,
                    split=split,
                    case_id=task_path.parent.name,
                    task_path=task_path,
                    sample_submission_path=sample if sample.exists() else None,
                )
            )
    return sorted(cases, key=lambda case: (case.family, case.split, case.case_id))


NORMALIZATION_TOLERANCE = 1e-6


def _dispatch_raw(module: Any, task: dict[str, Any], task_path: Path, submission_path: Path) -> dict[str, Any]:
    if hasattr(module, "evaluate_files"):
        return module.evaluate_files(task_path, submission_path)
    if hasattr(module, "evaluate_case"):
        return module.evaluate_case(task, load_json(submission_path))
    raise ValueError(f"Evaluator module lacks evaluate_files/evaluate_case: {module.__name__}")


def reference_optimum(family: str, task: dict[str, Any]) -> float | None:
    """Score the family's reference solver on this task, i.e. the achievable
    optimum used to normalize the score. Returns None if it cannot be computed.

    The reference solver is required to be optimal, so this is the maximum score
    any feasible solution can earn; the per-task score is reported relative to it
    so that an optimal answer scores 1.0 even on continuous-objective tasks.
    """
    try:
        baseline = importlib.import_module(f"baselines.{family}.baseline")
        solution = baseline.solve_case(task)
        module = importlib.import_module(EVALUATOR_MODULE_BY_FAMILY[family])
        if hasattr(module, "evaluate_case"):
            result = module.evaluate_case(task, solution)
        else:  # evaluate_files-only module: round-trip through a temporary file
            import tempfile

            with tempfile.TemporaryDirectory() as tmp:
                tp = Path(tmp) / "task.json"
                sp = Path(tmp) / "submission.json"
                tp.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")
                sp.write_text(json.dumps(solution, ensure_ascii=False), encoding="utf-8")
                result = module.evaluate_files(tp, sp)
        score = float(result.get("score", 0.0))
        return score if score > 0.0 else None
    except Exception:
        return None


def evaluate_submission_file(task_path: Path, submission_path: Path) -> dict[str, Any]:
    task = load_json(task_path)
    family = task.get("family")
    if family not in EVALUATOR_MODULE_BY_FAMILY:
        raise ValueError(f"No evaluator registered for family: {family}")
    module = importlib.import_module(EVALUATOR_MODULE_BY_FAMILY[family])
    result = _dispatch_raw(module, task, task_path, submission_path)

    # Normalize the score against the reference optimum so that 1.0 means optimal
    # on every task. The reference solver is optimal, so an agent cannot exceed it;
    # if one does, the reference is not optimal on this case — flag it as a defect
    # and clamp rather than report a score above one.
    absolute = float(result.get("score", 0.0))
    optimum = reference_optimum(family, task)
    result["absolute_score"] = round(absolute, 6)
    if optimum is None:
        result["reference_optimum"] = None
        result["reference_unavailable"] = True
    else:
        result["reference_optimum"] = round(optimum, 6)
        if absolute > optimum + NORMALIZATION_TOLERANCE:
            result["reference_suboptimal"] = True
            result["score"] = 1.0
        else:
            result["score"] = round(min(1.0, absolute / optimum), 6)
    return result


def result_row(task_path: Path, submission_path: Path, result: dict[str, Any]) -> dict[str, Any]:
    task = load_json(task_path)
    return {
        "family": task.get("family"),
        "split": task_path.parts[-3],
        "task_id": task.get("task_id"),
        "case_id": task_path.parent.name,
        "task_path": str(task_path),
        "submission_path": str(submission_path),
        "result": result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate one benchmark submission with family-based evaluator dispatch.")
    parser.add_argument("task", type=Path, help="Path to task.json")
    parser.add_argument("submission", type=Path, help="Path to submission JSON")
    parser.add_argument("--jsonl-row", action="store_true", help="Emit a result row with task/submission metadata")
    args = parser.parse_args(argv)

    result = evaluate_submission_file(args.task, args.submission)
    payload = result_row(args.task, args.submission, result) if args.jsonl_row else result
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if result.get("feasible") else 1


if __name__ == "__main__":
    raise SystemExit(main())
