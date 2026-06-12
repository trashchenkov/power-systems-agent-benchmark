"""Evaluator for critical clearing time via the equal-area criterion.

Single-machine-infinite-bus case with a bolted three-phase fault at the
generator high-voltage terminals, so electrical power transfer is zero during
the fault and both the critical clearing angle and the critical clearing time
have closed-form solutions:

    delta_0   = asin(Pm / Pmax_pre)
    delta_max = pi - asin(Pm / Pmax_post)
    cos(delta_cr) = (Pm * (delta_max - delta_0) + Pmax_post * cos(delta_max)) / Pmax_post
    t_cr = sqrt(4 * H * (delta_cr - delta_0) / (2 * pi * f0 * Pm))

The evaluator recomputes the study from the published machine data; nothing in
the task carries precomputed stability labels.
"""
from __future__ import annotations
import json, math
from pathlib import Path
TIME_TOL=1e-3
ANGLE_TOL_DEG=0.01
ALLOWED={"delta0_deg","delta_max_deg","delta_critical_deg","critical_clearing_time_s","rationale"}

def _round(x, nd=6): return round(float(x)+0.0, nd)
def _expected(task):
    spec=task["public_inputs"]["smib_cct_case"]
    if abs(float(spec["during_fault_pmax_pu"])) > 1e-12:
        raise ValueError("closed-form CCT requires zero power transfer during the fault")
    pm=float(spec["mechanical_power_pu"])
    p_pre=float(spec["prefault_pmax_pu"]); p_post=float(spec["postfault_pmax_pu"])
    h=float(spec["inertia_h_s"]); f0=float(spec["nominal_frequency_hz"])
    delta0=math.asin(pm/p_pre)
    delta_max=math.pi-math.asin(pm/p_post)
    cos_dcr=(pm*(delta_max-delta0)+p_post*math.cos(delta_max))/p_post
    if not -1.0 <= cos_dcr <= 1.0:
        raise ValueError("equal-area criterion has no critical angle for this case")
    delta_cr=math.acos(cos_dcr)
    t_cr=math.sqrt(4.0*h*(delta_cr-delta0)/(2.0*math.pi*f0*pm))
    return {
        "delta0_deg":_round(math.degrees(delta0)),
        "delta_max_deg":_round(math.degrees(delta_max)),
        "delta_critical_deg":_round(math.degrees(delta_cr)),
        "critical_clearing_time_s":_round(t_cr),
    }

def _num(a,b,tol):
    try:
        return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)
    except (TypeError, ValueError):
        return False
def evaluate_case(task, submission):
    exp=_expected(task); violations=[]
    extra=set(submission)-ALLOWED
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    for k,tol in [("delta0_deg",ANGLE_TOL_DEG),("delta_max_deg",ANGLE_TOL_DEG),("delta_critical_deg",ANGLE_TOL_DEG),("critical_clearing_time_s",TIME_TOL)]:
        if k not in submission: violations.append(f"missing answer field: {k}"); continue
        try: ok=_num(submission[k], exp[k], tol)
        except (TypeError, ValueError): violations.append(f"{k} must be numeric"); continue
        if not ok: violations.append(f"{k} expected {exp[k]} got {submission.get(k)}")
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}

def evaluate_files(case_path, submission_path):
    task=json.loads(Path(case_path).read_text(encoding="utf-8"))
    sub=json.loads(Path(submission_path).read_text(encoding="utf-8"))
    return evaluate_case(task, sub)

def main():
    import sys
    print(json.dumps(evaluate_files(sys.argv[1], sys.argv[2]), indent=2))
if __name__=="__main__": main()
