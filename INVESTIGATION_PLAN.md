# INVESTIGATION_PLAN.md

## Primary mode

benchmark-mining

## Initial threads

T1 — Existing agent/LLM benchmarks and any power/energy-specific benchmarks
- Why: avoid duplicating existing work and find positioning.
- Sources: papers, GitHub repos, benchmark pages.
- Stop: identify relevant benchmarks and gaps.

T2 — Power-systems substrate options
- Why: benchmark credibility depends on simulators, cases, solvers, deterministic scoring.
- Sources: pandapower, MATPOWER, Grid2Op, PowerModels.jl, OpenDSS, GridLAB-D docs/repos.
- Stop: shortlist substrate options and fit to agent tasks.

T3 — Candidate task taxonomy for agent benchmark
- Why: translate power systems work into agent-evaluable tasks.
- Sources: grid operation/planning/control literature, public tutorials, simulator examples.
- Stop: candidate tasks with inputs/outputs/metrics/failure modes.
