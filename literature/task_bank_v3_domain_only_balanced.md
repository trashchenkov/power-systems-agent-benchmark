# Task bank v3 — domain-only reliable-source tasks

Scope: curated version of `task_bank_v2_reliable_source_mining.md` that excludes tasks whose primary provenance is another AI/LLM/agent benchmark. It keeps only primary power/energy-domain sources: textbooks, domain papers, engineering manuals, standards-like procedures, and method/case-study material.

## Source policy

Core tasks may come from:
- primary power-systems / energy textbooks and references;
- domain papers with a concrete system, calculation, experiment, control problem, or case study;
- engineering manuals / laboratory materials / standard-like procedures with objective checks;
- methodological material if the evaluator can be made numerical or rule-based.

Excluded from core:
- other AI/LLM/agent benchmarks and leaderboard papers;
- tasks whose main novelty is LLM evaluation rather than an energy-domain problem;
- tasks that require LLM-as-a-Judge as the main evaluator.

## Summary

- v2 candidates: **62**
- excluded benchmark-derived candidates: **1**
- v3 domain-only candidates: **61**
- balanced MVP/core shortlist: **37**

## Excluded from domain-only core

- `REL-TASK-062` — ElecBench security: refuse harmful dispatch/report manipulation: other benchmark / LLM benchmark meta-safety task, not primary energy-domain task. Keep only as related-work/background, not benchmark substrate.

## Coverage by subdomain

- **Converter-dominated grids & storage:** 4
- **Distribution reliability & outage management:** 4
- **Distribution systems & DER/EV:** 5
- **Energy economics, planning & policy:** 4
- **Energy systems beyond electricity / heating:** 3
- **Forecasting & uncertainty:** 6
- **Grid operations & control / MAS:** 2
- **Grid operations & control / restoration:** 2
- **Market/dispatch planning & uncertainty:** 1
- **Microgrids & DER dispatch:** 7
- **Power flow, modelling & transmission analysis:** 2
- **Protection, faults & relay engineering:** 17
- **Stability & dynamics:** 2
- **Transmission operations & asset ratings:** 2

## Balanced core shortlist

### Converter-dominated grids & storage
- `REL-TASK-004` — BESS ancillary-service P/Q response under frequency/voltage disturbance
- `REL-TASK-006` — Large-scale PV remedial action after critical contingency
- `REL-TASK-007` — Minimum synchronous-machine share for high converter penetration

### Distribution reliability & outage management
- `REL-TASK-051` — FCI placement to reduce patrol time
- `REL-TASK-052` — Faulted-section localization using FCI states and outage complaints
- `REL-TASK-053` — SAIDI/CAIDI impact of FCI deployment

### Distribution systems & DER/EV
- `REL-TASK-017` — EV/V2G voltage support after feeder reconfiguration
- `REL-TASK-018` — Centralized charging-station siting and sizing for V2G support
- `REL-TASK-020` — EV/V2G outage schedule under uncertain event time and SoC
- `REL-TASK-021` — EN 50160 voltage-compliance check and mitigation

### Energy economics, planning & policy
- `REL-TASK-058` — Sobol sensitivity of PV soft-cost inputs
- `REL-TASK-059` — LCOE distribution for 2 MW commercial PV under soft-cost uncertainty
- `REL-TASK-061` — Extract probabilistic PV cost input distributions from document evidence

### Energy systems beyond electricity / heating
- `REL-TASK-055` — Electric boiler capacity sizing for building heat support
- `REL-TASK-056` — Stepwise electric-boiler control by return-water temperature

### Forecasting & uncertainty
- `REL-TASK-009` — Multi-step wind-power forecasting from history and textual context
- `REL-TASK-012` — Prediction intervals for wind generation

### Grid operations & control / MAS
- `REL-TASK-001` — MAS frequency regulation state classification and lead-station handover
- `REL-TASK-002` — MAS voltage-zone classification and neighbor-agent messaging

### Grid operations & control / restoration
- `REL-TASK-003` — Decentralized network restoration after short circuit
- `REL-TASK-050` — Operator breaker/load actions in one-line model

### Market/dispatch planning & uncertainty
- `REL-TASK-015` — Robust/scenario dispatch under renewable/load/outage/DLR uncertainty

### Microgrids & DER dispatch
- `REL-TASK-022` — Joint active/reactive dispatch in islanded microgrid
- `REL-TASK-023` — Reactive compensation to minimize active losses
- `REL-TASK-024` — Economic active-power dispatch in microgrid
- `REL-TASK-026` — Rolling 5-minute renewable microgrid dispatch with capability curves

### Power flow, modelling & transmission analysis
- `REL-TASK-046` — AC power-flow solve and violation diagnosis
- `REL-TASK-047` — Build Ybus from network data

### Protection, faults & relay engineering
- `REL-TASK-029` — Transformer differential vs downstream overcurrent fault classification
- `REL-TASK-033` — Three-phase short-circuit current calculation
- `REL-TASK-034` — Unsymmetrical and earth-fault calculation
- `REL-TASK-036` — Line overcurrent protection settings
- `REL-TASK-039` — Distance protection settings for 35–330 kV lines
- `REL-TASK-045` — Short-circuit currents for breaker and relay settings

### Stability & dynamics
- `REL-TASK-008` — Transient stability prediction with high wind penetration
- `REL-TASK-048` — Transient stability and critical clearing time

### Transmission operations & asset ratings
- `REL-TASK-014` — Dynamic/real-time thermal rating of overhead lines

## Full domain-only task list

## Grid operations & control / MAS

### REL-TASK-001 — MAS frequency regulation state classification and lead-station handover
- **Subdomain:** Grid operations & control / MAS
- **Balanced shortlist:** yes
- **Source:** `Active-Power-Distribution-Networks-with-Decentralized-Multi-Agent-Control-Mode-Part-1_57afd120.txt`, PDF pp. 6–7, lines 430–436, 438–665, 667–686.
- **Evidence:** source defines frequency/power regulation state classes and rules such as stopping ineffective secondary regulation after more than two ticks.
- **Operational problem:** classify the current frequency-control state and decide whether to continue secondary regulation, block a station, hand over lead-station function, or request generation up/down.
- **Input:** `f(t)`, `Δf`, nominal frequency, secondary-control zone, ranked stations, failed/ineffective regulation flags by tick.
- **Output/action:** state class 1–11 plus control command.
- **Evaluator:** deterministic finite-state rule checker; penalties for unsafe handover and delayed reserve restoration.
- **Substrate:** custom discrete-event / time-series simulator.
- **Confidence:** strong.

