# Task bank v4 — domain-only gap-fill and balanced coverage update

Scope: continues `task_bank_v3_domain_only_balanced.md` by targeted gap-fill for undercovered energy subdomains. New gap-fill candidates come from primary arXiv/domain papers where available plus explicitly marked local/generic gap signals where primary confirmation is still needed.

## Summary

- v3 domain-only candidates: **61**
- new gap-fill candidates: **14**
- total v4 candidates: **75**
- new gap-fill candidates promoted to provisional balanced core: **11**

## Evidence caveat

The gap-fill pass used arXiv metadata/abstracts plus local text search. Candidates marked `low-medium` or saying “needs primary source” should not enter the final core until a full-text domain source or dataset is inspected. They are included to make coverage gaps explicit and guide source acquisition.

## New gap-fill candidates

### GAP-TASK-001 — Security-constrained unit commitment with N-1 constraints
- **Subdomain:** Markets, unit commitment, reserves & adequacy
- **Provisional balanced core:** yes
- **Source:** Security Constrained Unit Commitment with Corrective Transmission Switching (2020-01-02, arXiv:2001.00597v1) — https://arxiv.org/abs/2001.00597v1
- **Evidence:** The paper frames SCUC as day-ahead scheduling under security constraints and studies corrective transmission switching / network topology reconfiguration to reduce operational cost while respecting contingencies.
- **Operational problem:** Choose generator on/off status, dispatch and reserves for a day-ahead horizon subject to unit constraints, demand balance and N-1 line outage security.
- **Input:** Generator cost/startup/min-up/down/ramp data, load profile, DC network, contingency list, reserve requirement.
- **Output/action:** Commitment binary schedule, dispatch MW, reserves, contingency feasibility report.
- **Evaluator:** MILP/DC-SCUC reference solver; score objective gap, infeasible hours, reserve shortfalls, contingency overloads.
- **Substrate:** PyPSA or custom Pyomo/CVXPY MILP over MATPOWER/PGLib-style cases.
- **Confidence:** medium-strong; primary paper identified, full evaluator details need full-text extraction.

### GAP-TASK-002 — Corrective transmission switching after contingency
- **Subdomain:** Transmission operations, contingency & congestion management
- **Provisional balanced core:** yes
- **Source:** Security Constrained Unit Commitment with Corrective Transmission Switching (2020-01-02, arXiv:2001.00597v1) — https://arxiv.org/abs/2001.00597v1
- **Evidence:** Security Constrained Unit Commitment with Corrective Transmission Switching focuses on using transmission switching after contingency to lower cost and relieve network issues.
- **Operational problem:** Given a post-contingency overloaded network, choose a limited corrective switching action that restores line limits without islanding or load shedding.
- **Input:** Base/post-contingency DC network state, candidate switchable branches, line limits, islanding constraints, allowed switching budget.
- **Output/action:** Switch/no-switch decision set and resulting flows.
- **Evaluator:** DC power flow after switching; check connectivity, overload removal, switching budget and cost/regret versus enumerated optimum.
- **Substrate:** NetworkX + PYPOWER/PyPSA DC power flow.
- **Confidence:** medium-strong.

### GAP-TASK-003 — Distribution service restoration with topology reconfiguration
- **Subdomain:** Distribution automation, FLISR & feeder reconfiguration
- **Provisional balanced core:** yes
- **Source:** A Two-Stage Service Restoration Method for Electric Power Distribution Systems (2020-04-16, arXiv:2004.07921v1) — https://arxiv.org/abs/2004.07921v1
- **Evidence:** A Two-Stage Service Restoration Method for Electric Power Distribution Systems targets self-healing distribution management and restoration.
- **Operational problem:** After fault isolation, choose switch operations and DER/load pickup to maximize restored critical load while preserving radiality and voltage/current constraints.
- **Input:** Distribution feeder graph, faulted section, tie/sectionalizing switches, load priorities, DER availability, voltage/current limits.
- **Output/action:** Switching sequence, energized islands/feeders, restored load list, DER dispatch.
- **Evaluator:** Radiality checker + AC distribution power flow; score restored priority load, violations, switching count and unsafe energization.
- **Substrate:** OpenDSS/pandapower + NetworkX restoration model.
- **Confidence:** medium-strong.

