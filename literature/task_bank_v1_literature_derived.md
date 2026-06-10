# Task bank v1 — literature-derived candidates from full local archive pass

Scope: all downloaded documents found under `literature/local_archive_extracted/local_lit/power_engineering`.

Extraction run:
- Source docs discovered: 127 (`98` PDF, `29` DOCX)
- Text extracted successfully: 124
- Extracted text directory: `literature/extracted_text/all_local_archive/`
- Extraction report: `literature/metadata/all_local_archive_extraction_report.json`
- Keyword/snippet index: `literature/metadata/all_local_archive_task_snippets.json`
- Top snippet review file: `literature/metadata/all_local_archive_task_snippets_top80.md`

Principle: every candidate below is phrased as `source -> operational problem -> executable benchmark task`. Some are strong paper-derived tasks; some are weaker textbook/manual-derived exercises that need later pruning.

Confidence labels:
- **strong**: source directly describes a problem, experiment, objective, case study, or benchmark task.
- **medium**: source clearly covers the operational calculation/control family, but exact executable case must be constructed.
- **weak**: source is mainly background/manual/course material; usable as task inspiration, not as final provenance alone.

## A. Steady-state power flow, voltage, OPF and dispatch

### LIT-TASK-001 — AC load-flow solve and violation diagnosis

- **Source provenance:** `J. Duncan Glover, Thomas J. Overbye, Mulukutla S. Sarma - Power System Analysis and Design-Cengage Learning (2017).pdf`; extracted text ranked #2 by task-keyword score.
- **Source type:** textbook / standard analytical reference.
- **Derived operational problem:** solve AC load flow and identify bus voltage / branch limit violations.
- **Agent input:** network case, bus loads/generation, voltage limits, line/transformer ratings.
- **Agent output/action:** report violated constraints and propose feasible corrective action candidates.
- **Evaluator idea:** run AC power flow on hidden case; compare feasibility, violation magnitudes, and action cost.
- **Substrate:** pandapower / MATPOWER case conversion.
- **Priority:** high.
- **Confidence:** medium — strong domain basis, but not one paper experiment.

### LIT-TASK-002 — Voltage violation repair by tap/reactive control

- **Source provenance:** `PAPER_VICTOR-OTHfglV6.docx` and duplicate `(1)`; lines in extracted text mention IEEE 1547-2018 smart inverters, voltage regulation by reactive power, and assessment by losses and voltage profile. Example locator: `PAPER_VICTOR-OTHfglV6_cc1dd373.txt:23-43`.
- **Source type:** paper / manuscript.
- **Derived operational problem:** coordinate DER/smart-inverter reactive power to keep distribution/transmission interface voltages within limits.
- **Agent input:** TSO-DSO or feeder case, DER capability curves, voltage measurements, control modes.
- **Agent output/action:** inverter Q setpoints / Volt-VAR parameters / OLTC or capacitor actions.
- **Evaluator idea:** quasi-static AC time-series; score voltage violations, losses, action smoothness, DER capability violations.
- **Substrate:** pandapower time-series first; PowerFactory as source workflow.
- **Priority:** high.
- **Confidence:** strong.

### LIT-TASK-003 — Dispatch / OPF benchmark from ElecBench

- **Source provenance:** `ElecBench_a_Power_Dispatch_Evaluation_Benchmark_fo.pdf`; extracted text ranked #21; earlier first-mining selected it as dispatch benchmark anchor.
- **Source type:** benchmark paper.
- **Derived operational problem:** evaluate an agent on power dispatch decisions under constraints.
- **Agent input:** generator costs/limits, load, renewable forecasts, reserve constraints, network limits.
- **Agent output/action:** dispatch schedule and reserves.
- **Evaluator idea:** compute OPF/economic-dispatch feasibility and cost regret against solver baseline; hidden load/renewable realizations.
- **Substrate:** pandapower OPF / PyPSA / MATPOWER-style DC/AC OPF.
- **Priority:** high.
- **Confidence:** strong.

### LIT-TASK-004 — Economic dispatch with renewable forecast uncertainty

