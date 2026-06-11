import json
import itertools

with open("task.json") as f:
    task = json.load(f)

case = task["v2g_outage_case"]
periods = case["time_periods"]
interval_h = case["interval_hours"]
load = case["critical_load_kw"]
evs_data = case["evs"]

# Build EV option lists
ev_options = {}
for eid, ed in evs_data.items():
    opts = []
    v = -ed["charge_max_kw"]
    while v <= ed["discharge_max_kw"]:
        opts.append(v)
        v += ed["dispatch_step_kw"]
    ev_options[eid] = opts

best = None
best_served = -1

# Enumerate all dispatch combinations: for each period, for each EV
for combo in itertools.product(
    itertools.product(ev_options["ev_a"], ev_options["ev_b"]),  # period t1
    itertools.product(ev_options["ev_a"], ev_options["ev_b"]),  # period t2
    itertools.product(ev_options["ev_a"], ev_options["ev_b"]),  # period t3
):
    dispatch = {}
    soc = {}
    served_total = 0.0
    feasible = True

    for eid in ["ev_a", "ev_b"]:
        soc[eid] = evs_data[eid]["initial_soc_kwh"]

    for pi, period in enumerate(periods):
        da, db = combo[pi]
        dispatch[period] = {"ev_a": da, "ev_b": db}
        served_kw = 0.0

        for eid, d in [("ev_a", da), ("ev_b", db)]:
            ed = evs_data[eid]
            if d > 0:  # discharge
                soc[eid] -= d * interval_h / ed["discharge_efficiency"]
                served_kw += d
            elif d < 0:  # charge
                soc[eid] += (-d) * interval_h * ed["charge_efficiency"]

        # Check SOC constraints after each period
        for eid in ["ev_a", "ev_b"]:
            ed = evs_data[eid]
            if soc[eid] < ed["reserve_soc_kwh"] - 1e-9:
                feasible = False
            if soc[eid] > ed["capacity_kwh"] + 1e-9:
                feasible = False
            if soc[eid] < -1e-9:
                feasible = False

        # Energy served to critical load at this period
        total_dispatch_kw = da + db
        served_kw_at_period = max(0.0, min(load[period], total_dispatch_kw))
        served_total += served_kw_at_period * interval_h

    if not feasible:
        continue

    if served_total > best_served + 1e-9:
        best_served = served_total
        best = {"dispatch": dispatch, "served": served_total, "soc": soc}

print("Best served energy (kWh):", best_served)
print("Dispatch:", json.dumps(best["dispatch"], indent=2))
print("Final SOC:", json.dumps(best["soc"], indent=2))

# Recalculate final SOC precisely for the best solution
soc_final = {}
for eid in ["ev_a", "ev_b"]:
    ed = evs_data[eid]
    s = ed["initial_soc_kwh"]
    for pi, period in enumerate(periods):
        d = best["dispatch"][period][eid]
        if d > 0:
            s -= d * interval_h / ed["discharge_efficiency"]
        elif d < 0:
            s += (-d) * interval_h * ed["charge_efficiency"]
    soc_final[eid] = round(s, 6)

print("\nVerified final SOC:", soc_final)

# Build submission
submission = {
    "dispatch_kw": {p: best["dispatch"][p] for p in periods},
    "served_energy_kwh": round(best_served, 6),
    "final_soc_kwh": soc_final,
    "rationale": "Enumerated all dispatch combinations to maximize critical-load energy served subject to EV power and reserve SOC constraints."
}

with open("submission.json", "w") as f:
    json.dump(submission, f, indent=2)

print("\nWritten submission.json")