### REL-TASK-002 — MAS voltage-zone classification and neighbor-agent messaging
- **Subdomain:** Grid operations & control / MAS
- **Balanced shortlist:** yes
- **Source:** same, PDF pp. 9–12, lines 800–806, 812–863, 867–940, 1009–1053.
- **Evidence:** source defines voltage-state classes and rules for changing reactive-power/tap setpoints and sending allow/deny/help messages to neighboring agents.
- **Operational problem:** local agent selects OLTC/Q-compensation action and coordination message based on area voltages and neighbor states.
- **Input:** controlled-node voltages, `Umin/Umax`, current tap/Q setpoint, regulation range, neighbor-zone states.
- **Output/action:** voltage class 1–7, setpoint up/down/hold, message: raise/lower/help/deny.
- **Evaluator:** AC load flow after each action; score violation removal, loss reduction, no worsening of neighboring zones, protocol correctness.
- **Substrate:** pandapower/OpenDSS with multi-agent message wrapper.
- **Confidence:** strong.

## Grid operations & control / restoration

### REL-TASK-003 — Decentralized network restoration after short circuit
- **Subdomain:** Grid operations & control / restoration
- **Balanced shortlist:** yes
- **Source:** same, PDF pp. 18–22, lines 1574–1683, 1703–1752, 1853–1865, 1991–2005.
- **Evidence:** source describes decentralized assembly of network islands up to synchronization sections, breaker close distribution by time quanta, and `f/U` scanning.
- **Operational problem:** after fault isolation and islanding, choose a safe breaker-closing sequence and synchronization parameters.
- **Input:** graph with breakers, disconnected sections, measured `U/f/phase`, slip/angle/voltage limits, switching time quanta.
- **Output/action:** ordered switching plan, scan parameters, close/hold decisions.
- **Evaluator:** discrete restoration simulator; check no asynchronous close, restoration time, restored load, unsafe close count.
- **Substrate:** networkx + synchronization checker + final pandapower AC state.
- **Confidence:** strong.

---

## B. Converter-dominated systems, BESS, PV, dynamic stability

## Converter-dominated grids & storage

### REL-TASK-004 — BESS ancillary-service P/Q response under frequency/voltage disturbance
- **Subdomain:** Converter-dominated grids & storage
- **Balanced shortlist:** yes
- **Source:** `...Modelling and Simu_867418d8.txt`, chapter 7, pp. 183–185, lines 7264–7359, 7401–7429.
- **Evidence:** source states BESS provides ancillary services; key metrics include RoCoF, frequency nadir, steady-state frequency; reactive capability supports severe voltage dips/FRT; SOC equation is given.
- **Operational problem:** set BESS active/reactive response policy under low-inertia disturbance, SOC and FRT constraints.
- **Input:** `f(t), V(t)`, BESS power/energy/SOC limits, converter Q capability, grid-code thresholds.
- **Output/action:** P/Q setpoints or controller parameters.
- **Evaluator:** dynamic surrogate; score RoCoF, nadir, steady-state frequency, voltage recovery, SOC bounds, throughput.
- **Substrate:** ANDES/OpenModelica simplified BESS model or custom ODE surrogate.
- **Confidence:** strong.

### REL-TASK-005 — SOC estimation for operational BESS commitments
- **Subdomain:** Converter-dominated grids & storage
- **Balanced shortlist:** no
- **Source:** same, pp. 184–185, lines 7308–7318, 7401–7429.
- **Evidence:** SOC depends on current and capacity; Coulomb-counting formula is provided.
- **Operational problem:** estimate SOC trajectory and remaining support window from current measurements.
- **Input:** initial SOC, current time series, cell capacity, sign convention, optional OCV/SOC table.
- **Output/action:** SOC trajectory, violation flags, admissible support duration.
- **Evaluator:** numerical integration reference; hidden traces with noise/sign-convention traps.
- **Substrate:** Python formula evaluator.
- **Confidence:** strong.

### REL-TASK-006 — Large-scale PV remedial action after critical contingency
- **Subdomain:** Converter-dominated grids & storage
- **Balanced shortlist:** yes
- **Source:** same, chapter 2, pp. 46–49, lines 1318–1354, 1455–1478.
- **Evidence:** source says LS-PVPP should participate in system stability, changing active/reactive generation after critical contingency to maintain voltage/frequency stability.
- **Operational problem:** select P/Q change of large PV plant after N-1/N-k event.
- **Input:** contingency, PV capability curve, local/WAMS measurements, current P/Q, voltage/frequency limits.
- **Output/action:** remedial P/Q command.
- **Evaluator:** dynamic or AC time-series; score voltage/frequency recovery, converter current limits, curtailed energy, delay.
- **Substrate:** pandapower + dynamic surrogate; PowerFactory optional.
- **Confidence:** strong.

### REL-TASK-007 — Minimum synchronous-machine share for high converter penetration
- **Subdomain:** Converter-dominated grids & storage
- **Balanced shortlist:** yes
- **Source:** same, contents lines 175–179, chapter 8 pp. 207–209, lines 8425–8466, 8528–8537.
- **Evidence:** source asks to determine minimum share of conventional synchronous generators; scenario includes 98% converter-based generation, primary control with 2% reserve, maximum rate of power change.
- **Operational problem:** decide whether a converter-heavy system remains stable and recommend minimum synchronous share/controller mode.
- **Input:** test-system summary, converter-generation share, SG locations, PI/DVC/GFM mode, disturbance, reserve.
- **Output/action:** stable/unstable verdict, minimum SG share, controller-mode recommendation.
- **Evaluator:** dynamic simulations or surrogate classifier; false-stable heavily penalized.
- **Substrate:** ANDES/PowerFactory-derived surrogate; PST-17-like case.
- **Confidence:** strong.

## Stability & dynamics

