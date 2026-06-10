# Source card: N-1 generation commitment

Family `n1_generation_commitment` (`GAP-TASK-001`, formerly published as
`scuc_n1`) is a compact single-period commitment surrogate: choose the
least-cost set of units whose total capacity covers demand plus reserve and
still covers demand after losing the largest committed unit (N-1 on
generation). Cost is startup plus no-load cost of the committed set.

Naming note: the family was renamed from `scuc_n1` because the original name
oversold the task. A real security-constrained unit commitment is a
multi-period MILP with ramps, minimum up/down times, network constraints, and
line contingencies; none of those are modeled here. The source paper
(Security Constrained Unit Commitment with Corrective Transmission Switching,
arXiv:2001.00597) motivates the security framing only — this executable case
keeps just the loss-of-largest-unit capacity rule. A full SCUC instance over
PGLib-style cases is a candidate for a simulator/solver-backed hidden track.
