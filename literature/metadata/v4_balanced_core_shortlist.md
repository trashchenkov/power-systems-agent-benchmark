# V4 balanced core shortlist

- Total v4 candidates: **75**
- Balanced core shortlist: **41**
- Principle: cap overrepresented subdomains, add primary-source gap-fill tasks for undercovered subdomains, and avoid tasks whose primary provenance is another AI/LLM benchmark.

## Converter-dominated grids & storage
- Core tasks: 2
- `REL-TASK-004` — BESS ancillary-service P/Q response under frequency/voltage disturbance
- `REL-TASK-007` — Minimum synchronous-machine share for high converter penetration

## Distribution reliability & outage management
- Core tasks: 3
- `REL-TASK-051` — FCI placement to reduce patrol time
- `REL-TASK-052` — Faulted-section localization using FCI states and outage complaints
- `REL-TASK-053` — SAIDI/CAIDI impact of FCI deployment

## Distribution systems & DER/EV
- Core tasks: 3
- `REL-TASK-017` — EV/V2G voltage support after feeder reconfiguration
- `REL-TASK-020` — EV/V2G outage schedule under uncertain event time and SoC
- `REL-TASK-021` — EN 50160 voltage-compliance check and mitigation

## Energy economics, planning & policy
- Core tasks: 2
- `REL-TASK-058` — Sobol sensitivity of PV soft-cost inputs
- `REL-TASK-059` — LCOE distribution for 2 MW commercial PV under soft-cost uncertainty

## Energy systems beyond electricity / heating
- Core tasks: 2
- `REL-TASK-055` — Electric boiler capacity sizing for building heat support
- `REL-TASK-056` — Stepwise electric-boiler control by return-water temperature

## Forecasting & uncertainty
- Core tasks: 2
- `REL-TASK-009` — Multi-step wind-power forecasting from history and textual context
- `REL-TASK-012` — Prediction intervals for wind generation

## Generation scheduling: hydro, thermal & storage
- Core tasks: 1
- `GAP-TASK-013` — Hydro/thermal/storage unit commitment with ramping and emissions constraints

## Grid codes, interconnection & standards compliance
- Core tasks: 2
- `GAP-TASK-011` — Grid-code FRT compliance check for inverter-based resource
- `GAP-TASK-012` — IBR short-circuit contribution under FRT strategy

## Grid operations & control / MAS
- Core tasks: 1
- `REL-TASK-001` — MAS frequency regulation state classification and lead-station handover

## Grid operations & control / restoration
- Core tasks: 2
- `REL-TASK-003` — Decentralized network restoration after short circuit
- `REL-TASK-050` — Operator breaker/load actions in one-line model

## Market/dispatch planning & uncertainty
- Core tasks: 1
- `REL-TASK-015` — Robust/scenario dispatch under renewable/load/outage/DLR uncertainty

## Markets, unit commitment, reserves & adequacy
- Core tasks: 1
- `GAP-TASK-001` — Security-constrained unit commitment with N-1 constraints

## Microgrids & DER dispatch
- Core tasks: 3
- `REL-TASK-022` — Joint active/reactive dispatch in islanded microgrid
- `REL-TASK-024` — Economic active-power dispatch in microgrid
- `REL-TASK-026` — Rolling 5-minute renewable microgrid dispatch with capability curves

## OT cybersecurity, state estimation & bad data
- Core tasks: 2
- `GAP-TASK-006` — False-data injection attack detection in state estimation
- `GAP-TASK-007` — Design protected meter placement against FDI attacks

## Power flow, modelling & transmission analysis
- Core tasks: 2
- `REL-TASK-046` — AC power-flow solve and violation diagnosis
- `REL-TASK-047` — Build Ybus from network data

## Power quality & standards
- Core tasks: 2
- `GAP-TASK-008` — Power-quality event classification from voltage/current waveforms
- `GAP-TASK-009` — PV reactive-power control for voltage sag/swell mitigation

## Protection, faults & relay engineering
- Core tasks: 5
- `REL-TASK-033` — Three-phase short-circuit current calculation
- `REL-TASK-034` — Unsymmetrical and earth-fault calculation
- `REL-TASK-036` — Line overcurrent protection settings
- `REL-TASK-039` — Distance protection settings for 35–330 kV lines
- `REL-TASK-045` — Short-circuit currents for breaker and relay settings

## Stability & dynamics
- Core tasks: 2
- `REL-TASK-008` — Transient stability prediction with high wind penetration
- `REL-TASK-048` — Transient stability and critical clearing time

## Transmission operations & asset ratings
- Core tasks: 1
- `REL-TASK-014` — Dynamic/real-time thermal rating of overhead lines

## Transmission operations, contingency & congestion management
- Core tasks: 2
- `GAP-TASK-002` — Corrective transmission switching after contingency
- `GAP-TASK-005` — Fast contingency screening and islanding detection

## Notes on excluded/placeholder gap-fill tasks

- `GAP-TASK-010` asset/RUL is intentionally **not** in balanced core yet: current evidence is too generic; needs a transformer/DGA/thermal-aging primary source.
- `GAP-TASK-014` electricity price forecasting is intentionally **not** in balanced core yet: current local evidence is LLM-oriented; needs a primary market-data/task source.
- Protection remains capped at 5 despite 17 available candidates; additional relay tasks should be held as variants or a separate protection track.
