"""Evaluator for IBR current-limited short-circuit/FRT response."""
from __future__ import annotations
import json, math
from pathlib import Path
TOL=1e-3
ALLOWED={"current_profile_pu","min_reactive_current_pu","max_total_current_pu","frt_compliant","rationale"}

def _round(x,nd=3): return round(float(x)+0.0, nd)
def _expected(task):
    spec=task["public_inputs"]["ibr_frt_case"]
    prof={}; min_iq=999; max_itot=0; compliant=True
    for s in spec["samples"]:
        v=s["voltage_pu"]
        if v < spec["reactive_deadband_pu"]:
            iq_req=min(spec["current_limit_pu"], spec["k_reactive_current_pu_per_pu"]*(spec["reactive_deadband_pu"]-v))
        else:
            iq_req=0.0
        iq=iq_req
        id_avail=math.sqrt(max(0.0, spec["current_limit_pu"]**2-iq**2))
        idc=min(spec["prefault_active_current_pu"], id_avail)
        it=math.sqrt(idc*idc+iq*iq)
        must_ride = v >= spec["frt_voltage_floor_pu"] or s["time_s"] <= spec["max_low_voltage_duration_s"]
        if not must_ride or iq + 1e-9 < iq_req: compliant=False
        min_iq=min(min_iq, iq); max_itot=max(max_itot,it)
        prof[s["sample_id"]]={"id_pu":_round(idc),"iq_pu":_round(iq),"total_current_pu":_round(it)}
    return {"current_profile_pu":prof,"min_reactive_current_pu":_round(min_iq),"max_total_current_pu":_round(max_itot),"frt_compliant":compliant}
def _num(a,b,tol=TOL):
    try:
        return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)
    except (TypeError, ValueError):
        return False
def evaluate_case(task, submission):
    exp=_expected(task); violations=[]
    extra=set(submission)-ALLOWED
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    cp=submission.get("current_profile_pu")
    if not isinstance(cp,dict): violations.append("current_profile_pu missing or not object")
    else:
        if set(cp)!=set(exp["current_profile_pu"]): violations.append(f"current_profile_pu sample ids expected {sorted(exp['current_profile_pu'])} got {sorted(cp) if isinstance(cp,dict) else cp}")
        for sid,er in exp["current_profile_pu"].items():
            sr=cp.get(sid,{})
            for k in ["id_pu","iq_pu","total_current_pu"]:
                if k not in sr or not _num(sr[k], er[k]): violations.append(f"current_profile_pu.{sid}.{k} expected {er[k]} got {sr.get(k)}")
    for k in ["min_reactive_current_pu","max_total_current_pu"]:
        if k not in submission or not _num(submission[k], exp[k]): violations.append(f"{k} expected {exp[k]} got {submission.get(k)}")
    if submission.get("frt_compliant") is not exp["frt_compliant"]: violations.append(f"frt_compliant expected {exp['frt_compliant']} got {submission.get('frt_compliant')}")
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def main():
    import sys
    task=json.loads(Path(sys.argv[1]).read_text()); sub=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(evaluate_case(task, sub), indent=2))
if __name__=="__main__": main()
