
from __future__ import annotations
import json, math, itertools
from pathlib import Path
from typing import Any
ALLOWED_EXTRA={"rationale"}
def _load_json(path: str|Path)->dict[str,Any]: return json.loads(Path(path).read_text(encoding="utf-8"))
def _close(a,b,tol=1e-3):
    try: return abs(float(a)-float(b))<=tol
    except Exception: return False


def solve_case(task):
    c=task["boiler_step_control_case"]; gain=float(c["heat_deficit_kw_per_deg_c"]); stages=sorted(c["available_stages_kw"]); dt=float(c["interval_hours"])
    out={}; energy=0.0; prev=0.0
    for t,v in c["measurements"].items():
        deficit=max(0.0, (float(c["return_temp_setpoint_c"])-float(v["return_temp_c"])-float(c["deadband_c"]))*gain)
        target=next((s for s in stages if s>=deficit-1e-12), stages[-1])
        # ramp limit in stage count per interval
        idx=stages.index(prev); tidx=stages.index(target); step=max(-c["max_stage_change_per_interval"], min(c["max_stage_change_per_interval"], tidx-idx)); cmd=stages[idx+step]
        corrected=float(v["return_temp_c"])+cmd/gain
        out[t]={"stage_kw": round(cmd,3), "corrected_return_temp_c": round(corrected,3)}
        energy += cmd*dt; prev=cmd
    return {"control_steps": out, "total_energy_kwh": round(energy,3)}

def evaluate_case(task, submission):
    exp=solve_case(task); violations=[]; allowed=set(exp)|ALLOWED_EXTRA
    extra=sorted(set(submission)-allowed)
    if extra: violations.append(f"unknown answer fields: {extra}")
    got=submission.get("control_steps",{})
    for t,vals in exp["control_steps"].items():
        for k,v in vals.items():
            if not _close(got.get(t,{}).get(k), v): violations.append(f"control_steps.{t}.{k} expected {v}, got {got.get(t,{}).get(k)}")
    if not _close(submission.get("total_energy_kwh"), exp["total_energy_kwh"]): violations.append(f"total_energy_kwh expected {exp['total_energy_kwh']}, got {submission.get('total_energy_kwh')}")
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def evaluate(task_path, submission_path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
if __name__=='__main__':
 import sys; print(json.dumps(evaluate(sys.argv[1],sys.argv[2]),indent=2,ensure_ascii=False))