### GAP-TASK-004 — Cold-load pickup aware service restoration
- **Subdomain:** Distribution automation, FLISR & feeder reconfiguration
- **Provisional balanced core:** yes
- **Source:** A Data-Driven Framework for Assessing Cold Load Pick-up Demand in Service Restoration (2018-10-11, arXiv:1810.05734v2) — https://arxiv.org/abs/1810.05734v2
- **Evidence:** A Data-Driven Framework for Assessing Cold Load Pick-up Demand in Service Restoration highlights CLPU impact on restoration planning.
- **Operational problem:** Estimate cold-load pickup demand after outage and use it to sequence restoration without overloading feeders/transformers.
- **Input:** Outage duration, historical AMI/load data, customer classes, restoration candidate sequence, equipment limits.
- **Output/action:** CLPU-adjusted demand estimates and safe restoration sequence.
- **Evaluator:** Hidden CLPU model/time-series; score demand-estimation error and overload/voltage violations during restoration.
- **Substrate:** pandas CLPU estimator + pandapower feeder replay.
- **Confidence:** medium-strong.

### GAP-TASK-005 — Fast contingency screening and islanding detection
- **Subdomain:** Transmission operations, contingency & congestion management
- **Provisional balanced core:** yes
- **Source:** Graph Computing based Fast Screening in Contingency Analysis (2019-03-29, arXiv:1904.00044v1) — https://arxiv.org/abs/1904.00044v1; Fast Grid Splitting Detection for N-1 Contingency Analysis by Graph Computing (2019-04-07, arXiv:1904.03587v1) — https://arxiv.org/abs/1904.03587v1
- **Evidence:** Graph-computing papers target fast contingency screening and grid splitting detection for N-1 contingency analysis in EMS.
- **Operational problem:** Rank N-1 outages by severity and flag outages that split the grid before expensive power-flow simulation.
- **Input:** Transmission graph, branch ratings, base flows, list of line/generator outages.
- **Output/action:** Criticality ranking, islanding flags, candidates requiring full AC PF.
- **Evaluator:** Graph connectivity + DC/AC PF reference; score missed critical outages, false negatives for islanding, runtime.
- **Substrate:** NetworkX + pandapower/PYPOWER contingency loop.
- **Confidence:** medium-strong.

### GAP-TASK-006 — False-data injection attack detection in state estimation
- **Subdomain:** OT cybersecurity, state estimation & bad data
- **Provisional balanced core:** yes
- **Source:** Modeling and performance evaluation of stealthy false data injection attacks on smart grid in the presence of corrupted measurements (2016-05-20, arXiv:1605.06180v1) — https://arxiv.org/abs/1605.06180v1; Graphical Methods for Defense Against False-data Injection Attacks on Power System State Estimation (2013-04-15, arXiv:1304.4151v4) — https://arxiv.org/abs/1304.4151v4
- **Evidence:** FDI attack papers describe attacks that bypass traditional bad-data detection in power-system state estimators and defenses using graph methods.
- **Operational problem:** Detect or localize malicious measurement modifications in DC state estimation while separating them from noise/gross errors.
- **Input:** Network H matrix, measurements z, noise covariance, bad-data/attack scenarios, optional protected meter set.
- **Output/action:** Attack/no-attack label, suspected measurements/states, corrected estimate.
- **Evaluator:** Known hidden attack vector; score detection F1, localization precision/recall, state-estimation error and false alarms.
- **Substrate:** DC state estimator with chi-square residual and graph-defense baseline.
- **Confidence:** strong; classic primary power cyber literature.

