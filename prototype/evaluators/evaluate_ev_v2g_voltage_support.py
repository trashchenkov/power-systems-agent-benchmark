"""Evaluator for EV/V2G reactive voltage support."""
from __future__ import annotations
import json, math
from pathlib import Path
from typing import Any

def _load_json(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding='utf-8'))
def _r(x): return round(float(x),3)

def solve_core(task):
    c=task['v2g_voltage_support_case']; commands={}; voltages={}; total_q=0.0
    for bus,base in c['base_voltage_pu'].items():
        need=(float(c['target_voltage_pu'])-float(base))/float(c['q_sensitivity_pu_per_kvar'][bus])
        avail=0.0
        for ev,cfg in c['evs'].items():
            if cfg['bus']==bus:
                s=float(cfg['s_rating_kva']); p=abs(float(cfg['active_power_kw'])); avail+=math.sqrt(max(0.0,s*s-p*p))
        q=max(-avail, min(avail, need))
        commands[bus]=_r(q); voltages[bus]=_r(float(base)+q*float(c['q_sensitivity_pu_per_kvar'][bus])); total_q+=abs(q)
    return {'q_dispatch_kvar':commands, 'corrected_voltage_pu':voltages, 'total_abs_q_kvar':_r(total_q)}

def solve_case(task):
    out=solve_core(task); out['rationale']='Computed per-bus reactive support needed to reach target voltage, clipped by EV inverter capability.'; return out

def _num(v,n,viol):
    try: x=float(v)
    except (TypeError,ValueError): viol.append(f'{n} must be numeric'); return None
    if not math.isfinite(x): viol.append(f'{n} must be finite'); return None
    return x

def _close(n,a,e,viol,tol=0.01):
    if a is not None and abs(a-e)>tol: viol.append(f'{n}={a:.6g} differs from expected {e:.6g}')

def evaluate_case(task, submission):
    viol=[]; allowed={'q_dispatch_kvar','corrected_voltage_pu','total_abs_q_kvar','rationale'}; extra=sorted(set(submission)-allowed)
    if extra: viol.append(f'unknown answer fields: {extra}')
    exp=solve_core(task)
    for key in ['q_dispatch_kvar','corrected_voltage_pu']:
        got=submission.get(key)
        if not isinstance(got,dict): viol.append(f'{key} must be an object'); got={}
        for bus,e in exp[key].items(): _close(f'{key}.{bus}', _num(got.get(bus),f'{key}.{bus}',viol), e, viol)
    _close('total_abs_q_kvar', _num(submission.get('total_abs_q_kvar'),'total_abs_q_kvar',viol), exp['total_abs_q_kvar'], viol)
    return {'task_id':task['task_id'],'feasible':not viol,'score':1.0 if not viol else 0.0,'study':exp,'violations':viol}

def evaluate(task_path: Path, submission_path: Path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
def main(argv=None):
    import argparse; p=argparse.ArgumentParser(); p.add_argument('task',type=Path); p.add_argument('submission',type=Path); a=p.parse_args(argv); print(json.dumps(evaluate(a.task,a.submission),ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