- **Source provenance:** `Advanced Prediction Techniques Applied to Smart Grids.pdf`; extracted text ranked #3 and previous v0 linked it to smart-grid forecasting and dispatch.
- **Source type:** book / technical reference.
- **Derived operational problem:** decide generation and reserve schedule when load/renewable forecast is uncertain.
- **Agent input:** historical load/weather/generation, forecast intervals, generator and reserve limits.
- **Agent output/action:** dispatch + reserve plan.
- **Evaluator idea:** hidden realization replay; score production cost, reserve shortfall, curtailment, power-flow infeasibility.
- **Substrate:** PyPSA or pandapower + custom uncertainty sampler.
- **Priority:** high.
- **Confidence:** medium.

### LIT-TASK-005 — OPF problem formulation / constrained optimization

- **Source provenance:** `fmincon.pdf` and broader OPF/load-flow corpus; `fmincon.pdf` ranked #28 by optimization/task terms.
- **Source type:** method/example document.
- **Derived operational problem:** formulate and solve constrained OPF/control parameter optimization.
- **Agent input:** objective terms, bounds, network constraints, candidate control variables.
- **Agent output/action:** feasible decision vector and rationale.
- **Evaluator idea:** independent solver computes feasibility and objective gap.
- **Substrate:** scipy/pandapower OPF.
- **Priority:** medium.
- **Confidence:** medium.

### LIT-TASK-006 — N-1 contingency screening and corrective mitigation

- **Source provenance:** standard power-system analysis corpus (`Power System Analysis and Design`, PowerFactory manuals) plus benchmark design note.
- **Source type:** textbook/manual/benchmark design.
- **Derived operational problem:** rank contingencies and propose mitigation for post-contingency overload/voltage violations.
- **Agent input:** base network, list of outages, allowed redispatch/topology/tap actions.
- **Agent output/action:** critical contingency ranking and preventive/corrective action plan.
- **Evaluator idea:** loop over hidden outages and run AC power flow; score missed critical cases, false-safe decisions, mitigation cost.
- **Substrate:** pandapower contingency loop; Grid2Op later.
- **Priority:** high.
- **Confidence:** medium.

### LIT-TASK-007 — Transmission/distribution congestion relief by topology or DER control

- **Source provenance:** `Active-Power-Distribution-Networks-with-Decentralized-Multi-Agent-Control-Mode-Part-1.pdf`; `PAPER_VICTOR-OTHfglV6.docx` lines 37-39 discuss TSO-DSO interaction, relieving congestion, smart-inverter voltage/reactive support.
- **Source type:** paper(s).
- **Derived operational problem:** relieve congestion at TSO-DSO interface using DER flexibility/reactive control/topology choices.
- **Agent input:** topology, line limits, DER flexibilities, TSO-DSO exchange constraints.
- **Agent output/action:** DER setpoints, curtailment, switching or congestion relief plan.
- **Evaluator idea:** AC time-series with hidden load/RES profile; score overload duration, voltage profile, curtailed energy, switching count.
- **Substrate:** pandapower / PowerFactory-derived case.
- **Priority:** high.
- **Confidence:** strong.

## B. DER, EV, microgrid, smart-grid operations

### LIT-TASK-008 — EV/V2G support during distribution-grid outage

- **Source provenance:** `TheRoleofElectricalVehiclesforPowerQualityandSecurityduringOutagesintheDistributionGrid_final.pdf`; extracted text ranked #49; previous v0 selected it directly.
- **Source type:** paper.
- **Derived operational problem:** use EVs/V2G to maintain power quality and security during outages.
- **Agent input:** feeder topology, outage event, EV locations, charger ratings, SoC, load priority.
- **Agent output/action:** EV dispatch / V2G schedule / island support plan.
- **Evaluator idea:** AC time-series replay; score served load, voltage violations, line overloads, SoC violations, switching feasibility.
- **Substrate:** pandapower or OpenDSS distribution feeder.
- **Priority:** high.
- **Confidence:** strong.

### LIT-TASK-009 — Smart-inverter Volt-VAR curve selection

