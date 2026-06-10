"""Evaluator for BESS ancillary P/Q response to frequency and voltage deviations."""
from __future__ import annotations
import json, math
from pathlib import Path
from typing import Any

def _load_json(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding='utf-8'))
def _r(x): return round(float(x),3)

def solve_core(task):
    c=task['bess_response_case']; p_cmd={}; q_cmd={}; soc=float(c['initial_soc_mwh']); dt=float(c['interval_seconds'])/3600.0
    for t,m in c['measurements'].items():
        df=float(c['nominal_frequency_hz'])-float(m['frequency_hz'])
        p=max(-float(c['p_charge_limit_mw']), min(float(c['p_discharge_limit_mw']), df*float(c['frequency_droop_mw_per_hz'])))
        dv=float(c['target_voltage_pu'])-float(m['voltage_pu'])
        q_raw=dv*float(c['voltage_droop_mvar_per_pu'])
        q_cap=math.sqrt(max(0.0,float(c['s_rating_mva'])**2-p*p))
        q=max(-q_cap,min(q_cap,q_raw))
        if p>=0: soc-=p*dt/float(c['discharge_efficiency'])
        else: soc-=p*dt*float(c['charge_efficiency'])
        p_cmd[t]=_r(p); q_cmd[t]=_r(q)
    return {'p_response_mw':p_cmd,'q_response_mvar':q_cmd,'final_soc_mwh':_r(soc)}

def solve_case(task):
    out=solve_core(task); out['rationale']='Applied frequency and voltage droop commands, clipped by P limits and inverter apparent-power capability.'; return out

def _num(v,n,viol):
    try: x=float(v)
    except (TypeError,ValueError): viol.append(f'{n} must be numeric'); return None
    if not math.isfinite(x): viol.append(f'{n} must be finite'); return None
    return x

def _close(n,a,e,viol,tol=0.01):
    if a is not None and abs(a-e)>tol: viol.append(f'{n}={a:.6g} differs from expected {e:.6g}')

def evaluate_case(task, submission):
    viol=[]; allowed={'p_response_mw','q_response_mvar','final_soc_mwh','rationale'}; extra=sorted(set(submission)-allowed)
    if extra: viol.append(f'unknown answer fields: {extra}')
    exp=solve_core(task)
    for key in ['p_response_mw','q_response_mvar']:
        got=submission.get(key)
        if not isinstance(got,dict): viol.append(f'{key} must be an object'); got={}
        for t,e in exp[key].items(): _close(f'{key}.{t}', _num(got.get(t),f'{key}.{t}',viol), e, viol)
    _close('final_soc_mwh', _num(submission.get('final_soc_mwh'),'final_soc_mwh',viol), exp['final_soc_mwh'], viol)
    return {'task_id':task['task_id'],'feasible':not viol,'score':1.0 if not viol else 0.0,'study':exp,'violations':viol}

def evaluate(task_path: Path, submission_path: Path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
def main(argv=None):
    import argparse; p=argparse.ArgumentParser(); p.add_argument('task',type=Path); p.add_argument('submission',type=Path); a=p.parse_args(argv); print(json.dumps(evaluate(a.task,a.submission),ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
