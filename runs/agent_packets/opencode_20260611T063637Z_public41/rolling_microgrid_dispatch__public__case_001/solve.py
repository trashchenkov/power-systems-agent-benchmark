import json
from itertools import product

load = {"t00": 38.0, "t05": 42.0, "t10": 48.0, "t15": 44.0}
pv = {"t00": 18.0, "t05": 15.0, "t10": 11.0, "t15": 9.0}
periods = ["t00", "t05", "t10", "t15"]
interval_hours = 0.0833333333

diesel_pmin = 12.0
diesel_pmax = 55.0
diesel_cost = 92.0

charge_pmax = 6.0
discharge_pmax = 10.0
charge_eff = 0.94
discharge_eff = 0.9
initial_soc = 5.0
soc_min = 2.5
soc_max = 8.0
step = 2.0

battery_options = []
v = -charge_pmax
while v <= discharge_pmax + 0.001:
    battery_options.append(v)
    v += step

print(f"Battery options: {battery_options}")

best_cost = float("inf")
best_dispatch = None

for b_vals in product(battery_options, repeat=4):
    soc = initial_soc
    feasible = True
    dispatch = {}

    for idx, t in enumerate(periods):
        b = b_vals[idx]

        # SOC change
        if b > 0:
            soc_change = -b * interval_hours / discharge_eff
        elif b < 0:
            soc_change = -b * interval_hours * charge_eff
        else:
            soc_change = 0

        soc_new = soc + soc_change

        if soc_new < soc_min - 1e-9 or soc_new > soc_max + 1e-9:
            feasible = False
            break

        net = load[t] - b
        diesel_needed = net - pv[t]

        if diesel_needed > diesel_pmax + 1e-9:
            feasible = False
            break
        elif diesel_needed < diesel_pmin - 1e-9:
            curtailment = diesel_pmin + b + pv[t] - load[t]
            if curtailment < -1e-9 or curtailment > pv[t] + 1e-9:
                feasible = False
                break
            diesel_mw = diesel_pmin
        else:
            diesel_mw = diesel_needed
            curtailment = 0.0

        dispatch[t] = {
            "diesel_mw": round(diesel_mw, 6),
            "battery_mw": b,
            "pv_curtailment_mw": round(curtailment, 6),
            "soc_mwh": round(soc_new, 6),
            "shed_mw": 0.0
        }

        soc = soc_new

    if feasible:
        total_cost = sum(
            dispatch[t]["diesel_mw"] * interval_hours * diesel_cost
            for t in periods
        )
        total_cost = round(total_cost, 6)

        if total_cost < best_cost - 1e-9:
            best_cost = total_cost
            best_dispatch = dispatch
            print(f"New best cost: {best_cost}")
            print(f"  b_vals: {b_vals}")
            print(f"  dispatch: {dispatch}")

if best_dispatch is not None:
    result = {
        "dispatch": best_dispatch,
        "total_cost": best_cost,
        "rationale": "Least-cost enumeration over battery dispatch step sizes respecting SOC, diesel, and PV curtailment constraints."
    }
    with open("submission.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nWrote submission.json with total_cost={best_cost}")
    print(json.dumps(result, indent=2))
else:
    print("No feasible solution found!")