### REL-TASK-008 — Transient stability prediction with high wind penetration
- **Subdomain:** Stability & dynamics
- **Balanced shortlist:** yes
- **Source:** `Advanced Prediction Techniques Applied to Smart Grids_1f598a10.txt`, lines 756–758, 792–797, 894–910.
- **Evidence:** source gives example “Transient Stability Prediction of Power Systems With High Wind Power Penetration”; features before/during/post fault include voltage, rotor speed; stability index is calculated.
- **Operational problem:** classify post-fault stability and/or estimate stability index.
- **Input:** voltage/rotor-speed traces, fault duration/location, wind penetration scenario.
- **Output/action:** stable/unstable label, SI estimate, optional emergency recommendation.
- **Evaluator:** accuracy/F1/AUROC for classification; MAE for SI; false-stable penalty.
- **Substrate:** synthetic dynamic dataset from ANDES/GridDyn/PowerFactory exports.
- **Confidence:** strong.

---

## C. Forecasting, uncertainty, dynamic line rating, dispatch under uncertainty

## Forecasting & uncertainty

### REL-TASK-009 — Multi-step wind-power forecasting from history and textual context
- **Subdomain:** Forecasting & uncertainty
- **Balanced shortlist:** yes
- **Source:** `LoRA-Finetuned-LLM-for-Multi-Step-Wind-Power-Forecasting_6ae0bbbf.txt`, pp. 1–2, lines 8–30, 141–215.
- **Evidence:** source states goal is forecasting wind power over next `T_out` steps from historical wind-power data and textual auxiliary representations.
- **Input:** historical window `T_in`, task description/statistical descriptors, metadata/weather if available.
- **Output:** forecast array `Y_{t+1...t+T_out}`.
- **Evaluator:** held-out series; MAE/RMSE/MAPE by horizon; strict format/unit checks.
- **Substrate:** Python time-series harness.
- **Confidence:** strong.

### REL-TASK-010 — Variable-horizon wind forecast
- **Subdomain:** Forecasting & uncertainty
- **Balanced shortlist:** no
- **Source:** same, lines 216–238.
- **Evidence:** fine-tuned LLM acts as flexible predictor for varying horizons.
- **Operational problem:** accept arbitrary requested horizon and output exactly that many forecast steps.
- **Input:** history, horizon `{6,12,24,48}`, sampling frequency.
- **Output:** forecast vector of length `T_out` with units/metadata.
- **Evaluator:** hidden horizons; length validation and MAE/RMSE per horizon versus seasonal baseline.
- **Substrate:** Python forecast benchmark.
- **Confidence:** strong.

### REL-TASK-011 — Wind-series preprocessing before forecasting
- **Subdomain:** Forecasting & uncertainty
- **Balanced shortlist:** no
- **Source:** same, lines 217–230.
- **Evidence:** source mentions min–max normalization, outlier removal, missing-value imputation.
- **Operational problem:** clean and normalize wind-generation CSV without leakage.
- **Input:** series with missing points/outliers/physical limits and train/test split.
- **Output:** cleaned normalized dataset and imputation/removal log.
- **Evaluator:** hidden clean ground truth; imputation error, leakage checks.
- **Substrate:** pandas/sklearn.
- **Confidence:** strong.

### REL-TASK-012 — Prediction intervals for wind generation
- **Subdomain:** Forecasting & uncertainty
- **Balanced shortlist:** yes
- **Source:** `Advanced Prediction Techniques...`, pp. 27–28, lines 603–633.
- **Evidence:** PI criteria: sharpness = average PI width; reliability = sample coverage; source reports reliable/sharp PIs.
- **Operational problem:** produce calibrated interval forecast for wind power.
- **Input:** historical wind series, point forecasts/residuals, target coverage 90/95%.
- **Output:** lower/upper PI per future step.
- **Evaluator:** PICP/coverage, PINAW/width, Winkler score; reject if coverage below threshold.
- **Substrate:** probabilistic forecasting harness.
- **Confidence:** strong.

### REL-TASK-013 — EEMD/chaotic smoothing multi-step short-term wind forecast
- **Subdomain:** Forecasting & uncertainty
- **Balanced shortlist:** no
- **Source:** same, p. 26, lines 562–597.
- **Evidence:** source describes multi-step short-term wind prediction using EEMD, chaotic time-series analysis, MSSSA.
- **Operational problem:** improve short-term forecast of chaotic wind-power series.
- **Input:** 10-minute samples, 1-hour/multi-step horizon, noisy series.
- **Output:** forecast and optional decomposition/smoothing choices.
- **Evaluator:** MAE/RMSE vs persistence/commercial baseline; no future-data leakage.
- **Substrate:** PyEMD/SSA optional.
- **Confidence:** strong.

## Transmission operations & asset ratings

### REL-TASK-014 — Dynamic/real-time thermal rating of overhead lines
- **Subdomain:** Transmission operations & asset ratings
- **Balanced shortlist:** yes
- **Source:** same, pp. 29–30, lines 639–671.
- **Evidence:** “Real-time Thermal Rating (Overhead Lines)”; factors include solar radiation, wind speed/direction, ambient temperature; goals include relieving congestion and lowering risk.
- **Operational problem:** compute allowed line current/MVA under weather conditions.
- **Input:** conductor parameters, ambient temp, wind speed/direction, solar radiation, current load.
- **Output/action:** RTTR ampacity/MVA and congestion flag/action.
- **Evaluator:** IEEE/CIGRE heat-balance reference; unsafe overrating hard penalty.
- **Substrate:** Python thermal-rating calculator + pandapower line-limit update.
- **Confidence:** strong.

## Market/dispatch planning & uncertainty

### REL-TASK-015 — Robust/scenario dispatch under renewable/load/outage/DLR uncertainty
- **Subdomain:** Market/dispatch planning & uncertainty
- **Balanced shortlist:** yes
- **Source:** same, pp. 19–20, lines 384–425.
- **Evidence:** source lists uncertainties: RES, load, dynamic line rating, line/generator outage, fuel/price/market; scenario and robust optimization.
- **Operational problem:** choose dispatch/reserve plan under uncertainty.
- **Input:** network case, scenarios/distributions, generator costs/limits, outages, DLR uncertainty.
- **Output/action:** dispatch + reserves + robust-feasibility rationale.
- **Evaluator:** hidden scenario replay; expected cost, worst-case violation, reserve shortfall, load shedding, overload.
- **Substrate:** PyPSA/pandapower OPF harness.
- **Confidence:** strong.

## Forecasting & uncertainty

