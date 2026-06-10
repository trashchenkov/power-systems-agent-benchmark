# v0 Executable Benchmark Implementation Plan

> **For Hermes:** implement task-by-task with strict TDD. Keep RU/EN externally-facing artifacts in sync and preserve explicit source provenance for every task.

**Goal:** Turn the bilingual v0 executable slice into a runnable benchmark skeleton with deterministic/simulator-backed evaluators.

**Architecture:** Implement one family at a time. Each family gets public cases, sample submissions, baseline, evaluator, tests, and structured source metadata. Hidden evaluators can start with deterministic public surrogates, but the contract must be compatible with later pandapower/OpenDSS/DC-SE implementations.

**Tech Stack:** Python stdlib first, then pandapower/NetworkX/NumPy where needed. unittest for existing tests; JSON task artifacts; shell check via `scripts/check.sh`.

---

## Task 1: Enforce structured source provenance in task artifacts

**Objective:** Make task sources machine-checkable so the benchmark cannot silently add unsourced tasks.

**Files:**
- Modify: `schemas/task.schema.json`
- Modify: `scripts/validate_benchmark_artifacts.py`
- Modify: existing `tasks/*/*/case_*/task.json`
- Test: `tests/test_artifact_validation.py`

**TDD steps:**
1. Add failing tests that reject a task without `source_provenance` and accept one with `title`, `locator`, `confidence`, and `notes`.
2. Run the specific test and confirm RED.
3. Add validation logic and schema property.
4. Update existing task JSON files with structured source provenance.
5. Run specific tests and `./scripts/check.sh`.

## Task 2: AC PF voltage repair public family hardening

**Objective:** Upgrade the existing voltage-repair surrogate into the first complete v0 family with source metadata and bilingual docs pointers.

**Files:**
- Modify: `prototype/evaluators/evaluate_voltage_repair.py`
- Modify: `tasks/pf_voltage_repair/public/case_001/task.json`
- Create/Modify: `baselines/pf_voltage_repair/baseline.py`
- Test: `tests/test_voltage_repair_evaluator.py`

**TDD steps:**
1. Add tests for unknown bus/action, out-of-bounds action, infeasible no-action submission, and minimal feasible action scoring.
2. Verify RED for any missing behavior.
3. Implement the smallest evaluator/baseline changes.
4. Run specific tests and full check.

## Task 3: N-1 contingency screening public surrogate

**Objective:** Add a graph/DC-flow-compatible public surrogate for contingency ranking and islanding detection.

**Files:**
- Create: `tasks/contingency_screening/public/case_001/task.json`
- Create: `tasks/contingency_screening/public/case_001/sample_submission.json`
- Create: `prototype/evaluators/evaluate_contingency_screening.py`
- Create: `baselines/contingency_screening/baseline.py`
- Test: `tests/test_contingency_screening_evaluator.py`

**TDD steps:** write tests for islanding flag, critical overload ranking, missed critical contingency penalty, then implement.

## Task 4: Protection setting deterministic evaluator

**Objective:** Add an overcurrent-protection task with formula-based checks.

**Files:** analogous `tasks/overcurrent_protection/...`, evaluator, baseline, tests.

**TDD steps:** test pickup above max load, below min fault sensitivity, time/selectivity margin, bounds, then implement.

## Task 5: Add remaining v0 families as stubs with strict contracts

**Objective:** Add FLISR, PV Volt-VAR, FDI detection, and FRT compliance as sourced task stubs before full simulator implementation.

**Rule:** stubs must pass artifact validation but should not pretend to be full hidden evaluators.

## Verification command

Run before reporting completion:

```bash
./scripts/check.sh
```
