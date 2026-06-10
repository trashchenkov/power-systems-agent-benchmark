
from __future__ import annotations
import json, math, itertools
from pathlib import Path
from typing import Any
ALLOWED_EXTRA={"rationale"}
def _load_json(path: str|Path)->dict[str,Any]: return json.loads(Path(path).read_text(encoding="utf-8"))
def _close(a,b,tol=1e-3):
    try: return abs(float(a)-float(b))<=tol
    except Exception: return False


def solve_case(task: dict[str,Any])->dict[str,Any]:
    c=task["boiler_capacity_case"]; eff=float(c["electric_boiler_efficiency"]); margin=float(c["sizing_margin_fraction"]); inc=float(c["capacity_increment_kw"])
    residual={t: max(0.0, float(v["heat_load_kw_th"])-float(v["heat_pump_heat_kw_th"])-float(v.get("waste_heat_kw_th",0))) for t,v in c["design_hours"].items()}
    peak=max(residual.values()); req_heat=peak*(1+margin); req_elec=req_heat/eff
    cap=math.ceil((req_elec-1e-12)/inc)*inc
    feeder_peak=cap+max(float(v["non_boiler_electric_kw"])+float(v["heat_pump_electric_kw"]) for v in c["design_hours"].values())
    return {"capacity_kw": round(cap,3), "peak_residual_heat_kw_th": round(peak,3), "feeder_peak_kw": round(feeder_peak,3)}

def evaluate_case(task, submission):
    exp=solve_case(task); violations=[]; allowed=set(exp)|ALLOWED_EXTRA
    extra=sorted(set(submission)-allowed)
    if extra: violations.append(f"unknown answer fields: {extra}")
    c=task["boiler_capacity_case"]
    if submission.get("capacity_kw", -1) > c["feeder_boiler_capacity_limit_kw"]+1e-6: violations.append("capacity_kw exceeds feeder boiler capacity limit")
    for k,v in exp.items():
        if not _close(submission.get(k), v): violations.append(f"{k} expected {v}, got {submission.get(k)}")
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def evaluate(task_path, submission_path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
if __name__=='__main__':
 import sys; print(json.dumps(evaluate(sys.argv[1],sys.argv[2]),indent=2,ensure_ascii=False))