- **Source provenance:** `PAPER_VICTOR-OTHfglV6_cc1dd373.txt:40-43` mentions Volt-VAR control and smart inverter reactive power injection/absorption.
- **Source type:** paper.
- **Derived operational problem:** choose Volt-VAR curve/control mode for inverters to improve voltage profile.
- **Agent input:** feeder snapshot/time-series, inverter P output, Q capability, voltage bounds.
- **Agent output/action:** curve breakpoints / Q setpoints / mode choice.
- **Evaluator idea:** hidden irradiance/load replay; score voltage violation-hours, losses, excessive Q use, control instability.
- **Substrate:** pandapower control loop / OpenDSS.
- **Priority:** high.
- **Confidence:** strong.

### LIT-TASK-010 — Microgrid or converter-dominated grid dynamic support

- **Source provenance:** `(Power Systems) Francisco M. Gonzalez-Longatt, José Luis Rueda Torres - Modelling and Simulation of Power Electronic Converter Dominated Power Systems in PowerFactory...pdf`; extracted text ranked #5.
- **Source type:** book / simulation reference.
- **Derived operational problem:** select converter control parameters/modes for frequency/voltage recovery after disturbances.
- **Agent input:** converter-dominated grid model summary, disturbance event, controller parameter bounds.
- **Agent output/action:** GFM/GFL mode and controller settings.
- **Evaluator idea:** dynamic replay/surrogate traces; score frequency nadir, ROCOF, voltage recovery, settling, limit violations.
- **Substrate:** ANDES/OpenModelica simplified model; PowerFactory optional licensed track.
- **Priority:** medium-high.
- **Confidence:** medium.

### LIT-TASK-011 — BESS frequency / fault-ride-through service control

- **Source provenance:** same converter-dominated PowerFactory source as LIT-TASK-010; previous v0 identified BESS chapter as task source.
- **Source type:** simulation reference.
- **Derived operational problem:** dispatch battery active/reactive response during frequency or voltage events.
- **Agent input:** BESS power/energy limits, SoC, event trace, grid-code constraints.
- **Agent output/action:** P/Q response policy or parameter set.
- **Evaluator idea:** dynamic simulation/surrogate; score frequency nadir, voltage recovery, SoC/thermal violations, energy throughput.
- **Substrate:** simplified dynamic model first.
- **Priority:** medium.
- **Confidence:** medium.

### LIT-TASK-012 — Decentralized multi-agent control in active distribution networks

- **Source provenance:** `Active-Power-Distribution-Networks-with-Decentralized-Multi-Agent-Control-Mode-Part-1.pdf`; extracted text ranked #30.
- **Source type:** paper.
- **Derived operational problem:** distributed/local controller coordination for active distribution network operation.
- **Agent input:** local observations per area/agent, network constraints, communication limits.
- **Agent output/action:** local DER/OLTC/capacitor actions or coordination messages.
- **Evaluator idea:** multi-step feeder simulation; score global voltage/thermal feasibility and coordination overhead.
- **Substrate:** pandapower/OpenDSS; multi-agent wrapper.
- **Priority:** medium.
- **Confidence:** medium.

### LIT-TASK-013 — Demand response / building heating flexibility

- **Source provenance:** `Enhancement_of_Building_Heating_Systems_Connected_.pdf`; ranked #58; smart-grid / demand-response-adjacent source.
- **Source type:** paper.
- **Derived operational problem:** use controllable heating/building load flexibility to reduce peak/cost while maintaining comfort.
- **Agent input:** heat demand, weather, tariffs/DR event, comfort bounds, building/storage parameters.
- **Agent output/action:** heating/load-shift schedule.
- **Evaluator idea:** thermal/load simulator; score cost/peak reduction and comfort violations.
- **Substrate:** simple RC building model / CityLearn-like environment.
- **Priority:** medium.
- **Confidence:** medium.

## C. Forecasting and uncertainty tasks

### LIT-TASK-014 — Multi-step wind power forecasting

