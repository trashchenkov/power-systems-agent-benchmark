# Source card: scenario dispatch under uncertainty

## Benchmark family

- Family: `dispatch_uncertainty`
- Candidate: `REL-TASK-015`
- Subdomain: market and dispatch planning under uncertainty
- Public case: `tasks/dispatch_uncertainty/public/case_001/task.json`

## Source basis

The task is based on robust/scenario economic dispatch: generation is scheduled against uncertain load and renewable output, with a reserve margin maintained for the worst net-load scenario.

Representative references:

- Scenario robust economic dispatch and reserve scheduling.
- Unit/economic dispatch practice with generator bounds and variable costs.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-015`.

## Operational instance

The public case gives two thermal generators, three time periods, and three load/renewable scenarios. The agent must schedule generator outputs that cover maximum net load plus reserve in every period while minimizing variable cost.

## Evaluation logic

The evaluator independently computes the worst-case net load by period, constructs the least-cost dispatch from the listed generators, verifies generator bounds and reserve margins, and checks the submitted dispatch, margins, and total cost.