### GAP-TASK-007 — Design protected meter placement against FDI attacks
- **Subdomain:** OT cybersecurity, state estimation & bad data
- **Provisional balanced core:** no
- **Source:** Graphical Methods for Defense Against False-data Injection Attacks on Power System State Estimation (2013-04-15, arXiv:1304.4151v4) — https://arxiv.org/abs/1304.4151v4
- **Evidence:** Graphical methods for defense against false-data injection attacks study protection strategies for power-system state estimation.
- **Operational problem:** Choose a limited set of meters/PMUs to secure so that targeted stealth attacks become impossible or less damaging.
- **Input:** Network topology, measurement placement, candidate meters, protection budget, target states/branches.
- **Output/action:** Protected meter set and residual attackability report.
- **Evaluator:** Graph/observability attackability checker; score number of protected critical states and budget compliance.
- **Substrate:** NetworkX observability + DC SE attack model.
- **Confidence:** medium-strong.

### GAP-TASK-008 — Power-quality event classification from voltage/current waveforms
- **Subdomain:** Power quality & standards
- **Provisional balanced core:** yes
- **Source:** Voltage Quality Time Series Classification using Convolutional Neural Network (2019-03-30, arXiv:1904.00228v1) — https://arxiv.org/abs/1904.00228v1
- **Evidence:** Voltage Quality Time Series Classification using CNN frames classification of power-quality problems from voltage-quality time series.
- **Operational problem:** Classify voltage sag/swell/interruption/harmonic/unbalance events from sampled waveform or RMS time series.
- **Input:** Voltage/current traces, sampling rate, nominal voltage, event labels in training set.
- **Output/action:** Event class, start/end time, severity metrics.
- **Evaluator:** Hidden labeled PQ event set; macro-F1, event timing error, severity error.
- **Substrate:** Synthetic IEEE 1159-like event generator + public PQ datasets where available.
- **Confidence:** medium-strong.

### GAP-TASK-009 — PV reactive-power control for voltage sag/swell mitigation
- **Subdomain:** Power quality & standards
- **Provisional balanced core:** yes
- **Source:** Local Control of Reactive Power by Distributed Photovoltaic Generators (2010-06-01, arXiv:1006.0160v1) — https://arxiv.org/abs/1006.0160v1; Options for Control of Reactive Power by Distributed Photovoltaic Generators (2010-08-04, arXiv:1008.0878v1) — https://arxiv.org/abs/1008.0878v1
- **Evidence:** Turitsyn/Sulc/Backhaus papers discuss reactive-power control by distributed PV to mitigate voltage sags/swells caused by rapidly varying PV generation and slow utility voltage regulation.
- **Operational problem:** Set local Volt-VAR/reactive control parameters for distributed PV to reduce voltage excursions without excessive reactive circulation.
- **Input:** Distribution feeder, PV locations/ratings, irradiance ramps, voltage limits, inverter Q capability.
- **Output/action:** Local control law/parameters or Q setpoints.
- **Evaluator:** Time-series AC PF; voltage violation-hours, losses, Q use, inverter limit violations.
- **Substrate:** pandapower/OpenDSS PV feeder.
- **Confidence:** strong.

### GAP-TASK-010 — Transformer condition / RUL prediction from monitoring data
- **Subdomain:** Asset management, maintenance & reliability
- **Provisional balanced core:** no
- **Source:** Local archive evidence: equipment fault detection/condition monitoring mention in `2403.09125v1_d2fc442e.txt:531-533`; arXiv RUL sources are general PHM and need power-transformer-specific replacement.
- **Evidence:** Local archive has only weak/generic condition-monitoring evidence; this task is added as a gap-fill target requiring a primary transformer/DGA/thermal-aging source before core promotion.
- **Operational problem:** Predict transformer health index or remaining useful life from dissolved gas, loading, temperature and maintenance history.
- **Input:** DGA time series, top-oil/hotspot temperature, load history, age, fault labels or failure times.
- **Output/action:** health index/RUL estimate and maintenance priority.
- **Evaluator:** Held-out labeled asset data; C-index/MAE for RUL, F1 for fault class, calibration of risk score.
- **Substrate:** tabular/time-series prognostics harness; IEC thermal aging formula baseline.
- **Confidence:** low-medium; needs better primary power-transformer source.

