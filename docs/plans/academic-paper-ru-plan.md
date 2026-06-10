# Академическая статья о Power Systems Agent Benchmark — план на русском

> **Назначение документа:** зафиксировать рабочий план русскоязычной академической статьи о бенче: центральный тезис, вклад, структуру, доказательную базу, необходимые эксперименты, таблицы/рисунки и очередь работ.

**Рабочее название:**

> Power Systems Agent Benchmark: исполняемый бенчмарк для оценки инструментальных ИИ-агентов в задачах электроэнергетики

**Короткая версия названия:**

> Исполняемый бенчмарк для ИИ-агентов в электроэнергетике

**Главная идея статьи:**

Существующие оценки ИИ-агентов часто опираются либо на текстовые вопросы, либо на LLM-as-a-Judge по полному отчёту. Для инженерной электроэнергетики этого недостаточно: важны физические ограничения, сетевые режимы, защита, надёжность, диспетчерские действия и воспроизводимость расчётов. Мы предлагаем исполняемый benchmark, в котором агент получает структурированный `task.json`, пишет `submission.json`, а оценка выполняется детерминированной программой проверки, пересчитывающей результат и ограничения.

**Текущий статус артефакта:**

- Репозиторий: `/root/investigation-runs/power-systems-agent-benchmark`.
- Публичных задач: 41.
- Зарегистрированных evaluator routes: 41.
- Generic expected-answer routes: 0.
- Публичные sample submissions: 41/41 feasible в baseline sanity check.
- Полная локальная проверка: `scripts/check.sh` проходит.
- Важное ограничение: текущие public evaluators — детерминированные компактные суррогаты, не полноценные simulator-backed hidden evaluators. В статье это надо сказать прямо.

---

## 1. Предполагаемый тип статьи

### Вариант A — методическая/benchmark paper

Наиболее естественный формат: статья о датасете/бенчмарке/инфраструктуре оценки.

**Фокус:**

- почему электроэнергетическим агентам нужна исполняемая оценка;
- какие классы задач покрыты;
- как устроен task/submission/evaluation contract;
- чем подход отличается от текстового QA и LLM-as-a-Judge;
- как бенчмарк допускает разные CLI-агенты без привязки к конкретному фреймворку.

**Ключевой риск:** текущие задачи пока компактные и суррогатные; нельзя продавать их как полную физическую симуляцию энергосистем.

**Как снять риск:** позиционировать работу как *benchmark framework + balanced executable public core*, а не как окончательную промышленную симуляционную среду.

### Вариант B — короткая конференционная статья / workshop paper

Если нужен быстрый публикационный результат, статья может быть короче и сфокусирована на постановке проблемы и прототипе.

**Фокус:**

- taxonomy of power-system agent tasks;
- executable evaluation protocol;
- first 41-task public core;
- preliminary agent smoke results;
- roadmap to simulator-backed hidden tracks.

### Вариант C — русскоязычная статья для инженерно-педагогического/отраслевого журнала

Можно сделать более прикладной текст: как проектировать задачи для оценки ИИ-агентов в энергетике и почему не хватает обычных бенчмарков.

**Фокус:**

- связь с обучением, инженерной экспертизой и цифровыми тренажёрами;
- примеры задач из релейной защиты, надёжности, DER, микросетей, устойчивости;
- воспроизводимые критерии проверки.

---

## 2. Центральный тезис

**Формулировка тезиса:**

Для оценки ИИ-агентов в электроэнергетике нужен не только корпус вопросов и ответов, а исполняемый бенчмарк: задачи должны содержать формализованные входные данные, агент должен выдавать машинно-проверяемое решение, а результат должен оцениваться повторным расчётом физических, эксплуатационных или нормативных ограничений. Такой подход уменьшает зависимость от LLM-судьи и позволяет сравнивать агентов по воспроизводимым инженерным критериям.

**Что доказываем:**

1. Текстовая оценка плохо подходит для электроэнергетических задач, где ответ может выглядеть убедительно, но нарушать ограничения.
2. Единый task/submission/evaluation protocol позволяет запускать разные агенты поверх одного набора задач.
3. Даже компактный public core из 41 задач покрывает широкий спектр электроэнергетических доменов.
4. Детерминированные evaluator-и дают прозрачный baseline и позволяют отделять ошибку агента от ошибки среды запуска.
5. Следующий уровень — simulator-backed hidden evaluators, но их можно внедрять постепенно, не меняя внешний контракт задачи.

