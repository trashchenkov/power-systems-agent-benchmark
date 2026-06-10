# Power-Systems Agent Benchmark Spec v0

Status: draft v0 derived from `literature/task_bank_v0_from_local_archive.md`.

Goal: define an executable, simulator-backed benchmark for power-systems agents where the primary score comes from hidden recomputation of physical/economic/reliability constraints, not from LLM-as-a-judge report grading.

## MVP slice

The first benchmark track should cover six task families:

1. AC load-flow correction / voltage violation repair — `pandapower` hidden evaluator; dependency-free public surrogate in this prototype.
2. Dispatch / OPF under forecast uncertainty — `pandapower` OPF first, PyPSA optional later.
3. N-1 contingency assessment and mitigation — `pandapower` contingency loop.
4. FCI reliability impact and placement — custom radial-feeder reliability graph evaluator.
5. Inverse-time overcurrent relay coordination — formula-based IEC/IEEE relay evaluator.
6. DER/EV voltage support in a distribution feeder — `pandapower` first, OpenDSS optional later.

## Benchmark object model

Each task instance is a directory with public inputs and hidden evaluator metadata:

```text
tasks/<family>/<split>/<case_id>/
  task.json              # public task statement + machine-readable input contract
  assets/                # public network/data files, if any
  sample_submission.json # optional trivial format example
```

Hidden evaluation keeps private perturbations, answer keys, random seeds, and evaluator configs outside the public task tree:

```text
hidden/<family>/<case_id>/
  evaluator_config.json
  perturbations.json
  expected_ranges.json
```

The agent must submit one JSON object per case. Free-form reasoning can be included under `rationale`, but only structured fields are scored by the hard evaluator.

## Common task schema

Required top-level fields:

- `task_id`: stable unique id.
- `family`: canonical family slug.
- `substrate`: simulator/model used by the hidden evaluator.
- `objective`: one-paragraph task objective.
- `public_inputs`: all data visible to the agent.
- `submission_schema`: JSON shape expected from the agent.
- `hard_constraints`: constraints that produce zero score or heavy penalty when violated.
- `metrics`: ordered scoring metrics.
- `source_evidence`: source documents or literature notes used to justify the task.

See `schemas/task.schema.json` for a machine-readable draft.

## Evaluation contract

Every evaluator must be callable as:

```bash
python prototype/evaluators/<evaluator>.py path/to/task.json path/to/submission.json
```

It must return JSON with:

- `task_id`
- `feasible`: boolean hard-constraint verdict
- `score`: numeric, normalized to `[0, 1]`, where `1.0` is the best feasible result`
- metric-specific evidence, e.g. final voltage, cost, violations, contingency list, SAIDI, relay trip times
- `violations`: list of machine-readable/human-readable reasons

## Public/hidden split

Public artifacts should teach the interface but not leak the hidden score distribution:

- public cases: small, synthetic, deterministic, with sample submissions;
- hidden cases: generated from versioned seeds, with perturbations of load/generation/faults/topology;
- hidden evaluator: independently recomputes physics/formulas from raw network/data, never trusts agent-provided derived values;
- replay logs: store tool calls, actions, simulator state, violations, and final metrics.

## Scoring philosophy

Primary score is execution-based:

1. Safety/physics constraints first: voltage limits, line loading, islanding, relay selectivity, illegal switching, unavailable resource use.
2. Objective value second: cost, regret, outage reduction, served load, reliability improvement.
3. Operational quality third: action count, switching burden, reserve margin, explanation/evidence.
4. LLM-as-a-judge only optional and secondary, for rationale readability/diagnostic quality; it must not determine the main benchmark ranking.

## MVP implementation order

1. Freeze schema and public/hidden layout.
2. Implement dependency-free smoke evaluator for voltage repair to validate submission/evaluator contracts.
3. Replace the surrogate voltage evaluator with a `pandapower` evaluator once dependencies are pinned.
4. Add dispatch/OPF public case and hidden forecast perturbation contract.
5. Add N-1 contingency loop.
6. Add one non-`pandapower` task: FCI reliability or relay coordination, to prove the benchmark is simulator-agnostic.
