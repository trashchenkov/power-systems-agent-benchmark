import json

task = json.load(open("task.json"))
trace = task["event_trace"]
curve = task["ride_through_curve"]
rcreq = task["reactive_current_requirement"]

# --- Ride-through envelope check ---
# Interpretation: piecewise-linear boundary between curve points (max_duration, min_voltage)
# For t outside the range, use the nearest segment.
min_voltage = min(p["voltage_pu"] for p in trace)
print(f"Min voltage in trace: {min_voltage}")

# Build interpolation function
import bisect

def envelope_min_voltage(t):
    if t <= curve[0]["max_duration_s"]:
        return curve[0]["min_voltage_pu"]
    if t >= curve[-1]["max_duration_s"]:
        return curve[-1]["min_voltage_pu"]
    # find which segment t falls in
    for i in range(len(curve)-1):
        if curve[i]["max_duration_s"] <= t <= curve[i+1]["max_duration_s"]:
            t1, v1 = curve[i]["max_duration_s"], curve[i]["min_voltage_pu"]
            t2, v2 = curve[i+1]["max_duration_s"], curve[i+1]["min_voltage_pu"]
            frac = (t - t1) / (t2 - t1) if t2 != t1 else 0
            return v1 + frac * (v2 - v1)
    return curve[-1]["min_voltage_pu"]

ride_through_ok = True
for p in trace:
    req = envelope_min_voltage(p["time_s"])
    ok = p["voltage_pu"] >= req
    print(f"  t={p['time_s']:.2f}: V={p['voltage_pu']} >= min_req={req:.3f} -> {'OK' if ok else 'VIOLATION'}")
    if not ok:
        ride_through_ok = False

# --- Alternative: duration-based check ("voltage must not stay below threshold for longer than max_duration") ---
# For each segment threshold, find the longest contiguous period where V < threshold
print()
for seg in curve:
    below = [p for p in trace if p["voltage_pu"] < seg["min_voltage_pu"]]
    if below:
        # compute longest span
        t_span = below[-1]["time_s"] - below[0]["time_s"]
        # but also need to interpolate crossing times
        pass
    # simpler: check voltage/stay-below duration
    times_below = []
    for i, p in enumerate(trace):
        if p["voltage_pu"] < seg["min_voltage_pu"]:
            # start of event
            t_start = p["time_s"]
            # find when it recovers (next point above, interpolate)
            t_end = trace[-1]["time_s"]
            for j in range(i, len(trace)):
                if trace[j]["voltage_pu"] >= seg["min_voltage_pu"]:
                    if j == i:
                        t_end = trace[i]["time_s"]
                    else:
                        # linear interpolate crossing
                        t0, v0 = trace[j-1]["time_s"], trace[j-1]["voltage_pu"]
                        t1, v1 = trace[j]["time_s"], trace[j]["voltage_pu"]
                        frac = (seg["min_voltage_pu"] - v0) / (v1 - v0) if v1 != v0 else 0
                        t_end = t0 + frac * (t1 - t0)
                    break
            duration = t_end - t_start
            print(f"  Below {seg['min_voltage_pu']} pu: t_start={t_start:.3f}, t_recover={t_end:.3f}, duration={duration:.3f}s, max={seg['max_duration_s']}s -> {'OK' if duration <= seg['max_duration_s'] else 'VIOLATION'}")
            break  # just need the first (and longest) contiguous segment
    else:
        print(f"  Below {seg['min_voltage_pu']} pu: never below threshold -> OK")


# --- Reactive current check ---
print()
v_threshold = rcreq["voltage_below_pu"]
min_iq = rcreq["min_iq_pu"]
deadline = rcreq["response_deadline_s"]

# Find when voltage first drops below threshold
sag_start = None
for p in trace:
    if p["voltage_pu"] < v_threshold:
        sag_start = p["time_s"]
        break

if sag_start is not None:
    deadline_time = sag_start + deadline
    print(f"Voltage sag starts at t={sag_start}s, deadline t={deadline_time}s")

    # Check iq at each point after sag start and before recovery
    reactive_ok = True
    met_deadline = False
    for p in trace:
        if p["time_s"] >= sag_start and p["voltage_pu"] < v_threshold:
            if p["time_s"] <= deadline_time and p["iq_pu"] >= min_iq:
                met_deadline = True
            if p["time_s"] >= deadline_time and p["iq_pu"] < min_iq:
                print(f"  VIOLATION at t={p['time_s']}: iq={p['iq_pu']} < min={min_iq}")
                reactive_ok = False
    print(f"  Met deadline requirement: {met_deadline}")
else:
    print("No voltage sag detected")
    reactive_ok = True

print(f"\nride_through_ok={ride_through_ok}, min_voltage={min_voltage}")
print(f"declared_compliant={ride_through_ok and reactive_ok}")
