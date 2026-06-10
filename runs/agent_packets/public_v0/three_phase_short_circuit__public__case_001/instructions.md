# Agent task packet

You are solving one executable power-systems benchmark task.

## Goal

Read `task.json` in this directory. Write exactly one JSON file named `submission.json` in this same directory.

## Rules

- Do not modify `task.json`.
- Do not read `sample_submission.json` unless the benchmark runner explicitly allows samples for a warm-up run.
- Use only the public inputs, objective, hard constraints, and submission schema in `task.json`.
- Output must be valid JSON, not Markdown.
- Include only fields compatible with the task's `submission_schema`; optional `rationale` is allowed when useful.
- After writing `submission.json`, stop. Do not run the hidden evaluator unless the benchmark runner asks you to.

## Local verification command for humans/runners

From the repository root, the submission can be evaluated with:

```bash
python scripts/evaluate_submission.py /root/investigation-runs/power-systems-agent-benchmark/tasks/three_phase_short_circuit/public/case_001/task.json runs/agent_packets/public_v0/three_phase_short_circuit__public__case_001/submission.json
```

## Expected output path

`runs/agent_packets/public_v0/three_phase_short_circuit__public__case_001/submission.json`
