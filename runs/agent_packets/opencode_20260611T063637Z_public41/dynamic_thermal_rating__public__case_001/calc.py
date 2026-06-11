import math

# Conductor parameters
diameter_m = 22.4 / 1000  # m
r20_per_km = 0.118  # ohm/km
r20_per_m = r20_per_km / 1000  # ohm/m
alpha = 0.00403  # per deg C
emissivity = 0.7
solar_abs = 0.7
t_max = 75.0  # deg C
sigma = 5.67e-8  # Stefan-Boltzmann
h_conv_at_1ms = 0.72  # W/m/degC at 1 m/s

# Resistance at Tmax
r_tmax = r20_per_m * (1 + alpha * (t_max - 20))

weather = [
    ("t00", 18.0, 2.8, 150.0),
    ("t01", 31.0, 0.7, 850.0),
    ("t02", 27.0, 1.4, 600.0),
    ("t03", 22.0, 3.2, 100.0),
]

results = {}
for ts, ta, v, solar in weather:
    # Solar heating per meter
    q_solar = solar_abs * solar * diameter_m

    # Convective cooling per meter (scaling with v^0.5)
    q_conv = h_conv_at_1ms * math.sqrt(v / 1.0) * (t_max - ta)

    # Radiative cooling per meter
    t_max_k = t_max + 273
    ta_k = ta + 273
    q_rad = emissivity * sigma * math.pi * diameter_m * (t_max_k**4 - ta_k**4)

    # Ampacity
    I = math.sqrt(max(0, (q_conv + q_rad - q_solar) / r_tmax))
    results[ts] = I
    print(f"{ts}: q_solar={q_solar:.4f}, q_conv={q_conv:.4f}, q_rad={q_rad:.4f}, I={I:.4f} A")

print()
scheduled = 520.0

# Find min ampacity and limiting timestamp
min_ts = min(results, key=results.get)
min_val = results[min_ts]

overload = [ts for ts, I in results.items() if I < scheduled]

print(f"Scheduled current: {scheduled} A")
print(f"Ampacities: {results}")
print(f"Minimum ampacity: {min_val:.4f} A at {min_ts}")
print(f"Overload timestamps: {overload}")
