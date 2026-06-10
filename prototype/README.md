# Prototype benchmark layout

This directory is a thin executable skeleton for `benchmark_spec_v0.md`.

Current status:

- `tasks/pf_voltage_repair/public/case_001/task.json`: first public voltage-repair case.
- `tasks/dispatch_uncertainty/public/case_001/task.json`: dispatch/uncertainty contract stub.
- `prototype/evaluators/evaluate_voltage_repair.py`: dependency-free evaluator surrogate for smoke testing the evaluator interface.
- `tests/test_voltage_repair_evaluator.py`: unittest coverage for the first evaluator contract.

The public voltage evaluator is deliberately simple: it applies linear voltage sensitivities instead of running AC power flow. The hidden production evaluator should replace this with `pandapower.runpp` / OPF recomputation while keeping the same input/output contract shape.

Smoke commands from repository root:

```bash
python -m unittest discover -v
python prototype/evaluators/evaluate_voltage_repair.py \
  tasks/pf_voltage_repair/public/case_001/task.json \
  tasks/pf_voltage_repair/public/case_001/sample_submission.json
```
