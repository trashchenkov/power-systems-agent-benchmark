"""Evaluator for EV/V2G outage support scheduling."""
from __future__ import annotations
import itertools, json, math
from pathlib import Path
from typing import Any

def _load_json(path: Path) -> dict[str, Any]: return json.loads(path.read_text(encoding='utf-8'))
def _r(x): return round(float(x),3)
def _times(c): return c['time_periods']

def _simulate(case, dispatch):
    soc={ev:float(cfg['initial_soc_kwh']) for ev,cfg in case['evs'].items()}
    rows={}; violations=[]; total_served=0.0
    dt=float(case['interval_hours'])
    for t in _times(case):
        rows[t]={}; load=float(case['critical_load_kw'][t]); support=0.0
        for ev,cfg in case['evs'].items():
            p=float(dispatch.get(ev,{}).get(t,0.0))
            if p < -float(cfg['charge_max_kw'])-1e-9 or p > float(cfg['discharge_max_kw'])+1e-9:
                violations.append(f'{ev}.{t} violates charge/discharge power limit')
            if p>=0: soc[ev]-=p*dt/float(cfg['discharge_efficiency'])
            else: soc[ev]-=p*dt*float(cfg['charge_efficiency'])
            if soc[ev] < float(cfg['reserve_soc_kwh'])-1e-9 or soc[ev] > float(cfg['capacity_kwh'])+1e-9:
                violations.append(f'{ev}.{t} SOC out of limits')
            if p>0: support += p
            rows[t][ev]=_r(p)
        served=min(load, support); total_served += served*dt
        rows[t]['served_kw']=_r(served); rows[t]['unserved_kw']=_r(max(0.0, load-support))
    return rows, {k:_r(v) for k,v in soc.items()}, _r(total_served), violations

def solve_core(task):
    case=task['v2g_outage_case']; vals={}
    for ev,cfg in case['evs'].items():
        step=float(cfg['dispatch_step_kw']); x=-float(cfg['charge_max_kw']); arr=[]
        while x <= float(cfg['discharge_max_kw'])+1e-9: arr.append(round(x,6)); x+=step
        vals[ev]=arr
    best=None; evs=list(case['evs'])
    # optimize outage-window discharge only; no charging inside event unless needed by enumeration.
    keys=[(ev,t) for ev in evs for t in _times(case)]
    domains=[vals[ev] for ev,t in keys]
    for combo in itertools.product(*domains):
        sched={ev:{} for ev in evs}
        for (ev,t),p in zip(keys,combo): sched[ev][t]=p
        rows,final_soc,served,viol=_simulate(case,sched)
        if viol: continue
        unserved=sum(rows[t]['unserved_kw'] for t in _times(case))
        throughput=sum(abs(sched[ev][t]) for ev,t in keys)
        key=(-served, unserved, throughput, combo)
        if best is None or key<best[0]: best=(key,rows,final_soc,served)
    if best is None: raise ValueError('no feasible V2G schedule')
    return {'dispatch_kw':{t:{ev:best[1][t][ev] for ev in evs} for t in _times(case)}, 'served_energy_kwh':best[3], 'final_soc_kwh':best[2]}

def solve_case(task):
    out=solve_core(task); out['rationale']='Enumerated EV charge/discharge schedules and maximized served critical-load energy while preserving reserve SOC.'; return out

def _num(v,n,viol):
    try: x=float(v)
    except (TypeError,ValueError): viol.append(f'{n} must be numeric'); return None
    if not math.isfinite(x): viol.append(f'{n} must be finite'); return None
    return x

def _close(n,a,e,viol,tol=0.01):
    if a is not None and abs(a-e)>tol: viol.append(f'{n}={a:.6g} differs from expected {e:.6g}')

def evaluate_case(task, submission):
    viol=[]; allowed={'dispatch_kw','served_energy_kwh','final_soc_kwh','rationale'}; extra=sorted(set(submission)-allowed)
    if extra: viol.append(f'unknown answer fields: {extra}')
    exp=solve_core(task); disp=submission.get('dispatch_kw')
    if not isinstance(disp,dict): viol.append('dispatch_kw must be an object'); disp={}
    for t,row in exp['dispatch_kw'].items():
        got=disp.get(t)
        if not isinstance(got,dict): viol.append(f'missing dispatch_kw.{t}'); got={}
        for ev,e in row.items(): _close(f'dispatch_kw.{t}.{ev}', _num(got.get(ev),f'dispatch_kw.{t}.{ev}',viol), e, viol)
    fs=submission.get('final_soc_kwh')
    if not isinstance(fs,dict): viol.append('final_soc_kwh must be an object'); fs={}
    for ev,e in exp['final_soc_kwh'].items(): _close(f'final_soc_kwh.{ev}', _num(fs.get(ev),f'final_soc_kwh.{ev}',viol), e, viol)
    _close('served_energy_kwh', _num(submission.get('served_energy_kwh'),'served_energy_kwh',viol), exp['served_energy_kwh'], viol)
    return {'task_id':task['task_id'],'feasible':not viol,'score':1.0 if not viol else 0.0,'study':exp,'violations':viol}

def evaluate(task_path: Path, submission_path: Path): return evaluate_case(_load_json(task_path), _load_json(submission_path))
def main(argv=None):
    import argparse; p=argparse.ArgumentParser(); p.add_argument('task',type=Path); p.add_argument('submission',type=Path); a=p.parse_args(argv); print(json.dumps(evaluate(a.task,a.submission),ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
