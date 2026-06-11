"""Evaluator for IEEE 519-style harmonic compliance at a point of common coupling.

The agent must pick the correct current-distortion limit row from the published
table by the short-circuit ratio Isc/IL, compute TDD and per-harmonic current
ratios against the maximum demand current IL, compute voltage THD, and report
violation lists plus the overall verdict. Both compliant and non-compliant
cases are valid benchmark instances.
"""
from __future__ import annotations
import json, math
from pathlib import Path
TOL_ABS=0.01
TOL_REL=1e-4
ALLOWED={"isc_over_il","tdd_pct","current_violations","voltage_thd_pct","voltage_violations","compliant","rationale"}

def _spec(task):
    inputs=task.get("public_inputs",{})
    return inputs.get("harmonic_case", task.get("harmonic_case"))

def _limit_row(spec, ratio):
    for row in spec["current_limit_table"]:
        if ratio < float(row["isc_il_below"]):
            return row
    return spec["current_limit_table"][-1]

def _bucket_limit(row, harmonic):
    h=int(harmonic)
    if h < 11: return float(row["h_below_11_pct"])
    if h < 17: return float(row["h_11_to_17_pct"])
    if h < 23: return float(row["h_17_to_23_pct"])
    if h < 35: return float(row["h_23_to_35_pct"])
    return float(row["h_35_up_pct"])

def _expected(task):
    spec=_spec(task)
    il=float(spec["pcc"]["max_demand_current_a"])
    ratio=float(spec["pcc"]["short_circuit_current_ka"])*1000.0/il
    row=_limit_row(spec, ratio)
    currents=spec["measured"]["harmonic_currents_a"]
    tdd=math.sqrt(sum(float(v)**2 for v in currents.values()))/il*100.0
    current_violations=[]
    if tdd>float(row["tdd_pct"]):
        current_violations.append("tdd")
    for h in sorted(currents, key=int):
        pct=float(currents[h])/il*100.0
        if pct>_bucket_limit(row, h):
            current_violations.append(h)
    voltages=spec["measured"]["harmonic_voltages_pct"]
    vthd=math.sqrt(sum(float(v)**2 for v in voltages.values()))
    voltage_violations=[]
    if vthd>float(spec["voltage_limits"]["thd_pct"]):
        voltage_violations.append("thd")
    for h in sorted(voltages, key=int):
        if float(voltages[h])>float(spec["voltage_limits"]["individual_pct"]):
            voltage_violations.append(h)
    return {
        "isc_over_il": round(ratio,6),
        "tdd_pct": round(tdd,6),
        "current_violations": current_violations,
        "voltage_thd_pct": round(vthd,6),
        "voltage_violations": voltage_violations,
        "compliant": not current_violations and not voltage_violations,
    }

def _close(a,b): return abs(float(a)-float(b))<=max(TOL_ABS,TOL_REL*max(1.0,abs(float(b))))
def evaluate_case(task, submission):
    exp=_expected(task); violations=[]
    extra=set(submission)-ALLOWED
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    for key in ("isc_over_il","tdd_pct","voltage_thd_pct"):
        if key not in submission: violations.append(f"missing answer field: {key}"); continue
        try: ok=_close(submission[key],exp[key])
        except (TypeError,ValueError): violations.append(f"{key} must be numeric"); continue
        if not ok: violations.append(f"{key} expected {exp[key]} got {submission[key]}")
    for key in ("current_violations","voltage_violations"):
        got=submission.get(key)
        if not isinstance(got,list) or sorted(str(x) for x in got)!=sorted(str(x) for x in exp[key]):
            violations.append(f"{key} expected {sorted(exp[key])} got {got}")
    if submission.get("compliant") is not exp["compliant"]:
        violations.append(f"compliant expected {exp['compliant']} got {submission.get('compliant')}")
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
