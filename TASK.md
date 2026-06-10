# TASK.md — power-systems-agent-benchmark

Created: 2026-06-08T05:34:55.820165+00:00

## User request

Sergey wants to develop a benchmark for AI agents solving tasks in electric power systems / электроэнергетика.

## Restated task

Investigate how to design a credible benchmark for LLM/tool-using agents in power systems: task taxonomy, simulators/case formats/solvers, datasets, evaluation contracts, baselines, failure modes, and relation to existing agent/energy benchmarks.

## Audience

Technical/research audience with power-systems background and interest in agent benchmarks.

## Assumptions from known context

- The benchmark should have a real power-systems substrate, not only text QA.
- Important substrate categories: simulators, case formats, solvers, contingency analysis, OPF, dynamics/control, protection/restoration, forecasting/scheduling.
- pandapower is a familiar starting point, but not necessarily the only substrate.
- Output should be practical: candidate tasks and architecture, not only literature summary.

## Scope update — prototype phase

The investigation has now moved from pure benchmark mining into a local executable prototype/repository scaffold. In scope for the current phase:

- benchmark repository skeleton;
- public task contracts;
- schema and evaluator contracts;
- dependency-free smoke evaluator(s);
- CI/check script drafts;
- clear split between autoinvestigation skill artifacts and runnable benchmark artifacts.

Still out of scope until explicit confirmation:

- pushing to GitHub or creating a remote repository;
- publishing leaderboard infrastructure;
- using paid/cloud resources;
- claiming full simulator validity before real `pandapower`/OpenDSS/etc evaluators exist.

## Open scope choices for later

- Target user: research benchmark vs teaching benchmark vs industry eval.
- Primary agent capabilities: tool use, coding, planning/control, diagnosis, report writing, or all.
- Whether tasks are deterministic scripted evaluations or interactive environments.
