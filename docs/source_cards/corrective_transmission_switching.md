# Source card: corrective transmission switching after contingency

## Benchmark family

- Family: `corrective_transmission_switching`
- Candidate: `GAP-TASK-002`
- Subdomain: transmission operations, contingency & congestion management

## Primary source provenance

- **Security Constrained Unit Commitment with Corrective Transmission Switching**
  - Locator: https://arxiv.org/abs/2001.00597v1
  - Local benchmark note: `literature/task_bank_v4_gap_fill_balanced.md#GAP-TASK-002`
  - Confidence: medium-strong

## Source-derived operational problem

The source frames corrective transmission switching as an operational/security action used after contingencies to remove network security violations and improve dispatch feasibility/cost. The benchmark adaptation isolates the corrective switching subproblem from the full SCUC formulation:

- a post-contingency network has an overloaded branch;
- a small set of candidate branch status changes is available;
- the operator/agent must choose a limited corrective action;
- the resulting topology must remain connected and satisfy emergency line limits.

## Public executable adaptation

The public case uses a compact lossless DC power-flow model so the task is executable without external solver dependencies:

- buses with balanced active-power injections;
- branches with reactance `x_pu`, emergency rating `rating_mw`, and initial `closed` state;
- one initiating contingency is already represented as an initially open branch;
- candidate switches are explicit open/close actions;
- the agent must compute post-action DC flows and submit the selected action.

This is intentionally a small instance, but it is no longer an oracle-copy task: the agent must derive the action from the network data and candidate actions.

## Agent-facing input

- `task.json` with buses, branches, candidate switches, switching budget, and DC model description.
- No `expected_submission`, `baseline_submission`, hidden evaluator state, or source-task path is exposed in the agent packet.

## Submission contract

```json
{
  "close_branches": ["l14"],
  "open_branches": [],
  "reported_flows_mw": {"l12": 70.714286},
  "rationale": "optional free text"
}
```

`reported_flows_mw` is diagnostic only; the evaluator recomputes flows independently.

## Evaluator

File: `prototype/evaluators/evaluate_corrective_transmission_switching.py`

Checks:

1. `close_branches` and `open_branches` are lists of known branch IDs.
2. Only candidate switches are used.
3. Switch count does not exceed `switching_budget`.
4. Resulting graph remains connected.
5. Independent DC power flow has no active branch above 100% rating.
6. Score is feasible-first, with minor penalties for extra switching or higher max loading relative to enumerated feasible candidates.

## Baselines

File: `baselines/corrective_transmission_switching/baseline.py`

The reference baseline enumerates no-action and all one-switch candidates, runs the same DC model, and returns the feasible minimum-action repair.

## Known limitations and next step

- Public v1 uses a small DC instance, not the full SCUC+CTS MILP from the source.
- Hidden variants should scale to larger MATPOWER/PGLib-style DC cases and include multiple contingencies.
- A later advanced version should couple this with SCUC dispatch decisions and objective-gap scoring against a MILP reference.
