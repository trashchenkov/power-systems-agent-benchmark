# REPORT.md — first pass

## Direct answer

The benchmark should probably be designed as an executable, tiered power-systems agent benchmark rather than a pure QA/literature benchmark.

Recommended initial positioning:

- MVP: pandapower-first tasks for deterministic PF/OPF/contingency diagnosis and mitigation.
- Advanced sequential-operation tier: Grid2Op/L2RPN-style environments.
- Distribution tier: OpenDSS/DSS-Extensions for unbalanced feeders, DER and Volt/VAR.
- OPF rigor tier: PGLib-OPF + PowerModels.jl or MATPOWER-compatible cases.
- Dynamics tier: ANDES for transient/small-signal tasks.
- Planning/dispatch tier: PyPSA for multi-period dispatch/storage/planning.

## Benchmark gap

Existing public work splits into two groups:

1. Agentic LLM/energy benchmarks:
   - PowerAgentBench: closest to physical grid tool-agent benchmark.
   - EnergyAgentBench: adjacent, energy infrastructure and planning over live data.

2. Simulator/RL/optimization benchmarks:
   - Grid2Op/L2RPN, PowerGym, PowerGridworld, CityLearn, SustainGym, PGLib-OPF, MATPOWER.

The opportunity is to combine executable physical tasks with LLM-agent-specific evaluation: tool-call validity, evidence, schema adherence, explanation fidelity, constraint violations, action cost, and hidden recomputation.

## Candidate MVP task families

1. Power-flow diagnosis
   - Input: network case + observed violations or failed PF.
   - Agent output: diagnosis, violated elements, proposed repair.
   - Evaluator: recompute PF; score violations, correctness, action cost, evidence.

2. N-1 contingency audit
   - Input: case + contingency set or budget.
   - Agent output: ranked dangerous contingencies with evidence.
   - Evaluator: hidden recomputation; recall@k, severity regret, evidence rate.

3. Corrective dispatch / OPF repair
   - Input: stressed case, constraints, allowed controls.
   - Output: generator setpoint/load shedding/topology/control action JSON.
   - Evaluator: feasibility, objective/action cost, residual violations.

4. Distribution Volt/VAR control
   - Input: feeder, load/PV profile, allowed taps/caps/inverter vars.
   - Output: schedule/actions.
   - Evaluator: voltage violations, losses, action count, device limits.

5. Restoration / outage response
   - Input: failed elements, switch states, load priorities.
   - Output: switching/restoration plan.
   - Evaluator: served load, radiality/safety constraints, violations, action cost.

6. Dynamics/stability triage
   - Input: event/fault scenario and dynamic model.
   - Output: stability assessment or emergency action.
   - Evaluator: time-domain simulation; stability margins, load shed, violations.

## Evaluation contract idea

Each task should have:

- natural-language operator prompt;
- machine-readable case files;
- allowed tools and schemas;
- budget limits;
- required final JSON answer;
- optional explanatory report;
- hidden evaluator that recomputes physical validity;
- trajectory log for tool calls and evidence.

Core scoring dimensions:

- physical correctness;
- constraint violation severity;
- objective/action cost;
- reliability over randomized hidden cases;
- tool-call/schema validity;
- evidence fidelity;
- explanation vs simulation consistency;
- refusal/timeout/invalid-action rate.

## Immediate next steps

1. Deep inspect PowerAgentBench repo and reproduce its evaluator mentally or via smoke run.
2. Draft a concrete MVP schema for 3 pandapower tasks.
3. Choose 5–10 public cases and define hidden perturbation generation.
4. Create a minimal harness: `task.json`, `case/`, `tools.py`, `evaluator.py`, `expected_schema.json`.
5. Run one baseline: scripted solver baseline + one LLM-agent run.


# Update — PowerAgentBench deep inspection (2026-06-08T05:56:10.940140+00:00)

## What to copy from PowerAgentBench

- Public/hidden split: agent sees public case/action/tool APIs; evaluator recomputes hidden physical validity.
- Small curated entry level: a 39-bus, few-contingency task is acceptable as Level 0/1 if the workflow is real.
- Discrete bounded action space: easier validation and more operationally interpretable actions.
- Separate physical and agentic metrics: violation/action cost vs evidence/tool/schema/budget behavior.
- Scripted baselines: random, heuristic, LODF/base-loading, hybrid+redispatch.

## What not to copy blindly

- Narrow scope: current release is steady-state IEEE 39.
- Level 2 DC approximation is useful for benchmark mechanics, but not enough for a serious AC security benchmark.
- JSON-command LLM interface is portable but less natural than native tool/function calling.
- No declared license was visible in GitHub metadata; reuse code carefully unless license is clarified.

## Revised MVP recommendation

Build a pandapower-first MVP with three task families:

1. PF diagnosis and repair.
2. N-1/N-k contingency ranking under validation budget.
3. Corrective dispatch / OPF repair.

Use PowerAgentBench's public/hidden and metrics design, but define a simulator-agnostic task schema from day one so future tiers can use Grid2Op, OpenDSS, PowerModels/PGLib, ANDES, and PyPSA.

See:

```text
notes/PowerAgentBench_deep_inspection.md
notes/MVP_task_contract.md
```