### REL-TASK-016 — Load/state forecasting as sequence task
- **Subdomain:** Forecasting & uncertainty
- **Balanced shortlist:** no
- **Source:** same, lines 369–372.
- **Evidence:** applications include short/long-term wind prediction, load forecasting, power-system state forecasting.
- **Operational problem:** forecast load or state vector.
- **Input:** historical load/state, calendar/weather features, horizon.
- **Output:** load or state-vector forecast.
- **Evaluator:** MAE/RMSE/sMAPE plus downstream reserve/dispatch penalty.
- **Substrate:** Python time-series benchmark.
- **Confidence:** medium.

---

## D. EV/V2G and outage support

## Distribution systems & DER/EV

### REL-TASK-017 — EV/V2G voltage support after feeder reconfiguration
- **Subdomain:** Distribution systems & DER/EV
- **Balanced shortlist:** yes
- **Source:** `TheRoleofElectricalVehicles...dfd6cf96.txt`, pp. 2–3, lines 141–183.
- **Evidence:** source observes voltage drops exceeding limits after outage/reconfiguration; EV battery infeed can improve voltage profile.
- **Operational problem:** select EV injections to remove undervoltage and avoid overloads.
- **Input:** feeder model, emergency switched configuration, EV locations, P/SoC limits, voltage 0.9–1.1 pu, line ratings.
- **Output/action:** EV/charger P-infeed schedule and constraints fixed.
- **Evaluator:** AC/quasi-dynamic PF; min voltage ≥0.9, loading ≤100%, EV limits.
- **Substrate:** pandapower/OpenDSS.
- **Confidence:** strong.

### REL-TASK-018 — Centralized charging-station siting and sizing for V2G support
- **Subdomain:** Distribution systems & DER/EV
- **Balanced shortlist:** yes
- **Source:** same, p. 3, lines 191–233.
- **Evidence:** source compares charging-station locations and required infeed: examples 80, 100, 170 kW.
- **Operational problem:** choose bus and minimum centralized V2G power to restore voltage.
- **Input:** candidate buses, 420 kW peak load, emergency mode, station P bounds.
- **Output/action:** selected node and power with expected voltage margin.
- **Evaluator:** exhaustive/OPF baseline; penalties for excess power and voltage violations.
- **Substrate:** pandapower AC PF + discrete siting optimization.
- **Confidence:** strong.

### REL-TASK-019 — Distributed individual-EV support selection
- **Subdomain:** Distribution systems & DER/EV
- **Balanced shortlist:** no
- **Source:** same, pp. 3–4, lines 234–296.
- **Evidence:** source simulates 8–10 individual EVs, 6.6–10 kW types, every 8–10th customer owning EV.
- **Operational problem:** choose which individual EVs to activate and at what power.
- **Input:** EV list by bus, charger ratings, SoC, load profile.
- **Output/action:** distributed EV dispatch by bus/time.
- **Evaluator:** violation-hours, EV energy, fairness/number of activated EVs.
- **Substrate:** OpenDSS/pandapower time series.
- **Confidence:** strong.

### REL-TASK-020 — EV/V2G outage schedule under uncertain event time and SoC
- **Subdomain:** Distribution systems & DER/EV
- **Balanced shortlist:** yes
- **Source:** same, p. 4, lines 297–321.
- **Evidence:** source notes accident time affects support; SoC may be low; grid needs 3 hours and ~120 kWh.
- **Operational problem:** plan 3-hour EV discharge under SoC/availability constraints.
- **Input:** EV arrival/availability, initial SoC, min SoC contracts, outage start, load profile, feeder constraints.
- **Output/action:** time-indexed EV P schedule; excluded EVs.
- **Evaluator:** replay different outage starts; score unserved load/violations/degradation proxy.
- **Substrate:** pandapower + MILP/heuristic controller.
- **Confidence:** strong.

### REL-TASK-021 — EN 50160 voltage-compliance check and mitigation
- **Subdomain:** Distribution systems & DER/EV
- **Balanced shortlist:** yes
- **Source:** same, p. 1, lines 96–104.
- **Evidence:** EN 50160 requires voltage between 90% and 110% for 95% of supplied time.
- **Operational problem:** evaluate compliance and propose corrective actions.
- **Input:** voltage traces, nominal voltage, possible EV/OLTC/reconfiguration actions.
- **Output/action:** compliance report + mitigation plan.
- **Evaluator:** compute share of time outside limits; pass if ≥95% compliant time.
- **Substrate:** pandas + PF trace evaluator.
- **Confidence:** strong.

---

## E. Microgrid P/Q dispatch and optimization

## Microgrids & DER dispatch

### REL-TASK-022 — Joint active/reactive dispatch in islanded microgrid
- **Subdomain:** Microgrids & DER dispatch
- **Balanced shortlist:** yes
- **Source:** `fmincon_78640f47.txt`, lines 57–65.
- **Evidence:** source describes distributed strategy for joint active/reactive dispatch in isolated microgrids to reduce losses, improve voltages, minimize generation cost.
- **Input:** topology, DG cost/limits, load, voltage bounds, renewables, communication graph.
- **Output/action:** P/Q setpoints for each DG.
- **Evaluator:** independent AC PF + OPF baseline; cost/loss/voltage penalties.
- **Substrate:** pandapower/PyPSA + scipy/Ipopt baseline.
- **Confidence:** strong.

### REL-TASK-023 — Reactive compensation to minimize active losses
- **Subdomain:** Microgrids & DER dispatch
- **Balanced shortlist:** yes
- **Source:** same, lines 700–842.
- **Evidence:** reactive compensation minimizes active-power losses subject to voltage and DG Q limits.
- **Input:** bus voltages/angles, line conductance/susceptance, Q demand, DG Q capability.
- **Output/action:** Q dispatch and expected losses.
- **Evaluator:** AC PF and OPF optimum gap; hard fail for V/Q limit violations.
- **Substrate:** pandapower AC OPF/custom nonlinear evaluator.
- **Confidence:** strong.

### REL-TASK-024 — Economic active-power dispatch in microgrid
- **Subdomain:** Microgrids & DER dispatch
- **Balanced shortlist:** yes
- **Source:** same, lines 853–946.
- **Evidence:** minimize quadratic generation costs with demand+loss balance and P limits.
- **Input:** cost coefficients, Pmin/Pmax, demand, loss estimate, renewable availability.
- **Output/action:** generator active powers.
- **Evaluator:** QP/OPF baseline; objective regret and balance residual.
- **Substrate:** scipy/cvxpy/pandapower.
- **Confidence:** strong.