### GAP-TASK-011 — Grid-code FRT compliance check for inverter-based resource
- **Subdomain:** Grid codes, interconnection & standards compliance
- **Provisional balanced core:** yes
- **Source:** Grid-Forming Control Based On Emulated Synchronous Condenser Strategy Compliant With Challenging Grid Code Requirements (2023-03-01, arXiv:2303.00391v2) — https://arxiv.org/abs/2303.00391v2; A Novel Decentralized Inverter Control Algorithm for Loss Minimization and LVRT Improvement (2022-07-24, arXiv:2207.11700v3) — https://arxiv.org/abs/2207.11700v3
- **Evidence:** Grid-forming and inverter-control papers discuss compliance with challenging grid-code requirements, LVRT/FRT and reactive support tradeoffs.
- **Operational problem:** Given voltage/frequency event traces and inverter response, decide whether the plant satisfies fault-ride-through and reactive current support requirements.
- **Input:** Voltage/frequency traces, active/reactive current response, grid-code curve thresholds, plant rating.
- **Output/action:** pass/fail compliance report, violated clauses/thresholds, minimal corrective settings.
- **Evaluator:** Rule-based curve checker; ride-through region, current support timing/magnitude, recovery constraints.
- **Substrate:** Python grid-code rules + synthetic FRT traces.
- **Confidence:** medium-strong; exact standard clauses still need source-specific extraction.

### GAP-TASK-012 — IBR short-circuit contribution under FRT strategy
- **Subdomain:** Grid codes, interconnection & standards compliance
- **Provisional balanced core:** yes
- **Source:** A New Paradigm in IBR Modeling for Power Flow and Short Circuit Analysis (2025-04-14, arXiv:2504.10181v1) — https://arxiv.org/abs/2504.10181v1
- **Evidence:** A New Paradigm in IBR Modeling for Power Flow and Short Circuit Analysis states IBR fault response differs from synchronous generators and is determined by FRT strategies and saturation.
- **Operational problem:** Compute or classify inverter fault-current contribution under voltage sag and current limiting strategy for protection studies.
- **Input:** IBR rating, control mode, voltage sag profile, current limit, FRT strategy, sequence network context.
- **Output/action:** fault-current profile/limits and protection adequacy notes.
- **Evaluator:** Reference IBR short-circuit model; numeric error and protection-setting implications.
- **Substrate:** custom IBR fault-current model + pandapower shortcircuit extension.
- **Confidence:** medium-strong.

### GAP-TASK-013 — Hydro/thermal/storage unit commitment with ramping and emissions constraints
- **Subdomain:** Generation scheduling: hydro, thermal & storage
- **Provisional balanced core:** yes
- **Source:** Quantification of the Impact of GHG Emissions on Unit Commitment in Microgrids (2020-12-13, arXiv:2012.07118v1) — https://arxiv.org/abs/2012.07118v1; New efficient ADMM algorithm for the Unit Commitment Problem (2023-11-22, arXiv:2311.13438v1) — https://arxiv.org/abs/2311.13438v1
- **Evidence:** Unit commitment papers include thermal generation, GHG constraints and decentralized ADMM solution for UC.
- **Operational problem:** Schedule thermal units and storage/hydro-like energy constraints over a horizon with ramping, startup and emissions budget.
- **Input:** Unit costs, startup/shutdown, min up/down, ramp limits, storage/hydro energy constraints, load/renewable forecast, emissions factors.
- **Output/action:** commitment, dispatch, storage/hydro schedule, emissions/cost report.
- **Evaluator:** MILP baseline; objective gap, unmet load, ramp/min-up/down violations, emissions violations.
- **Substrate:** Pyomo/PyPSA unit commitment.
- **Confidence:** medium; source is UC primary but hydro-specific source still needed.