---

## 3. Заявляемые вклады статьи

### Contribution 1 — исполняемый контракт оценки

Описать контракт:

```text
task.json → agent → submission.json → evaluator → evaluation-result.json
```

Ключевые свойства:

- структурированные входы;
- структурированный ответ;
- детерминированная проверка;
- `feasible`, `score`, `violations`;
- отделение основного численного score от необязательного rationale.

### Contribution 2 — таксономия электроэнергетических agent tasks

Показать 41-task balanced core по группам:

- расчёт режимов и моделирование сети;
- короткие замыкания и релейная защита;
- устойчивость и динамика;
- DER, PV, EV/V2G, BESS;
- микросети и диспетчеризация;
- надёжность и восстановление;
- качество электроэнергии и стандарты;
- кибербезопасность измерений;
- unit commitment, резервы и adequacy;
- прогнозирование и неопределённость;
- экономика и soft-cost uncertainty.

### Contribution 3 — открытый public core из 41 executable tasks

Зафиксировать, что на текущем срезе:

- 41 public task family;
- каждая family имеет `task.json` и `sample_submission.json`;
- каждая имеет registered evaluator;
- все generic expected-answer routes устранены;
- baseline runner получает 41/41 feasible.

### Contribution 4 — агент-агностичная инфраструктура запуска

Описать:

- `prepare_agent_tasks.py`;
- `run_agent_command.py`;
- env-variable protocol для любого CLI-агента;
- `run_public_baselines.py`;
- разделение benchmark failure, agent failure, provider/auth failure.

### Contribution 5 — честная дорожная карта к simulator-backed оценке

Не скрывать, что многие public evaluators — компактные детерминированные суррогаты.

Показать план развития:

- `pandapower` для AC PF/contingency/voltage repair;
- OpenDSS для distribution/DER;
- PowerModels/PGLib для OPF/SCUC-подобных задач;
- ANDES/GridCal/динамические модели для transient stability;
- Grid2Op/L2RPN-подобный слой для последовательного управления.

---

## 4. Предлагаемая структура статьи

## Аннотация

Кратко:

- проблема: LLM-агенты всё чаще применяются к инженерным задачам, но стандартные бенчмарки слабо проверяют физическую корректность;
- решение: executable benchmark для электроэнергетики;
- артефакт: 41 публичная задача, структурированный протокол, deterministic evaluators, agent-agnostic runner;
- результат: baseline sanity и smoke-инфраструктура;
- ограничение: текущий public core — прототип с суррогатными проверками; simulator-backed hidden cases — следующий этап.

## 1. Введение

### Цель раздела

Поставить проблему так, чтобы она была понятна и специалисту по ИИ, и специалисту по электроэнергетике.

### Основные тезисы

- Инженерные энергетические решения нельзя оценивать только по убедительности текста.
- Важны ограничения: токи, напряжения, устойчивость, селективность защиты, надёжность, нормативное соответствие.
- LLM-as-a-Judge может быть полезен для качества объяснения, но не должен быть главным score для инженерного бенча.
- Нужна воспроизводимая машинная проверка действий/решений агента.

### Возможный фрагмент текста

> В электроэнергетике ошибка агента часто проявляется не как неправильная формулировка, а как нарушение физического или эксплуатационного ограничения: перегрузка линии, неселективная защита, недопустимое напряжение, неправильная локализация повреждения или невыполнение требования grid code. Поэтому основной результат оценки должен определяться не общим впечатлением от отчёта, а исполняемой проверкой предложенного решения.

## 2. Связанные работы

### Нужно покрыть

1. Общие benchmark-и для LLM/tool agents.
2. LLM-as-a-Judge и его ограничения.
3. PowerAgentBench как ближайший источник по physical/power-system tool-agent задачам.
4. Grid2Op/L2RPN как mature среда для grid operation, но не прямо тот же формат.
5. Электроэнергетические симуляторы и библиотеки:
   - pandapower;
   - OpenDSS;
   - PowerModels/PGLib;
   - Grid2Op;
   - ANDES/GridCal/PyPSA, если нужно.