### REL-TASK-025 — Distributed dispatch with local-only information and communication graph
- **Subdomain:** Microgrids & DER dispatch
- **Balanced shortlist:** no
- **Source:** same, lines 947–957, 1114–1117.
- **Evidence:** graph nodes are DG buses; arcs are communication channels; local information only.
- **Input:** local observations, communication graph, neighbor messages, local constraints.
- **Output/action:** message-passing policy or final local setpoints.
- **Evaluator:** restrict observation API; compare feasibility/cost to centralized optimum; penalize forbidden global-data use.
- **Substrate:** multi-agent gym + pandapower.
- **Confidence:** strong.

### REL-TASK-026 — Rolling 5-minute renewable microgrid dispatch with capability curves
- **Subdomain:** Microgrids & DER dispatch
- **Balanced shortlist:** yes
- **Source:** same, lines 2235–2263, 2272–2328.
- **Evidence:** daily irradiance/wind profiles sampled every 5 minutes; reactive power limited by capability curve; dispatch periods of 5 minutes.
- **Input:** 5-min solar/wind/load profiles, inverter S ratings, PF/capability curve, previous setpoints.
- **Output/action:** rolling P/Q schedule.
- **Evaluator:** time-series AC PF; violations, cost, ramping, curtailment; hard fail outside capability curve.
- **Substrate:** pandapower time-series.
- **Confidence:** strong.

### REL-TASK-027 — Co-simulation controller loop for microgrid dispatch
- **Subdomain:** Microgrids & DER dispatch
- **Balanced shortlist:** no
- **Source:** same, lines 2264–2277.
- **Evidence:** Matlab-DIgSILENT loop: load flow → measurements to optimizer → setpoints back → repeat each 5 min.
- **Input:** simulator API, horizon, measurement fields.
- **Output/action:** executable controller loop/config and dispatch logs.
- **Evaluator:** mocked simulator integration test; API-call sequence, convergence, interval feasibility.
- **Substrate:** pandapower-as-simulator + Python controller harness.
- **Confidence:** medium-strong.

### REL-TASK-028 — Worst-case DG limit sizing by sensitivity sweep
- **Subdomain:** Microgrids & DER dispatch
- **Balanced shortlist:** no
- **Source:** same, lines 2220–2230.
- **Evidence:** power limits established from worst-case scenario using PF and sensitivity evaluation in DIgSILENT.
- **Input:** candidate DG capacities/locations, worst-case load/renewables, voltage/line constraints.
- **Output/action:** derated safe operating limits per DG.
- **Evaluator:** hidden worst-case scenarios; feasibility and retained utilization.
- **Substrate:** pandapower scenario sweep.
- **Confidence:** medium.

---

## F. Protection, relay labs, short-circuit, restoration calculations

## Protection, faults & relay engineering

### REL-TASK-029 — Transformer differential vs downstream overcurrent fault classification
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** yes
- **Source:** `development-of-laboratory-experiments...450a8562.txt`, pp. 4–5, lines 199–223, 235–250.
- **Evidence:** symmetrical components, differential protection for transformer winding faults, phase/negative-sequence inverse-time overcurrent downstream.
- **Input:** transformer connection, CT convention, phase currents, negative sequence, differential/restraint settings.
- **Output/action:** differential trip/no-trip, backup trip time, breaker.
- **Evaluator:** relay characteristic + symmetrical components; missed internal and false differential trip penalties.
- **Substrate:** formula-based protection simulator.
- **Confidence:** strong.

### REL-TASK-030 — Motor locked-rotor and definite-time overcurrent protection
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, p. 5, lines 251–275.
- **Evidence:** SEL-710 locked-rotor and definite-time overcurrent; current rises as torque increases to locked-rotor.
- **Input:** motor FLA, torque/current trace, definite-time settings, locked-rotor thresholds/delays.
- **Output/action:** trip/no-trip, cause, trip time.
- **Evaluator:** relay automaton; no false trip during allowed high-torque, trip locked rotor.
- **Substrate:** discrete relay simulator.
- **Confidence:** strong.

### REL-TASK-031 — Distance/impedance protection zone setting
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, pp. 5–6, lines 255–282.
- **Evidence:** SEL-311L impedance protection; characterize line and implement protection zones by perceived line length.
- **Input:** line R/X/length, CT/PT ratios, apparent impedance samples, reach/delay policy.
- **Output/action:** zone 1/2/3 reaches, delays, trip zone per fault.
- **Evaluator:** impedance-plane checker with hidden faults and load encroachment.
- **Substrate:** formula impedance evaluator.
- **Confidence:** strong.

### REL-TASK-032 — Relay coordination with synchronized event records
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, pp. 5–6, lines 284–297.
- **Evidence:** communications processor, IRIG-B time-stamping, time-dial setting for backup protection and minimizing affected areas.
- **Input:** feeder, fault-current table, relay curves, CTI, time-stamped event records.
- **Output/action:** time-dial settings, primary/backup order, miscoordination diagnosis.
- **Evaluator:** inverse-time curves + event-log alignment; CTI violations and affected area.
- **Substrate:** protection curve simulator.
- **Confidence:** strong.

### REL-TASK-033 — Three-phase short-circuit current calculation
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** yes
- **Source:** `РЕЛЕЙНАЯ ЗАЩИТА...bed306ea.txt`, lines 47–62, 106–114, 511–521.
- **Evidence:** text covers initial subtransient and steady-state currents for symmetrical three-phase faults.
- **Input:** single-line diagram, generator `xd''`, transformer impedances, voltage bases, fault bus.
- **Output/action:** per-unit and physical fault currents by element.
- **Evaluator:** symmetrical short-circuit solver tolerance.
- **Substrate:** Python fault solver / pandapower shortcircuit.
- **Confidence:** strong.

### REL-TASK-034 — Unsymmetrical and earth-fault calculation
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** yes
- **Source:** same, lines 47–60, 523–540.
- **Evidence:** source covers unsymmetrical short circuits and single-phase earth faults.
- **Input:** positive/negative/zero sequence impedances, grounding, fault resistance/location.
- **Output/action:** sequence currents/voltages and phase quantities.
- **Evaluator:** sequence-network equations; numeric tolerance and correct topology.
- **Substrate:** custom symmetrical-components solver.
- **Confidence:** strong.

