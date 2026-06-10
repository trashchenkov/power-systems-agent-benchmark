# Power Systems Agent Benchmark — исполнимый v0 slice

## Назначение

Этот документ фиксирует небольшой исполнимый v0 slice из большого domain-only task bank. Цель — доказать, что benchmark может оценивать tool-using agents через hidden physical/symbolic evaluators, а не через LLM-as-a-Judge.

## Ограничение scope

- v0 включает **7 семейств задач**, а не весь balanced core из 41 задачи.
- У каждой задачи должен быть явно указан доменный источник.
- У каждой задачи должен быть deterministic или simulator-backed hidden evaluator.
- ElecBench-derived задачи в v0 не включаются.
- Asset/RUL и electricity-price placeholders остаются вне v0 до появления более сильных primary sources/datasets.

## Выбранные семейства задач

### REL-TASK-046 — Диагностика AC load flow и коррекция напряжения

- **Источник:** `Power System Analysis and Design_030246bc.txt`, lines 2502–2512.
- **Поддомен:** Power flow, modelling & transmission analysis
- **Достоверность источника:** strong
- **Почему входит в v0:** покрывает отдельную исполнимую способность в электроэнергетике и может оцениваться физическим/символьным evaluator, а не LLM-as-a-Judge.
- **Substrate:** pandapower AC power flow
- **Публичный вход / ответ агента:** public feeder/network case; proposed bus voltage setpoints, shunt/tap/DER Q changes.
- **Hidden evaluator:** run hidden AC PF; score voltage/current violations, action budget, losses/regret.
- **Baseline:** pandapower/PYPOWER no-op and greedy voltage repair baseline.
- **Первичная цель реализации:** один public case, одно семейство hidden/randomized cases, schema validation, baseline и smoke test.

### GAP-TASK-005 — N-1 contingency screening и обнаружение islanding

- **Источник:** Graph Computing based Fast Screening in Contingency Analysis (2019-03-29, arXiv:1904.00044v1) — https://arxiv.org/abs/1904.00044v1; Fast Grid Splitting Detection for N-1 Contingency Analysis by Graph Computing (2019-04-07, arXiv:1904.03587v1) — https://arxiv.org/abs/1904.03587v1
- **Поддомен:** Transmission operations, contingency & congestion management
- **Достоверность источника:** medium-strong.
- **Почему входит в v0:** покрывает отдельную исполнимую способность в электроэнергетике и может оцениваться физическим/символьным evaluator, а не LLM-as-a-Judge.
- **Substrate:** NetworkX + pandapower/PYPOWER DC/AC PF
- **Публичный вход / ответ агента:** network graph, base flows, contingency list; severity ranking and islanding flags.
- **Hidden evaluator:** hidden contingencies; missed critical outage rate, false negatives for islanding, runtime.
- **Baseline:** all-branches DC screening baseline.
- **Первичная цель реализации:** один public case, одно семейство hidden/randomized cases, schema validation, baseline и smoke test.

### GAP-TASK-003 — Восстановление распределительной сети / FLISR

- **Источник:** A Two-Stage Service Restoration Method for Electric Power Distribution Systems (2020-04-16, arXiv:2004.07921v1) — https://arxiv.org/abs/2004.07921v1
- **Поддомен:** Distribution automation, FLISR & feeder reconfiguration
- **Достоверность источника:** medium-strong.
- **Почему входит в v0:** покрывает отдельную исполнимую способность в электроэнергетике и может оцениваться физическим/символьным evaluator, а не LLM-as-a-Judge.
- **Substrate:** pandapower or OpenDSS + NetworkX
- **Публичный вход / ответ агента:** faulted feeder graph, switch states, priorities, DER; switching/restoration plan.
- **Hidden evaluator:** radiality, voltage/current constraints, restored priority load, switch count.
- **Baseline:** greedy critical-load restoration baseline.
- **Первичная цель реализации:** один public case, одно семейство hidden/randomized cases, schema validation, baseline и smoke test.

### REL-TASK-036 — Настройка максимальной токовой защиты линии

- **Источник:** same, lines 548–558.
- **Поддомен:** Protection, faults & relay engineering
- **Достоверность источника:** strong
- **Почему входит в v0:** покрывает отдельную исполнимую способность в электроэнергетике и может оцениваться физическим/символьным evaluator, а не LLM-as-a-Judge.
- **Substrate:** deterministic protection formula engine
- **Публичный вход / ответ агента:** short-circuit currents, load currents, CT/relay data; pickup/time-dial settings.
- **Hidden evaluator:** selectivity, sensitivity, thermal/equipment constraints, numeric tolerance.
- **Baseline:** rule-based textbook formula baseline.
- **Первичная цель реализации:** один public case, одно семейство hidden/randomized cases, schema validation, baseline и smoke test.

### GAP-TASK-009 — Volt-VAR управление PV для снижения sag/swell

