# Аннотированная библиография

Рабочая библиография статьи о Power Systems Agent Benchmark. Каждая запись:
полная ссылка + аннотация «зачем цитируем». BibTeX-версия: `references.bib`.

> Примечание о PowerAgentBench: существует как GitHub-репозиторий
> (github.com/Power-Agent/PowerAgentBench) без сопутствующей публикации,
> поэтому не индексируется arXiv/Semantic Scholar и был ошибочно помечен как
> несуществующий в первой версии этой библиографии. Включён в раздел 3 как
> ближайшая по концепции работа.

---

## 1. Бенчмарки LLM- и tool-агентов

1. **Liu X. et al.** AgentBench: Evaluating LLMs as Agents. ICLR 2024.
   arXiv:2308.03688. — Первый широкий бенчмарк LLM-как-агентов по восьми
   средам. Цитируем как точку отсчёта агентной оценки общего назначения, не
   покрывающей инженерные домены.
2. **Jimenez C. E. et al.** SWE-bench: Can Language Models Resolve Real-World
   GitHub Issues? ICLR 2024. arXiv:2310.06770. — Канонический пример
   исполняемой оценки (решение проверяется тестами, а не судьёй); наш контракт
   переносит этот принцип с кода на инженерные расчёты.
3. **Mialon G. et al.** GAIA: A Benchmark for General AI Assistants. 2023.
   arXiv:2311.12983. — Оценка ассистентов с однозначно проверяемыми ответами;
   аргумент в пользу машинной проверки вместо судейства.
4. **Zhou S. et al.** WebArena: A Realistic Web Environment for Building
   Autonomous Agents. ICLR 2024. arXiv:2307.13854. — Исполняемая среда с
   функциональной проверкой результата; параллель к нашему «evaluator
   пересчитывает исход».
5. **Yao S., Shinn N., Razavi P., Narasimhan K.** τ-bench: A Benchmark for
   Tool-Agent-User Interaction in Real-World Domains. 2024. arXiv:2406.12045.
   — Проверка по конечному состоянию БД + метрика pass^k для устойчивости;
   методологически ближайший к нам подход «сравнивай состояние, не текст».
6. **Chan J. S. et al.** MLE-bench: Evaluating Machine Learning Agents on
   Machine Learning Engineering. 2024. arXiv:2410.07095. — Агентная оценка
   на инженерных ML-задачах с объективным скорингом; пример доменного
   агентного бенчмарка вне веба и кода.
7. **Chen M. et al.** Evaluating Large Language Models Trained on Code.
   2021. arXiv:2107.03374. — Codex/HumanEval; вводит pass@k и сам жанр
   «оценка через исполнение». Цитируем при обсуждении метрик и best-of-N.

## 2. LLM-as-a-Judge и его ограничения

8. **Zheng L. et al.** Judging LLM-as-a-Judge with MT-Bench and Chatbot
   Arena. NeurIPS 2023 (Datasets & Benchmarks). arXiv:2306.05685. —
   Каноническая работа о судействе LLM и его смещениях (позиция, длина,
   самопредпочтение). Наш аргумент: для инженерии судья не нужен — есть
   пересчёт.
9. **Gu J. et al.** A Survey on LLM-as-a-Judge. 2024. arXiv:2411.15594. —
   Систематизация надёжности/смещений судейских оценок.
10. **Li D. et al.** From Generation to Judgment: Opportunities and
    Challenges of LLM-as-a-Judge. 2024. arXiv:2411.16594. — Обзор областей
    применимости и провалов судейства.
11. **Wang P. et al.** Large Language Models are not Fair Evaluators. 2023.
    arXiv:2305.17926. — Экспериментальная демонстрация позиционного смещения;
    короткий сильный аргумент против судьи как основного скора.

## 3. LLM и агенты в электроэнергетике

12. **Zhou Y. et al.** ElecBench: a Power Dispatch Evaluation Benchmark for
    Large Language Models. IEEE PESGM 2025 (Best Paper). arXiv:2407.05365. —
    Ближайший по домену бенчмарк: сценарии диспетчеризации, 6 метрик / 24
    субметрики, но оценка преимущественно текстовая/судейская. Ключевой
    контраст к нашей исполняемой проверке.
13. **PFBench: Power-Flow Benchmark for LLM-based Power System Agent
    Evaluation.** IEEE DataPort, 2025. — Замороженные сценарии стандартных
    тестовых сетей с solver-derived gold answers и программной проверкой;
    концептуально близок нашему подходу, но покрывает только power flow.
    Цитируем как независимое подтверждение тренда на исполняемую оценку в домене.
