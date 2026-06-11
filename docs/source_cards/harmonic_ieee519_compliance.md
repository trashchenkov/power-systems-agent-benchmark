# Source card: IEEE 519 harmonic compliance at the PCC

Family `harmonic_ieee519_compliance` (`CORE-SWAP-003`) models the routine
power-quality study at a point of common coupling: compute the short-circuit
ratio Isc/IL, select the matching IEEE 519-2014 current-distortion limit row,
compute TDD and per-harmonic current percentages against the maximum demand
current IL, compute voltage THD, and report every violated limit plus the
overall verdict.

Key engineering trap preserved by the task: TDD is normalized by the maximum
demand current IL, not by the measured fundamental — the case publishes both so
a careless denominator choice produces a wrong answer. The IEEE 519 limit
table (current rows keyed by Isc/IL for 120 V-69 kV systems; voltage limits
3 % individual / 5 % THD for 1-69 kV buses) is published inside the task so
the deterministic evaluator and the agent share identical reference data.

Both compliant and non-compliant draws are valid benchmark instances; hidden
cases vary Isc/IL across table rows and harmonic magnitudes across the limits.

Replacement note: this family replaces `pv_soft_cost_sobol` in the 41-task
balanced core. Harmonic compliance was uncovered (the existing power-quality
family classifies RMS events such as sags and swells), while Sobol
decomposition of PV soft costs was generic sensitivity analysis with little
power-systems content.
