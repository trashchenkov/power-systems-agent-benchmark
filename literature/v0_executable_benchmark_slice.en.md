# Power Systems Agent Benchmark — v0 Executable Slice

## Purpose

This document freezes a small executable v0 slice from the larger domain-only task bank. The goal is to prove that the benchmark can evaluate tool-using agents with hidden physical/symbolic evaluators instead of relying on LLM-as-a-judge.

## Scope guard

- v0 includes **7 task families**, not the full 41-task balanced core.
- Every task must name its domain source.
- Every task must have a deterministic or simulator-backed hidden evaluator.
- No ElecBench-derived task is included in v0.
- Asset/RUL and electricity-price placeholders remain excluded until stronger primary sources/datasets are mined.

## Selected task families

### REL-TASK-046 — AC power-flow diagnosis and voltage repair

- **Source:** `Power System Analysis and Design_030246bc.txt`, lines 2502–2512.
- **Subdomain:** Power flow, modelling & transmission analysis
- **Confidence:** strong
- **Why in v0:** covers a distinct executable power-systems capability and can be evaluated by deterministic physical/symbolic checks rather than LLM-as-a-judge.
- **Substrate:** pandapower AC power flow
- **Public input / agent output:** public feeder/network case; proposed bus voltage setpoints, shunt/tap/DER Q changes.
- **Hidden evaluator:** run hidden AC PF; score voltage/current violations, action budget, losses/regret.
- **Baseline:** pandapower/PYPOWER no-op and greedy voltage repair baseline.
- **Initial implementation target:** one public case, one hidden randomized case family, schema validation, baseline, and smoke test.

### GAP-TASK-005 — N-1 contingency screening and islanding detection

- **Source:** Graph Computing based Fast Screening in Contingency Analysis (2019-03-29, arXiv:1904.00044v1) — https://arxiv.org/abs/1904.00044v1; Fast Grid Splitting Detection for N-1 Contingency Analysis by Graph Computing (2019-04-07, arXiv:1904.03587v1) — https://arxiv.org/abs/1904.03587v1
- **Subdomain:** Transmission operations, contingency & congestion management
- **Confidence:** medium-strong.
- **Why in v0:** covers a distinct executable power-systems capability and can be evaluated by deterministic physical/symbolic checks rather than LLM-as-a-judge.
- **Substrate:** NetworkX + pandapower/PYPOWER DC/AC PF
- **Public input / agent output:** network graph, base flows, contingency list; severity ranking and islanding flags.
- **Hidden evaluator:** hidden contingencies; missed critical outage rate, false negatives for islanding, runtime.
- **Baseline:** all-branches DC screening baseline.
- **Initial implementation target:** one public case, one hidden randomized case family, schema validation, baseline, and smoke test.

### GAP-TASK-003 — Distribution service restoration / FLISR

- **Source:** A Two-Stage Service Restoration Method for Electric Power Distribution Systems (2020-04-16, arXiv:2004.07921v1) — https://arxiv.org/abs/2004.07921v1
- **Subdomain:** Distribution automation, FLISR & feeder reconfiguration
- **Confidence:** medium-strong.
- **Why in v0:** covers a distinct executable power-systems capability and can be evaluated by deterministic physical/symbolic checks rather than LLM-as-a-judge.
- **Substrate:** pandapower or OpenDSS + NetworkX
- **Public input / agent output:** faulted feeder graph, switch states, priorities, DER; switching/restoration plan.
- **Hidden evaluator:** radiality, voltage/current constraints, restored priority load, switch count.
- **Baseline:** greedy critical-load restoration baseline.
- **Initial implementation target:** one public case, one hidden randomized case family, schema validation, baseline, and smoke test.

### REL-TASK-036 — Line overcurrent protection setting

- **Source:** same, lines 548–558.
- **Subdomain:** Protection, faults & relay engineering
- **Confidence:** strong
- **Why in v0:** covers a distinct executable power-systems capability and can be evaluated by deterministic physical/symbolic checks rather than LLM-as-a-judge.
- **Substrate:** deterministic protection formula engine
- **Public input / agent output:** short-circuit currents, load currents, CT/relay data; pickup/time-dial settings.
- **Hidden evaluator:** selectivity, sensitivity, thermal/equipment constraints, numeric tolerance.
- **Baseline:** rule-based textbook formula baseline.
- **Initial implementation target:** one public case, one hidden randomized case family, schema validation, baseline, and smoke test.

### GAP-TASK-009 — PV Volt-VAR control for sag/swell mitigation