### REL-TASK-035 — CT/VT selection for relay protection
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, lines 68–70, 541–547; references lines 290–321.
- **Evidence:** tasks on current and voltage transformers in protection devices.
- **Input:** CT/VT ratings, burden, relay pickup, max/min fault currents, operating current.
- **Output/action:** pass/fail and recommended ratio/class.
- **Evaluator:** ratio, secondary current, burden, saturation margin rules.
- **Substrate:** Python rule engine.
- **Confidence:** medium-strong.

### REL-TASK-036 — Line overcurrent protection settings
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** yes
- **Source:** same, lines 548–558.
- **Evidence:** non-directional/directional maximum current protections, cutoffs, line protections.
- **Input:** load current, max/min fault currents, downstream settings, CT ratio, sensitivity/selectivity coefficients.
- **Output/action:** pickup, time delay/curve, sensitivity, coordination report.
- **Evaluator:** pickup > max load, operate for min fault, selectivity margin.
- **Substrate:** relay coordination evaluator.
- **Confidence:** strong.

### REL-TASK-037 — Zero-sequence / earth-fault protection settings
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, lines 559–568.
- **Evidence:** zero-sequence current protection in networks with high/low earth-fault current.
- **Input:** zero-sequence currents, grounding mode, capacitive current, directionality, feeder topology.
- **Output/action:** 3I0 pickup, directional element, delays/stages.
- **Evaluator:** internal/external earth faults; sensitivity/selectivity/no healthy-feeder trip.
- **Substrate:** sequence-network simulator.
- **Confidence:** strong.

### REL-TASK-038 — Line differential protection
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, lines 573–581.
- **Evidence:** longitudinal/transverse differential line protection and parallel-line directional differential protection.
- **Input:** CT ratios/errors, end currents, pilot channel, internal/external fault cases.
- **Output/action:** differential/restraint thresholds, trip/block decision.
- **Evaluator:** internal/external confusion matrix; hard fail external through-fault trip.
- **Substrate:** relay logic simulator.
- **Confidence:** strong.

### REL-TASK-039 — Distance protection settings for 35–330 kV lines
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** yes
- **Source:** same, lines 582–584; refs 367–370.
- **Input:** line positive-sequence impedance, adjacent-line data, load encroachment, fault locations, CT/PT ratios.
- **Output/action:** zones 1/2/3, delays, trip/block.
- **Evaluator:** impedance-plane cases and selectivity margins.
- **Substrate:** mho/quadrilateral distance relay simulator.
- **Confidence:** strong.

### REL-TASK-040 — Transformer/autotransformer protection settings
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, lines 591–597.
- **Input:** transformer rating/vector group/impedance, CT ratios, inrush/blocking assumptions, HV/LV fault currents.
- **Output/action:** overcurrent/differential settings and trip logic.
- **Evaluator:** internal winding, external through-fault, inrush scenarios.
- **Substrate:** transformer relay logic + fault solver.
- **Confidence:** strong.

### REL-TASK-041 — Generator and generator-transformer block protection
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, lines 589–611.
- **Input:** generator MVA/kV, grounding, transformer data, CT/VT, fault scenarios.
- **Output/action:** protection functions and settings.
- **Evaluator:** protection coverage matrix + simulated internal/external faults.
- **Substrate:** rules + sequence-fault simulator.
- **Confidence:** medium-strong.

### REL-TASK-042 — HV motor protection settings
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, lines 612–615.
- **Input:** motor rating, starting current/time, thermal limits, CT ratio, fault currents.
- **Output/action:** overload, short-circuit, earth-fault, locked-rotor/start settings.
- **Evaluator:** start vs fault traces; no false trip during allowed start, trip fault/locked rotor.
- **Substrate:** motor thermal/relay curve simulator.
- **Confidence:** medium.

### REL-TASK-043 — Busbar differential protection
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, lines 617–618.
- **Input:** bus topology, feeder currents, CT classes/errors, fault cases.
- **Output/action:** zone trip decision and differential/restraint settings.
- **Evaluator:** internal bus fault trips all connected breakers; external faults restrain.
- **Substrate:** relay logic simulator.
- **Confidence:** medium.

### REL-TASK-044 — AC/rectified auxiliary trip supply feasibility
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** no
- **Source:** same, lines 119–150, 619–628.
- **Evidence:** protection on AC/rectified operating current for 6–10 kV networks with direct-acting relays RTM/RTV.
- **Input:** substation voltage, trip-coil demand, CT/VT/aux transformer data, relay type.
- **Output/action:** auxiliary supply scheme and trip feasibility report.
- **Evaluator:** available secondary power/voltage/current ≥ trip-coil need under min fault/voltage.
- **Substrate:** electrical sizing calculator.
- **Confidence:** medium-strong.

### REL-TASK-045 — Short-circuit currents for breaker and relay settings
- **Subdomain:** Protection, faults & relay engineering
- **Balanced shortlist:** yes
- **Source:** `Power System Analysis and Design_030246bc.txt`, lines 2522–2527.
- **Evidence:** short-circuit programs compute 3-phase and line-to-ground faults, select breakers, determine relay settings, min/max fault currents.
- **Input:** network sequence data, equipment ratings, outage states, fault types/locations.
- **Output/action:** fault-current table, breaker adequacy, relay pickup recommendations.
- **Evaluator:** IEC/ANSI short-circuit reference; breaker rating ≥ max fault and sensitivity at min fault.
- **Substrate:** pandapower shortcircuit/OpenDSS/custom symmetrical components.
- **Confidence:** strong.

---

## G. Power-flow, stability, operator action, modelling primitives

## Power flow, modelling & transmission analysis

### REL-TASK-046 — AC power-flow solve and violation diagnosis
- **Subdomain:** Power flow, modelling & transmission analysis
- **Balanced shortlist:** yes
- **Source:** `Power System Analysis and Design_030246bc.txt`, lines 2502–2512.
- **Evidence:** power-flow programs compute voltage magnitudes/angles and line flows; variables include transformer taps and generator reactive outputs.
- **Input:** MATPOWER/pandapower case, limits, controllable taps/Q/generation.
- **Output/action:** voltages, angles, branch flows, violations, corrective actions.
- **Evaluator:** independent AC PF; numeric tolerances and action validation.
- **Substrate:** pandapower/MATPOWER.
- **Confidence:** strong.