- **Source provenance:** `LoRA-Finetuned-LLM-for-Multi-Step-Wind-Power-Forecasting.pdf`; extracted text ranked #72.
- **Source type:** paper.
- **Derived operational problem:** forecast wind power over multiple future steps.
- **Agent input:** historical wind power/weather/time features.
- **Agent output/action:** point forecast and optionally prediction intervals.
- **Evaluator idea:** held-out time-series; score MAE/RMSE and interval calibration if probabilistic.
- **Substrate:** Python time-series benchmark; optional downstream dispatch penalty.
- **Priority:** medium-high.
- **Confidence:** strong.

### LIT-TASK-015 — Short-term wind speed / wind energy facility forecasting

- **Source provenance:** `elibrary_71966528_24523599_4818a08c.txt:77-108` discusses models for wind characteristics and short-term wind speed forecast.
- **Source type:** paper.
- **Derived operational problem:** forecast wind speed/generation for an existing or projected wind facility.
- **Agent input:** meteorological history, site metadata, forecast horizon.
- **Agent output/action:** wind speed / power forecast.
- **Evaluator idea:** held-out site/time horizon; score MAE/RMSE, ramp error, calibration.
- **Substrate:** Python forecasting dataset.
- **Priority:** medium.
- **Confidence:** strong.

### LIT-TASK-016 — Solar PV output / soft-cost uncertainty analysis

- **Source provenance:** `quantifying-the-uncertainty-of-solar-photovoltaic-soft-costs...txt:143-147` mentions tools for 3D shade analysis, solar output and economic forecasting.
- **Source type:** paper.
- **Derived operational problem:** estimate solar project output/economic uncertainty under uncertain assumptions.
- **Agent input:** PV system/site assumptions, irradiance/shade/economic parameter distributions.
- **Agent output/action:** output forecast and uncertainty interval / sensitivity report.
- **Evaluator idea:** hidden synthetic parameter sets with known simulator output; score interval coverage and error.
- **Substrate:** pvlib / spreadsheet-style model.
- **Priority:** low-medium.
- **Confidence:** medium.

### LIT-TASK-017 — Advanced smart-grid prediction model selection

- **Source provenance:** `Advanced Prediction Techniques Applied to Smart Grids.pdf`.
- **Source type:** book / technical reference.
- **Derived operational problem:** choose and apply forecasting method for load/RES/line rating depending on data conditions.
- **Agent input:** dataset metadata, missingness/noise, forecast target, operational cost function.
- **Agent output/action:** model choice + forecast.
- **Evaluator idea:** hidden datasets; score forecast and model-selection regret.
- **Substrate:** Python time-series harness.
- **Priority:** medium.
- **Confidence:** medium.

## D. Reliability, outages and asset placement

### LIT-TASK-018 — Faulted circuit indicator reliability impact

- **Source provenance:** `faulted-circuit-indicators-and-system-reliability.pdf`; extracted text ranked #43; previous v0 selected it directly.
- **Source type:** paper.
- **Derived operational problem:** quantify how FCIs reduce outage duration/reliability indices in a feeder.
- **Agent input:** radial feeder graph, customers/load per section, failure/repair rates, FCI placements, crew assumptions.
- **Agent output/action:** SAIDI/CAIDI or outage-duration estimate for base vs FCI scenario.
- **Evaluator idea:** deterministic graph reliability calculator; score numerical error.
- **Substrate:** custom graph/reliability simulator.
- **Priority:** high.
- **Confidence:** strong.

### LIT-TASK-019 — Optimal placement of faulted circuit indicators

- **Source provenance:** `faulted-circuit-indicators-and-system-reliability.pdf`.
- **Source type:** paper.
- **Derived operational problem:** choose FCI locations to maximize expected outage-duration reduction under budget.
- **Agent input:** feeder graph, failure rates, customer weights, budget k.
- **Agent output/action:** FCI placement list.
- **Evaluator idea:** exact enumeration/MILP on hidden small feeders; heuristic baseline on larger feeders.
- **Substrate:** networkx/custom optimizer.
- **Priority:** high.
- **Confidence:** strong.

