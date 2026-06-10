# Source card: BESS ancillary response

## Benchmark family

- Family: `bess_ancillary_response`
- Candidate: `REL-TASK-004`
- Subdomain: converter-dominated grids and storage
- Public case: `tasks/bess_ancillary_response/public/case_001/task.json`

## Source basis

This task models standard battery energy storage ancillary response: frequency-watt active-power droop and volt-var reactive-power droop, with inverter apparent-power capability and SOC update.

Representative references:

- Grid-forming/grid-following storage ancillary-service response models.
- Frequency-watt and volt-var controls with inverter capability constraints.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-004`.

## Evaluation logic

The evaluator independently applies the public droop coefficients to each measurement, clips active power by charge/discharge limits, clips reactive power by remaining apparent-power capability, simulates SOC, and checks submitted P/Q traces and final SOC.
