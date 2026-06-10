# Source card: dynamic thermal rating of overhead lines

## Benchmark family

- Family: `dynamic_thermal_rating`
- Candidate: `REL-TASK-014`
- Subdomain: transmission operations and asset ratings
- Public case: `tasks/dynamic_thermal_rating/public/case_001/task.json`

## Source basis

The task is based on standard overhead-conductor dynamic thermal rating practice. A conductor current limit is obtained from a steady-state heat balance: Joule heating and solar heating must not exceed convective and radiative cooling at the maximum allowed conductor temperature.

Representative engineering references:

- IEEE 738 style heat-balance methods for calculating current-temperature relationships of bare overhead conductors.
- CIGRE/utility dynamic line rating practice using weather-dependent wind speed, ambient temperature, and solar radiation.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-014`.

## Operational instance

The public case gives conductor diameter, resistance, emissivity, absorptivity, maximum conductor temperature, scheduled current, and a four-point weather series. The agent must compute ampacity at each timestamp, identify the limiting timestamp, and list timestamps where the scheduled current exceeds the dynamic rating.

## Evaluation logic

The evaluator independently solves the compact heat balance for each weather point. It checks all timestamp ampacities, the minimum rating, the limiting timestamp, and overload timestamps. The public task no longer exposes an expected answer.

## Limitations

The instance is intentionally compact and omits conductor heat capacity, wind angle, detailed air-property corrections, and full IEEE/CIGRE parameterization. Those can be added in hidden or larger cases.
