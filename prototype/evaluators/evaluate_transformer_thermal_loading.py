"""Evaluator for transformer thermal loading per the IEC 60076-7 exponential model.

Discretized step form of the loading-guide equations for an ONAN unit:

    target_top_oil_rise(K) = dTheta_or_rated * ((1 + R*K^2) / (1 + R))^x
    rise_end = target + (rise_start - target) * exp(-duration / tau_oil)
    hot_spot = ambient + rise_end + dTheta_hs_rated * K^y
    ageing_rate V = 2^((hot_spot - 98) / 6)          (non-upgraded paper)
    equivalent ageing over the step = V_end * duration

End-of-step values are the reporting convention; the winding time constant is
neglected (hot-spot gradient follows the load instantaneously), which is the
standard compact simplification of the guide.
"""
from __future__ import annotations
import json, math
from pathlib import Path
TOL_ABS=0.01
TOL_REL=1e-4
ALLOWED={"top_oil_c","hot_spot_c","ageing_rate","total_ageing_hours","max_hot_spot_c","overload_admissible","rationale"}

def _expected(task):
    spec=task["public_inputs"]["transformer_thermal_case"] if "transformer_thermal_case" in task.get("public_inputs",{}) else task["transformer_thermal_case"]
    rated=spec["rated"]; ageing=spec["ageing"]
    rise=float(spec["initial_top_oil_rise_k"])
    ratio=float(rated["loss_ratio_r"]); x=float(rated["oil_exponent_x"]); y=float(rated["winding_exponent_y"])
    tau=float(rated["oil_time_constant_h"])
    top_oil={}; hot_spot={}; rate={}; total=0.0; peak=-1e9
    for step in spec["load_steps"]:
        k=float(step["load_factor_pu"]); d=float(step["duration_h"]); amb=float(step["ambient_c"])
        target=float(rated["top_oil_rise_rated_k"])*(((1.0+ratio*k*k)/(1.0+ratio))**x)
        rise=target+(rise-target)*math.exp(-d/tau)
        oil=amb+rise
        hs=oil+float(rated["hot_spot_gradient_rated_k"])*(k**y)
        v=2.0**((hs-float(ageing["reference_hot_spot_c"]))/float(ageing["doubling_interval_k"]))
        sid=step["id"]
        top_oil[sid]=round(oil,6); hot_spot[sid]=round(hs,6); rate[sid]=round(v,6)
        total+=v*d; peak=max(peak,hs)
    return {
        "top_oil_c":top_oil,
        "hot_spot_c":hot_spot,
        "ageing_rate":rate,
        "total_ageing_hours":round(total,6),
        "max_hot_spot_c":round(peak,6),
        "overload_admissible":peak<=float(spec["limits"]["max_hot_spot_c"]),
    }

def _close(a,b): return abs(float(a)-float(b))<=max(TOL_ABS,TOL_REL*max(1.0,abs(float(b))))
def evaluate_case(task, submission):
    exp=_expected(task); violations=[]
    extra=set(submission)-ALLOWED
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    for key in ("top_oil_c","hot_spot_c","ageing_rate"):
        got=submission.get(key)
        if not isinstance(got,dict):
            violations.append(f"{key} must be an object keyed by load-step id"); continue
        for sid,value in exp[key].items():
            if sid not in got: violations.append(f"{key} missing step {sid}"); continue
            try: ok=_close(got[sid],value)
            except (TypeError,ValueError): violations.append(f"{key}.{sid} must be numeric"); continue
            if not ok: violations.append(f"{key}.{sid} expected {value} got {got[sid]}")
    for key in ("total_ageing_hours","max_hot_spot_c"):
        if key not in submission: violations.append(f"missing answer field: {key}"); continue
        try: ok=_close(submission[key],exp[key])
        except (TypeError,ValueError): violations.append(f"{key} must be numeric"); continue
        if not ok: violations.append(f"{key} expected {exp[key]} got {submission[key]}")
    if submission.get("overload_admissible") is not exp["overload_admissible"]:
        violations.append(f"overload_admissible expected {exp['overload_admissible']} got {submission.get('overload_admissible')}")
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
