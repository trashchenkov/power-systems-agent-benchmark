#!/usr/bin/env python3
import json
import math
from pathlib import Path

task = json.loads(Path("task.json").read_text())
case = task["wind_interval_case"]

ref_rho = case["reference_air_density_kg_m3"]
count = case["turbine"]["count"]
rated_each = case["turbine"]["rated_mw_each"]
rated_total = count * rated_each
cut_in = case["power_curve"]["cut_in_m_s"]
rated_v = case["power_curve"]["rated_m_s"]
cut_out = case["power_curve"]["cut_out_m_s"]


def corrected_speed(wind_speed_m_s: float, air_density_kg_m3: float) -> float:
    return wind_speed_m_s * (air_density_kg_m3 / ref_rho) ** (1 / 3)


def power_mw(wind_speed_m_s: float, air_density_kg_m3: float) -> float:
    v_c = corrected_speed(wind_speed_m_s, air_density_kg_m3)
    if v_c < cut_in or v_c >= cut_out:
        return 0.0
    if v_c >= rated_v:
        return rated_total
    frac = (v_c - cut_in) / (rated_v - cut_in)
    return rated_total * frac**3


def quantile(sorted_powers: list[float], q: float) -> float:
    n = len(sorted_powers)
    pos = q * (n - 1)
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return sorted_powers[lo]
    w = pos - lo
    return sorted_powers[lo] * (1 - w) + sorted_powers[hi] * w


prediction_interval_mw_by_timestamp = {}
widths = []

for horizon in case["horizons"]:
    ts = horizon["timestamp"]
    powers = sorted(power_mw(s["wind_speed_m_s"], s["air_density_kg_m3"]) for s in horizon["scenarios"])
    p10 = quantile(powers, 0.10)
    p50 = quantile(powers, 0.50)
    p90 = quantile(powers, 0.90)
    prediction_interval_mw_by_timestamp[ts] = {
        "p10": round(p10, 6),
        "p50": round(p50, 6),
        "p90": round(p90, 6),
    }
    widths.append(p90 - p10)
    print(ts, powers, prediction_interval_mw_by_timestamp[ts])

average_interval_width_mw = sum(widths) / len(widths)

submission = {
    "prediction_interval_mw_by_timestamp": prediction_interval_mw_by_timestamp,
    "average_interval_width_mw": round(average_interval_width_mw, 6),
}

Path("submission.json").write_text(json.dumps(submission, indent=2) + "\n")
print("average_interval_width_mw", submission["average_interval_width_mw"])
