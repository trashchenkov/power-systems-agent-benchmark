#!/usr/bin/env bash
set -euo pipefail

python3 -m unittest discover -v
python3 scripts/validate_benchmark_artifacts.py
python3 prototype/evaluators/evaluate_voltage_repair.py \
  tasks/pf_voltage_repair/public/case_001/task.json \
  tasks/pf_voltage_repair/public/case_001/sample_submission.json
python3 prototype/evaluators/evaluate_contingency_screening.py \
  tasks/contingency_screening/public/case_001/task.json \
  tasks/contingency_screening/public/case_001/sample_submission.json
python3 prototype/evaluators/evaluate_overcurrent_protection.py \
  tasks/overcurrent_protection/public/case_001/task.json \
  tasks/overcurrent_protection/public/case_001/sample_submission.json
python3 prototype/evaluators/evaluate_pv_volt_var.py \
  tasks/pv_volt_var/public/case_001/task.json \
  tasks/pv_volt_var/public/case_001/sample_submission.json
python3 prototype/evaluators/evaluate_flisr_restoration.py \
  tasks/flisr_restoration/public/case_001/task.json \
  tasks/flisr_restoration/public/case_001/sample_submission.json
python3 prototype/evaluators/evaluate_fdi_state_estimation.py \
  tasks/fdi_state_estimation/public/case_001/task.json \
  tasks/fdi_state_estimation/public/case_001/sample_submission.json
python3 prototype/evaluators/evaluate_frt_compliance.py \
  tasks/frt_compliance/public/case_001/task.json \
  tasks/frt_compliance/public/case_001/sample_submission.json
python3 - <<'PY'
from pathlib import Path
from scripts.evaluate_submission import discover_executable_cases, evaluate_submission_file

root = Path.cwd()
cases = discover_executable_cases(root)
for case in cases:
    sample = case.task_path.with_name("sample_submission.json")
    if not sample.exists():
        raise SystemExit(f"missing public sample submission: {sample}")
    result = evaluate_submission_file(case.task_path, sample)
    if not result.get("feasible"):
        raise SystemExit(f"sample submission infeasible for {case.family}/{case.case_id}: {result}")
print(f"OK: evaluated {len(cases)} public sample submission(s) one by one")
PY
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
python3 scripts/run_public_baselines.py --out "$TMPDIR/public_baselines"
python3 scripts/prepare_agent_tasks.py --out "$TMPDIR/agent_packets"
