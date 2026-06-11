"""Run all public baseline solvers and evaluate their submissions."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

from scripts.evaluate_submission import discover_executable_cases, evaluate_submission_file, load_json, result_row

BASELINE_MODULE_BY_FAMILY = {
    "bess_ancillary_response": "baselines.bess_ancillary_response.baseline",
    "breaker_relay_short_circuit": "baselines.breaker_relay_short_circuit.baseline",
    "cable_ampacity_sizing": "baselines.cable_ampacity_sizing.baseline",
    "commercial_pv_lcoe_uncertainty": "baselines.commercial_pv_lcoe_uncertainty.baseline",
    "contingency_screening": "baselines.contingency_screening.baseline",
    "corrective_transmission_switching": "baselines.corrective_transmission_switching.baseline",
    "critical_clearing_time": "baselines.critical_clearing_time.baseline",
    "dispatch_uncertainty": "baselines.dispatch_uncertainty.baseline",
    "distance_protection_settings": "baselines.distance_protection_settings.baseline",
    "dynamic_thermal_rating": "baselines.dynamic_thermal_rating.baseline",
    "earth_fault_calculation": "baselines.earth_fault_calculation.baseline",
    "en50160_voltage_compliance": "baselines.en50160_voltage_compliance.baseline",
    "ev_v2g_outage_schedule": "baselines.ev_v2g_outage_schedule.baseline",
    "ev_v2g_voltage_support": "baselines.ev_v2g_voltage_support.baseline",
    "fault_section_localization": "baselines.fault_section_localization.baseline",
    "fci_placement": "baselines.fci_placement.baseline",
    "fci_saidi_caidi": "baselines.fci_saidi_caidi.baseline",
    "fdi_state_estimation": "baselines.fdi_state_estimation.baseline",
    "flisr_restoration": "baselines.flisr_restoration.baseline",
    "frt_compliance": "baselines.frt_compliance.baseline",
    "harmonic_ieee519_compliance": "baselines.harmonic_ieee519_compliance.baseline",
    "hydro_thermal_storage_uc": "baselines.hydro_thermal_storage_uc.baseline",
    "ibr_short_circuit_frt": "baselines.ibr_short_circuit_frt.baseline",
    "islanded_microgrid_pq_dispatch": "baselines.islanded_microgrid_pq_dispatch.baseline",
    "mas_frequency_handover": "baselines.mas_frequency_handover.baseline",
    "microgrid_economic_dispatch": "baselines.microgrid_economic_dispatch.baseline",
    "min_synchronous_share": "baselines.min_synchronous_share.baseline",
    "operator_breaker_load_actions": "baselines.operator_breaker_load_actions.baseline",
    "overcurrent_protection": "baselines.overcurrent_protection.baseline",
    "pf_voltage_repair": "baselines.pf_voltage_repair.baseline",
    "power_quality_event_classification": "baselines.power_quality_event_classification.baseline",
    "protected_meter_placement": "baselines.protected_meter_placement.baseline",
    "pv_volt_var": "baselines.pv_volt_var.baseline",
    "rolling_microgrid_dispatch": "baselines.rolling_microgrid_dispatch.baseline",
    "n1_generation_commitment": "baselines.n1_generation_commitment.baseline",
    "three_phase_short_circuit": "baselines.three_phase_short_circuit.baseline",
    "transformer_thermal_loading": "baselines.transformer_thermal_loading.baseline",
    "transient_stability_prediction": "baselines.transient_stability_prediction.baseline",
    "wind_power_forecast": "baselines.wind_power_forecast.baseline",
    "wind_prediction_interval": "baselines.wind_prediction_interval.baseline",
    "ybus_construction": "baselines.ybus_construction.baseline",
}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def solve_with_baseline(family: str, task: dict[str, Any]) -> dict[str, Any]:
    if family not in BASELINE_MODULE_BY_FAMILY:
        if "baseline_submission" in task:
            return task["baseline_submission"]
        raise ValueError(f"No baseline registered for family: {family}")
    module = importlib.import_module(BASELINE_MODULE_BY_FAMILY[family])
    if not hasattr(module, "solve_case"):
        raise ValueError(f"Baseline module lacks solve_case: {BASELINE_MODULE_BY_FAMILY[family]}")
    return module.solve_case(task)


def run_public_baselines(root: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    submissions_dir = out_dir / "submissions"
    rows = []
    for case in discover_executable_cases(root):
        task = load_json(case.task_path)
        submission = solve_with_baseline(case.family, task)
        submission_path = submissions_dir / f"{case.family}__{case.case_id}.json"
        _write_json(submission_path, submission)
        result = evaluate_submission_file(case.task_path, submission_path)
        row = result_row(case.task_path, submission_path, result)
        row["agent"] = "public_baseline"
        rows.append(row)

    results_path = out_dir / "results.jsonl"
    with results_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {
        "agent": "public_baseline",
        "case_count": len(rows),
        "feasible_count": sum(1 for row in rows if row["result"].get("feasible")),
        "mean_score": round(
            sum(float(row["result"].get("score", 0.0)) for row in rows) / len(rows), 6
            if rows
            else 0.0,
        ),
        "results_path": str(results_path),
        "submissions_dir": str(submissions_dir),
    }
    _write_json(out_dir / "summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run all public baselines and evaluate them.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Benchmark repository root")
    parser.add_argument("--out", type=Path, required=True, help="Output run directory")
    args = parser.parse_args(argv)
    summary = run_public_baselines(args.root, args.out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["feasible_count"] == summary["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
