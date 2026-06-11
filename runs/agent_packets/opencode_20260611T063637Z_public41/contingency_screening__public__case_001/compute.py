import json

branches = {
    "l12": {"from": "b1", "to": "b2", "rating": 100.0},
    "l23": {"from": "b2", "to": "b3", "rating": 100.0},
    "l13": {"from": "b1", "to": "b3", "rating": 70.0},
    "l34": {"from": "b3", "to": "b4", "rating": 60.0},
}

contingencies = {
    "out_l12": {"outaged": "l12", "post_flows": {"l23": 95.0, "l13": 88.0, "l34": 30.0}},
    "out_l23": {"outaged": "l23", "post_flows": {"l12": 91.0, "l13": 55.0, "l34": 30.0}},
    "out_l13": {"outaged": "l13", "post_flows": {"l12": 99.0, "l23": 80.0, "l34": 30.0}},
    "out_l34": {"outaged": "l34", "post_flows": {"l12": 80.0, "l23": 60.0, "l13": 40.0}},
}

def is_islanding(outaged_branch):
    # Build adjacency after removing the outaged branch
    adj = {b: set() for b in ["b1", "b2", "b3", "b4"]}
    for bid, br in branches.items():
        if bid == outaged_branch:
            continue
        adj[br["from"]].add(br["to"])
        adj[br["to"]].add(br["from"])
    # BFS from b1
    visited = set()
    stack = ["b1"]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        for n in adj[v]:
            if n not in visited:
                stack.append(n)
    return len(visited) < 4

results = []
for cid, c in contingencies.items():
    overloads = []
    max_loading = 0.0
    for bid, flow in c["post_flows"].items():
        rating = branches[bid]["rating"]
        loading = flow / rating * 100
        max_loading = max(max_loading, loading)
        if loading > 100.0:
            overloads.append((bid, loading))
    islanding = is_islanding(c["outaged"])
    results.append((cid, len(overloads), max_loading, islanding, overloads))
    print(f"{cid}: overloads={len(overloads)}, max_loading={max_loading:.1f}%, islanding={islanding}")

# Sort: more overloads first, then max loading descending, then islanding
results.sort(key=lambda r: (-r[1], -r[2], -r[3]))
print()
ranking = [r[0] for r in results]
print("Ranking:", ranking)
islanding_flags = {r[0]: r[3] for r in results}
print("Islanding flags:", islanding_flags)