14. **GridMind: LLMs-Powered Agents for Power System Analysis and
    Operations.** 2025. arXiv:2509.02494. — Агентная система анализа
    энергосистем; пример «производственного» агента, которому нужен наш тип
    бенчмарка.
15. **Large Language Models for Power System Applications: A Comprehensive
    Literature Survey.** 2025. arXiv:2512.13004. — Свежий обзор LLM-применений
    в энергетике (2020–2025): диагностика, прогноз, кибербезопасность,
    планирование; фиксирует отсутствие стандартизированной оценки как
    открытую проблему.
16. **X-GridAgent: An LLM-Powered Agentic AI System for Assisting Power Grid
    Analysis.** 2025. arXiv:2512.20789. — Ещё одна агентная система анализа
    сетей; усиливает мотивацию.
17. **Grid-Mind: An LLM-Orchestrated Multi-Fidelity Agent for Automated
    Connection Impact Assessment.** 2026. arXiv:2602.20683. — Оркестрация
    мультифидельных симуляций агентом; пример будущего потребителя
    simulator-backed проверок.
17a. **PowerAgentBench.** GitHub: Power-Agent/PowerAgentBench (без
    публикации, 2025–2026). — Ближайшая по концепции работа: три уровня
    (N-1 аудит и митигация на IEEE 39-bus; агентный N-2 поиск с
    evidence-backed отчётом; ревизия качества динамической модели WECC solar
    PV с инструментами PSS/E), public/hidden split, скрытый evaluator
    пересчитывает физическую корректность. Отличия нашей работы: 41 семейство
    против 3 уровней, охват восьми доменных групп (защита, активы, качество,
    кибер, прогноз), генератор скрытых кейсов из приватного seed вместо
    статического hidden-набора, агент-агностичный CLI-протокол и
    формализованный цикл контроля качества постановок.
17b. **Agentic AI Systems in Electrical Power Systems Engineering: Current
    State-of-the-Art and Challenges.** 2025. arXiv:2511.14478. — Обзор именно
    агентных (а не просто LLM) систем в электроэнергетике; называет
    отсутствие стандартизированных бенчмарков ключевым вызовом — прямая
    мотивация нашей работы.
17c. **PFAgent: A Tractable and Self-Evolving Power-Flow Agent for
    Interactive Grid Analysis.** 2026. arXiv:2604.10846. — Самоэволюционирующий
    power-flow агент; ещё один целевой «испытуемый».

## 4. RL-среды управления сетью

18. **Marot A. et al.** Learning to Run a Power Network Challenge for
    Training Topology Controllers. Electric Power Systems Research 189 (2020).
    arXiv:1912.04211. — Постановка L2RPN; топологическое управление сетью как
    RL-задача.
19. **Marot A. et al.** Learning to Run a Power Network Challenge: a
    Retrospective Analysis. PMLR v133 (NeurIPS 2020 Competition Track), 2021.
    — Ретроспектива соревнования, Grid2Op как фреймворк. Цитируем как зрелую
    среду последовательного управления, отличие — наш агент-агностичный
    контракт однократных инженерных решений по 41 подзадаче, а не RL-петля.

## 5. Симуляторы и открытые библиотеки (substrate дорожной карты)

20. **Thurner L. et al.** pandapower — An Open-Source Python Tool for
    Convenient Modeling, Analysis, and Optimization of Electric Power
    Systems. IEEE Trans. Power Systems 33(6), 2018. — Целевой substrate для
    simulator-backed PF/contingency проверок.
21. **Zimmerman R. D., Murillo-Sánchez C. E., Thomas R. J.** MATPOWER:
    Steady-State Operations, Planning, and Analysis Tools for Power Systems
    Research and Education. IEEE Trans. Power Systems 26(1), 2011. —
    Классическая референс-реализация PF/OPF.
22. **Dugan R. C., McDermott T. E.** An Open Source Platform for
    Collaborating on Smart Grid Research (OpenDSS). IEEE PES GM 2011. —
    Распределительные сети/DER; целевой substrate распределённых задач.
23. **Coffrin C., Bent R., Sundar K., Ng Y., Lubin M.** PowerModels.jl: An
    Open-Source Framework for Exploring Power Flow Formulations. PSCC 2018.
    — Формулировки OPF; substrate для OPF/SCUC-подобных треков.
