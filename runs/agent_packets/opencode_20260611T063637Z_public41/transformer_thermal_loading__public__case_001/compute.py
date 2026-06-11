#!/usr/bin/env python3
import math

case = {
    "initial_top_oil_rise_k": 41.3,
    "rated": {
        "top_oil_rise_rated_k": 55.0,
        "loss_ratio_r": 5.0,
        "oil_exponent_x": 0.8,
        "winding_exponent_y": 1.3,
        "hot_spot_gradient_rated_k": 23.0,
        "oil_time_constant_h": 3.0
    },
    "limits": {
        "max_hot_spot_c": 120.0
    },
    "ageing": {
        "reference_hot_spot_c": 98.0,
        "doubling_interval_k": 6.0
    },
    "load_steps": [
        {"id": "s1", "duration_h": 2.0, "ambient_c": 25.0, "load_factor_pu": 0.8},
        {"id": "s2", "duration_h": 1.0, "ambient_c": 28.0, "load_factor_pu": 1.15},
        {"id": "s3", "duration_h": 2.0, "ambient_c": 30.0, "load_factor_pu": 1.0},
        {"id": "s4", "duration_h": 1.0, "ambient_c": 27.0, "load_factor_pu": 0.7}
    ]
}

R = case["rated"]["loss_ratio_r"]
x = case["rated"]["oil_exponent_x"]
y = case["rated"]["winding_exponent_y"]
theta_or = case["rated"]["top_oil_rise_rated_k"]
delta_h = case["rated"]["hot_spot_gradient_rated_k"]
tau_o = case["rated"]["oil_time_constant_h"]
theta_ref = case["ageing"]["reference_hot_spot_c"]
D = case["ageing"]["doubling_interval_k"]
max_hs = case["limits"]["max_hot_spot_c"]

theta_o_init = case["initial_top_oil_rise_k"]

top_oil_c = {}
hot_spot_c = {}
ageing_rate = {}
total_ageing_hours = 0.0

for step in case["load_steps"]:
    sid = step["id"]
    t = step["duration_h"]
    theta_a = step["ambient_c"]
    K = step["load_factor_pu"]

    # Steady-state top-oil rise
    theta_o_steady = theta_or * ((1 + R * K**2) / (1 + R)) ** x

    # Exponential approach
    theta_o_end = theta_o_steady + (theta_o_init - theta_o_steady) * math.exp(-t / tau_o)

    # Top-oil temperature
    theta_o_temp = theta_a + theta_o_end

    # Hot-spot temperature
    theta_h = theta_o_temp + delta_h * (K ** y)

    # Relative ageing rate at end of step
    V = 2 ** ((theta_h - theta_ref) / D)

    # Equivalent ageing for this step
    eq_ageing = V * t
    total_ageing_hours += eq_ageing

    top_oil_c[sid] = round(theta_o_temp, 4)
    hot_spot_c[sid] = round(theta_h, 4)
    ageing_rate[sid] = round(V, 6)

    theta_o_init = theta_o_end  # for next step

    print(f"{sid}: K={K}, ambient={theta_a}, duration={t}")
    print(f"  steady_rise={theta_o_steady:.4f}, end_rise={theta_o_end:.4f}")
    print(f"  top_oil_temp={theta_o_temp:.4f}")
    print(f"  hot_spot={theta_h:.4f}")
    print(f"  V={V:.6f}, eq_ageing={eq_ageing:.4f}")
    print()

max_hs_val = max(hot_spot_c.values())
admissible = max_hs_val <= max_hs

print(f"total_ageing_hours = {total_ageing_hours:.4f}")
print(f"max_hot_spot_c = {max_hs_val}")
print(f"overload_admissible = {admissible}")
print()

import json
result = {
    "top_oil_c": {k: round(v, 4) for k, v in top_oil_c.items()},
    "hot_spot_c": {k: round(v, 4) for k, v in hot_spot_c.items()},
    "ageing_rate": {k: round(v, 6) for k, v in ageing_rate.items()},
    "total_ageing_hours": round(total_ageing_hours, 4),
    "max_hot_spot_c": round(max_hs_val, 4),
    "overload_admissible": admissible
}
print(json.dumps(result, indent=2))
