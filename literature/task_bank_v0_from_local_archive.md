# Task bank v0 from Sergey local literature archive

Source bundle: `literature/local_archive_extracted/local_lit`

Extraction pass: `literature/extracted_text/local_archive_first_mining`

Selection manifest: `literature/metadata/local_archive_first_mining_selection.json`

This is a first executable-task mining pass. It intentionally converts literature/manual ideas into benchmark task families with simulator substrate, input/output contract, hidden evaluator and metrics. It is not yet the final benchmark spec.

## Priority MVP families

### 1. AC load-flow correction / voltage violation repair

- **Substrate:** pandapower first; OpenDSS for distribution variants.
- **Agent input:** network case, bus/line limits, load/generation snapshot, violation report.
- **Agent output:** corrective actions: tap changes, reactive compensation, generator voltage setpoints, load shedding if unavoidable.
- **Hidden evaluator:** rerun AC power flow on hidden perturbed cases and compare final constraints.
- **Metrics:** all constraints satisfied; total action cost; voltage deviation; line loading; minimal load shed.
- **Sources:** broad power-system corpus; smart-grid/power-flow documents; `Power System Analysis and Design`; `Advanced Prediction Techniques Applied to Smart Grids`.
- **Why important:** best pandapower-first MVP: deterministic, executable, easy hidden tests.

### 2. Real-time dispatch / OPF under renewable forecast uncertainty

- **Substrate:** pandapower OPF / PyPSA / MATPOWER-style economic dispatch.
- **Agent input:** load forecast, renewable forecast intervals, generator costs/limits, reserve constraints.
- **Agent output:** dispatch schedule and reserve plan.
- **Hidden evaluator:** hidden forecast realization + AC feasibility rerun.
- **Metrics:** feasibility, production cost regret, reserve violations, renewable curtailment.
- **Sources:** `ElecBench_a_Power_Dispatch_Evaluation_Benchmark_fo.pdf`; benchmark design note; smart-grid prediction materials.
- **Why important:** directly aligned with ElecBench/power-dispatch benchmarking and easy to score numerically.

### 3. Contingency / N-1 security assessment and mitigation

- **Substrate:** pandapower contingency loop; Grid2Op for sequential variant.
- **Agent input:** base case, list of candidate outages, allowed redispatch/topology actions.
- **Agent output:** ranked critical contingencies + preventive/corrective mitigation.
- **Hidden evaluator:** recompute hidden N-1/N-2 outages and AC constraints.
- **Metrics:** detected critical contingencies, post-contingency violations, cost of mitigation, false-safe penalty.
- **Sources:** benchmark design note; PowerAgentBench-adjacent discussion; power-system manuals.
- **Why important:** differentiates from text QA and maps to real operator workflows.

### 4. Grid reconfiguration / congestion relief

- **Substrate:** Grid2Op for topology actions; pandapower for static validation.
- **Agent input:** topology, thermal limits, forecasts, alarms, line statuses.
- **Agent output:** switch/redispatch sequence with rollback if needed.
- **Hidden evaluator:** hidden chronics and contingencies; legal-action checker.
- **Metrics:** load served, max overload, voltage deviation, switching count, operating cost.
- **Sources:** Russian benchmark design note task matrix; Grid2Op/L2RPN references.
- **Why important:** turns agent planning into a sequential operational benchmark.

### 5. DER / EV / V2G voltage support during distribution outage

- **Substrate:** pandapower or OpenDSS LV/MV feeder time-series.
- **Agent input:** feeder topology, outage event, EV availability, SoC, charger locations, load profiles.
- **Agent output:** EV/V2G dispatch plan and connection/location choice.
- **Hidden evaluator:** AC time-series with hidden load and EV availability.
- **Metrics:** voltage violation-hours, line overloads, served load, EV energy used, number of devices.
- **Sources:** `TheRoleofElectricalVehiclesforPowerQualityandSecurityduringOutagesintheDistributionGrid_final.pdf`.
- **Why important:** concrete DER task with realistic distribution constraints.