### GAP-TASK-014 — Electricity price forecasting for market-aware dispatch
- **Subdomain:** Markets, unit commitment, reserves & adequacy
- **Provisional balanced core:** no
- **Source:** Local archive: `2403.09125v1_d2fc442e.txt:691-693` contains a prompt/example for electricity price prediction from previous-day information; needs primary market-data source before core promotion.
- **Evidence:** Local source mentions electricity price prediction task, but it is LLM-oriented; use only as gap signal, not final provenance.
- **Operational problem:** Forecast day-ahead/real-time electricity price from previous-day prices, load, renewables and calendar/weather features.
- **Input:** Historical prices, load/RES forecasts, calendar/weather, bidding zone.
- **Output/action:** price forecast with intervals and downstream dispatch risk note.
- **Evaluator:** MAE/RMSE/Pinball loss and cost impact in storage arbitrage/dispatch replay.
- **Substrate:** market time-series dataset + storage arbitrage simulator.
- **Confidence:** low-medium; needs primary market dataset/paper.

## Combined v4 coverage by subdomain

- **Asset management, maintenance & reliability:** 1 candidates; 0 in provisional balanced core
- **Converter-dominated grids & storage:** 4 candidates; 3 in provisional balanced core
- **Distribution automation, FLISR & feeder reconfiguration:** 2 candidates; 2 in provisional balanced core
- **Distribution reliability & outage management:** 4 candidates; 3 in provisional balanced core
- **Distribution systems & DER/EV:** 5 candidates; 4 in provisional balanced core
- **Energy economics, planning & policy:** 4 candidates; 3 in provisional balanced core
- **Energy systems beyond electricity / heating:** 3 candidates; 2 in provisional balanced core
- **Forecasting & uncertainty:** 6 candidates; 2 in provisional balanced core
- **Generation scheduling: hydro, thermal & storage:** 1 candidates; 1 in provisional balanced core
- **Grid codes, interconnection & standards compliance:** 2 candidates; 2 in provisional balanced core
- **Grid operations & control / MAS:** 2 candidates; 2 in provisional balanced core
- **Grid operations & control / restoration:** 2 candidates; 2 in provisional balanced core
- **Market/dispatch planning & uncertainty:** 1 candidates; 1 in provisional balanced core
- **Markets, unit commitment, reserves & adequacy:** 2 candidates; 1 in provisional balanced core
- **Microgrids & DER dispatch:** 7 candidates; 4 in provisional balanced core
- **OT cybersecurity, state estimation & bad data:** 2 candidates; 1 in provisional balanced core
- **Power flow, modelling & transmission analysis:** 2 candidates; 2 in provisional balanced core
- **Power quality & standards:** 2 candidates; 2 in provisional balanced core
- **Protection, faults & relay engineering:** 17 candidates; 6 in provisional balanced core
- **Stability & dynamics:** 2 candidates; 2 in provisional balanced core
- **Transmission operations & asset ratings:** 2 candidates; 1 in provisional balanced core
- **Transmission operations, contingency & congestion management:** 2 candidates; 2 in provisional balanced core

## Remaining source gaps

- **Asset management:** GAP-TASK-010 is only a placeholder until a power-transformer/DGA/thermal-aging primary source is mined.
- **Markets:** Need non-LLM primary market data sources for electricity price forecasting and reserve-market tasks.
- **Hydro scheduling:** UC sources are available; hydro-specific reservoir constraints need a primary source.
- **Standards:** FRT/grid-code tasks need exact IEEE/IEC/GOST clauses and thresholds before final evaluator implementation.
## Final v4 balanced core shortlist

See `literature/metadata/v4_balanced_core_shortlist.md` for the final quota-balanced **39-task** core shortlist. This final shortlist replaces the earlier provisional core flag: it caps protection/microgrid-heavy areas and promotes gap-fill tasks for markets, FLISR/restoration, contingency analysis, power quality, grid-code/FRT, and OT cybersecurity.