### LIT-TASK-020 — Analytical reliability of reserved / series-parallel supply schemes

- **Source provenance:** `Надежн.docx`; extracted text ranked #46; previous first-mining selected it.
- **Source type:** teaching/problem document.
- **Derived operational problem:** calculate reliability indices for component topologies with redundancy/repair.
- **Agent input:** components, failure/repair rates, topology, standby/repair assumptions.
- **Agent output/action:** availability, failure frequency, expected outage time, unserved energy.
- **Evaluator idea:** closed-form or Markov reliability calculator on hidden generated topologies.
- **Substrate:** custom reliability-block/Markov solver.
- **Priority:** medium-high.
- **Confidence:** medium.

### LIT-TASK-021 — Preventive maintenance scheduling by reliability risk

- **Source provenance:** reliability corpus plus `monograph_2020_ed_kulagin_v_a.pdf`; extracted text ranked #23; Russian benchmark design note also listed maintenance/ops as benchmark family.
- **Source type:** monograph / benchmark design.
- **Derived operational problem:** schedule maintenance to reduce expected failure/outage risk under crew/budget constraints.
- **Agent input:** asset health, failure probabilities, criticality, crews, outage windows.
- **Agent output/action:** maintenance schedule.
- **Evaluator idea:** hidden degradation/failure simulation; score expected risk/cost and constraint violations.
- **Substrate:** custom scheduling simulator.
- **Priority:** medium.
- **Confidence:** weak-medium; needs stronger direct maintenance paper.

### LIT-TASK-022 — Ice/wind outage prevention by conductor heating device placement

- **Source provenance:** `статья Бандурин №102 исправленная.docx`; locator `статья Бандурин №102 исправленная_dd62a53f.txt:1-24,76-86`; lines 77-78 explicitly frame nonlinear optimization and optimal reactor resistances for typical overhead line; lines 85-86 summarize mathematical model for selecting type/power of preventive heating devices.
- **Source type:** published article (user-confirmed; local filename is a DOCX copy, not merely an unknown draft). OpenAlex lookup in this pass did not find indexed citations, so citation weight is low/unknown rather than bibliographic status unknown.
- **Derived operational problem:** choose reactive devices/artificial load to heat 6–35 kV overhead conductors during icing risk without exceeding voltage/current constraints.
- **Agent input:** radial line data, weather/icing risk, load table, current/voltage limits, candidate reactor/capacitor/load locations.
- **Agent output/action:** device type/power/resistance per section and activation plan.
- **Evaluator idea:** nonlinear power-flow/current-temperature surrogate; score min heating current achieved, max current/voltage-drop constraints, served load.
- **Substrate:** custom feeder model; pandapower possible for electrical constraints.
- **Priority:** high — locally distinctive and literature-grounded.
- **Confidence:** strong.

## E. Protection, relay coordination, automation

### LIT-TASK-023 — Inverse-time overcurrent relay setting and coordination

- **Source provenance:** `development-of-laboratory-experiments-for-protection-and-communication-in-radial-and-bidirectional-power-systems.pdf`; Russian relay manuals (`Релейная защита...`, `Евминов Л. Релейная...pdf`, `shneerson-em-cifrovaya-releynaya-zaschita.pdf`).
- **Source type:** paper + manuals/textbooks.
- **Derived operational problem:** set pickup/time dial and verify selectivity for radial or bidirectional feeder faults.
- **Agent input:** CT ratio, load current, fault currents at locations, relay curve type, coordination time interval.
- **Agent output/action:** pickup, time dial, trip times, selectivity verdict.
- **Evaluator idea:** independent IEC/IEEE inverse-time curve calculator; hidden fault cases.
- **Substrate:** formula-based protection evaluator.
- **Priority:** high.
- **Confidence:** strong.

### LIT-TASK-024 — Directional relay coordination in DER/bidirectional feeder

