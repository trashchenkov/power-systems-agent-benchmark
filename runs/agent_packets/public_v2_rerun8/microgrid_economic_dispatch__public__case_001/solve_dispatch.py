#!/usr/bin/env python3
"""Enumerate battery schedules for microgrid economic dispatch."""
import json
from itertools import product

# Load task
with open("task.json") as f:
    task = json.load(f)

case = task["microgrid_dispatch_case"]
periods = case["time_periods"]
dt = case["interval_hours"]
load = case["load_mw"]
pv = case["pv_mw"]
gen = case["generator"]
bat = case["battery"]

pmin = gen["pmin_mw"]
pmax = gen["pmax_mw"]
cost_per_mwh = gen["variable_cost_per_mwh"]

soc0 = bat["initial_soc_mwh"]
soc_min = bat["soc_min_mwh"]
soc_max = bat["soc_max_mwh"]
charge_pmax = bat["charge_pmax_mw"]
discharge_pmax = bat["discharge_pmax_mw"]
eta_c = bat["charge_efficiency"]
eta_d = bat["discharge_efficiency"]
step = bat["dispatch_step_mw"]

# Battery power choices in 2 MW steps
battery_choices = []
v = -charge_pmax
while v <= discharge_pmax + 1e-9:
    battery_choices.append(round(v, 6))
    v += step


def soc_update(soc, battery_mw):
  if battery_mw < 0:
    return soc + (-battery_mw) * eta_c * dt
  if battery_mw > 0:
    return soc - (battery_mw / eta_d) * dt
  return soc


def simulate_schedule(battery_schedule):
  """Return dispatch dict and total cost if feasible, else None."""
  soc = soc0
  dispatch = {}
  total_cost = 0.0

  for t in periods:
    b = battery_schedule[t]
    if b < -charge_pmax - 1e-9 or b > discharge_pmax + 1e-9:
      return None
    if abs(b / step - round(b / step)) > 1e-6:
      return None

    L = load[t]
    P = pv[t]

    # Minimize diesel: use all PV first, then battery, diesel fills gap
    # diesel = L - (P - curtail) - b  => curtail = P - (L - b - diesel)
    # For min diesel cost: use max PV, so curtail = 0 unless excess
    # diesel_raw = L - P - b
    diesel_raw = L - P - b

    if diesel_raw < pmin - 1e-9:
      # Need curtailment to raise diesel to pmin
      # diesel = pmin => L - (P - curtail) - b = pmin => curtail = pmin + b + P - L
      curtail = pmin + b + P - L
      if curtail < -1e-9:
        return None
      if curtail > P + 1e-9:
        return None
      diesel = pmin
    elif diesel_raw > pmax + 1e-9:
      # Need more supply - can't curtail more, infeasible unless we shed (not allowed)
      return None
    else:
      curtail = 0.0
      diesel = diesel_raw

    # Excess PV when diesel would be below pmin handled above.
    # Excess PV when battery charging and diesel at pmin - curtail handles it.
    # Check if we have excess generation with diesel at pmin and full battery constraints
    net = diesel + P - curtail + b
    if abs(net - L) > 1e-6:
      return None

    if diesel < pmin - 1e-9 or diesel > pmax + 1e-9:
      return None

    shed = 0.0
    soc_end = soc_update(soc, b)
    if soc_end < soc_min - 1e-9 or soc_end > soc_max + 1e-9:
      return None

    dispatch[t] = {
      "diesel_mw": round(diesel, 6),
      "battery_mw": round(b, 6),
      "pv_curtailment_mw": round(curtail, 6),
      "soc_mwh": round(soc_end, 6),
      "shed_mw": shed,
    }
    total_cost += diesel * dt * cost_per_mwh
    soc = soc_end

  return dispatch, total_cost


best = None
best_cost = float("inf")
best_battery = None

for combo in product(battery_choices, repeat=len(periods)):
  schedule = dict(zip(periods, combo))
  result = simulate_schedule(schedule)
  if result is None:
    continue
  dispatch, cost = result
  if cost < best_cost - 1e-9:
    best_cost = cost
    best = dispatch
    best_battery = schedule

if best is None:
  print("No feasible solution found!")
else:
  submission = {
    "dispatch": best,
    "total_cost": round(best_cost, 6),
    "rationale": (
      "Enumerated all battery schedules on 2 MW steps; selected minimum-cost "
      "feasible dispatch respecting SOC, diesel limits, and no load shedding."
    ),
  }
  with open("submission.json", "w") as f:
    json.dump(submission, f, indent=2)
  print(json.dumps(submission, indent=2))
  print(f"\nBattery schedule: {best_battery}")
  print(f"Total cost: {best_cost}")