6. Отраслевые источники для задач:
   - релейная защита;
   - FCI/reliability;
   - DER/PV/EV;
   - FRT/grid code;
   - dispatch/forecasting/uncertainty.

### Важно

Не делать вид, что наш бенч уже превосходит все симуляционные среды. Тезис другой: мы предлагаем *агентный контракт оценки*, который может использовать разные субстраты.

## 3. Требования к бенчмарку для электроэнергетических агентов

### Предлагаемые требования

1. **Исполнимость:** решение можно проверить кодом.
2. **Физическая проверяемость:** evaluator пересчитывает величины или проверяет ограничения.
3. **Разделение public/hidden:** public cases помогают разработке, hidden cases нужны для честной оценки.
4. **Агент-агностичность:** benchmark не должен зависеть от конкретной LLM, CLI или платформы.
5. **Источник постановки:** каждая задача должна иметь provenance.
6. **Машиночитаемый результат:** score, feasible, violations, metrics.
7. **Возможность роста сложности:** от формул и графов к полноценным симуляторам.

## 4. Архитектура Power Systems Agent Benchmark

### Описать компоненты

- `tasks/<family>/public/case_001/task.json`;
- `sample_submission.json`;
- `prototype/evaluators/evaluate_<family>.py`;
- `baselines/<family>/baseline.py`;
- `scripts/evaluate_submission.py`;
- `scripts/run_public_baselines.py`;
- `scripts/prepare_agent_tasks.py`;
- `scripts/run_agent_command.py`;
- `schemas/*.json`;
- `docs/source_cards/*.md`.

### Рисунок 1

**Название:** Общий цикл оценки агента.

```text
описание задачи → агент → структурированный ответ → evaluator → score/violations
```

### Рисунок 2

**Название:** Уровни зрелости evaluator-ов.

```text
formula/graph surrogate → deterministic engineering model → simulator-backed hidden evaluator → stochastic/larger scenario suite
```

## 5. Набор задач

### Таблица 1 — домены и количество задач

Использовать статистику из репозитория:

- всего 41 задача;
- текущая доменная разметка частично неоднородна, поэтому перед статьёй желательно нормализовать `subdomain` в 8–10 крупных категорий.

### Таблица 2 — полный каталог 41 tasks

Колонки:

- family;
- домен;
- тип решения;
- evaluator substrate;
- основные выходные поля;
- source provenance.

### Нормализованные группы для статьи

Предлагаю не показывать сырые `subdomain`, а сгруппировать так:

1. **Сетевые расчёты и ограничения режима**
   - `ybus_construction`
   - `pf_voltage_repair`
   - `contingency_screening`
   - `corrective_transmission_switching`
   - `dynamic_thermal_rating`

2. **Короткие замыкания и защита**
   - `three_phase_short_circuit`
   - `earth_fault_calculation`
   - `breaker_relay_short_circuit`
   - `distance_protection_settings`
   - `overcurrent_protection`

3. **Устойчивость, grid code и IBR**
   - `critical_clearing_time`
   - `transient_stability_prediction`
   - `frt_compliance`
   - `ibr_short_circuit_frt`
   - `min_synchronous_share`

4. **DER, PV, EV и накопители**
   - `pv_volt_var`
   - `ev_v2g_outage_schedule`
   - `ev_v2g_voltage_support`
   - `bess_ancillary_response`
   - `commercial_pv_lcoe_uncertainty`
   - `pv_soft_cost_sobol`

5. **Микросети и диспетчеризация**
   - `microgrid_economic_dispatch`
   - `rolling_microgrid_dispatch`
   - `islanded_microgrid_pq_dispatch`
   - `dispatch_uncertainty`
   - `hydro_thermal_storage_uc`
   - `n1_generation_commitment`

6. **Надёжность и восстановление**
   - `flisr_restoration`
   - `fault_section_localization`
   - `fci_placement`
   - `fci_saidi_caidi`
   - `operator_breaker_load_actions`

