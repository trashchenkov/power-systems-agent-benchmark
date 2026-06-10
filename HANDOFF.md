# Handoff

This workspace contains the runnable benchmark prototype.

## Track A — runnable benchmark repository scaffold

Location:

```text
/root/investigation-runs/power-systems-agent-benchmark
```

Recommended future GitHub repo name:

```text
power-systems-agent-benchmark
```

Core files ready for a first repo draft:

```text
README.md
LICENSE
.gitignore
pyproject.toml
.github/workflows/check.yml
benchmark_spec_v0.md
PACKAGING_STRATEGY.md
docs/evaluator_contract.md
docs/public_hidden_split.md
docs/metrics.md
docs/agent_protocol.md
schemas/task.schema.json
schemas/submission.schema.json
schemas/evaluation-result.schema.json
scripts/check.sh
scripts/validate_benchmark_artifacts.py
scripts/evaluate_submission.py
scripts/run_public_baselines.py
scripts/prepare_agent_tasks.py
scripts/run_agent_command.py
scripts/local_agent_run_commands.sh
tasks/<family>/public/case_001/task.json
tasks/<family>/public/case_001/sample_submission.json
prototype/evaluators/evaluate_<family>.py
baselines/<family>/baseline.py
tests/test_*_evaluator.py
tests/test_agent_harness.py
runs/public_agent_smoke/REPORT.md
```

Executable public families currently implemented:

```text
contingency_screening
fdi_state_estimation
flisr_restoration
frt_compliance
overcurrent_protection
pf_voltage_repair
pv_volt_var
```

Local verification:

```bash
./scripts/check.sh
```

Current expected result:

```text
OK: 42 unittest tests pass
OK: 44 task artifacts validate: 41 public executable tasks plus 3 hidden harder cases
OK: one-by-one evaluator checks pass for all 41 public sample submissions
OK: public baseline runner sees 41 cases and 41 feasible baseline outputs
OK: portable agent-packet preparation sees 41 public cases
```

First public agent smoke artifacts:

```text
runs/public_agent_smoke/REPORT.md
runs/public_agent_smoke/codex-latest/
runs/public_agent_smoke/opencode-latest/
runs/public_agent_smoke/hermes-latest/
```

Latest historical smoke summary:

- Historical 0–100 run before the normalized-score migration: Hermes CLI (`--toolsets file`) was 7/7 feasible.
- Historical 0–100 run before the normalized-score migration: OpenCode (`opencode/deepseek-v4-flash-free`) was 6/7 feasible and failed `pv_volt_var` on voltage-limit violations.
- Codex CLI: 0/7 feasible because local Codex OAuth failed (`401 Unauthorized`, expired/reused refresh token) before writing submissions.

Latest hidden normalized smoke summary:

- Report: `runs/hidden_agent_smoke/REPORT.md`.
- Hermes CLI (`--toolsets file`): 3/3 feasible, `mean_score=0.864412`.
- OpenCode (`opencode/deepseek-v4-flash-free`): 2/3 feasible, `mean_score=0.541778`; failed hidden `pv_volt_var` on voltage-limit violations.
- Hidden normalized run artifacts: `runs/hidden_agent_smoke/hermes-hidden-101-normalized/` and `runs/hidden_agent_smoke/opencode-hidden-101-normalized/`.

Current public task inventory:

- Full balanced-core public set: 41 executable public tasks.
- Bilingual EN/RU inventory: `docs/bilingual_task_inventory.md`.
- Regenerated public packets: `runs/agent_packets/public_v0/`.
- Regenerated public baselines: `runs/public_baselines/latest/summary.json` with `case_count=41`, `feasible_count=41`, `mean_score=0.997228`.

Important caveats:

- Current evaluators are deterministic public surrogates, not yet full simulator-backed hidden evaluators.
- Do not claim AC power-flow fidelity until `pandapower` or equivalent verification exists.
- Codex should be rerun only after local CLI auth is refreshed.
- If Hermes/OpenCode solve everything easily after more hidden cases are added, the benchmark needs harder cases: larger networks/time series, ambiguity-resistant schemas, hidden perturbations, multi-objective scoring, and less direct oracle leakage in public cases.

## Next implementation queue

1. Current balanced-core packaging slice is complete: 41 public executable tasks, EN/RU task presentation, hidden packet/evaluation mechanics, first harder hidden cases, normalized scoring, and Hermes/OpenCode hidden rerun report.
2. Next benchmark hardening is beyond this slice: simulator-backed evaluators, larger hidden case sets across all 41 public tasks, and CI/report automation.

## Track B — autoinvestigation skill patch

Temporary prepared patch location from an earlier phase:

```text
/tmp/hermes-autoinvestigation-skill
```

Intent:

- teach Hermes how to investigate/design power-systems agent benchmarks;
- keep this as a reusable research workflow layer;
- do not put runnable benchmark datasets/evaluators into the skill repo.

## Boundary rule

- Skill repo: how to research/mine/design benchmark tasks.
- Benchmark repo: how to run/score benchmark tasks.

## Do not do without explicit confirmation

- Do not push either repo.
- Do not create a GitHub remote.
- Do not commit to `main` automatically.
- Do not claim the evaluator is a real power-flow evaluator until simulator-backed verification exists.