- **Source provenance:** `development-of-laboratory-experiments-for-protection-and-communication-in-radial-and-bidirectional-power-systems.pdf`; source title explicitly mentions radial and bidirectional systems.
- **Source type:** paper.
- **Derived operational problem:** coordinate directional protection when DER causes bidirectional fault currents.
- **Agent input:** feeder topology, source/DER statuses, directional relay settings, fault cases.
- **Agent output/action:** directional trip/block decisions and trip sequence.
- **Evaluator idea:** hidden fault-current solver; score correct isolation, selectivity, false trips.
- **Substrate:** custom radial feeder fault simulator.
- **Priority:** high.
- **Confidence:** strong.

### LIT-TASK-025 — Ground-fault / zero-sequence feeder identification in 6–35 kV networks

- **Source provenance:** `Релейная защита и автоматизация электроэнергетических систем_d2ff6eb4.txt:70-74` mentions zero-sequence current distribution and ground-fault protection in 6–35 kV networks; `статья Бандурин...txt:32` also mentions zero-sequence current sensors for locating single-phase ground faults.
- **Source type:** curriculum/manual + paper.
- **Derived operational problem:** identify faulted feeder and operate/block zero-sequence/directional ground-fault protection.
- **Agent input:** three-phase currents/voltages or sequence components, neutral grounding mode, feeder labels.
- **Agent output/action:** faulted feeder, 3I0/3U0 values, trip/no-trip.
- **Evaluator idea:** symmetrical-components solver over hidden ground-fault cases.
- **Substrate:** formula-based protection evaluator.
- **Priority:** high.
- **Confidence:** strong.

### LIT-TASK-026 — Transformer differential protection trip/no-trip classification

- **Source provenance:** Russian relay corpus (`Евминов Л. Релейная...pdf`, `shneerson-em-cifrovaya-releynaya-zaschita.pdf`, `Markevich_A_I_Releynaya_zaschita...pdf`) ranked highly by protection keywords.
- **Source type:** manuals/textbooks.
- **Derived operational problem:** classify internal/external transformer faults and inrush/blocking cases from current measurements/settings.
- **Agent input:** winding/vector group, CT ratios, phase currents, restraint/slope settings, harmonic content if available.
- **Agent output/action:** differential/restraint currents and trip/block decision.
- **Evaluator idea:** synthetic event generator + exact relay characteristic; score false-trip and missed-trip penalties.
- **Substrate:** formula/signal evaluator.
- **Priority:** medium-high.
- **Confidence:** medium.

### LIT-TASK-027 — Distance protection zone setting and fault-zone classification

- **Source provenance:** Russian relay corpus; extracted text shows strong coverage of line protection and fault analysis across multiple manuals.
- **Source type:** manuals/textbooks.
- **Derived operational problem:** set distance relay zones and classify apparent impedance fault location.
- **Agent input:** line impedance/length, source impedance, load/fault apparent impedance samples.
- **Agent output/action:** zone 1/2/3 reach and delay settings; trip zone per case.
- **Evaluator idea:** hidden fault locations and load-encroachment cases; score zone accuracy and over/underreach.
- **Substrate:** formula-based impedance evaluator.
- **Priority:** medium-high.
- **Confidence:** medium.

### LIT-TASK-028 — Motor protection and undervoltage/loss-of-phase automation

- **Source provenance:** `Релейная защита и автоматизация электроэнергетических систем_d2ff6eb4.txt:117-123` mentions protection of low/high-voltage asynchronous motors, overloads, loss of phase, undervoltage, APV/AVR of motors.
- **Source type:** curriculum/manual.
- **Derived operational problem:** decide motor trip/restart/block action from voltage/current event trace.
- **Agent input:** motor ratings, current/voltage traces, protection settings, restart constraints.
- **Agent output/action:** trip/no-trip, restart/AVR decision, timing.
- **Evaluator idea:** discrete-event relay automaton; score state trace and unsafe restart penalties.
- **Substrate:** custom event simulator.
- **Priority:** medium.
- **Confidence:** medium.

### LIT-TASK-029 — APV/АВР automation logic verification

