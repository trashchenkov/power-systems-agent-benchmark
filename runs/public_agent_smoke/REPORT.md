# Public agent smoke runs — latest

Ran the agent-agnostic harness over 7 executable public benchmark cases.

## Commands

Prepared per-agent packet directories:

```bash
python scripts/prepare_agent_tasks.py --out runs/agent_packets/codex_latest
python scripts/prepare_agent_tasks.py --out runs/agent_packets/opencode_latest
python scripts/prepare_agent_tasks.py --out runs/agent_packets/hermes_latest
```

Agent runs:

- Codex: `runs/public_agent_smoke/codex-latest/`
- OpenCode: `runs/public_agent_smoke/opencode-latest/`
- Hermes: `runs/public_agent_smoke/hermes-latest/`

Command templates are captured in `scripts/local_agent_run_commands.sh`.

## Summary

- `codex`: 0/7 feasible, total score 0.0.
  - Root cause: Codex CLI auth failed before writing submissions: expired/reused refresh token, 401 Unauthorized. Logs are in `runs/public_agent_smoke/codex-latest/logs/*.stderr.txt`.
- `opencode-deepseek-v4-flash-free`: 6/7 feasible, total score 591.8333.
  - Failed case: `pv_volt_var`, score 0.0, violations: voltage outside limits at `t_low` and `t_high`.
- `hermes-file-toolset`: 7/7 feasible, total score 690.969333.

## Per-case results

### Codex

- `contingency_screening`: infeasible, score 0.0 — agent did not write `submission.json`.
- `fdi_state_estimation`: infeasible, score 0.0 — agent did not write `submission.json`.
- `flisr_restoration`: infeasible, score 0.0 — agent did not write `submission.json`.
- `frt_compliance`: infeasible, score 0.0 — agent did not write `submission.json`.
- `overcurrent_protection`: infeasible, score 0.0 — agent did not write `submission.json`.
- `pf_voltage_repair`: infeasible, score 0.0 — agent did not write `submission.json`.
- `pv_volt_var`: infeasible, score 0.0 — agent did not write `submission.json`.

### OpenCode

- `contingency_screening`: feasible, score 100.0.
- `fdi_state_estimation`: feasible, score 100.0.
- `flisr_restoration`: feasible, score 96.0.
- `frt_compliance`: feasible, score 100.0.
- `overcurrent_protection`: feasible, score 100.0.
- `pf_voltage_repair`: feasible, score 95.8333.
- `pv_volt_var`: infeasible, score 0.0 — voltage outside limits at `t_low` and `t_high`.

### Hermes

- `contingency_screening`: feasible, score 100.0.
- `fdi_state_estimation`: feasible, score 100.0.
- `flisr_restoration`: feasible, score 96.0.
- `frt_compliance`: feasible, score 100.0.
- `overcurrent_protection`: feasible, score 100.0.
- `pf_voltage_repair`: feasible, score 95.833333.
- `pv_volt_var`: feasible, score 99.136.

## Notes

The first harness run is already useful:

- It confirmed that the packet contract works for a Hermes subagent-style CLI run.
- It confirmed OpenCode can solve most cases using a free model, with one domain/control failure in Volt-VAR.
- It surfaced an environment/auth issue for Codex that is separate from benchmark mechanics.
