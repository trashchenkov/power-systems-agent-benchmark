# Source card: wind-power prediction intervals

## Benchmark family

- Family: `wind_prediction_interval`
- Candidate: `REL-TASK-012`
- Subdomain: forecasting and uncertainty
- Public case: `tasks/wind_prediction_interval/public/case_001/task.json`

## Source basis

The task is based on scenario and ensemble wind forecasting: multiple weather scenarios are transformed into power outputs, then empirical quantiles summarize forecast uncertainty.

Representative references:

- Scenario/ensemble renewable forecasting practice.
- Wind-turbine power-curve conversion with air-density correction.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-012`.

## Operational instance

The public case gives a turbine power curve and five wind-speed scenarios for each forecast horizon. The agent must compute p10, p50, and p90 power quantiles and the average interval width.

## Evaluation logic

The evaluator independently converts all scenarios to MW, computes empirical quantiles by linear interpolation, verifies interval monotonicity, and checks the reported average p90-p10 width.