- **Source provenance:** Russian relay/APV/АВР corpus (`Релейная защита...`, `РЭ1_Алтей-УЗТ.pdf`, `Markevich...`, `shneerson...`).
- **Source type:** manuals/textbooks.
- **Derived operational problem:** simulate auto-reclose / automatic transfer switching logic under transient vs permanent faults and synchronism constraints.
- **Agent input:** breaker states, voltage presence, fault type/event timeline, reserve source status, timers.
- **Agent output/action:** APV/AVR action trace and final topology.
- **Evaluator idea:** hidden event traces; score trace equality, restoration time, unsafe close penalty.
- **Substrate:** discrete-event automation simulator.
- **Priority:** medium-high.
- **Confidence:** medium.

### LIT-TASK-030 — Relay settings calculation from worked examples

- **Source provenance:** `РЕЛЕЙНАЯ ЗАЩИТА В ЗАДАЧАХ С РЕШЕНИЯМИ И ПРИМЕРАМИ.pdf`; extracted text ranked #38; `Булычев...Релейная защита распределительных сетей в примерах и задачах...pdf` ranked #14.
- **Source type:** problem book.
- **Derived operational problem:** solve parameterized relay-protection calculation exercises.
- **Agent input:** variant data: line/transformer/motor parameters, fault currents, CT ratios, selectivity requirements.
- **Agent output/action:** protection setting values and check calculations.
- **Evaluator idea:** closed-form answer generator for randomized variants; score numeric error and constraint violations.
- **Substrate:** formula-based evaluator.
- **Priority:** high as a source of many tasks.
- **Confidence:** strong.

## F. Power quality, dynamic rating, equipment and misc. operations

### LIT-TASK-031 — Dynamic line rating / safe overload decision

- **Source provenance:** `Advanced Prediction Techniques Applied to Smart Grids.pdf`; previous v0 found RTTR/dynamic-rating-relevant section.
- **Source type:** technical reference.
- **Derived operational problem:** estimate safe ampacity/temporary overload using weather and conductor conditions.
- **Agent input:** conductor parameters, current, ambient temperature, wind speed/direction, solar radiation forecast.
- **Agent output/action:** ampacity forecast and safe/unsafe loading recommendation.
- **Evaluator idea:** hidden heat-balance traces; score overestimation heavily and underutilization moderately.
- **Substrate:** IEEE/CIGRE heat-balance model.
- **Priority:** medium.
- **Confidence:** medium.

### LIT-TASK-032 — Power quality event diagnosis and mitigation

- **Source provenance:** `TheRoleofElectricalVehicles...` title links EVs to power quality/security during outages; smart-grid prediction/control corpus also covers power quality.
- **Source type:** paper / smart-grid reference.
- **Derived operational problem:** diagnose voltage sag/swell/harmonic-like event and recommend mitigation actions.
- **Agent input:** time-series voltage/current/PQ measurements, event labels, DER/EV controllability.
- **Agent output/action:** diagnosis and mitigation plan.
- **Evaluator idea:** hidden labeled events + AC replay for actions.
- **Substrate:** synthetic PQ event generator + pandapower for voltage actions.
- **Priority:** low-medium.
- **Confidence:** weak-medium.

### LIT-TASK-033 — Synchronous/asynchronous motor operation constraint checks

- **Source provenance:** `sinchronnye-i-asinchronnye-dvigateli6-10kv (1) (1).pdf`; extracted text ranked #19.
- **Source type:** equipment/manual.
- **Derived operational problem:** assess motor start/operation constraints and protection requirements for 6–10 kV motors.
- **Agent input:** motor parameters, network short-circuit power, start current, voltage dip limits, protection settings.
- **Agent output/action:** start allowed/not allowed, protection setting recommendations.
- **Evaluator idea:** formula checks for voltage dip, thermal/overcurrent constraints, setting feasibility.
- **Substrate:** formula-based equipment evaluator.
- **Priority:** low-medium.
- **Confidence:** medium.

### LIT-TASK-034 — SCADA/situational awareness incident interpretation

