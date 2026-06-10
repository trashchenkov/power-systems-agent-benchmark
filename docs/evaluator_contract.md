# Evaluator contract

Every benchmark task must have a programmatic evaluator. Human/LLM judging can be added only as secondary diagnostics.

## CLI shape

```bash
python prototype/evaluators/<family>.py TASK_JSON SUBMISSION_JSON
```

The evaluator must:

1. load the public task artifact;
2. load the submitted structured answer;
3. validate schema and action bounds;
4. apply the submitted actions/decision to the simulator, formula, graph, or hidden realization set;
5. recompute all scored quantities independently;
6. return one JSON object to stdout.

## Required output fields

```json
{
  "task_id": "string",
  "family": "string",
  "feasible": true,
  "score": 0.0,
  "violations": [],
  "metrics": {},
  "evidence": {}
}
```

Minimum semantics:

- `task_id`: copied from task artifact.
- `family`: canonical family slug.
- `feasible`: true only if all hard constraints pass.
- `score`: normalized `[0, 1]`, with zero reserved for infeasible outputs unless the family explicitly defines partial safety scoring.
- `violations`: list of human-readable and stable-enough machine-debuggable violation strings.
- `metrics`: raw metrics used to compute score.
- `evidence`: evaluator-side evidence such as final voltage table, contingency severities, trip times, SAIDI/CAIDI components.

## Evaluator invariants

- Never trust agent-provided derived metrics.
- Never use hidden oracle data from the submission.
- Keep public and hidden cases callable through the same evaluator interface.
- Use deterministic seeds and record them in evaluator logs, but do not expose hidden seeds to agents in sealed evaluation.
- Validate illegal actions before scoring objective quality.
- Fail closed: unknown actions, unknown components, malformed values, or non-convergence must be violations.

## Family-specific evaluator examples

### `pf_voltage_repair`

- Load network/case.
- Apply bounded actions: taps, voltage setpoints, shunts, redispatch, load shed if allowed.
- Run AC power flow.
- Check convergence, bus voltage limits, line/trafo loading, generator bounds.
- Score feasibility first, then action cost and residual deviation.

### `dispatch_uncertainty`

- Validate dispatch/reserve schedule.
- Sample or load hidden forecast realizations.
- Check balance, generator limits, ramp limits, reserve deployment, curtailment.
- Score expected cost, regret, violations, and renewable curtailment.

### `n1_contingency`

- Apply submitted preventive/corrective plan.
- Enumerate hidden contingency set.
- Run AC power flow for each outage.
- Score critical-contingency recall, post-contingency violations, severity regret, and false-safe penalties.

### `fci_reliability`

- Load radial feeder graph and reliability parameters.
- Apply FCI placement or requested calculation.
- Recompute expected patrol/repair/outage durations.
- Score SAIDI/CAIDI error and placement objective gap.

### `relay_coordination`

- Load CT/fault-current/relay-curve parameters.
- Compute pickup, time dial, IEC/IEEE trip times.
- Check coordination interval and selectivity.
- Score numerical error and safety violations.
