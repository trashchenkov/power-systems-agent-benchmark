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
    "commercial_pv_lcoe_uncertainty": "prototype.evaluators.evaluate_commercial_pv_lcoe_uncertainty",
    "contingency_screening": "prototype.evaluators.evaluate_contingency_screening",
    "corrective_transmission_switching": "prototype.evaluators.evaluate_corrective_transmission_switching",
    "critical_clearing_time": "prototype.evaluators.evaluate_critical_clearing_time",
    "dispatch_uncertainty": "prototype.evaluators.evaluate_dispatch_uncertainty",
    "distance_protection_settings": "prototype.evaluators.evaluate_distance_protection_settings",
    "dynamic_thermal_rating": "prototype.evaluators.evaluate_dynamic_thermal_rating",
    "earth_fault_calculation": "prototype.evaluators.evaluate_earth_fault_calculation",
    "electric_boiler_capacity_sizing": "prototype.evaluators.evaluate_electric_boiler_capacity_sizing",
    "electric_boiler_step_control": "prototype.evaluators.evaluate_electric_boiler_step_control",
    "en50160_voltage_compliance": "prototype.evaluators.evaluate_en50160_voltage_compliance",
    "ev_v2g_outage_schedule": "prototype.evaluators.evaluate_ev_v2g_outage_schedule",
    "ev_v2g_voltage_support": "prototype.evaluators.evaluate_ev_v2g_voltage_support",
    "fault_section_localization": "prototype.evaluators.evaluate_fault_section_localization",
    "fci_placement": "prototype.evaluators.evaluate_fci_placement",
    "fci_saidi_caidi": "prototype.evaluators.evaluate_fci_saidi_caidi",
    "fdi_state_estimation": "prototype.evaluators.evaluate_fdi_state_estimation",
    "flisr_restoration": "prototype.evaluators.evaluate_flisr_restoration",
    "frt_compliance": "prototype.evaluators.evaluate_frt_compliance",
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
    "pv_soft_cost_sobol": "prototype.evaluators.evaluate_pv_soft_cost_sobol",
    "pv_volt_var": "prototype.evaluators.evaluate_pv_volt_var",
    "rolling_microgrid_dispatch": "prototype.evaluators.evaluate_rolling_microgrid_dispatch",
    "scuc_n1": "prototype.evaluators.evaluate_scuc_n1",
    "three_phase_short_circuit": "prototype.evaluators.evaluate_three_phase_short_circuit",
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


def evaluate_submission_file(task_path: Path, submission_path: Path) -> dict[str, Any]:
    task = load_json(task_path)
    family = task.get("family")
    if family not in EVALUATOR_MODULE_BY_FAMILY:
        raise ValueError(f"No evaluator registered for family: {family}")
    module = importlib.import_module(EVALUATOR_MODULE_BY_FAMILY_BY_FAMILY := EVALUATOR_MODULE_BY_FAMILY[family])
    if hasattr(module, "evaluate_files"):
        return module.evaluate_files(task_path, submission_path)
    if hasattr(module, "evaluate_case"):
        return module.evaluate_case(task, load_json(submission_path))
    raise ValueError(f"Evaluator module lacks evaluate_files/evaluate_case: {EVALUATOR_MODULE_BY_FAMILY_BY_FAMILY}")


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
