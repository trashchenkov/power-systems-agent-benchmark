# Source card: power-quality event classification

## Benchmark family

- Family: `power_quality_event_classification`
- Candidate: `GAP-TASK-008`
- Subdomain: power quality and standards
- Public case: `tasks/power_quality_event_classification/public/case_001/task.json`

## Source basis

The task is based on common power-quality monitoring practice: RMS voltage traces are classified into normal operation, voltage sag, voltage swell, or interruption according to threshold bands. Event start/end times are obtained from the contiguous interval where voltage leaves the normal band.

Representative engineering references:

- IEC 61000-4-30 style measurement of power-quality events.
- IEEE/IEC power-quality terminology for sags, swells, and interruptions.
- Repository task-bank source: `literature/task_bank_v4_gap_fill_balanced.md#gap-task-008`.

## Operational instance

The public case gives a short RMS voltage/current trace and explicit classification thresholds. The agent must identify the non-normal interval, classify the event, and report duration, minimum voltage, and maximum current.

## Evaluation logic

The evaluator independently classifies every timestamp by the published thresholds, determines the event interval, and checks the submitted class and numeric summaries. Unknown answer fields are rejected.

## Limitations

The public instance uses RMS samples rather than raw waveform windows, so it does not test harmonic analysis, flicker, notching, or transient waveform feature extraction. Those are natural extensions for hidden cases.
