# Source card: EV/V2G voltage support

## Benchmark family

- Family: `ev_v2g_voltage_support`
- Candidate: `REL-TASK-017`
- Subdomain: distribution systems and DER/EV
- Public case: `tasks/ev_v2g_voltage_support/public/case_001/task.json`

## Source basis

This task models EV charger inverter reactive-power support after feeder reconfiguration. Reactive commands are chosen from voltage sensitivity coefficients and clipped by aggregate EV apparent-power capability.

Representative references:

- Volt-var support using DER/EV inverters in distribution feeders.
- Apparent-power capability limits under simultaneous active charging/discharging.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-017`.

## Evaluation logic

The evaluator computes per-bus reactive support needed to reach the target voltage, clips it by aggregate EV capability at each bus, computes corrected voltages, and checks the submitted commands.
