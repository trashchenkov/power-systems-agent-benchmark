"""Evaluator for minimum synchronous-machine share under inertia/SCR constraints."""
from __future__ import annotations
import itertools, json, math
from pathlib import Path
TOL=1e-3
ALLOWED={"online_units","min_synchronous_share_pct","system_inertia_gws","rocof_hz_per_s","short_circuit_ratio","rationale"}

def _round(x,nd=3): return round(float(x)+0.0, nd)
def _eval_combo(units, spec):
    p=sum(u["p_mw"] for u in units); inertia=sum(u["h_s"]*u["p_mw"] for u in units)/1000.0
    # Swing equation: |df/dt| = dP * f0 / (2 * E_kinetic), with E_kinetic = sum(H_i * S_i) in MW*s.
    rocof=spec["largest_loss_mw"]*spec["nominal_frequency_hz"]/(2*inertia*1000) if inertia>0 else float('inf')
    scr=(spec["grid_short_circuit_mva_base"]+sum(u["short_circuit_mva"] for u in units))/spec["ibr_capacity_mva"]
    share=100*p/spec["demand_mw"]
    ok=rocof<=spec["max_rocof_hz_per_s"] and scr>=spec["min_scr"]
    return ok, share, inertia, rocof, scr
def _expected(task):
    spec=task["public_inputs"]["synchronous_share_case"]
    units=spec["sync_units"]
    best=None
    for r in range(1,len(units)+1):
        for combo in itertools.combinations(units,r):
            ok,share,inertia,rocof,scr=_eval_combo(combo,spec)
            if ok:
                ids=[u["unit_id"] for u in combo]
                cand=(share, len(ids), ids, inertia, rocof, scr)
                if best is None or cand < best: best=cand
    if best is None: raise ValueError("no feasible combo")
    share,_,ids,inertia,rocof,scr=best
    return {"online_units":ids,"min_synchronous_share_pct":_round(share),"system_inertia_gws":_round(inertia),"rocof_hz_per_s":_round(rocof),"short_circuit_ratio":_round(scr)}
def _num(a,b,tol=TOL): return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)
def evaluate_case(task, submission):
    exp=_expected(task); violations=[]
    extra=set(submission)-ALLOWED
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    if submission.get("online_units")!=exp["online_units"]: violations.append(f"online_units expected {exp['online_units']} got {submission.get('online_units')}")
    for k in ["min_synchronous_share_pct","system_inertia_gws","rocof_hz_per_s","short_circuit_ratio"]:
        if k not in submission or not _num(submission[k], exp[k]): violations.append(f"{k} expected {exp[k]} got {submission.get(k)}")
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def main():
    import sys
    task=json.loads(Path(sys.argv[1]).read_text()); sub=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(evaluate_case(task, sub), indent=2))
if __name__=="__main__": main()
