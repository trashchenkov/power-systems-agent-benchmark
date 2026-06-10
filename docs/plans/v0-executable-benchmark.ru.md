# План реализации v0 executable benchmark

> **Для Hermes:** реализовывать task-by-task через строгий TDD. Внешние артефакты держать синхронно на RU/EN и сохранять явный источник у каждой задачи.

**Цель:** Превратить bilingual v0 executable slice в запускаемый benchmark skeleton с deterministic/simulator-backed evaluators.

**Архитектура:** Реализуем по одному семейству задач. Каждое семейство получает public cases, sample submissions, baseline, evaluator, tests и структурированную metadata источника. Hidden evaluators могут начинаться с deterministic public surrogates, но contract должен быть совместим с будущими pandapower/OpenDSS/DC-SE реализациями.

**Tech Stack:** сначала Python stdlib, затем pandapower/NetworkX/NumPy при необходимости. unittest для текущих тестов; JSON task artifacts; общий check через `scripts/check.sh`.

---

## Task 1: Ввести обязательный structured source provenance

**Objective:** Сделать источники задач machine-checkable, чтобы benchmark не мог незаметно пополняться задачами без provenance.

**Files:**
- Modify: `schemas/task.schema.json`
- Modify: `scripts/validate_benchmark_artifacts.py`
- Modify: existing `tasks/*/*/case_*/task.json`
- Test: `tests/test_artifact_validation.py`

**TDD steps:**
1. Добавить failing tests: task без `source_provenance` должен отклоняться; task с `title`, `locator`, `confidence`, `notes` должен приниматься.
2. Запустить specific test и подтвердить RED.
3. Добавить validation logic и schema property.
4. Обновить существующие task JSON structured source provenance.
5. Запустить specific tests и `./scripts/check.sh`.

## Task 2: Усилить public family AC PF voltage repair

**Objective:** Довести существующий voltage-repair surrogate до первого полноценного v0 family с source metadata и ссылками на bilingual docs.

**Files:**
- Modify: `prototype/evaluators/evaluate_voltage_repair.py`
- Modify: `tasks/pf_voltage_repair/public/case_001/task.json`
- Create/Modify: `baselines/pf_voltage_repair/baseline.py`
- Test: `tests/test_voltage_repair_evaluator.py`

**TDD steps:**
1. Добавить tests для unknown bus/action, out-of-bounds action, infeasible no-action submission и minimal feasible action scoring.
2. Подтвердить RED для отсутствующего поведения.
3. Реализовать минимальные изменения evaluator/baseline.
4. Запустить specific tests и полный check.

## Task 3: Public surrogate для N-1 contingency screening

**Objective:** Добавить graph/DC-flow-compatible public surrogate для contingency ranking и islanding detection.

**Files:**
- Create: `tasks/contingency_screening/public/case_001/task.json`
- Create: `tasks/contingency_screening/public/case_001/sample_submission.json`
- Create: `prototype/evaluators/evaluate_contingency_screening.py`
- Create: `baselines/contingency_screening/baseline.py`
- Test: `tests/test_contingency_screening_evaluator.py`

**TDD steps:** tests для islanding flag, critical overload ranking, missed critical contingency penalty, затем implementation.

## Task 4: Deterministic evaluator для protection setting

**Objective:** Добавить overcurrent-protection task с formula-based checks.

**Files:** аналогичные `tasks/overcurrent_protection/...`, evaluator, baseline, tests.

**TDD steps:** test pickup выше max load, ниже min fault sensitivity, time/selectivity margin, bounds, затем implementation.

## Task 5: Добавить оставшиеся v0 families как строгие stubs

**Objective:** Добавить FLISR, PV Volt-VAR, FDI detection и FRT compliance как sourced task stubs до полной simulator implementation.

**Rule:** stubs должны проходить artifact validation, но не должны притворяться полноценными hidden evaluators.

## Verification command

Перед отчётом запускать:

```bash
./scripts/check.sh
```