7. **Качество электроэнергии, стандарты, кибербезопасность**
   - `en50160_voltage_compliance`
   - `power_quality_event_classification`
   - `fdi_state_estimation`
   - `protected_meter_placement`
   - `mas_frequency_handover`

8. **Прогнозирование и неопределённость**
   - `wind_power_forecast`
   - `wind_prediction_interval`

## 6. Проверяющие программы и метрики

### Основные поля evaluation result

- `feasible`: выполнены ли жёсткие ограничения;
- `score`: нормированная оценка;
- `violations`: список нарушений;
- task-specific computed evidence.

### Подход к метрикам

- Для задач с точным расчётом: score 1/0 или penalty за отклонение.
- Для задач управления/оптимизации: feasible + objective quality.
- Для классификации: precision/recall/F1 или exact labels.
- Для стандартов и grid-code: pass/fail + diagnostic fields.

### Важная позиция

LLM explanation/rationale может храниться, но не должен определять основной leaderboard score.

## 7. Экспериментальная часть

### Минимальный эксперимент для статьи v1

1. Прогнать `scripts/check.sh` и зафиксировать:
   - число unittest tests;
   - число валидированных артефактов;
   - 41 public sample submissions;
   - baseline summary.
2. Прогнать public baselines:
   - `case_count=41`;
   - `feasible_count=41`;
   - `mean_score=0.997228` на текущем срезе.
3. Прогнать 2–3 agent surfaces на public packets:
   - Hermes CLI;
   - OpenCode;
   - Codex после обновления auth, если возможно.
4. Разделить failures:
   - task quality failure;
   - agent reasoning failure;
   - harness failure;
   - provider/auth failure.

### Более сильный эксперимент для статьи v2

1. Добавить hidden cases не только для 3 задач, а хотя бы для 10–15 representative families.
2. Запустить несколько агентов на hidden cases.
3. Показать, что public sample не является oracle и что hidden performance ниже/различимее.
4. Сделать ablation:
   - без инструментов;
   - с чтением файлов;
   - с Python/tool use;
   - с разным context budget.

### Что нельзя утверждать без дополнительных экспериментов

- Нельзя утверждать промышленную точность AC power-flow, пока не подключены simulator-backed evaluators.
- Нельзя утверждать устойчивое ранжирование моделей, пока hidden cases слишком мало.
- Нельзя смешивать старые 0–100 historical runs с normalized-score runs.

## 8. Обсуждение ограничений

Обязательные ограничения для честной статьи:

1. Public cases пока малы; многие решаются эвристически.
2. Часть evaluator-ов — компактные формульные или графовые суррогаты.
3. Hidden coverage пока недостаточен для полноценного leaderboard.
4. Source cards местами краткие; перед публикацией нужны более точные библиографические ссылки.
5. Для ряда задач нужен переход к настоящим симуляторам.
6. Слишком прямые public sample submissions могут создавать oracle leakage, поэтому leaderboard должен быть только на hidden cases.

## 9. Заключение

Основной вывод:

Power Systems Agent Benchmark демонстрирует практический путь от текстовых задач к исполняемой оценке ИИ-агентов в электроэнергетике. Даже текущий прототип показывает, как формализовать широкий спектр инженерных задач в единый agent-agnostic protocol. Главная ценность — не в конкретных public toy cases, а в контракте, таксономии, проверяющих программах и дорожной карте к simulator-backed hidden evaluation.

---

# План подготовки статьи

## Этап 1 — Зафиксировать корпус и факты

**Цель:** получить воспроизводимые числа для статьи.

**Файлы:**

- `README.md`
- `HANDOFF.md`
- `reports/power_systems_agent_benchmark_ru_overview.md`
- `scripts/evaluate_submission.py`
- `scripts/run_public_baselines.py`
- `tasks/*/public/case_001/task.json`

**Действия:**

1. Выполнить `bash scripts/check.sh`.
2. Сохранить полный stdout в `reports/check_latest.txt`.
3. Выполнить `python scripts/run_public_baselines.py --out runs/public_baselines/article_snapshot`.
4. Сохранить summary в таблицу для статьи.
5. Сгенерировать machine-readable task catalog: family, domain, objective, evaluator, baseline, source_provenance.

**Результат:** воспроизводимая таблица фактов.