- **Source:** Local Control of Reactive Power by Distributed Photovoltaic Generators (2010-06-01, arXiv:1006.0160v1) — https://arxiv.org/abs/1006.0160v1; Options for Control of Reactive Power by Distributed Photovoltaic Generators (2010-08-04, arXiv:1008.0878v1) — https://arxiv.org/abs/1008.0878v1
- **Subdomain:** Power quality & standards
- **Confidence:** strong.
- **Why in v0:** covers a distinct executable power-systems capability and can be evaluated by deterministic physical/symbolic checks rather than LLM-as-a-judge.
- **Substrate:** pandapower/OpenDSS time-series distribution PF
- **Public input / agent output:** feeder, PV ratings, irradiance ramps, inverter Q limits; control law/parameters.
- **Hidden evaluator:** violation-hours, losses, Q limit violations, oscillation/control effort.
- **Baseline:** IEEE 1547-like default Volt-VAR curve baseline.
- **Initial implementation target:** one public case, one hidden randomized case family, schema validation, baseline, and smoke test.

### GAP-TASK-006 — False-data injection detection in state estimation

- **Source:** Modeling and performance evaluation of stealthy false data injection attacks on smart grid in the presence of corrupted measurements (2016-05-20, arXiv:1605.06180v1) — https://arxiv.org/abs/1605.06180v1; Graphical Methods for Defense Against False-data Injection Attacks on Power System State Estimation (2013-04-15, arXiv:1304.4151v4) — https://arxiv.org/abs/1304.4151v4
- **Subdomain:** OT cybersecurity, state estimation & bad data
- **Confidence:** strong; classic primary power cyber literature.
- **Why in v0:** covers a distinct executable power-systems capability and can be evaluated by deterministic physical/symbolic checks rather than LLM-as-a-judge.
- **Substrate:** DC state estimator + attack generator
- **Public input / agent output:** H matrix/network, measurements, noise covariance; attack labels/localization/corrected state.
- **Hidden evaluator:** detection F1, localization precision/recall, false alarms, estimation error.
- **Baseline:** chi-square residual bad-data detector baseline.
- **Initial implementation target:** one public case, one hidden randomized case family, schema validation, baseline, and smoke test.

### GAP-TASK-011 — Grid-code FRT compliance check for IBR

- **Source:** Grid-Forming Control Based On Emulated Synchronous Condenser Strategy Compliant With Challenging Grid Code Requirements (2023-03-01, arXiv:2303.00391v2) — https://arxiv.org/abs/2303.00391v2; A Novel Decentralized Inverter Control Algorithm for Loss Minimization and LVRT Improvement (2022-07-24, arXiv:2207.11700v3) — https://arxiv.org/abs/2207.11700v3
- **Subdomain:** Grid codes, interconnection & standards compliance
- **Confidence:** medium-strong; exact standard clauses still need source-specific extraction.
- **Why in v0:** covers a distinct executable power-systems capability and can be evaluated by deterministic physical/symbolic checks rather than LLM-as-a-judge.
- **Substrate:** rule-based compliance checker over event traces
- **Public input / agent output:** voltage/frequency trace, current response, grid-code curve; pass/fail report.
- **Hidden evaluator:** clause-level pass/fail, ride-through envelope, reactive current support timing/magnitude.
- **Baseline:** static envelope checker baseline.
- **Initial implementation target:** one public case, one hidden randomized case family, schema validation, baseline, and smoke test.

## Implementation order

1. **AC PF diagnosis/voltage repair** — easiest pandapower-first MVP and validates the public/hidden evaluator contract.
2. **N-1 contingency screening** — reuses network cases and adds ranking/islanding metrics.
3. **Protection setting** — deterministic formula engine; strong domain specificity.
4. **PV Volt-VAR** — time-series distribution PF and DER control.
5. **FLISR restoration** — topology/action task with radiality and priority-load scoring.
6. **FDI state-estimation detection** — cyber/SE layer with synthetic hidden attacks.
7. **FRT compliance** — standards/compliance task; initially rule-based, later tied to exact clauses.

## Public/hidden split

- **Public:** task statement, schema, one small case, baseline run, scoring description.
- **Hidden:** randomized seeds, larger cases, ground-truth simulator outputs, attack vectors, contingency lists, compliance thresholds when license/standard text requires caution.

## Required artifacts per task family

- `tasks/public/<family>/<case_id>/task.json`
- `tasks/public/<family>/<case_id>/input.*`
- `baselines/<family>/baseline.py`
- `prototype/evaluators/evaluate_<family>.py`
- `tests/test_<family>_evaluator.py`
- source note in task metadata: `source.title`, `source.url_or_local_path`, `source.locator`, `source.confidence`