### 6. Demand response orchestration / peak reduction

- **Substrate:** CityLearn-style building district simulator or custom load-shaping simulator.
- **Agent input:** tariffs, DR event, building states, weather, comfort constraints, DER/storage limits.
- **Agent output:** curtailment/load-shift/storage/HVAC schedule.
- **Hidden evaluator:** hidden weather/occupancy and rebound effects.
- **Metrics:** peak reduction, cost, comfort violations, rebound peak, emissions.
- **Sources:** benchmark design note; previous Drive DR materials; `DR` folder candidates.
- **Why important:** good bridge between power systems, agents and market/consumer interaction.

### 7. Probabilistic wind/PV generation forecasting

- **Substrate:** Python forecasting task with held-out time-series; optional downstream dispatch evaluation.
- **Agent input:** historical generation, weather forecasts, calendar/site metadata.
- **Agent output:** point forecast + prediction intervals.
- **Hidden evaluator:** held-out days/sites.
- **Metrics:** MAE/RMSE, pinball loss/CRPS, interval coverage and sharpness.
- **Sources:** `Advanced Prediction Techniques Applied to Smart Grids.pdf`; `LoRA-Finetuned-LLM-for-Multi-Step-Wind-Power-Forecasting.pdf`.
- **Why important:** data task that can feed dispatch/OPF tasks.

### 8. Dynamic line rating / safe temporary overload decision

- **Substrate:** line thermal model using CIGRE/IEEE heat balance.
- **Agent input:** conductor parameters, current, ambient temperature, wind speed/direction, solar radiation forecast.
- **Agent output:** dynamic ampacity forecast and safe/unsafe loading recommendation.
- **Hidden evaluator:** hidden rating/temperature traces.
- **Metrics:** overestimation penalty, underutilization penalty, confidence coverage, congestion value.
- **Sources:** `Advanced Prediction Techniques Applied to Smart Grids.pdf` RTTR section.
- **Why important:** combines physics and uncertainty; good for tool-using agents.

### 9. PowerFactory-derived converter-dominated grid stability

- **Substrate:** PowerFactory as source workflow; open benchmark can use simplified dynamic traces / OpenModelica / ANDES where possible.
- **Agent input:** converter-dominated grid case, disturbance, GFM/GFL mode options, controller parameter bounds.
- **Agent output:** controller mode/settings and stability rationale.
- **Hidden evaluator:** dynamic simulation/replay traces with hidden disturbances.
- **Metrics:** frequency nadir, ROCOF, voltage recovery, settling time, loss-of-synchronism, limit violations.
- **Sources:** `Modelling and Simulation of Power Electronic Converter Dominated Power Systems in PowerFactory`.
- **Why important:** addresses modern inverter-dominated systems beyond steady-state OPF.

### 10. Battery energy storage control for frequency/FRT services

- **Substrate:** dynamic BESS model; simplified first-order frequency model for MVP.
- **Agent input:** BESS P/Q/SoC limits, event schedule, frequency/voltage trace, grid-code constraints.
- **Agent output:** active/reactive control policy and parameters.
- **Hidden evaluator:** hidden load steps/faults.
- **Metrics:** frequency nadir, voltage recovery, SoC violations, converter limit violations, energy throughput.
- **Sources:** PowerFactory BESS chapter from converter-dominated systems book.
- **Why important:** clean dynamic-control task with clear constraints.

## Protection and reliability families

### 11. Faulted circuit indicator impact on reliability

- **Substrate:** graph/radial feeder reliability simulator.
- **Agent input:** feeder graph, section lengths, customers, failure rates, patrol/repair assumptions, FCI placements.
- **Agent output:** SAIDI/CAIDI and outage-duration reduction for base vs FCI scenario.
- **Hidden evaluator:** deterministic reliability calculator on hidden feeders.
- **Metrics:** SAIDI/CAIDI error, patrol route correctness, reduction estimate error.
- **Sources:** `faulted-circuit-indicators-and-system-reliability.pdf`.
- **Why important:** executable reliability task with simple formulas and real operational meaning.

