# Source card: wind-power point forecast

## Benchmark family

- Family: `wind_power_forecast`
- Candidate: `REL-TASK-009`
- Subdomain: forecasting and uncertainty
- Public case: `tasks/wind_power_forecast/public/case_001/task.json`

## Source basis

The task is based on wind-power forecasting practice: weather forecasts, especially wind speed and air density, are transformed into generation estimates through a turbine power curve. Recent measured production can be used to estimate a simple residual bias.

Representative references:

- Wind-turbine power-curve forecasting practice used in operational renewable forecasting.
- Density-corrected speed-to-power conversion for wind turbines.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-009`.

## Operational instance

The public case gives turbine count, rated power, cut-in/rated/cut-out speeds, historical weather and actual power, and a four-step weather forecast. The agent must compute a bias-corrected MW forecast, total forecast energy, and the peak timestamp.

## Evaluation logic

The evaluator independently applies the power curve, computes the historical residual bias, clamps forecasts to the physical farm capacity, and checks submitted values within tolerance.