## Этап 2 — Нормализовать таксономию задач

**Цель:** не показывать в статье хаотичные `subdomain` labels.

**Создать:**

- `docs/paper/task_taxonomy_ru.md`
- `docs/paper/task_catalog_article.csv`

**Действия:**

1. Назначить каждой из 41 family одну из 8 крупных категорий.
2. Для каждой family дать короткое русское описание на 1–2 предложения.
3. Добавить колонку `source_type`: literature/manual/arxiv/local archive/benchmark-derived/etc.
4. Добавить колонку `evaluator_type`: formula, graph, optimization, classification, compliance, dispatch, simulator-backed planned.

## Этап 3 — Доработать источники

**Цель:** чтобы статья выдержала академическую проверку по источникам.

**Проблема:** сейчас source provenance есть в task artifacts, но source cards местами слишком краткие.

**Действия:**

1. Для каждой задачи проверить `source_provenance`.
2. Для слабых карточек добавить:
   - полное название источника;
   - авторов, если доступны;
   - год;
   - DOI/arXiv/URL или локальный locator;
   - как именно источник связан с задачей.
3. Отдельно пометить источники, где provenance пока low/medium confidence.

**Результат:** таблица источников, пригодная для приложения к статье.

## Этап 4 — Написать черновик статьи

**Создать:**

- `docs/paper/paper_ru_draft.md`

**Скелет:**

1. Аннотация.
2. Введение.
3. Связанные работы.
4. Требования к бенчмарку электроэнергетических агентов.
5. Архитектура benchmark protocol.
6. Набор задач и источники.
7. Проверяющие программы и метрики.
8. Эксперименты.
9. Ограничения.
10. Заключение.
11. Приложение: каталог задач.

## Этап 5 — Подготовить рисунки и таблицы

**Минимальные рисунки:**

1. Цикл оценки агента.
2. Архитектура репозитория.
3. Лестница зрелости evaluator-ов.
4. Таксономия задач по доменам.

**Минимальные таблицы:**

1. Сравнение с QA / LLM-as-a-Judge / симуляторными средами.
2. 41-task catalog.
3. Типы evaluator-ов.
4. Baseline/agent smoke results.
5. Ограничения и planned simulator-backed tracks.

## Этап 6 — Эксперименты перед публикацией

**Минимум:**

- public baseline sanity;
- existing hidden normalized smoke для Hermes/OpenCode;
- актуализировать Codex после auth refresh или явно исключить как setup failure.

**Лучше:**

- добавить hidden cases для 10–15 family;
- прогнать Hermes/OpenCode/Codex/ещё один open-source agent;
- сделать таблицу ошибок по типам.

## Этап 7 — Версия для подачи

**Возможные форматы:**

- русская markdown-статья → PDF;
- LaTeX article;
- bilingual extended abstract;
- arXiv-style English version позже.

**Перед финализацией проверить:**

- не завышаем claims;
- все источники есть;
- baseline numbers воспроизводимы;
- limitations явно написаны;
- public/hidden split объяснён;
- simulator-backed roadmap не подаётся как уже реализованный факт.

---

# Предлагаемый первый абзац аннотации

В работе представлен Power Systems Agent Benchmark — прототип исполняемого бенчмарка для оценки инструментальных ИИ-агентов в задачах электроэнергетики. В отличие от текстовых question-answering наборов и оценки отчётов через LLM-as-a-Judge, предлагаемый подход требует от агента сформировать структурированное решение, которое затем проверяется программой-оценщиком: пересчитываются инженерные величины, проверяются физические и эксплуатационные ограничения, формируются машинно-читаемые метрики и диагностические нарушения. Текущий публичный срез включает 41 задачу из разных областей электроэнергетики — от расчёта режимов, защиты и устойчивости до DER, микросетей, надёжности, качества электроэнергии и кибербезопасности измерений.

# Предлагаемый основной claim в статье

Мы не утверждаем, что текущий public core уже является полной заменой специализированных энергетических симуляторов. Наш claim точнее: предложен и реализован воспроизводимый benchmark contract, который переводит электроэнергетические задачи из формата текстовых ответов в формат исполняемой проверки и может постепенно наполняться более реалистичными simulator-backed hidden evaluators.