### 12. Optimal placement of faulted circuit indicators

- **Substrate:** graph optimization over radial feeders.
- **Agent input:** feeder graph, budget `k`, failure probabilities, crew starting location.
- **Agent output:** FCI node/edge placements and expected outage reduction.
- **Hidden evaluator:** exhaustive/MILP optimum on small hidden cases; heuristic baseline on larger cases.
- **Metrics:** objective gap, runtime, placement feasibility.
- **Sources:** `faulted-circuit-indicators-and-system-reliability.pdf`.
- **Why important:** good optimization/planning task for agents.

### 13. Analytical reliability of series/parallel/reserved supply schemes

- **Substrate:** reliability block diagram / Markov calculator.
- **Agent input:** components with failure/repair rates, topology, repair/standby assumptions.
- **Agent output:** availability, failure frequency, expected outage duration, unserved energy.
- **Hidden evaluator:** generated RBDs with closed-form solutions.
- **Metrics:** numerical error and topology interpretation accuracy.
- **Sources:** `Надежн.docx`.
- **Why important:** compact math-heavy task; useful for checking domain reasoning.

### 14. Inverse-time overcurrent relay setting and coordination

- **Substrate:** IEC/IEEE inverse-time relay curve calculator.
- **Agent input:** CT ratio, load/fault currents, pickup/time-dial bounds, coordination interval.
- **Agent output:** pickup, time dial, trip time per fault, selectivity verdict.
- **Hidden evaluator:** hidden fault currents and independent curve equations.
- **Metrics:** trip-time error, selectivity violations, setting feasibility.
- **Sources:** `development-of-laboratory-experiments-for-protection-and-communication-in-radial-and-bidirectional-power-systems.pdf`; Russian relay docs.
- **Why important:** precise numerical protection task.

### 15. Transformer differential protection classification

- **Substrate:** synthetic relay event/COMTRADE-like generator.
- **Agent input:** transformer winding/vector group, CT ratios, sampled phase currents, slope/restraint settings.
- **Agent output:** differential/restraint currents, internal/external fault classification, trip/no-trip.
- **Hidden evaluator:** hidden event traces with labels.
- **Metrics:** F1, false-trip rate for external faults, missed internal faults, numeric setting error.
- **Sources:** lab relay protection paper; Russian relay automation docs.
- **Why important:** protection decision task with high safety relevance.

### 16. Distance protection zone setting

- **Substrate:** line impedance and apparent-impedance calculator.
- **Agent input:** line impedance, length, source impedance, fault apparent impedance samples.
- **Agent output:** zone 1/2/3 reach settings, trip zone and delay.
- **Hidden evaluator:** hidden fault locations/load encroachment cases.
- **Metrics:** zone classification accuracy, reach-setting error, overreach/underreach penalty.
- **Sources:** relay lab and Russian relay docs.
- **Why important:** realistic transmission protection task.

### 17. Directional/DER-aware relay coordination

- **Substrate:** radial/bidirectional feeder fault-current simulator.
- **Agent input:** topology with DER sources, source statuses, directional relay settings, fault cases.
- **Agent output:** directional decisions and trip sequence.
- **Hidden evaluator:** hidden topologies/faults with reverse power flow.
- **Metrics:** correct isolation rate, false trip/non-trip penalty, coordination margin.
- **Sources:** bidirectional relay lab paper.
- **Why important:** modern distribution protection issue caused by DER.

### 18. Ground-fault / zero-sequence protection in 6–35 kV networks

- **Substrate:** symmetrical components / zero-sequence network solver.
- **Agent input:** neutral grounding mode, measured 3-phase currents/voltages, feeder labels.
- **Agent output:** `3I0`, `3U0`, faulted feeder, operate/no-operate.
- **Hidden evaluator:** hidden ground-fault cases including isolated/compensated neutral.
- **Metrics:** feeder identification accuracy, sensitivity/selectivity, numeric error.
- **Sources:** Russian relay automation docs.
- **Why important:** domain-specific protection task not covered by generic power-flow benchmarks.

