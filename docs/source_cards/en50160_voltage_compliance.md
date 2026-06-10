# Source card: EN 50160 voltage compliance

## Benchmark family

- Family: `en50160_voltage_compliance`
- Candidate: `REL-TASK-021`
- Subdomain: distribution systems and power quality
- Public case: `tasks/en50160_voltage_compliance/public/case_001/task.json`

## Source basis

The task is based on voltage-quality compliance practice inspired by EN 50160: supply voltage is assessed over RMS measurement intervals, with most values expected to remain within a normal band around nominal voltage and no values breaching broader absolute limits.

Representative engineering references:

- EN 50160 voltage characteristics of electricity supplied by public distribution systems.
- Utility voltage-quality monitoring practice using 10-minute RMS values.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#rel-task-021`.

## Operational instance

The public case gives a short series of per-unit voltages, normal and absolute limits, and a list of candidate tap changes. The agent must decide whether the unmitigated series is compliant, report out-of-band timestamps, summarize minimum/maximum voltage, and select the best listed tap correction.

## Evaluation logic

The evaluator independently counts values inside the normal band, checks absolute-limit violations, and recomputes the best tap change. It checks the submitted decision, percentages, timestamp lists, and tap recommendation.

## Limitations

The public case uses a compact ten-point trace rather than a full weekly EN 50160 assessment. It is intended to test whether the agent can apply the threshold logic and mitigation selection without copying an exposed answer.