- **Source provenance:** `situationalawareness.pdf`; extracted text ranked #18.
- **Source type:** technical paper/report.
- **Derived operational problem:** infer grid state / alarms / incident severity from partial telemetry.
- **Agent input:** alarm log, measurements, topology, missing/uncertain telemetry.
- **Agent output/action:** event diagnosis, prioritized operator actions, confidence.
- **Evaluator idea:** hidden event ground truth; score diagnosis, unsafe action penalties, detection latency.
- **Substrate:** synthetic SCADA/event replay + power-flow backend.
- **Priority:** medium.
- **Confidence:** medium.

### LIT-TASK-035 — Digital substation / IEC 61850 automation conformance check

- **Source provenance:** relay/digital protection corpus (`shneerson-em-cifrovaya-releynaya-zaschita.pdf`, `РЭ1_Алтей-УЗТ.pdf`, `UserManual_2019_en.pdf` as PowerFactory/manual source).
- **Source type:** manuals.
- **Derived operational problem:** validate protection/automation settings and event logic against digital-substation constraints.
- **Agent input:** IED settings, GOOSE-like events, breaker states, protection functions.
- **Agent output/action:** conformance/logic verdict and corrected settings.
- **Evaluator idea:** discrete-event checker; score missed/block/trip errors and timing.
- **Substrate:** custom IED-event simulator.
- **Priority:** low-medium.
- **Confidence:** weak-medium.

### LIT-TASK-036 — Energy saving / efficiency recommendation under operational constraints

- **Source provenance:** `Программа ПК Энергосбережение.docx`; extracted text ranked #80.
- **Source type:** program/course document.
- **Derived operational problem:** select energy-saving measures subject to cost/payback/technical constraints.
- **Agent input:** load profile, equipment efficiency, tariff, candidate measures, budget.
- **Agent output/action:** ranked measures and schedule.
- **Evaluator idea:** hidden financial/energy model; score NPV/payback correctness and constraint compliance.
- **Substrate:** spreadsheet-style evaluator.
- **Priority:** low.
- **Confidence:** weak.

## G. Benchmark/meta tasks from agent benchmark literature

### LIT-TASK-037 — Power-systems benchmark task design critique

- **Source provenance:** `Отраслевые_агентные_бенчмарки_и_проектирование_benchmark_для_электроэнергетики.pdf`; extracted text ranked #27.
- **Source type:** benchmark design note.
- **Derived operational problem:** classify whether a proposed power-system agent task has executable ground truth or degenerates into LLM-as-judge report scoring.
- **Agent input:** task proposal, source reference, evaluator draft.
- **Agent output/action:** critique, missing substrate/evaluator, revised contract.
- **Evaluator idea:** rubric plus structural checks; secondary LLM judge only, not core benchmark.
- **Substrate:** document/schema checker.
- **Priority:** medium as internal QA, not public benchmark task.
- **Confidence:** strong.

## Immediate shortlist for executable MVP after this pass

1. **LIT-TASK-022** — ice/wind outage prevention by conductor heating device placement. Strong local literature provenance, distinctive, optimization + electrical constraints.
2. **LIT-TASK-002 / 009** — smart-inverter Volt-VAR voltage support. Strong paper provenance and pandapower/OpenDSS-friendly.
3. **LIT-TASK-003 / 004** — dispatch/OPF under uncertainty. Benchmark-aligned and easy to compare with solver baseline.
4. **LIT-TASK-018 / 019** — FCI reliability impact/placement. Very executable, graph/reliability evaluator.
5. **LIT-TASK-023 / 024 / 025 / 030** — relay/protection calculations. Many source documents and exact formula-based evaluation.
6. **LIT-TASK-008** — EV/V2G support during outage. Good DER/distribution time-series task.

## Pruning notes

- Several high-scoring documents are large manuals (`UserManual_2019_en.pdf`, PowerFactory manuals, relay textbooks). They are useful for task/evaluator mechanics but should not be the sole provenance for final benchmark tasks unless paired with a paper or worked example.
- Strongest final tasks should prefer: paper-derived, benchmark-derived, or worked-example-derived provenance.
- For every task promoted from this bank, create a separate `literature_cards/<citation_key>.md` extraction card with exact source quotes, page/line locator, preserved assumptions, simplifications, and evaluator mapping.