24. **Babaeinejadsarookolaee S. et al.** The Power Grid Library for
    Benchmarking AC Optimal Power Flow Algorithms (PGLib-OPF). 2019.
    arXiv:1908.02788. — Стандартные OPF-кейсы; источник масштабных сетей для
    v2-генератора.
25. **Cui H., Li F., Tomsovic K.** Hybrid Symbolic-Numeric Framework for
    Power System Modeling and Analysis (ANDES). IEEE Trans. Power Systems
    36(2), 2021. — Динамика/переходные процессы; substrate для
    simulator-backed устойчивости.
26. **Brown T., Hörsch J., Schlachtberger D.** PyPSA: Python for Power
    System Analysis. Journal of Open Research Software 6(1), 2018. —
    Планирование/диспетчеризация; substrate экономических треков.

## 6. Целостность бенчмарков: контаминация, скрытые наборы, динамическая оценка

27. **Kiela D. et al.** Dynabench: Rethinking Benchmarking in NLP. NAACL
    2021. — Динамическая генерация тестов против переобучения на бенчмарк;
    концептуальный предок нашего hidden-генератора.
28. **White C. et al.** LiveBench: A Challenging, Contamination-Free LLM
    Benchmark. 2024. arXiv:2406.19314. — Регулярно обновляемые свежие
    вопросы; та же цель, другой механизм (у нас — приватный seed +
    параметрические возмущения).
29. **Cheng Y. et al. (ред.)** A Survey on Data Contamination for Large
    Language Models. 2025. arXiv:2502.14425. — Систематика контаминации и
    contamination-free стратегий (data updating / rewriting / prevention);
    наш генератор — prevention-подход.
30. **Benchmarking Large Language Models Under Data Contamination: A Survey
    from Static to Dynamic Evaluation.** 2025. arXiv:2502.17521. — Обзор
    перехода к динамической оценке; позиционируем hidden-генератор в этой
    таксономии.
31. **Jain N. et al.** LiveCodeBench: Holistic and Contamination Free
    Evaluation of Large Language Models for Code. 2024. arXiv:2403.07974. —
    Контаминационно-чистая оценка кода по датам публикации задач; смежный
    механизм.

## 7. Доменные первоисточники задач (из source provenance бенчмарка)

32. **Zhou M. et al.** Graph Computing based Fast Screening in Contingency
    Analysis. 2019. arXiv:1904.00044. — Основа `contingency_screening`.
33. **Yuan C. et al.** Fast Grid Splitting Detection for N-1 Contingency
    Analysis by Graph Computing. 2019. arXiv:1904.03587. — Детект
    островления в N-1 (там же).
34. **SCUC-CTS.** Security Constrained Unit Commitment with Corrective
    Transmission Switching. 2020. arXiv:2001.00597. — Мотив
    `corrective_transmission_switching` и `n1_generation_commitment`
    (с явной оговоркой о дистанции компактного суррогата от полного MILP).
35. **Two-Stage Service Restoration Method for Electric Power Distribution
    Systems.** 2020. arXiv:2004.07921. — Основа `flisr_restoration`.
36. **Data-Driven Framework for Assessing Cold Load Pick-up Demand in
    Service Restoration.** 2018. arXiv:1810.05734. — Контекст восстановления
    (CLPU).
37. **Liu Y., Ning P., Reiter M. K.** False Data Injection Attacks against
    State Estimation in Electric Power Grids. ACM CCS 2009 / ACM TISSEC
    14(1), 2011. — Каноническая работа о стелс-FDI; обосновывает оговорку
    скоупа `fdi_state_estimation` (резидуальные тесты не видят
    координированную атаку).
38. **Modeling and Performance Evaluation of Stealthy False Data Injection
    Attacks on Smart Grid.** 2016. arXiv:1605.06180. — Provenance FDI-задачи.
39. **Graphical Methods for Defense Against False-Data Injection Attacks on
    Power System State Estimation.** 2013. arXiv:1304.4151. — Защита от FDI;
    контекст `protected_meter_placement`.
40. **Voltage Quality Time Series Classification using Convolutional Neural
    Network.** 2019. arXiv:1904.00228. — Контекст
    `power_quality_event_classification`.
41. **Turitsyn K. et al.** Local Control of Reactive Power by Distributed
    Photovoltaic Generators. 2010. arXiv:1006.0160 (+ Options for Control...,
    arXiv:1008.0878). — Классика volt-var управления PV; основа
    `pv_volt_var`.