### REL-TASK-047 — Build Ybus from network data
- **Subdomain:** Power flow, modelling & transmission analysis
- **Balanced shortlist:** yes
- **Source:** same, lines 4317–4403.
- **Evidence:** source defines bus admittance matrix diagonal/off-diagonal construction and computer input data.
- **Input:** buses, branch admittances, shunts, current injections/reference bus.
- **Output/action:** complex Ybus and voltage vector.
- **Evaluator:** exact matrix comparison and residual `||YV-I||`.
- **Substrate:** numpy/pandapower internal Ybus.
- **Confidence:** strong.

## Stability & dynamics

### REL-TASK-048 — Transient stability and critical clearing time
- **Subdomain:** Stability & dynamics
- **Balanced shortlist:** yes
- **Source:** same, lines 2513–2521.
- **Evidence:** stability programs decide whether synchronous machines remain in synchronism and compute critical clearing times.
- **Input:** generator dynamic params, pre-fault PF, fault location/type, clearing action.
- **Output/action:** stable/unstable, CCT, recommended clearing time.
- **Evaluator:** dynamic simulator/bisection baseline; CCT error and false-stable penalty.
- **Substrate:** ANDES/GridCal/swing-equation simulator.
- **Confidence:** strong.

## Transmission operations & asset ratings

### REL-TASK-049 — Transient overvoltage and surge arrester selection
- **Subdomain:** Transmission operations & asset ratings
- **Balanced shortlist:** no
- **Source:** same, lines 2528–2532.
- **Evidence:** transient programs compute overvoltages/currents to determine insulation and select surge arresters.
- **Input:** transient traces or equipment/line params, insulation classes, arrester catalog.
- **Output/action:** arrester rating and insulation margin.
- **Evaluator:** residual voltage below withstand; energy duty within arrester limit.
- **Substrate:** EMTP surrogate traces + rules.
- **Confidence:** medium.

## Grid operations & control / restoration

### REL-TASK-050 — Operator breaker/load actions in one-line model
- **Subdomain:** Grid operations & control / restoration
- **Balanced shortlist:** yes
- **Source:** same, lines 2615–2624.
- **Evidence:** source describes clicking breakers to isolate/restore load and voltage drop as load increases.
- **Input:** one-line graph, breaker states, generator/load/line impedance, target load.
- **Output/action:** breaker/load sequence to restore service while maintaining voltage.
- **Evaluator:** graph connectivity + PF; no energized faulted island, load served, voltage bounds.
- **Substrate:** small pandapower interactive environment.
- **Confidence:** medium-strong.

---

## H. Faulted circuit indicators and distribution reliability

## Distribution reliability & outage management

### REL-TASK-051 — FCI placement to reduce patrol time
- **Subdomain:** Distribution reliability & outage management
- **Balanced shortlist:** yes
- **Source:** `faulted-circuit-indicators-and-system-reliability_daefd9c5.txt`, pp. 1–2, lines 12–23, 46–57, 121–161.
- **Evidence:** FCIs reduce crew patrol time; placed where feeder bifurcates; patrol reduction 46%/80% scenarios.
- **Input:** radial feeder graph, line lengths, fault rates, candidate FCI nodes, budget K, crew start rule.
- **Output/action:** selected FCI locations and expected patrol reduction.
- **Evaluator:** graph simulation/Monte Carlo faults vs optimum/greedy baseline; budget strict.
- **Substrate:** NetworkX reliability simulator.
- **Confidence:** strong.

### REL-TASK-052 — Faulted-section localization using FCI states and outage complaints
- **Subdomain:** Distribution reliability & outage management
- **Balanced shortlist:** yes
- **Source:** same, lines 140–157, 150–154.
- **Evidence:** FCIs indicate fault-current direction and patrol direction; customer-reported outage start can reduce miles.
- **Input:** topology, FCI trip/no-trip, customer complaint location, switch/recloser status.
- **Output/action:** ranked fault sections and patrol/isolation route.
- **Evaluator:** hidden fault section; top-k accuracy and patrol miles until found.
- **Substrate:** graph search distribution outage simulator.
- **Confidence:** strong.

### REL-TASK-053 — SAIDI/CAIDI impact of FCI deployment
- **Subdomain:** Distribution reliability & outage management
- **Balanced shortlist:** yes
- **Source:** same, lines 83–103, 162–203.
- **Evidence:** source reports SAIDI/CAIDI analysis and outage-duration reductions; example SAIDI values.
- **Input:** fault rates, customers interrupted, baseline repair/patrol time, patrol reductions.
- **Output/action:** SAIDI/CAIDI before/after and percent improvement.
- **Evaluator:** deterministic formula checker with units/customer-year.
- **Substrate:** Python reliability-index calculator.
- **Confidence:** strong.

### REL-TASK-054 — FCI economic benefit calculation
- **Subdomain:** Distribution reliability & outage management
- **Balanced shortlist:** no
- **Source:** same, p. 3, lines 230–267.
- **Evidence:** source computes crew/truck cost, outages/year, hours saved, annual savings.
- **Input:** faults/mile/year, circuit miles, outage-duration reduction, crew hourly cost, customer outage cost.
- **Output/action:** annual crew-hours saved, utility savings, customer avoided-cost estimate.
- **Evaluator:** deterministic arithmetic and sensitivity cases.
- **Substrate:** Python calculator.
- **Confidence:** strong.

---

## I. Heating systems / district heating flexibility

## Energy systems beyond electricity / heating

### REL-TASK-055 — Electric boiler capacity sizing for building heat support
- **Subdomain:** Energy systems beyond electricity / heating
- **Balanced shortlist:** yes
- **Source:** `Enhancement_of_Building_Heating_Systems_Connected__062d9eb7.txt`, pp. 9–12, lines 500–528, 638–665.
- **Evidence:** capacity depends on building volume/purpose/design; case gives volume 8300 m3, heat demand 250 kW, indoor 25°C, deviation 5°C; 30 kW boiler sufficient.
- **Input:** building volume, heat demand, indoor/outdoor temps, supply temp deviation, envelope/thermal params.
- **Output/action:** required boiler capacity kW and feasibility.
- **Evaluator:** heat-balance model; numeric tolerance and comfort constraint.
- **Substrate:** thermal calculator / Modelica optional.
- **Confidence:** strong.

