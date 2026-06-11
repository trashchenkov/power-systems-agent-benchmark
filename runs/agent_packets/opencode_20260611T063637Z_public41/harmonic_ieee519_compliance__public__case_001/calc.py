import json, math

with open("task.json") as f:
    task = json.load(f)

hc = task["harmonic_case"]
pcc = hc["pcc"]
meas = hc["measured"]

# Step 1: Isc/IL
isc_a = pcc["short_circuit_current_ka"] * 1000.0
il = pcc["max_demand_current_a"]
ratio = isc_a / il
print(f"Isc = {isc_a} A, IL = {il} A")
print(f"Isc/IL = {ratio}")

# Step 2: select limit row
table = hc["current_limit_table"]
selected = None
for row in table:
    if row["isc_il_below"] > ratio:
        selected = row
        break
print(f"Selected row: isc_il_below={selected['isc_il_below']}")
print(f"  TDD limit: {selected['tdd_pct']}")
print(f"  h<11: {selected['h_below_11_pct']}")
print(f"  11-17: {selected['h_11_to_17_pct']}")
print(f"  17-23: {selected['h_17_to_23_pct']}")
print(f"  23-35: {selected['h_23_to_35_pct']}")
print(f"  h>=35: {selected['h_35_up_pct']}")

# Step 3: TDD
cur = meas["harmonic_currents_a"]
sum_sq = sum(float(v)**2 for v in cur.values())
tdd = math.sqrt(sum_sq) / il * 100
print(f"\nTDD = {tdd}% (limit {selected['tdd_pct']}%)")
print(f"TDD violation: {tdd > selected['tdd_pct']}")

# Step 4: Individual current harmonics
current_violations = []
for h_str, val_a in cur.items():
    h = int(h_str)
    pct = val_a / il * 100
    if h < 11:
        limit = selected["h_below_11_pct"]
    elif h < 17:
        limit = selected["h_11_to_17_pct"]
    elif h < 23:
        limit = selected["h_17_to_23_pct"]
    elif h < 35:
        limit = selected["h_23_to_35_pct"]
    else:
        limit = selected["h_35_up_pct"]
    violation = pct > limit
    print(f"  h={h}: {pct}% vs limit {limit}% - {'VIOLATION' if violation else 'ok'}")
    if violation:
        current_violations.append(h_str)

if tdd > selected["tdd_pct"]:
    current_violations.append("tdd")

print(f"\nCurrent violations: {current_violations}")

# Step 5: Voltage THD
v_pct = meas["harmonic_voltages_pct"]
v_sum_sq = sum(float(v)**2 for v in v_pct.values())
v_thd = math.sqrt(v_sum_sq)
v_limits = hc["voltage_limits"]
print(f"\nVoltage THD = {v_thd}% (limit {v_limits['thd_pct']}%)")
print(f"VTHD violation: {v_thd > v_limits['thd_pct']}")

# Step 6: Individual voltage harmonics
voltage_violations = []
for h_str, pct in v_pct.items():
    violation = pct > v_limits["individual_pct"]
    print(f"  Vh={h_str}: {pct}% vs limit {v_limits['individual_pct']}% - {'VIOLATION' if violation else 'ok'}")
    if violation:
        voltage_violations.append(h_str)

if v_thd > v_limits["thd_pct"]:
    voltage_violations.append("thd")

print(f"\nVoltage violations: {voltage_violations}")

# Step 7: Verdict
compliant = len(current_violations) == 0 and len(voltage_violations) == 0
print(f"\nCompliant: {compliant}")

result = {
    "isc_over_il": ratio,
    "tdd_pct": round(tdd, 6),
    "current_violations": current_violations,
    "voltage_thd_pct": round(v_thd, 6),
    "voltage_violations": voltage_violations,
    "compliant": compliant,
    "rationale": f"Isc/IL={ratio:.2f} selects row isc_il_below={selected['isc_il_below']}; TDD={tdd:.3f}% (limit {selected['tdd_pct']}%); VTHD={v_thd:.3f}% (limit {v_limits['thd_pct']}%)"
}

print("\n\nSubmission:")
print(json.dumps(result, indent=2))