42. **Grid-Forming Control Based On Emulated Synchronous Condenser Strategy
    Compliant With Challenging Grid Codes.** 2023. arXiv:2303.00391. —
    Контекст grid-code/FRT задач.
43. **A New Paradigm in IBR Modeling for Power Flow and Short Circuit
    Analysis.** 2025. arXiv:2504.10181. — Контекст `ibr_short_circuit_frt`.
44. **Quantification of the Impact of GHG Emissions on Unit Commitment in
    Microgrids.** 2020. arXiv:2012.07118. — Контекст эмиссионного ограничения
    `hydro_thermal_storage_uc`.

## 8. Учебники и стандарты

45. **Kundur P.** Power System Stability and Control. McGraw-Hill, 1994. —
    Критерий равных площадей (`critical_clearing_time`), уравнение движения
    (формула RoCoF в `min_synchronous_share`).
46. **Abur A., Expósito A. G.** Power System State Estimation: Theory and
    Implementation. Marcel Dekker, 2004. — WLS и тест наибольшей
    нормированной невязки (`fdi_state_estimation`).
47. **Wood A. J., Wollenberg B. F., Sheblé G. B.** Power Generation,
    Operation, and Control. 3rd ed., Wiley, 2013. — Economic dispatch / unit
    commitment (микросетевые и UC-задачи).
48. **IEC 60909-0:2016.** Short-circuit currents in three-phase a.c.
    systems. — Эквивалентный источник c·Un/√3, c_max/c_min, болтовое КЗ
    (`three_phase_short_circuit`, `breaker_relay_short_circuit`).
49. **IEC 60076-7:2018.** Loading guide for mineral-oil-immersed power
    transformers (экв. IEEE C57.91). — Экспоненциальная тепловая модель и
    старение изоляции (`transformer_thermal_loading`).
50. **IEEE Std 738-2012.** Calculating the Current-Temperature Relationship
    of Bare Overhead Conductors. — Тепловой баланс провода
    (`dynamic_thermal_rating`).
51. **IEEE Std 519-2014.** Harmonic Control in Electric Power Systems. —
    TDD/лимиты по Isc/IL (`harmonic_ieee519_compliance`).
52. **EN 50160:2010.** Voltage characteristics of electricity supplied by
    public distribution networks. — Нормы 10-минутных RMS
    (`en50160_voltage_compliance`).
53. **IEC 60364-5-52 / IEC 60949.** Selection of wiring systems; calculation
    of thermally permissible short-circuit currents. — Ампаситет с
    поправками и адиабатический критерий (`cable_ampacity_sizing`).
54. **IEEE Std 1366-2012.** Electric Power Distribution Reliability Indices.
    — SAIDI/SAIFI/CAIDI (`fci_saidi_caidi`, `fci_placement`).
55. **IEEE Std 2800-2022.** Interconnection and Interoperability of
    Inverter-Based Resources. — Требования ride-through/реактивной поддержки
    (`frt_compliance`, `ibr_short_circuit_frt`).
56. **ENTSO-E RfG / IEC 61400-27.** Requirements for Generators: RoCoF
    withstand, FRT-кривые. — Лимит 2 Гц/с (`min_synchronous_share`).

## 9. Методология оценивания агентов

57. **Brown B. et al.** Large Language Monkeys: Scaling Inference Compute
    with Repeated Sampling. 2024. arXiv:2407.21787. — Покрытие растёт с
    числом сэмплов по степенному закону: количественное обоснование, почему
    best-of-N — другая метрика, и почему наши ретраи ограничены
    инфраструктурным классом.
58. **Yao S. et al.** (τ-bench, см. №5) — метрика pass^k как мера
    УСТОЙЧИВОСТИ агента при повторных прогонах; кандидат для v2 при оценке
    дисперсии.
59. **Kapoor S. et al.** AI Agents That Matter. 2024. arXiv:2407.01502. —
    Критика агентных бенчмарков: стоимость, воспроизводимость, переобучение
    на бенчмарк; чек-лист, по которому мы строили harness (фиксация команд,
    разделение классов провалов, обе метрики).

---

## Сводка пробелов, закрытых этой библиографией

- Раздел 2 статьи: блоки 1–4, 6 дают полноценные «Связанные работы».
- Раздел «Метрики»: №5, 7, 57–59.
- Source cards задач: блоки 7–8 (точные первоисточники и стандарты).
- Находка про оракул и hidden-генератор: блок 6.
