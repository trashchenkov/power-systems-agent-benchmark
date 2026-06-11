import numpy as np

p_inj = np.array([100.0, -20.0, -50.0, -30.0])

branches = [
    ("l12", 0, 1, 0.1, 75.0),
    ("l13", 0, 2, 0.1, 40.0),
    ("l23", 1, 2, 0.1, 50.0),
    ("l24", 1, 3, 0.1, 50.0),
    ("l34", 2, 3, 0.1, 50.0),
    ("l14", 0, 3, 0.3, 50.0),
]

def solve_pf(closed_set):
    n = 3  # non-slack buses: b2,b3,b4 -> indices 0,1,2
    rmap = {1: 0, 2: 1, 3: 2}
    B = np.zeros((n, n))
    P = np.array([p_inj[1], p_inj[2], p_inj[3]])

    for bid, f, t, x, _ in branches:
        if bid not in closed_set:
            continue
        susc = 1.0 / x
        if f == 0 and t != 0:
            # slack to non-slack: only diagonal
            B[rmap[t], rmap[t]] += susc
        elif f != 0 and t == 0:
            # non-slack to slack: only diagonal
            B[rmap[f], rmap[f]] += susc
        elif f != 0 and t != 0:
            # both non-slack: full coupling
            B[rmap[f], rmap[f]] += susc
            B[rmap[t], rmap[t]] += susc
            B[rmap[f], rmap[t]] -= susc
            B[rmap[t], rmap[f]] -= susc

    theta = np.linalg.solve(B, P)
    full_theta = np.zeros(4)
    full_theta[0] = 0.0
    full_theta[1] = theta[0]
    full_theta[2] = theta[1]
    full_theta[3] = theta[2]

    flows = {}
    loadings = {}
    for bid, f, t, x, rating in branches:
        if bid not in closed_set:
            flows[bid] = 0.0
            loadings[bid] = 0.0
            continue
        flow = (full_theta[f] - full_theta[t]) / x
        flows[bid] = flow
        loadings[bid] = abs(flow) / rating * 100.0 if rating > 0 else 0.0

    return full_theta, flows, loadings

# Base case
base_closed = {"l12", "l23", "l24", "l34"}
theta, flows, loadings = solve_pf(base_closed)
print("===== BASE (post-contingency, no corrective action) =====")
print(f"Theta: {theta}")
for bid, f in flows.items():
    print(f"  {bid}: {f:.4f} MW  (loading {loadings[bid]:.2f}%)")

# Verify P_inj at slack bus
print(f"Slack injection: {theta[0]:.4f} -> check: ", end="")
slack_flow = 0
for bid, f, t, x, _ in branches:
    if bid in base_closed:
        if f == 0:
            slack_flow += (theta[f] - theta[t]) / x
        elif t == 0:
            slack_flow += (theta[f] - theta[t]) / x
print(f"P_slack = {slack_flow:.4f} MW")
print(f"Net injection check (should be near 0): {slack_flow + 20 + 50 + 30:.4f}")
print()

candidates = [
    ("Close l14", {"l12", "l23", "l24", "l34", "l14"}),
    ("Open l23", {"l12", "l24", "l34"}),
    ("Open l24", {"l12", "l23", "l34"}),
    ("Open l34", {"l12", "l23", "l24"}),
]

for name, closed_set in candidates:
    print(f"===== {name} =====")
    theta, flows, loadings = solve_pf(closed_set)
    print(f"Theta: {theta}")
    for bid, f in flows.items():
        print(f"  {bid}: {f:.4f} MW  (loading {loadings[bid]:.2f}%)")
    overloaded = [bid for bid, ld in loadings.items() if ld > 100.0]
    print(f"Overloaded: {overloaded if overloaded else 'None'}")
    # Check connectivity: simple adjacency
    print()
