import json, itertools

case = {
    "time_periods": ["t1","t2","t3"],
    "interval_hours": 0.5,
    "critical_load_kw": {"t1": 10.0, "t2": 12.0, "t3": 9.0},
    "evs": {
        "ev_a": {"capacity_kwh": 40.0, "initial_soc_kwh": 24.0, "reserve_soc_kwh": 16.0,
                 "charge_max_kw": 4.0, "discharge_max_kw": 8.0,
                 "charge_efficiency": 0.95, "discharge_efficiency": 0.9, "dispatch_step_kw": 4.0},
        "ev_b": {"capacity_kwh": 32.0, "initial_soc_kwh": 20.0, "reserve_soc_kwh": 12.0,
                 "charge_max_kw": 3.0, "discharge_max_kw": 6.0,
                 "charge_efficiency": 0.95, "discharge_efficiency": 0.9, "dispatch_step_kw": 3.0}
    }
}

DT = case["interval_hours"]
periods = case["time_periods"]
loads = case["critical_load_kw"]

def make_opts(ev):
    step = ev["dispatch_step_kw"]
    vals = []
    v = -ev["charge_max_kw"]
    while v <= ev["discharge_max_kw"] + 0.001:
        vals.append(v)
        v += step
    return vals

opts_a = make_opts(case["evs"]["ev_a"])
opts_b = make_opts(case["evs"]["ev_b"])

def soc_delta(ev, d, dt):
    if d > 0:
        return -d * dt / ev["discharge_efficiency"]
    elif d < 0:
        return -d * dt * ev["charge_efficiency"]
    return 0.0

best = None
best_served = -1

for da1, da2, da3, db1, db2, db3 in itertools.product(opts_a, opts_a, opts_a, opts_b, opts_b, opts_b):
    eva, evb = case["evs"]["ev_a"], case["evs"]["ev_b"]

    soc_a = [eva["initial_soc_kwh"]]
    for d in [da1, da2, da3]:
        soc_a.append(soc_a[-1] + soc_delta(eva, d, DT))
    if any(s < eva["reserve_soc_kwh"] - 1e-9 or s > eva["capacity_kwh"] + 1e-9 for s in soc_a):
        continue

    soc_b = [evb["initial_soc_kwh"]]
    for d in [db1, db2, db3]:
        soc_b.append(soc_b[-1] + soc_delta(evb, d, DT))
    if any(s < evb["reserve_soc_kwh"] - 1e-9 or s > evb["capacity_kwh"] + 1e-9 for s in soc_b):
        continue

    served = 0.0
    da = [da1, da2, da3]
    db = [db1, db2, db3]
    for i, t in enumerate(periods):
        tot = max(0, da[i]) + max(0, db[i])
        served += min(tot, loads[t]) * DT

    if served > best_served + 1e-9:
        best_served = served
        best = {
            "dispatch_kw": {
                "t1": {"ev_a": da1, "ev_b": db1},
                "t2": {"ev_a": da2, "ev_b": db2},
                "t3": {"ev_a": da3, "ev_b": db3}
            },
            "served_energy_kwh": round(served, 6),
            "final_soc_kwh": {
                "ev_a": round(soc_a[-1], 6),
                "ev_b": round(soc_b[-1], 6)
            }
        }

print(f"Best served: {best_served}")
print(json.dumps(best, indent=2))
