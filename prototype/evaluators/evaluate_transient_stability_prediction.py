"""Evaluator for transient stability classification from contingency features."""
from __future__ import annotations
import json, math
from pathlib import Path
TOL=1e-3
ALLOWED={"case_results","stable_case_count","highest_risk_case","rationale"}

def _round(x, nd=3): return round(float(x)+0.0, nd)
def _case_result(c, spec):
    angle_margin=spec["angle_limit_deg"]-c["max_rotor_angle_deg"]
    voltage_margin=c["min_voltage_pu"]-spec["voltage_floor_pu"]
    clearing_margin=c["estimated_cct_s"]-c["fault_clearing_time_s"]
    damping_margin=c["damping_ratio_pct"]-spec["min_damping_pct"]
    stable=angle_margin>=0 and voltage_margin>=0 and clearing_margin>=0 and damping_margin>=0
    risk=max(0.0, -angle_margin/60)+max(0.0,-voltage_margin/0.1)+max(0.0,-clearing_margin/0.1)+max(0.0,-damping_margin/5)
    risk += max(0.0, 1.0-clearing_margin/0.2)*0.1
    return {"label":"stable" if stable else "unstable", "risk_score":_round(risk), "clearing_margin_s":_round(clearing_margin)}
def _expected(task):
    spec=task["public_inputs"]["transient_stability_cases"]
    results={c["case_id"]:_case_result(c,spec) for c in spec["cases"]}
    stable_count=sum(1 for r in results.values() if r["label"]=="stable")
    high=max(results, key=lambda k:(results[k]["risk_score"], k))
    return {"case_results":results,"stable_case_count":stable_count,"highest_risk_case":high}
def _num(a,b,tol=TOL): return math.isclose(float(a), float(b), rel_tol=0, abs_tol=tol)
def evaluate_case(task, submission):
    exp=_expected(task); violations=[]
    extra=set(submission)-ALLOWED
    if extra: violations.append(f"unknown answer fields: {sorted(extra)}")
    cr=submission.get("case_results")
    if not isinstance(cr, dict): violations.append("case_results missing or not object")
    else:
        if set(cr)!=set(exp["case_results"]): violations.append(f"case_results case ids expected {sorted(exp['case_results'])} got {sorted(cr) if isinstance(cr,dict) else cr}")
        for cid,er in exp["case_results"].items():
            sr=cr.get(cid,{}) if isinstance(cr,dict) else {}
            if sr.get("label")!=er["label"]: violations.append(f"case_results.{cid}.label expected {er['label']} got {sr.get('label')}")
            for k in ["risk_score","clearing_margin_s"]:
                if k not in sr or not _num(sr[k], er[k]): violations.append(f"case_results.{cid}.{k} expected {er[k]} got {sr.get(k)}")
    for k in ["stable_case_count","highest_risk_case"]:
        if submission.get(k)!=exp[k]: violations.append(f"{k} expected {exp[k]} got {submission.get(k)}")
    return {"task_id":task.get("task_id"),"feasible":not violations,"score":1.0 if not violations else 0.0,"study":exp,"violations":violations}
def main():
    import sys
    task=json.loads(Path(sys.argv[1]).read_text()); sub=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(evaluate_case(task, sub), indent=2))
if __name__=="__main__": main()
