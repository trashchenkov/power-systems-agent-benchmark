"""Evaluator for LV cable cross-section selection.

Three independent checks per catalog candidate, smallest passing section wins:

1. continuous current: base ampacity derated by ambient and grouping factors
   must cover the design current;
2. voltage drop: dU = sqrt(3) * I * L * (R*cos(phi) + X*sin(phi)) must stay
   within the percentage limit of the system voltage;
3. short-circuit withstand (adiabatic): S >= I_fault * sqrt(t) / k.
"""
from __future__ import annotations
import json, math
from pathlib import Path
TOL_ABS=0.01
TOL_REL=1e-3
ALLOWED={"selected_cross_section_mm2","selected_derated_ampacity_a","selected_voltage_drop_pct","min_thermal_section_mm2","rationale"}

def _spec(task):
    inputs=task.get("public_inputs",{})
    return inputs.get("cable_sizing_case", task.get("cable_sizing_case"))

def _candidate_checks(spec, candidate):
    derate=spec["derating"]
    derated=candidate["base_ampacity_a"]*derate["ambient_factor"]*derate["grouping_factor"]
    pf=float(spec["power_factor"])
    sin_phi=math.sqrt(max(0.0,1.0-pf*pf))
    drop_v=math.sqrt(3.0)*spec["design_current_a"]*(spec["length_m"]/1000.0)*(
        candidate["r_ohm_per_km"]*pf+candidate["x_ohm_per_km"]*sin_phi)
    drop_pct=drop_v/float(spec["system_voltage_v"])*100.0
    return derated, drop_pct

def _min_thermal_section(spec):
    fault=spec["fault"]
    return fault["fault_current_ka"]*1000.0*math.sqrt(fault["clearing_time_s"])/fault["k_adiabatic_a_sqrt_s_per_mm2"]

def _expected(task):
    spec=_spec(task)
    s_min=_min_thermal_section(spec)
    chosen=None
    for candidate in sorted(spec["catalog"], key=lambda c: c["cross_section_mm2"]):
        derated, drop_pct=_candidate_checks(spec, candidate)
        ok=(derated>=spec["design_current_a"]
            and drop_pct<=spec["max_voltage_drop_pct"]
            and candidate["cross_section_mm2"]>=s_min)
        if ok:
            chosen=(candidate, derated, drop_pct)
            break
    if chosen is None:
        raise ValueError("no catalog cross-section satisfies all three checks")
    candidate, derated, drop_pct=chosen
    return {
        "selected_cross_section_mm2": candidate["cross_section_mm2"],
        "selected_derated_ampacity_a": round(derated,6),
        "selected_voltage_drop_pct": round(drop_pct,6),
        "min_thermal_section_mm2": round(s_min,6),
    }

def _close(a,b): return abs(float(a)-float(b))<=max(TOL_ABS,TOL_REL*max(1.0,abs(float(b))))
def evaluate_case(task, submission):
    exp=_expected(task); violations=[]
    extra=set(submission)-ALLOWED
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    for key in ("selected_cross_section_mm2","selected_derated_ampacity_a","selected_voltage_drop_pct","min_thermal_section_mm2"):
        if key not in submission: violations.append(f"missing answer field: {key}"); continue
        try: ok=_close(submission[key],exp[key])
        except (TypeError,ValueError): violations.append(f"{key} must be numeric"); continue
        if not ok: violations.append(f"{key} expected {exp[key]} got {submission[key]}")
    feasible=not violations
    return {"task_id":task.get("task_id"),"feasible":feasible,"score":1.0 if feasible else 0.0,"study":exp,"violations":violations}

def evaluate_files(case_path, submission_path):
    task=json.loads(Path(case_path).read_text(encoding="utf-8"))
    sub=json.loads(Path(submission_path).read_text(encoding="utf-8"))
    return evaluate_case(task, sub)

def main():
    import sys
    print(json.dumps(evaluate_files(sys.argv[1], sys.argv[2]), indent=2))
if __name__=="__main__": main()
