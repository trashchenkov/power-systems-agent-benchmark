"""Deterministic hidden-case generator for all public task families.

The repository intentionally does not distribute hidden cases (.gitignore:
**/hidden/). Instead, this script derives them on the evaluation host from the
public case_001 artifacts: each family has a registered perturbation that
redraws the numeric content of the case from a seeded RNG, and every generated
case is accepted only if the family baseline solves it and the evaluator marks
that solution feasible. Leaderboard operators keep the seed private; anyone
with the repository can still audit exactly how hidden cases are produced.

Usage:
    python scripts/generate_hidden_cases.py --seed <private-seed> --case-id 201
    python scripts/generate_hidden_cases.py --families pv_volt_var ybus_construction \
        --seed s1 --case-id 202 --out tasks
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

from scripts.evaluate_submission import EVALUATOR_MODULE_BY_FAMILY, evaluate_submission_file
from scripts.run_public_baselines import solve_with_baseline

MAX_ATTEMPTS = 60
META_INPUT_KEYS = {"candidate_id", "subdomain", "input_fields", "calculation_spec"}


def _case(task: dict[str, Any], key: str) -> Any:
    """Return the case object stored under `key`, unifying the top-level copy
    and the public_inputs copy so that mutations stay in sync."""
    inputs = task.get("public_inputs", {})
    obj = task.get(key, inputs.get(key))
    if obj is None:
        raise KeyError(f"case key not found: {key}")
    if key in task:
        task[key] = obj
    if isinstance(inputs, dict) and key in inputs:
        inputs[key] = obj
    return obj


def _scale(rng: random.Random, value: float, lo: float = 0.85, hi: float = 1.2, nd: int = 4) -> float:
    return round(float(value) * rng.uniform(lo, hi), nd)


def _pick(rng: random.Random, lo: float, hi: float, nd: int = 4) -> float:
    return round(rng.uniform(lo, hi), nd)


# ---------------------------------------------------------------------------
# Family generators. Each mutates the task in place using the provided RNG.
# ---------------------------------------------------------------------------

def gen_bess_ancillary_response(task, rng):
    c = _case(task, "bess_response_case")
    c["initial_soc_mwh"] = _pick(rng, c["soc_min_mwh"] + 1.5, c["soc_max_mwh"] - 1.5, 2)
    c["frequency_droop_mw_per_hz"] = _scale(rng, c["frequency_droop_mw_per_hz"], 0.7, 1.4, 2)
    c["voltage_droop_mvar_per_pu"] = _scale(rng, c["voltage_droop_mvar_per_pu"], 0.7, 1.4, 2)
    c["p_discharge_limit_mw"] = _scale(rng, c["p_discharge_limit_mw"], 0.8, 1.3, 2)
    c["p_charge_limit_mw"] = _scale(rng, c["p_charge_limit_mw"], 0.8, 1.3, 2)
    for m in c["measurements"].values():
        m["frequency_hz"] = round(c["nominal_frequency_hz"] + rng.uniform(-0.25, 0.25), 3)
        m["voltage_pu"] = _pick(rng, 0.95, 1.05, 3)


def gen_breaker_relay_short_circuit(task, rng):
    c = _case(task, "short_circuit_case")
    for imp in (c["source_thevenin_impedance"], c["transformer_impedance"]):
        imp["r_ohm"] = _scale(rng, imp["r_ohm"], 0.8, 1.3)
        imp["x_ohm"] = _scale(rng, imp["x_ohm"], 0.8, 1.3)
    f = c["feeder"]
    f["length_km"] = _pick(rng, 5.0, 12.0, 1)
    f["r_ohm_per_km"] = _scale(rng, f["r_ohm_per_km"], 0.85, 1.25)
    f["x_ohm_per_km"] = _scale(rng, f["x_ohm_per_km"], 0.85, 1.25)
    length = f["length_km"]
    c["fault_locations"] = [
        {"id": "near_bus_fault", "distance_km": round(0.05 * length, 2)},
        {"id": "mid_feeder_fault", "distance_km": round(0.5 * length, 2)},
        {"id": "remote_end_fault", "distance_km": length},
    ]
    c["max_load_current_a"] = _pick(rng, 250.0, 450.0, 0)


def gen_cable_ampacity_sizing(task, rng):
    c = _case(task, "cable_sizing_case")
    c["design_current_a"] = _pick(rng, 150.0, 280.0, 0)
    c["length_m"] = _pick(rng, 120.0, 420.0, 0)
    c["power_factor"] = _pick(rng, 0.85, 0.95, 2)
    c["derating"]["ambient_factor"] = _pick(rng, 0.87, 1.0, 2)
    c["derating"]["grouping_factor"] = _pick(rng, 0.7, 1.0, 2)
    c["fault"]["fault_current_ka"] = _pick(rng, 8.0, 18.0, 1)
    c["fault"]["clearing_time_s"] = _pick(rng, 0.2, 0.6, 2)


def gen_commercial_pv_lcoe_uncertainty(task, rng):
    c = _case(task, "pv_lcoe_case")
    c["system_size_kw_dc"] = int(rng.randrange(1000, 4001, 100))
    c["hard_cost_usd_per_kw"] = int(_pick(rng, 600, 950, 0))
    for k in c["soft_cost_components_usd_per_kw"]:
        c["soft_cost_components_usd_per_kw"][k] = int(_pick(rng, 35, 120, 0))
    c["capital_recovery_factor"] = _pick(rng, 0.07, 0.1, 4)
    c["fixed_om_usd_per_kw_year"] = int(_pick(rng, 12, 25, 0))
    c["annual_energy_mwh_year1"] = int(c["system_size_kw_dc"] * _pick(rng, 1.45, 1.75, 3))
    for scenario in c["soft_cost_scenarios"].values():
        for k in scenario:
            scenario[k] = round(max(0.6, min(1.7, scenario[k] * rng.uniform(0.9, 1.15))), 3)


def gen_contingency_screening(task, rng):
    branches = _case(task, "branches")
    contingencies = _case(task, "contingencies")
    for b in branches:
        b["rating_mw"] = _scale(rng, b["rating_mw"], 0.9, 1.15, 1)
        b["base_flow_mw"] = round(b["rating_mw"] * rng.uniform(0.4, 0.9), 1)
    rating = {b["id"]: b["rating_mw"] for b in branches}
    for cont in contingencies:
        for bid in cont["post_flows_mw"]:
            cont["post_flows_mw"][bid] = round(rating[bid] * rng.uniform(0.5, 1.3), 1)


def gen_corrective_transmission_switching(task, rng):
    buses = _case(task, "buses")
    branches = _case(task, "branches")
    injection = _pick(rng, 80.0, 120.0, 1)
    shares = [rng.uniform(0.2, 0.5) for _ in range(len(buses) - 1)]
    total = sum(shares)
    buses[0]["p_mw"] = injection
    for bus, share in zip(buses[1:], shares):
        bus["p_mw"] = round(-injection * share / total, 1)
    buses[-1]["p_mw"] = round(-(injection + sum(b["p_mw"] for b in buses[1:-1])), 1)
    for br in branches:
        br["rating_mw"] = _scale(rng, br["rating_mw"], 0.9, 1.2, 1)


def gen_critical_clearing_time(task, rng):
    c = _case(task, "smib_cct_case")
    c["inertia_h_s"] = _pick(rng, 3.0, 6.0, 2)
    c["prefault_pmax_pu"] = _pick(rng, 1.8, 2.3, 2)
    c["postfault_pmax_pu"] = _pick(rng, 1.3, 1.7, 2)
    c["mechanical_power_pu"] = _pick(rng, 0.7, min(1.0, c["postfault_pmax_pu"] * 0.75), 2)


def gen_dispatch_uncertainty(task, rng):
    c = _case(task, "dispatch_uncertainty_case")
    c["reserve_requirement_mw"] = _pick(rng, 5.0, 12.0, 1)
    for g in c["generators"]:
        g["pmax_mw"] = _scale(rng, g["pmax_mw"], 0.9, 1.2, 1)
        g["variable_cost_per_mwh"] = _scale(rng, g["variable_cost_per_mwh"], 0.8, 1.3, 1)
    for s in c["scenarios"]:
        for t in s["load_mw"]:
            s["load_mw"][t] = _scale(rng, s["load_mw"][t], 0.9, 1.1, 1)
        for t in s["renewable_mw"]:
            s["renewable_mw"][t] = _scale(rng, s["renewable_mw"][t], 0.7, 1.2, 1)


def gen_distance_protection_settings(task, rng):
    c = _case(task, "protection_case")
    line = c["protected_line"]
    line["length_km"] = _pick(rng, 50.0, 120.0, 1)
    line["r1_ohm_per_km"] = _scale(rng, line["r1_ohm_per_km"], 0.85, 1.2)
    line["x1_ohm_per_km"] = _scale(rng, line["x1_ohm_per_km"], 0.85, 1.2)
    for backup in c["remote_backup_lines"]:
        backup["length_km"] = _pick(rng, 30.0, 80.0, 1)
        backup["r1_ohm_per_km"] = _scale(rng, backup["r1_ohm_per_km"], 0.85, 1.2)
        backup["x1_ohm_per_km"] = _scale(rng, backup["x1_ohm_per_km"], 0.85, 1.2)
    c["maximum_load"]["apparent_power_mva"] = _pick(rng, 60.0, 100.0, 1)


def gen_dynamic_thermal_rating(task, rng):
    c = _case(task, "thermal_rating_case")
    c["scheduled_current_a"] = _pick(rng, 450.0, 620.0, 0)
    cond = c["conductor"]
    cond["resistance_ohm_per_km_at_20c"] = _scale(rng, cond["resistance_ohm_per_km_at_20c"], 0.85, 1.2, 4)
    for w in c["weather_series"]:
        w["ambient_temperature_c"] = _pick(rng, 12.0, 36.0, 1)
        w["wind_speed_m_s"] = _pick(rng, 0.5, 4.0, 1)
        w["solar_w_per_m2"] = _pick(rng, 50.0, 950.0, 0)


def gen_earth_fault_calculation(task, rng):
    c = _case(task, "earth_fault_case")
    c["fault_resistance_pu"] = _pick(rng, 0.02, 0.09, 3)
    for seq in c["sequence_impedances_pu"].values():
        seq["r_pu"] = _scale(rng, seq["r_pu"], 0.8, 1.3)
        seq["x_pu"] = _scale(rng, seq["x_pu"], 0.8, 1.3)


def gen_en50160_voltage_compliance(task, rng):
    c = _case(task, "voltage_compliance_case")
    drift = rng.uniform(-0.08, 0.04)
    for point in c["voltage_series_pu"]:
        point["voltage_pu"] = round(min(1.09, max(0.86, 1.0 + drift + rng.uniform(-0.04, 0.04))), 3)


def gen_ev_v2g_outage_schedule(task, rng):
    c = _case(task, "v2g_outage_case")
    for t in c["critical_load_kw"]:
        c["critical_load_kw"][t] = _pick(rng, 7.0, 14.0, 1)
    for ev in c["evs"].values():
        ev["capacity_kwh"] = _pick(rng, 28.0, 60.0, 1)
        ev["reserve_soc_kwh"] = round(ev["capacity_kwh"] * rng.uniform(0.3, 0.45), 1)
        ev["initial_soc_kwh"] = round(ev["capacity_kwh"] * rng.uniform(0.55, 0.85), 1)
        ev["discharge_max_kw"] = _pick(rng, 5.0, 10.0, 1)


def gen_ev_v2g_voltage_support(task, rng):
    c = _case(task, "v2g_voltage_support_case")
    for bus in c["base_voltage_pu"]:
        c["base_voltage_pu"][bus] = _pick(rng, 0.93, 0.965, 3)
    for bus in c["q_sensitivity_pu_per_kvar"]:
        c["q_sensitivity_pu_per_kvar"][bus] = _scale(rng, c["q_sensitivity_pu_per_kvar"][bus], 0.8, 1.3, 5)
    for ev in c["evs"].values():
        ev["s_rating_kva"] = _pick(rng, 10.0, 22.0, 1)
        ev["active_power_kw"] = round(ev["s_rating_kva"] * rng.uniform(0.4, 0.75), 1)


def _downstream_nodes(sections: dict[str, Any], source: str, removed: str) -> set[str]:
    adjacency: dict[str, set[str]] = {}
    for sid, sec in sections.items():
        if sid == removed:
            continue
        adjacency.setdefault(sec["from"], set()).add(sec["to"])
        adjacency.setdefault(sec["to"], set()).add(sec["from"])
    seen = {source}
    stack = [source]
    while stack:
        for nxt in adjacency.get(stack.pop(), set()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    all_nodes = {sec["from"] for sec in sections.values()} | {sec["to"] for sec in sections.values()}
    return all_nodes - seen


def gen_fault_section_localization(task, rng):
    c = _case(task, "fault_localization_case")
    sections = c["sections"]
    original = (dict(c["observed_fci_state"]), sorted(c["outage_complaint_nodes"]))
    faulted = rng.choice(sorted(sections))
    outaged = _downstream_nodes(sections, c["source_node"], faulted) | {sections[faulted]["to"]}
    for fci_id, node in c["fci_locations"].items():
        c["observed_fci_state"][fci_id] = node not in outaged and node != c["source_node"] and _node_feeds_fault(
            sections, c["source_node"], node, faulted
        )
    complaining = sorted(set(c["customer_nodes"]) & outaged)
    c["outage_complaint_nodes"] = complaining or [sorted(outaged)[0]]
    if (dict(c["observed_fci_state"]), sorted(c["outage_complaint_nodes"])) == original:
        raise ValueError("drawn fault reproduces the public observation; redraw")


def _node_feeds_fault(sections, source, node, faulted) -> bool:
    """True when fault current flows through `node` on its way to the faulted section."""
    target = sections[faulted]["from"]
    # walk from source toward the faulted section's upstream node
    parent = {source: None}
    stack = [source]
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for sid, sec in sections.items():
        adjacency.setdefault(sec["from"], []).append((sec["to"], sid))
        adjacency.setdefault(sec["to"], []).append((sec["from"], sid))
    while stack:
        current = stack.pop()
        for nxt, _sid in adjacency.get(current, []):
            if nxt not in parent:
                parent[nxt] = current
                stack.append(nxt)
    path = []
    cursor = target
    while cursor is not None:
        path.append(cursor)
        cursor = parent.get(cursor)
    return node in path


def gen_fci_placement(task, rng):
    c = _case(task, "fci_placement_case")
    for sec in c["fault_sections"].values():
        sec["annual_fault_rate"] = _pick(rng, 0.05, 0.25, 2)
        sec["customers_interrupted"] = int(_pick(rng, 30, 150, 0))
    for loc in c["candidate_locations"].values():
        for sid in loc["section_gain_minutes"]:
            loc["section_gain_minutes"][sid] = int(max(0, loc["section_gain_minutes"][sid] * rng.uniform(0.6, 1.4)))


def gen_fci_saidi_caidi(task, rng):
    c = _case(task, "fci_reliability_case")
    c["total_customers"] = int(_pick(rng, 250, 450, 0))
    for sec in c["fault_sections"].values():
        sec["annual_fault_rate"] = _pick(rng, 0.05, 0.25, 2)
        sec["customers_interrupted"] = int(_pick(rng, 30, min(150, c["total_customers"]), 0))
        sec["base_restoration_minutes"] = int(_pick(rng, 60, 110, 0))
    for loc in c["fci_locations"].values():
        for sid in loc["restoration_time_reduction_min"]:
            loc["restoration_time_reduction_min"][sid] = int(
                max(0, loc["restoration_time_reduction_min"][sid] * rng.uniform(0.6, 1.4))
            )


def gen_fdi_state_estimation(task, rng):
    from prototype.evaluators.evaluate_fdi_state_estimation import _expected, _h_row, _spec

    network = _case(task, "network")  # noqa: F841 — unify copies before mutation
    measurements = _case(task, "measurements")
    spec = _spec(task)
    truth = [rng.uniform(-0.09, -0.02), rng.uniform(-0.09, -0.02)]
    attacked = rng.choice(measurements)["id"]
    for m in measurements:
        row = _h_row(spec, m)
        clean = sum(h * x for h, x in zip(row, truth))
        sigma = float(m["sigma_pu"])
        noise = rng.uniform(-0.3, 0.3) * sigma
        bias = rng.choice([-1.0, 1.0]) * rng.uniform(12.0, 20.0) * sigma if m["id"] == attacked else 0.0
        m["value_pu"] = round(clean + noise + bias, 4)
    expected = _expected(task)
    if expected["attacked_measurements"] != [attacked]:
        raise ValueError("LNR identification did not isolate the injected measurement; redraw")


def gen_flisr_restoration(task, rng):
    buses = _case(task, "buses")
    branches = _case(task, "branches")
    for bus in buses:
        if bus["load_kw"] > 0:
            bus["load_kw"] = _pick(rng, 30.0, 110.0, 1)
            bus["priority"] = rng.randint(1, 5)
    for br in branches:
        br["capacity_kw"] = _scale(rng, br["capacity_kw"], 0.85, 1.3, 1)
    closed_mid = [b["id"] for b in branches if b["normally_closed"] and not b["id"].endswith("_s1")]
    task_faulted = _case(task, "faulted_branches")
    task_faulted[:] = [rng.choice(closed_mid)]


def gen_frt_compliance(task, rng):
    trace = _case(task, "event_trace")
    depth = _pick(rng, 0.3, 0.75, 2)
    iq = _pick(rng, 0.1, 0.3, 2)
    times = [0.0, 0.05, round(rng.uniform(0.1, 0.2), 2), round(rng.uniform(0.4, 0.6), 2), 0.8]
    voltages = [1.0, depth, depth, round(min(1.0, depth + rng.uniform(0.2, 0.45)), 2), 1.0]
    iqs = [0.0, round(iq * rng.uniform(0.3, 0.6), 2), iq, round(iq * rng.uniform(0.7, 1.0), 2), 0.0]
    trace[:] = [
        {"time_s": t, "voltage_pu": v, "iq_pu": q, "connected": True}
        for t, v, q in zip(times, voltages, iqs)
    ]


def gen_harmonic_ieee519_compliance(task, rng):
    c = _case(task, "harmonic_case")
    c["pcc"]["max_demand_current_a"] = _pick(rng, 350.0, 650.0, 0)
    c["pcc"]["short_circuit_current_ka"] = _pick(rng, 5.0, 40.0, 1)
    il = c["pcc"]["max_demand_current_a"]
    c["measured"]["fundamental_current_a"] = round(il * rng.uniform(0.85, 1.0), 0)
    for h in c["measured"]["harmonic_currents_a"]:
        c["measured"]["harmonic_currents_a"][h] = round(il * rng.uniform(0.001, 0.075), 1)
    for h in c["measured"]["harmonic_voltages_pct"]:
        c["measured"]["harmonic_voltages_pct"][h] = _pick(rng, 0.3, 3.6, 2)


def gen_hydro_thermal_storage_uc(task, rng):
    c = _case(task, "uc_case")
    c["emission_cap_ton"] = int(_pick(rng, 150, 260, 0))
    for h in c["hours"]:
        h["load_mw"] = int(_pick(rng, 110, 160, 0))
        h["hydro_mw"] = int(_pick(rng, 25, 45, 0))
        h["storage_discharge_mw"] = int(_pick(rng, 8, 25, 0))
    for u in c["thermal_units"]:
        u["cost_usd_per_mwh"] = _scale(rng, u["cost_usd_per_mwh"], 0.8, 1.3, 1)
        u["pmax_mw"] = int(_scale(rng, u["pmax_mw"], 0.9, 1.2, 0))


def gen_ibr_short_circuit_frt(task, rng):
    c = _case(task, "ibr_frt_case")
    c["current_limit_pu"] = _pick(rng, 1.1, 1.3, 2)
    c["prefault_active_current_pu"] = round(c["current_limit_pu"] * rng.uniform(0.6, 0.85), 2)
    c["k_reactive_current_pu_per_pu"] = _pick(rng, 2.0, 5.0, 1)
    for sample in c["samples"]:
        sample["voltage_pu"] = _pick(rng, 0.42, 0.95, 2)


def gen_islanded_microgrid_pq_dispatch(task, rng):
    c = _case(task, "islanded_pq_case")
    c["load"]["p_mw"] = _pick(rng, 25.0, 42.0, 1)
    c["load"]["q_mvar"] = _pick(rng, 8.0, 16.0, 1)
    c["inverter"]["p_available_mw"] = _pick(rng, 14.0, 24.0, 1)
    c["inverter"]["s_rating_mva"] = round(c["inverter"]["p_available_mw"] * rng.uniform(1.1, 1.4), 1)
    c["voltage_model"]["base_voltage_pu"] = _pick(rng, 0.95, 0.985, 3)


def gen_mas_frequency_handover(task, rng):
    c = _case(task, "mas_handover_case")
    c["frequency_hz"] = round(c["nominal_hz"] + rng.choice([-1, 1]) * rng.uniform(0.02, 0.45), 3)
    for agent in c["agents"]:
        agent["latency_ms"] = int(_pick(rng, 15, 120, 0))
        agent["current_mw"] = int(_pick(rng, agent["pmin_mw"], agent["pmax_mw"], 0))
        agent["available"] = rng.random() > 0.2
    c["agents"][rng.randrange(len(c["agents"]))]["available"] = True


def gen_microgrid_economic_dispatch(task, rng):
    c = _case(task, "microgrid_dispatch_case")
    for t in c["load_mw"]:
        c["load_mw"][t] = _scale(rng, c["load_mw"][t], 0.85, 1.15, 1)
    for t in c["pv_mw"]:
        c["pv_mw"][t] = _scale(rng, c["pv_mw"][t], 0.6, 1.3, 1)
    c["generator"]["variable_cost_per_mwh"] = _scale(rng, c["generator"]["variable_cost_per_mwh"], 0.8, 1.3, 1)
    c["battery"]["initial_soc_mwh"] = _pick(rng, c["battery"]["soc_min_mwh"] + 2, c["battery"]["soc_max_mwh"] - 2, 1)


def gen_rolling_microgrid_dispatch(task, rng):
    c = _case(task, "rolling_microgrid_dispatch_case")
    for t in c["load_mw"]:
        c["load_mw"][t] = _scale(rng, c["load_mw"][t], 0.85, 1.15, 1)
    for t in c["pv_mw"]:
        c["pv_mw"][t] = _scale(rng, c["pv_mw"][t], 0.6, 1.3, 1)
    c["generator"]["variable_cost_per_mwh"] = _scale(rng, c["generator"]["variable_cost_per_mwh"], 0.8, 1.3, 1)
    c["battery"]["initial_soc_mwh"] = _pick(rng, c["battery"]["soc_min_mwh"] + 1, c["battery"]["soc_max_mwh"] - 1, 1)


def gen_min_synchronous_share(task, rng):
    c = _case(task, "synchronous_share_case")
    c["demand_mw"] = _pick(rng, 800.0, 1200.0, 0)
    c["largest_loss_mw"] = round(c["demand_mw"] * rng.uniform(0.12, 0.2), 0)
    c["max_rocof_hz_per_s"] = _pick(rng, 1.5, 2.5, 2)
    c["min_scr"] = _pick(rng, 2.0, 2.5, 2)
    c["grid_short_circuit_mva_base"] = _scale(rng, c["grid_short_circuit_mva_base"], 0.85, 1.2, 0)
    for unit in c["sync_units"]:
        unit["p_mw"] = _scale(rng, unit["p_mw"], 0.85, 1.25, 0)
        unit["h_s"] = _pick(rng, 3.0, 7.0, 1)
        unit["short_circuit_mva"] = _scale(rng, unit["short_circuit_mva"], 0.85, 1.25, 0)


def gen_n1_generation_commitment(task, rng):
    c = _case(task, "commitment_case")
    c["demand_mw"] = int(_pick(rng, 200, 320, 0))
    c["reserve_mw"] = int(_pick(rng, 30, 60, 0))
    for unit in c["units"]:
        unit["pmax_mw"] = int(_scale(rng, unit["pmax_mw"], 0.85, 1.25, 0))
        unit["startup_cost_usd"] = int(_scale(rng, unit["startup_cost_usd"], 0.8, 1.3, 0))
        unit["no_load_cost_usd"] = int(_scale(rng, unit["no_load_cost_usd"], 0.8, 1.3, 0))


def gen_operator_breaker_load_actions(task, rng):
    c = _case(task, "operator_action_case")
    c["max_shed_mw"] = int(_pick(rng, 20, 32, 0))
    for br in c["branches"]:
        br["limit_mw"] = int(_scale(rng, br["limit_mw"], 0.9, 1.15, 0))
    overloaded = c["branches"][0]
    overloaded["base_flow_mw"] = int(overloaded["limit_mw"] * rng.uniform(1.1, 1.25))
    for br in c["branches"][1:]:
        br["base_flow_mw"] = int(br["limit_mw"] * rng.uniform(0.6, 0.9))
    for action in c["candidate_actions"]:
        for bid in action.get("flow_delta_mw", {}):
            action["flow_delta_mw"][bid] = round(action["flow_delta_mw"][bid] * rng.uniform(0.8, 1.3), 1)
        if action.get("type") == "shed_load":
            action["mw"] = int(_pick(rng, 8, 18, 0))


def gen_overcurrent_protection(task, rng):
    load = _pick(rng, 250.0, 450.0, 0)
    fault = _pick(rng, 1600.0, 2600.0, 0)
    for key, value in (("max_load_current_a", load), ("min_fault_current_a", fault)):
        task[key] = value
        if key in task.get("public_inputs", {}):
            task["public_inputs"][key] = value
    delay = round(rng.uniform(0.15, 0.35), 2)
    task["downstream_time_delay_s"] = delay
    if "downstream_time_delay_s" in task.get("public_inputs", {}):
        task["public_inputs"]["downstream_time_delay_s"] = delay


def gen_pf_voltage_repair(task, rng):
    base = _case(task, "base_voltage_pu")
    sens = _case(task, "sensitivities")
    bounds = _case(task, "action_bounds")
    base["bus_2"] = _pick(rng, 0.9, 0.94, 3)
    sens["bus_2"]["q_cap_mvar"] = _pick(rng, 0.004, 0.008, 4)
    bounds["q_cap_mvar"]["max"] = _pick(rng, 15.0, 25.0, 1)


def gen_power_quality_event_classification(task, rng):
    c = _case(task, "power_quality_case")
    rules = c["classification_rules"]
    kind = rng.choice(["sag", "swell", "interruption"])
    if kind == "sag":
        level = _pick(rng, rules["sag_lower_pu"] + 0.1, rules["sag_upper_pu"] - 0.05, 2)
    elif kind == "swell":
        level = _pick(rng, rules["swell_lower_pu"] + 0.02, rules["swell_lower_pu"] + 0.18, 2)
    else:
        level = _pick(rng, 0.0, rules["interruption_upper_pu"] - 0.02, 2)
    n = len(c["rms_trace"])
    start = rng.randint(1, max(1, n - 5))
    duration = rng.randint(2, 4)
    for i, point in enumerate(c["rms_trace"]):
        in_event = start <= i < start + duration
        point["voltage_pu"] = level if in_event else _pick(rng, 0.97, 1.03, 2)
        point["current_pu"] = _pick(rng, 1.1, 1.6, 2) if in_event and kind != "swell" else _pick(rng, 0.6, 0.9, 2)


def gen_protected_meter_placement(task, rng):
    c = _case(task, "meter_placement_case")
    meters = c["candidate_meters"]
    for attack in c["attack_vectors"]:
        attack["risk_weight"] = rng.randint(3, 10)
        count = rng.randint(1, 2)
        attack["detectable_by"] = sorted(rng.sample(meters, count))


def gen_pv_volt_var(task, rng):
    timesteps = _case(task, "timesteps")
    for step in timesteps:
        step["base_voltage_pu"] = _pick(rng, 0.93, 1.07, 3)
        step["voltage_sensitivity_pu_per_kvar"] = _pick(rng, 0.0002, 0.0004, 6)
        step["pv_kw"] = _pick(rng, 80.0, 110.0, 1)
        step["inverter_kva"] = round(step["pv_kw"] * rng.uniform(1.15, 1.4), 1)


def gen_three_phase_short_circuit(task, rng):
    c = _case(task, "short_circuit_case")
    c["fault_resistance_pu"] = _pick(rng, 0.003, 0.012, 4)
    for comp in c["positive_sequence_impedances_pu"]:
        comp["r_pu"] = _scale(rng, comp["r_pu"], 0.8, 1.3)
        comp["x_pu"] = _scale(rng, comp["x_pu"], 0.8, 1.3)


def gen_transformer_thermal_loading(task, rng):
    c = _case(task, "transformer_thermal_case")
    c["initial_top_oil_rise_k"] = _pick(rng, 32.0, 50.0, 1)
    for step in c["load_steps"]:
        step["duration_h"] = _pick(rng, 0.5, 3.0, 1)
        step["ambient_c"] = _pick(rng, 12.0, 36.0, 1)
        step["load_factor_pu"] = _pick(rng, 0.6, 1.3, 2)


def gen_transient_stability_prediction(task, rng):
    c = _case(task, "transient_stability_cases")
    for case in c["cases"]:
        case["fault_clearing_time_s"] = _pick(rng, 0.06, 0.2, 3)
        case["estimated_cct_s"] = _pick(rng, 0.08, 0.2, 3)
        case["max_rotor_angle_deg"] = _pick(rng, 120.0, 260.0, 1)
        case["min_voltage_pu"] = _pick(rng, 0.6, 0.82, 2)
        case["damping_ratio_pct"] = _pick(rng, 1.0, 6.0, 1)


def gen_wind_power_forecast(task, rng):
    c = _case(task, "wind_forecast_case")
    for h in c["history"]:
        h["wind_speed_m_s"] = _pick(rng, 5.0, 11.0, 1)
        h["air_density_kg_m3"] = _pick(rng, 1.15, 1.25, 2)
        h["actual_power_mw"] = _pick(rng, 0.5, c["turbine"]["count"] * c["turbine"]["rated_mw_each"] * 0.6, 2)
    for w in c["weather_forecast"]:
        w["wind_speed_m_s"] = _pick(rng, 5.0, 13.0, 1)
        w["air_density_kg_m3"] = _pick(rng, 1.15, 1.25, 2)


def gen_wind_prediction_interval(task, rng):
    c = _case(task, "wind_interval_case")
    for horizon in c["horizons"]:
        base = _pick(rng, 5.0, 11.0, 1)
        for scenario in horizon["scenarios"]:
            scenario["wind_speed_m_s"] = round(max(0.5, base + rng.uniform(-2.0, 2.5)), 1)
            scenario["air_density_kg_m3"] = _pick(rng, 1.15, 1.25, 2)


def gen_ybus_construction(task, rng):
    network = _case(task, "network")
    for br in network["branches"]:
        br["r_pu"] = _scale(rng, br["r_pu"], 0.8, 1.3)
        br["x_pu"] = _scale(rng, br["x_pu"], 0.8, 1.3)
        br["b_pu"] = _scale(rng, br["b_pu"], 0.7, 1.4)
    for shunt in network["shunts"]:
        shunt["b_pu"] = _scale(rng, shunt["b_pu"], 0.7, 1.4)
        shunt["g_pu"] = round(rng.uniform(0.0, 0.02), 4)


GENERATORS: dict[str, Callable[[dict[str, Any], random.Random], None]] = {
    "bess_ancillary_response": gen_bess_ancillary_response,
    "breaker_relay_short_circuit": gen_breaker_relay_short_circuit,
    "cable_ampacity_sizing": gen_cable_ampacity_sizing,
    "commercial_pv_lcoe_uncertainty": gen_commercial_pv_lcoe_uncertainty,
    "contingency_screening": gen_contingency_screening,
    "corrective_transmission_switching": gen_corrective_transmission_switching,
    "critical_clearing_time": gen_critical_clearing_time,
    "dispatch_uncertainty": gen_dispatch_uncertainty,
    "distance_protection_settings": gen_distance_protection_settings,
    "dynamic_thermal_rating": gen_dynamic_thermal_rating,
    "earth_fault_calculation": gen_earth_fault_calculation,
    "en50160_voltage_compliance": gen_en50160_voltage_compliance,
    "ev_v2g_outage_schedule": gen_ev_v2g_outage_schedule,
    "ev_v2g_voltage_support": gen_ev_v2g_voltage_support,
    "fault_section_localization": gen_fault_section_localization,
    "fci_placement": gen_fci_placement,
    "fci_saidi_caidi": gen_fci_saidi_caidi,
    "fdi_state_estimation": gen_fdi_state_estimation,
    "flisr_restoration": gen_flisr_restoration,
    "frt_compliance": gen_frt_compliance,
    "harmonic_ieee519_compliance": gen_harmonic_ieee519_compliance,
    "hydro_thermal_storage_uc": gen_hydro_thermal_storage_uc,
    "ibr_short_circuit_frt": gen_ibr_short_circuit_frt,
    "islanded_microgrid_pq_dispatch": gen_islanded_microgrid_pq_dispatch,
    "mas_frequency_handover": gen_mas_frequency_handover,
    "microgrid_economic_dispatch": gen_microgrid_economic_dispatch,
    "min_synchronous_share": gen_min_synchronous_share,
    "n1_generation_commitment": gen_n1_generation_commitment,
    "operator_breaker_load_actions": gen_operator_breaker_load_actions,
    "overcurrent_protection": gen_overcurrent_protection,
    "pf_voltage_repair": gen_pf_voltage_repair,
    "power_quality_event_classification": gen_power_quality_event_classification,
    "protected_meter_placement": gen_protected_meter_placement,
    "pv_volt_var": gen_pv_volt_var,
    "rolling_microgrid_dispatch": gen_rolling_microgrid_dispatch,
    "three_phase_short_circuit": gen_three_phase_short_circuit,
    "transformer_thermal_loading": gen_transformer_thermal_loading,
    "transient_stability_prediction": gen_transient_stability_prediction,
    "wind_power_forecast": gen_wind_power_forecast,
    "wind_prediction_interval": gen_wind_prediction_interval,
    "ybus_construction": gen_ybus_construction,
}


def generate_case(root: Path, family: str, seed: str, case_id: str) -> dict[str, Any]:
    public_path = root / "tasks" / family / "public" / "case_001" / "task.json"
    public = json.loads(public_path.read_text(encoding="utf-8"))
    last_error: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        task = copy.deepcopy(public)
        rng = random.Random(f"{seed}:{family}:{case_id}:{attempt}")
        try:
            GENERATORS[family](task, rng)
            task["task_id"] = f"{family}_hidden_{case_id}"
            submission = solve_with_baseline(family, task)
        except Exception as exc:  # infeasible draw — try again deterministically
            last_error = exc
            continue
        with tempfile.TemporaryDirectory() as tmpdir:
            task_path = Path(tmpdir) / "task.json"
            submission_path = Path(tmpdir) / "submission.json"
            task_path.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")
            submission_path.write_text(json.dumps(submission, ensure_ascii=False), encoding="utf-8")
            result = evaluate_submission_file(task_path, submission_path)
        if result.get("feasible") and float(result.get("score", 0.0)) > 0.0:
            return task
        last_error = ValueError(f"baseline solution infeasible: {result.get('violations')}")
    raise RuntimeError(f"could not generate feasible hidden case for {family}: {last_error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate hidden benchmark cases deterministically from a seed.")
    parser.add_argument("--seed", required=True, help="Private seed; keep it off the public record.")
    parser.add_argument("--case-id", default="201", help="Hidden case id suffix (default: 201).")
    parser.add_argument("--families", nargs="*", default=None, help="Subset of families (default: all registered).")
    parser.add_argument("--out", default="tasks", help="Output tasks root (default: tasks).")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    families = args.families or sorted(GENERATORS)
    unknown = sorted(set(families) - set(GENERATORS))
    if unknown:
        raise SystemExit(f"no generator registered for: {unknown}")
    missing_eval = sorted(set(families) - set(EVALUATOR_MODULE_BY_FAMILY))
    if missing_eval:
        raise SystemExit(f"no evaluator registered for: {missing_eval}")

    out_root = Path(args.out)
    if not out_root.is_absolute():
        out_root = root / out_root
    written = []
    for family in families:
        task = generate_case(root, family, args.seed, args.case_id)
        case_dir = out_root / family / "hidden" / f"case_{args.case_id}"
        case_dir.mkdir(parents=True, exist_ok=True)
        path = case_dir / "task.json"
        path.write_text(json.dumps(task, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(str(path.relative_to(root) if path.is_relative_to(root) else path))
    print(json.dumps({"generated": len(written), "cases": written}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
