# Benchmark run artifacts

This directory is for local smoke/evaluation outputs. Commit only small documentation or curated examples; avoid committing large or model-specific run logs unless they are intentionally selected as benchmark evidence.

Recommended layout:

```text
runs/
  public_baselines/<timestamp>/
    summary.json
    results.jsonl
    submissions/*.json
  agent_packets/public_v0/
    manifest.json
    <family>__public__case_001/
      instructions.md
      task.json
      submission.json        # produced by an agent, not by packet prep
  public_agent_smoke/<agent-name>-<timestamp>/
    summary.json
    results.jsonl
    submissions/<family>__<split>__<case_id>.json
    logs/<family>__<split>__<case_id>.stdout.txt
    logs/<family>__<split>__<case_id>.stderr.txt
  hidden_agent_smoke/<agent-name>-<timestamp>/
    summary.json          # normalized mean_score, not old total_score
    results.jsonl
    submissions/<family>__hidden__<case_id>.json
    logs/<family>__hidden__<case_id>.stdout.txt
    logs/<family>__hidden__<case_id>.stderr.txt
```

Use:

```bash
python scripts/run_public_baselines.py --out runs/public_baselines/latest
python scripts/prepare_agent_tasks.py --out runs/agent_packets/public_v0
python scripts/prepare_agent_tasks.py --split hidden --out runs/agent_packets/hidden_101
```

Current regenerated public artifacts cover all 41 public executable tasks from the balanced core. The latest public baseline summary is `runs/public_baselines/latest/summary.json`.

Then run any command-line agent with `scripts/run_agent_command.py` as described in `docs/agent_protocol.md`.