- **Источник:** Local Control of Reactive Power by Distributed Photovoltaic Generators (2010-06-01, arXiv:1006.0160v1) — https://arxiv.org/abs/1006.0160v1; Options for Control of Reactive Power by Distributed Photovoltaic Generators (2010-08-04, arXiv:1008.0878v1) — https://arxiv.org/abs/1008.0878v1
- **Поддомен:** Power quality & standards
- **Достоверность источника:** strong.
- **Почему входит в v0:** покрывает отдельную исполнимую способность в электроэнергетике и может оцениваться физическим/символьным evaluator, а не LLM-as-a-Judge.
- **Substrate:** pandapower/OpenDSS time-series distribution PF
- **Публичный вход / ответ агента:** feeder, PV ratings, irradiance ramps, inverter Q limits; control law/parameters.
- **Hidden evaluator:** violation-hours, losses, Q limit violations, oscillation/control effort.
- **Baseline:** IEEE 1547-like default Volt-VAR curve baseline.
- **Первичная цель реализации:** один public case, одно семейство hidden/randomized cases, schema validation, baseline и smoke test.

### GAP-TASK-006 — Обнаружение false-data injection в оценивании состояния

- **Источник:** Modeling and performance evaluation of stealthy false data injection attacks on smart grid in the presence of corrupted measurements (2016-05-20, arXiv:1605.06180v1) — https://arxiv.org/abs/1605.06180v1; Graphical Methods for Defense Against False-data Injection Attacks on Power System State Estimation (2013-04-15, arXiv:1304.4151v4) — https://arxiv.org/abs/1304.4151v4
- **Поддомен:** OT cybersecurity, state estimation & bad data
- **Достоверность источника:** strong; classic primary power cyber literature.
- **Почему входит в v0:** покрывает отдельную исполнимую способность в электроэнергетике и может оцениваться физическим/символьным evaluator, а не LLM-as-a-Judge.
- **Substrate:** DC state estimator + attack generator
- **Публичный вход / ответ агента:** H matrix/network, measurements, noise covariance; attack labels/localization/corrected state.
- **Hidden evaluator:** detection F1, localization precision/recall, false alarms, estimation error.
- **Baseline:** chi-square residual bad-data detector baseline.
- **Первичная цель реализации:** один public case, одно семейство hidden/randomized cases, schema validation, baseline и smoke test.

### GAP-TASK-011 — Проверка FRT/grid-code compliance для IBR

- **Источник:** Grid-Forming Control Based On Emulated Synchronous Condenser Strategy Compliant With Challenging Grid Code Requirements (2023-03-01, arXiv:2303.00391v2) — https://arxiv.org/abs/2303.00391v2; A Novel Decentralized Inverter Control Algorithm for Loss Minimization and LVRT Improvement (2022-07-24, arXiv:2207.11700v3) — https://arxiv.org/abs/2207.11700v3
- **Поддомен:** Grid codes, interconnection & standards compliance
- **Достоверность источника:** medium-strong; exact standard clauses still need source-specific extraction.
- **Почему входит в v0:** покрывает отдельную исполнимую способность в электроэнергетике и может оцениваться физическим/символьным evaluator, а не LLM-as-a-Judge.
- **Substrate:** rule-based compliance checker over event traces
- **Публичный вход / ответ агента:** voltage/frequency trace, current response, grid-code curve; pass/fail report.
- **Hidden evaluator:** clause-level pass/fail, ride-through envelope, reactive current support timing/magnitude.
- **Baseline:** static envelope checker baseline.
- **Первичная цель реализации:** один public case, одно семейство hidden/randomized cases, schema validation, baseline и smoke test.

## Порядок реализации

1. **AC PF diagnosis / voltage repair** — самый простой pandapower-first MVP; проверяет public/hidden evaluator contract.
2. **N-1 contingency screening** — переиспользует network cases и добавляет ranking/islanding metrics.
3. **Protection setting** — deterministic formula engine; сильная доменная специфика.
4. **PV Volt-VAR** — time-series distribution PF и DER control.
5. **FLISR restoration** — topology/action task с radiality и priority-load scoring.
6. **FDI state-estimation detection** — cyber/state-estimation слой с synthetic hidden attacks.
7. **FRT compliance** — standards/compliance task; сначала rule-based, затем с привязкой к точным clauses.

## Public/hidden split

- **Public:** постановка задачи, schema, один маленький case, baseline run, описание scoring.
- **Hidden:** randomized seeds, более крупные cases, ground-truth simulator outputs, attack vectors, contingency lists, compliance thresholds, если текст стандарта/лицензия требует осторожности.

## Обязательные артефакты на каждое семейство задач

- `tasks/public/<family>/<case_id>/task.json`
- `tasks/public/<family>/<case_id>/input.*`
- `baselines/<family>/baseline.py`
- `prototype/evaluators/evaluate_<family>.py`
- `tests/test_<family>_evaluator.py`
- source note в metadata задачи: `source.title`, `source.url_or_local_path`, `source.locator`, `source.confidence`
