# Packaging strategy: skill vs benchmark repository

Question: should the power-systems agent benchmark work be pushed forward through `trashchenkov/hermes-autoinvestigation-skill`, or as a separate benchmark repository?

## Recommendation

Use a two-layer route:

1. **Keep/extend `hermes-autoinvestigation-skill` as the research workflow layer.**
   - Purpose: repeatable autonomous literature/repository/task mining.
   - Good contents: investigation pattern, task-mining prompts, source/evidence ledgers, benchmark-design templates, power-systems benchmark reference notes.
   - Not ideal contents: full benchmark datasets, simulator cases, evaluator code, leaderboard harness, CI-heavy dependencies.

2. **Create a separate benchmark repository for the executable artifact.**
   - Working name: `power-systems-agent-benchmark` or `power-agent-benchmark`.
   - Purpose: installable/runnable benchmark with task cases, schemas, hidden/public split, evaluators, baselines, CI, docs.
   - Good contents: `tasks/`, `schemas/`, `prototype/evaluators/`, `tests/`, dependency files, examples, baseline agents.

This avoids mixing a Hermes procedural skill with a research benchmark package. The skill should teach Hermes how to discover/design benchmark tasks; the benchmark repo should be the thing users clone and run.

## What should go into the skill repo

Candidate additions to `trashchenkov/hermes-autoinvestigation-skill`:

- `references/power-systems-agent-benchmark.md` — reusable investigation pattern for this domain.
- `templates/power_systems_agent_benchmark_task_contract.md` — template for turning a task family into an executable contract.
- optional `assets/evaluator_contract.template.md` — standard public/hidden evaluator shape.
- optional README examples:
  - “Use autoinvestigation to mine executable power-systems agent benchmark tasks from this folder of papers.”
  - “Use autoinvestigation to compare PowerAgentBench, Grid2Op, PGLib-OPF, pandapower, OpenDSS, ANDES, PyPSA.”

Current local Hermes skill already has a power-systems reference/template, so the GitHub skill repo should be synced with those if they are not present upstream.

## What should go into the benchmark repo

Current local prototype artifacts that belong in a benchmark repo:

```text
benchmark_spec_v0.md
schemas/task.schema.json
tasks/pf_voltage_repair/public/case_001/task.json
tasks/pf_voltage_repair/public/case_001/sample_submission.json
tasks/dispatch_uncertainty/public/case_001/task.json
prototype/evaluators/evaluate_voltage_repair.py
prototype/README.md
scripts/validate_benchmark_artifacts.py
tests/test_voltage_repair_evaluator.py
```

Next files to add before publishing:

```text
README.md
LICENSE
pyproject.toml or requirements.txt
.gitignore
.github/workflows/ci.yml
Makefile or scripts/check.sh
docs/metrics.md
docs/public_hidden_split.md
docs/evaluator_contract.md
```

## Boundary rule

- If it helps Hermes **investigate and design** benchmark tasks, it belongs in the skill.
- If it lets someone **run and score** benchmark tasks, it belongs in the benchmark repo.

## Immediate next implementation steps

1. Add a proper `README.md` and dependency file to the local benchmark prototype.
2. Add a local `make check`/`scripts/check.sh` that runs tests, artifact validation, and smoke evaluator.
3. Add CI workflow draft.
4. Package the local folder as a git repo, but do not push without explicit user confirmation and target repo decision.
5. Separately compare the GitHub skill repo with the local installed `autoinvestigation` skill and prepare a patch that syncs power-systems benchmark reference/template into the skill repo.
