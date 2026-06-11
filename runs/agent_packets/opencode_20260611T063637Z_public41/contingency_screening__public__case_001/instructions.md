# Agent task packet

You are solving one executable power-systems benchmark task.

## Goal

Read `task.json` in this directory. Use the public inputs/specification to compute the answer. Write exactly one JSON file named `submission.json` in this same directory.

## Rules

- Treat this as an executable agent task, not a copy task: derive the answer from `public_inputs`, `objective`, `hard_constraints`, and `submission_schema`.
- Do not modify `task.json`.
- Do not inspect files outside this packet directory. The packet intentionally omits hidden expected answers and evaluator internals.
- Do not search for benchmark evaluator code, baseline submissions, sample submissions, or hidden answers.
- You may create and run a short helper script/scratch calculation inside this packet directory if useful.
- Output must be valid JSON, not Markdown.
- Include only fields compatible with the task's `submission_schema`; optional `rationale` is free text and is not required to match any hidden string.
- After writing `submission.json`, stop.

## Expected output path

`runs/agent_packets/opencode_20260611T063637Z_public41/contingency_screening__public__case_001/submission.json`