### 19. APV/АВР automation logic verification

- **Substrate:** discrete-event protection automation simulator.
- **Agent input:** breaker states, voltage/current events, synchronism measurements, reserve source status, time delays.
- **Agent output:** APV/АВР action trace, block/permit decision, final topology.
- **Hidden evaluator:** hidden event traces for transient/permanent faults and synchronism constraints.
- **Metrics:** state trace match, unsafe close/trip penalty, restoration time.
- **Sources:** Russian relay/APV/АВР docs.
- **Why important:** agent must reason over state machines, not just compute load flow.

## Market/cyber/ops families from benchmark design note

### 20. Market bidding / broker strategy

- **Substrate:** PowerTAC-style market simulator or simplified auction/imbalance market.
- **Agent input:** demand/renewable forecasts, market rules, historical prices, portfolio constraints.
- **Agent output:** bids, reserve/imbalance strategy, risk rationale.
- **Hidden evaluator:** hidden market shocks and counterparties.
- **Metrics:** profit/surplus, regret, imbalance cost, rule violations.
- **Sources:** Russian benchmark design note; PowerTAC references.

### 21. Cyber/SCADA incident response

- **Substrate:** SCADA/IED emulator + physical grid simulator; simplified log/event benchmark for MVP.
- **Agent input:** network telemetry, IEC 61850/DNP3/OPC-UA-like events, host alerts, grid state.
- **Agent output:** incident classification, containment/recovery actions, blocked commands, report.
- **Hidden evaluator:** hidden true attack graph and physical consequences.
- **Metrics:** detection/response time, false positives, load served, policy violations, physical impact.
- **Sources:** Russian benchmark design note; ESPSGrid/OpenPLC61850 references.

### 22. Preventive maintenance scheduling

- **Substrate:** CMMS/work-order simulator + reliability model + grid criticality.
- **Agent input:** asset health, inspection backlog, weather, crews, budget, outage windows.
- **Agent output:** maintenance schedule and deferral rationale.
- **Hidden evaluator:** hidden degradation/failure and weather realizations.
- **Metrics:** expected failure cost, deferred risk, crew utilization, reliability violations.
- **Sources:** Russian benchmark design note; FCI/reliability materials.

## Cross-cutting benchmark design rules extracted from sources

1. Prefer **execution-based evaluation** over report scoring: final simulator/environment state is the primary ground truth.
2. Keep tool API narrow and operational: `read_state`, `query_alarm_log`, `switch_line`, `set_redispatch`, `dispatch_der`, `open_breaker`, `submit_bid`, `ack_alarm`, `create_ticket`, `rollback_action`, `end_episode`.
3. Use layered scoring:
   - hard physics/safety constraints;
   - task objective value;
   - operational quality/cost;
   - explanation/evidence quality as secondary score.
4. Maintain public examples + hidden cases:
   - public synthetic/open cases for development;
   - hidden chronics/fault sequences/market shocks/cyber events for evaluation.
5. Make tasks reproducible with versioned seeds and replay logs.
6. Treat proprietary tools such as DIgSILENT PowerFactory as **workflow/literature sources** or optional licensed track, not required open-core substrate.

## Recommended MVP slice

For the first implementable benchmark prototype, start with 6 families:

1. AC load-flow correction / voltage violation repair — pandapower.
2. Dispatch / OPF under forecast uncertainty — pandapower/PyPSA.
3. N-1 contingency assessment and mitigation — pandapower.
4. FCI reliability impact and placement — custom graph/reliability simulator.
5. Inverse-time overcurrent relay coordination — formula-based protection evaluator.
6. DER/EV voltage support in distribution feeder — pandapower/OpenDSS.

This mix covers steady-state power flow, optimization, reliability, protection, DER and agentic decision-making while staying executable without proprietary software.
