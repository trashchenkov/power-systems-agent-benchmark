# Agent protocol for public benchmark smoke runs

This protocol is intentionally CLI- and model-agnostic. Any tool-using agent that can read files and write a JSON file can be tested: Codex, OpenCode, local agents, hosted coding agents, or a human-operated workflow.

## Core loop

1. Prepare portable task packets:

```bash
python scripts/prepare_agent_tasks.py \
  --out runs/agent_packets/public_v0

# For sealed/maintainer-only hidden smoke packets, add:
python scripts/prepare_agent_tasks.py \
  --split hidden \
  --out runs/agent_packets/hidden_v0
```

2. For each packet directory, the agent receives only:

- `instructions.md`
- `task.json`

3. The agent must write exactly one file in the packet directory:

- `submission.json`

4. Evaluate submissions with the generic dispatcher:

```bash
python scripts/evaluate_submission.py \
  tasks/<family>/public/case_001/task.json \
  runs/agent_packets/public_v0/<family>__case_001/submission.json
```

5. Aggregate results from a command-line agent with:

```bash
python scripts/run_agent_command.py \
  --packets runs/agent_packets/public_v0 \
  --out runs/public_agent_smoke/<agent-name> \
  --agent-name <agent-name> \
  --command '<agent command here>'
```

The command is run once per task packet.

## Environment variables exposed to command agents

`run_agent_command.py` passes these variables to every command invocation:

- `BENCH_ROOT` — repository root
- `BENCH_AGENT` — agent label
- `BENCH_FAMILY` — task family, e.g. `pv_volt_var`
- `BENCH_CASE_ID` — public case ID, e.g. `case_001`
- `BENCH_TASK_ID` — task ID from `task.json`
- `BENCH_PACKET_DIR` — packet directory containing `instructions.md` and `task.json`
- `BENCH_TASK_PATH` — packet-local `task.json`
- `BENCH_SOURCE_TASK_PATH` — canonical repository `task.json` used for evaluation
- `BENCH_INSTRUCTIONS_PATH` — packet-local instructions file
- `BENCH_SUBMISSION_PATH` — required output file path

This makes the harness work with almost any command-line agent. The agent command only has to read `$BENCH_INSTRUCTIONS_PATH` / `$BENCH_TASK_PATH` and write `$BENCH_SUBMISSION_PATH`.

## Codex example

Codex requires a git repository and PTY for direct interactive use. For a bounded one-shot command, wrap it so the final answer writes to `$BENCH_SUBMISSION_PATH`:

```bash
python scripts/run_agent_command.py \
  --packets runs/agent_packets/public_v0 \
  --out runs/public_agent_smoke/codex \
  --agent-name codex \
  --command 'codex exec "Read $BENCH_INSTRUCTIONS_PATH and $BENCH_TASK_PATH, solve the task, and write valid JSON to $BENCH_SUBMISSION_PATH. Do not modify other files."'
```

If Codex needs an initialized repo, run from a git clone/worktree of this benchmark package.

## OpenCode example

```bash
python scripts/run_agent_command.py \
  --packets runs/agent_packets/public_v0 \
  --out runs/public_agent_smoke/opencode \
  --agent-name opencode \
  --command 'opencode run --dir "$BENCH_PACKET_DIR" "Read instructions.md and task.json, solve the benchmark task, and write only submission.json."'
```

OpenCode provider/model selection can be added to the command, for example `--model openrouter/...` or a local/free model if available.

## Output format

A run directory contains:

- `summary.json` — aggregate counts and score
- `results.jsonl` — one row per case with evaluator result
- `submissions/*.json` — submissions copied from packets. Filenames include split, e.g. `<family>__public__case_001.json` or `<family>__hidden__case_101.json`.
- `logs/*.stdout.txt` / `logs/*.stderr.txt` — command output per case

## Recommended first evaluation sequence

1. `./scripts/check.sh` — local deterministic gate.
2. `python scripts/run_public_baselines.py --out runs/public_baselines/latest` — baseline sanity.
3. `python scripts/prepare_agent_tasks.py --out runs/agent_packets/public_v0` — portable packets.
4. Run different command-line agents via the same packet contract.
5. Compare `results.jsonl` across agents; inspect `violations` before trusting aggregate score.