### REL-TASK-056 — Stepwise electric-boiler control by return-water temperature
- **Subdomain:** Energy systems beyond electricity / heating
- **Balanced shortlist:** yes
- **Source:** same, pp. 10–11, lines 539–586.
- **Evidence:** sequential heating stages; switch off if return temp exceeds setpoint by 5°C; activate next stage if decreases by 5°C.
- **Input:** return-water temperature time series, setpoint, stage capacities, delay timer, power limit.
- **Output/action:** stage on/off, valve/pump commands.
- **Evaluator:** thermal response; comfort error, switching count, energy, peak power.
- **Substrate:** discrete-time control simulator.
- **Confidence:** strong.

### REL-TASK-057 — Pre-emergency state diagnosis in building heat supply
- **Subdomain:** Energy systems beyond electricity / heating
- **Balanced shortlist:** no
- **Source:** same, pp. 11–12, lines 631–637, 656–657.
- **Evidence:** monitoring heat-transfer-medium parameters enables diagnosis of pre-emergency state and selection of control actions.
- **Input:** supply/return temp, flow, pressure, setpoints, weather, normal bands.
- **Output/action:** normal/pre-emergency/emergency label + action.
- **Evaluator:** labeled scenarios; F1 and action feasibility.
- **Substrate:** anomaly detection + thermal rule simulator.
- **Confidence:** medium-strong.

---

## J. PV soft-cost uncertainty and LCOE

## Energy economics, planning & policy

### REL-TASK-058 — Sobol sensitivity of PV soft-cost inputs
- **Subdomain:** Energy economics, planning & policy
- **Balanced shortlist:** yes
- **Source:** `quantifying-the-uncertainty...58e251ef.txt`, lines 16–21, 62–75, 316–332.
- **Evidence:** source quantifies uncertainty of three soft-cost inputs using variance-based/Sobol indices; CREST computes LCOE.
- **Input:** distributions for development cost, land lease, interconnection; LCOE model.
- **Output/action:** first/total-order Sobol indices and ranked drivers.
- **Evaluator:** reference UQ computation; index/ranking tolerance.
- **Substrate:** Python SALib/effective quadratures.
- **Confidence:** strong.

### REL-TASK-059 — LCOE distribution for 2 MW commercial PV under soft-cost uncertainty
- **Subdomain:** Energy economics, planning & policy
- **Balanced shortlist:** yes
- **Source:** same, lines 200–210, 322–328.
- **Evidence:** 2 MW California project; polynomial/linear LCOE expression with soft-cost terms.
- **Input:** project size/location, finance/tax assumptions, distributions for x1/x2/x3.
- **Output/action:** mean/P5/P50/P95 LCOE and exceedance probability.
- **Evaluator:** Monte Carlo reference distribution; quantile errors and formula check.
- **Substrate:** Python Monte Carlo financial model.
- **Confidence:** strong.

### REL-TASK-060 — Prioritize PV soft-cost reduction interventions
- **Subdomain:** Energy economics, planning & policy
- **Balanced shortlist:** no
- **Source:** same, lines 333–373.
- **Evidence:** development cost and fees are most important; land lease relatively unimportant; prioritize permitting/interconnection.
- **Input:** sensitivity ranking, intervention costs, achievable reductions.
- **Output/action:** intervention plan and expected LCOE reduction.
- **Evaluator:** hidden LCOE model; achieved reduction per budget; explanation alignment.
- **Substrate:** optimization over cost-reduction levers.
- **Confidence:** medium-strong.

### REL-TASK-061 — Extract probabilistic PV cost input distributions from document evidence
- **Subdomain:** Energy economics, planning & policy
- **Balanced shortlist:** yes
- **Source:** same, lines 211–226, 231–249, 263–274, 294–315.
- **Evidence:** source gives development-cost uniform range, land acres/MW normal distribution, interconnection uniform range.
- **Input:** textual cost evidence, 2 MW project, lease rate.
- **Output/action:** JSON distributions and derived formulas.
- **Evaluator:** schema validation and numeric bound check.
- **Substrate:** document-to-model extraction benchmark.
- **Confidence:** strong.

---

## K. Benchmark and safety/meta-operational tasks

## Coverage gaps and recommended additions

The current 61 domain-only tasks are strong but not yet evenly distributed. Protection and microgrid/control are overrepresented because the local archive contains rich protection textbooks/labs and microgrid dispatch material. For a balanced public benchmark, use quotas rather than raw availability.

- **Markets, unit commitment, reserves, adequacy:** Need more primary sources/cases for unit commitment, reserve procurement, economic dispatch with market constraints, adequacy/resource planning. Current material has dispatch/UQ but little market operation.
- **Distribution automation beyond EV/FCI:** Add capacitor/OLTC coordination, feeder reconfiguration, FLISR, hosting capacity, Volt-VAR optimization from distribution papers/manuals.
- **Transmission operations beyond PF/CCT:** Add contingency analysis, remedial action schemes, topology control, congestion management with objective AC/DC evaluators.
- **Asset management / maintenance:** Add transformer/cable/line condition assessment, thermal ageing, failure prediction, inspection prioritization.
- **Cybersecurity for OT/SCADA:** Avoid generic LLM safety benchmark tasks; add power-domain intrusion/anomaly detection or relay/SCADA bad-data cases from primary OT security datasets/papers.
- **Hydro, thermal generation, storage portfolio:** Add generation-specific tasks: hydro scheduling, thermal ramping/start constraints, storage arbitrage/degradation.
- **Power quality:** Add harmonics, flicker, unbalance, sag/swell diagnosis and mitigation. EV paper provides voltage compliance only.
- **Standards/grid codes:** Add tasks based on IEEE/IEC/GOST grid-code checks: interconnection compliance, FRT curves, protection selectivity requirements.

## Suggested balanced benchmark quotas

- **Power flow, modelling & transmission analysis:** target 3
- **Protection, faults & relay engineering:** target 4
- **Distribution systems & DER/EV:** target 3
- **Distribution reliability & outage management:** target 3
- **Microgrids & DER dispatch:** target 3
- **Forecasting & uncertainty:** target 3
- **Stability & dynamics / converter grids:** target 3
- **Grid operations & restoration / MAS:** target 3
- **Energy economics/planning/markets:** target 3
- **Energy systems beyond electricity / heating:** target 2
- **Power quality & standards:** target 2
- **Asset management / maintenance:** target 2
- **OT cybersecurity / bad data:** target 2

This gives a 35–40 task benchmark with no single subdomain dominating. Use the 37-task balanced shortlist above as the current seed, then replace/augment overrepresented protection/microgrid items as new primary sources are added.
