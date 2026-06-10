# Power Systems Agent Benchmark — подробный обзор

Сгенерировано: 2026-06-09 08:56

## Краткий итог

- Всего публичных задач: 41
- Зарегистрированных проверяющих программ: 41
- Generic expected-answer проверок: 0
- Остались generic: нет

### bess_ancillary_response

- Идентификаторы: `bess_ancillary_response_public_001`, candidate `REL-TASK-004`
- Область: converter-dominated grids & storage
- Назначение: Применить частотные и напряженческие droop-правила для получения команд P/Q BESS с учётом ограничений инвертора и SOC.
- English objective: Apply frequency and voltage droop rules to produce BESS P/Q commands within inverter and SOC constraints.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-004; subdomain: converter-dominated grids & storage; input_fields: список[4]: bess_response_case.measurements, bess_response_case.frequency_droop_mw_per_hz, bess_response_case.voltage_droop_mvar_per_pu, bess_response_case.s_rating_mva; calculation_spec: For each timestamp, compute p_response_mw = clip((nominal_frequency_hz - frequency_hz) * frequency_droop_mw_per_hz,…}; bess_response_case: {nominal_frequency_hz: 50.0; target_voltage_pu: 1.0; interval_seconds: 10.0; initial_soc_mwh: 4.8; soc_min_mwh: 1.0; soc_max_mwh: 8.0; … ещё 8}
- Выход: p_response_mw: object mapping timestamp to active-power response; q_response_mvar: object mapping timestamp to reactive-power response; final_soc_mwh: final state of charge; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_bess_ancillary_response`; baseline: `baselines.bess_ancillary_response.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-004; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from converter-dominated grids and storage taxonomy.
  - BESS ancillary service droop response practice; локатор: standard frequency-watt and volt-var droop with inverter capability; доверие: medium; примечание: Public case is a compact deterministic executable instance.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-004
  - source card: docs/source_cards/bess_ancillary_response.md

### breaker_relay_short_circuit

- Идентификаторы: `breaker_relay_short_circuit_public_001`, candidate `REL-TASK-045`
- Область: protection, faults & relay engineering
- Назначение: Рассчитайте токи КЗ в начале и конце фидера, выберите стандартную отключающую способность выключателя и уставку реле с учётом нагрузки и чувствительности к минимальному КЗ.
- English objective: Compute near/far feeder short-circuit currents, select a standard breaker interrupting rating, and choose a relay pickup satisfying load margin and minimum-fault sensitivity.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-045; subdomain: protection, faults & relay engineering; input_fields: список[5]: short_circuit_case.source_thevenin_impedance, short_circuit_case.transformer_impedance, short_circuit_case.feeder, short_circuit_case.fault_locations, … ещё 1}; short_circuit_case: {voltage_kv: 10.5; source_thevenin_impedance: {r_ohm: 0.045; x_ohm: 0.42}; transformer_impedance: {r_ohm: 0.018; x_ohm: 0.16}; feeder: {id: F1; length_km: 8.0; r_ohm_per_km: 0.18; x_ohm_per_km: 0.32}; fault_locations: список[3]: {id: …; distance_km: …}, {id: …; distance_km: …}, {id: …; distance_km: …}; max_load_current_a: 360.0; … ещё 2}
- Выход: max_3ph_fault_ka: float kA, maximum over fault locations; min_2ph_fault_ka: float kA, minimum over fault locations; breaker_interrupting_rating_ka: float kA selected from available standard ratings; relay_pickup_a_primary: float primary amperes; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_breaker_relay_short_circuit`; baseline: `baselines.breaker_relay_short_circuit.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-045; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Balanced-core candidate selected from literature-derived power-systems task taxonomy for short-circuit and relay-setting tasks.
  - Task bank v4 — REL-TASK-045; локатор: literature/task_bank_v4_gap_fill_balanced.md#rel-task-045; доверие: medium; примечание: Identifies short-circuit current calculation for breaker and relay settings as a benchmarkable protection engineering task.
  - Source card: breaker_relay_short_circuit; локатор: docs/source_cards/breaker_relay_short_circuit.md; доверие: medium; примечание: Documents the adaptation into an executable feeder short-circuit, breaker-rating, and relay-pickup selection task.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-045
  - source_evidence: docs/source_cards/breaker_relay_short_circuit.md
  - source card: docs/source_cards/breaker_relay_short_circuit.md

### commercial_pv_lcoe_uncertainty

- Идентификаторы: `commercial_pv_lcoe_uncertainty_public_001`, candidate `REL-TASK-059`
- Область: energy economics, planning & policy
- Назначение: Распределение LCOE коммерческой PV при неопределённости мягких затрат
- English objective: Compute commercial PV LCOE quantiles under soft-cost uncertainty
- Исходные данные: public_inputs: {candidate_id: REL-TASK-059; subdomain: energy economics, planning & policy; input_fields: список[3]: pv_lcoe_case.system_size_kw_dc, pv_lcoe_case.soft_cost_components_usd_per_kw, pv_lcoe_case.soft_cost_scenarios; calculation_spec: For each scenario, capex = system_size_kw * (hard_cost_usd_per_kw + sum(component_cost * scenario_multiplier)). LCOE…}; pv_lcoe_case: {system_size_kw_dc: 2000; hard_cost_usd_per_kw: 760; soft_cost_components_usd_per_kw: {permitting: 80; interconnection: 95; customer_acquisition: 45; engineering: 60}; capital_recovery_factor: 0.082; fixed_om_usd_per_kw_year: 18; annual_energy_mwh_year1: 3200; … ещё 1}
- Выход: scenario_lcoe_usd_per_mwh: object mapping scenario IDs to LCOE; lcoe_quantiles_usd_per_mwh: object with p10/p50/p90; expected_lcoe_usd_per_mwh: arithmetic mean across scenarios; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_commercial_pv_lcoe_uncertainty`; baseline: `baselines.commercial_pv_lcoe_uncertainty.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-059; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from literature-derived power-systems task taxonomy.
  - Executable public calculation instance; локатор: public task.json calculation_spec and case inputs; доверие: medium; примечание: Compact deterministic instance with independent evaluator and baseline.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-059
  - source card: docs/source_cards/commercial_pv_lcoe_uncertainty.md

### contingency_screening

- Идентификаторы: `contingency_screening_public_001`, candidate `GAP-TASK-005`
- Область: не указана
- Назначение: Быстрый скрининг аварий и обнаружение островного режима
- English objective: Rank N-1 branch outage contingencies by operational severity and flag outages that island the network.
- Исходные данные: public_inputs: {branches: список[4]: {id: …; from_bus: …; to_bus: …; … ещё 2}, {id: …; from_bus: …; to_bus: …; … ещё 2}, {id: …; from_bus: …; to_bus: …; … ещё 2}, {id: …; from_bus: …; to_bus: …; … ещё 2}; contingencies: список[4]: {id: …; outaged_branch: …; post_flows_mw: …}, {id: …; outaged_branch: …; post_flows_mw: …}, {id: …; outaged_branch: …; post_flows_mw: …}, {id: …; outaged_branch: …; post_flows_mw: …}; critical_loading_threshold_pct: 100.0}; branches: список[4]: {id: l12; from_bus: b1; to_bus: b2; … ещё 2}, {id: l23; from_bus: b2; to_bus: b3; … ещё 2}, {id: l13; from_bus: b1; to_bus: b3; … ещё 2}, {id: l34; from_bus: b3; to_bus: b4; … ещё 2}; contingencies: список[4]: {id: out_l12; outaged_branch: l12; post_flows_mw: {l23: …; l13: …; l34: …}}, {id: out_l23; outaged_branch: l23; post_flows_mw: {l12: …; l13: …; l34: …}}, {id: out_l13; outaged_branch: l13; post_flows_mw: {l12: …; l23: …; l34: …}}, {id: out_l34; outaged_branch: l34; post_flows_mw: {l12: …; l23: …; l13: …}}
- Выход: ranking: список / список[1]: ordered contingency IDs from most severe to least severe; islanding_flags: объект (<contingency_id>); rationale: optional string
- Проверка: `prototype.evaluators.evaluate_contingency_screening`; baseline: `baselines.contingency_screening.baseline`
- Источники:
  - Graph Computing based Fast Screening in Contingency Analysis; локатор: https://arxiv.org/abs/1904.00044v1; доверие: medium-strong; примечание: Supports fast screening of contingencies as an EMS/security-analysis task; public surrogate uses precomputed post-contingency flows while hidden variants can compute flows with a simulator.
  - Fast Grid Splitting Detection for N-1 Contingency Analysis by Graph Computing; локатор: https://arxiv.org/abs/1904.03587v1; доверие: medium-strong; примечание: Supports islanding/grid-splitting detection as part of N-1 contingency analysis.
  - v0 executable benchmark slice — GAP-TASK-005; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium-strong; примечание: Bilingual benchmark planning artifact selecting N-1 contingency screening and islanding detection for the executable v0 slice.
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#GAP-TASK-005
  - source_evidence: Graph Computing based Fast Screening in Contingency Analysis (arXiv:1904.00044v1)
  - source_evidence: Fast Grid Splitting Detection for N-1 Contingency Analysis by Graph Computing (arXiv:1904.03587v1)

### corrective_transmission_switching

- Идентификаторы: `corrective_transmission_switching_public_001`, candidate `GAP-TASK-002`
- Область: transmission operations, contingency & congestion management
- Назначение: Для послеаварийного состояния DC-сети с перегруженной ветвью выберите не более одного допустимого переключения, которое устранит все перегрузки без разделения сети на острова.
- English objective: Given a post-contingency DC network state with one overloaded branch, choose at most one candidate switching action that restores all emergency line limits without islanding.
- Исходные данные: public_inputs: {contingency: Branch l13 is out of service after the initiating contingency. Branch l14 is an available normally-open tie that may be…; dc_power_flow_model: Lossless DC model. Bus p_mw injections sum to zero. Branch flow is (theta_from - theta_to) / x_pu. Slack bus is the…; candidate_switches: Only branches listed in candidate_switches may be opened or closed. Use at most switching_budget actions.}; buses: список[4]: {id: b1; p_mw: 100.0}, {id: b2; p_mw: -20.0}, {id: b3; p_mw: -50.0}, {id: b4; p_mw: -30.0}; branches: список[6]: {id: l12; from_bus: b1; to_bus: b2; … ещё 4}, {id: l13; from_bus: b1; to_bus: b3; … ещё 4}, {id: l23; from_bus: b2; to_bus: b3; … ещё 4}, {id: l24; from_bus: b2; to_bus: b4; … ещё 4}, {id: l34; from_bus: b3; to_bus: b4; … ещё 4}, {id: l14; from_bus: b1; to_bus: b4; … ещё 4}; candidate_switches: список[4]: {branch_id: l14; action: close; cost: 1.0}, {branch_id: l23; action: open; cost: 1.0}, {branch_id: l24; action: open; cost: 1.0}, {branch_id: l34; action: open; cost: 1.0}; switching_budget: 1
- Выход: close_branches: list[str] of candidate branch ids to close; open_branches: list[str] of candidate branch ids to open; reported_flows_mw: optional object branch_id -> MW, diagnostic only; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_corrective_transmission_switching`; baseline: `baselines.corrective_transmission_switching.baseline`
- Источники:
  - Security Constrained Unit Commitment with Corrective Transmission Switching; локатор: https://arxiv.org/abs/2001.00597v1; summarized in literature/task_bank_v4_gap_fill_balanced.md#GAP-TASK-002; доверие: medium-strong; примечание: Supports the operational framing: post-contingency corrective switching can relieve security violations while preserving network feasibility. This public case is a compact DC power-flow adaptation, not a reproduction of the paper's full SCUC MILP.
  - V4 balanced core shortlist — GAP-TASK-002; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Selects corrective transmission switching as a balanced-core task family for transmission operations and contingency management.
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#gap-task-002
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md#transmission-operations-contingency--congestion-management
  - source_evidence: docs/source_cards/corrective_transmission_switching.md
  - source card: docs/source_cards/corrective_transmission_switching.md

### critical_clearing_time

- Идентификаторы: `critical_clearing_time_public_001`, candidate `REL-TASK-048`
- Область: stability & dynamics
- Назначение: Расчёт критического времени отключения по набору расчётов переходной устойчивости
- English objective: Compute critical clearing time from a transient-stability sweep
- Исходные данные: public_inputs: {stability_sweep: {max_angle_deg: 180.0; min_voltage_pu: 0.7; cases: список[5]: …, …, …, …, … ещё 1}}
- Выход: critical_clearing_time_s: largest clearing time that remains stable and satisfies angle/voltage thresholds; limiting_case: case_id of the last stable clearing-time case; stable_times_s: list of stable clearing times; unstable_times_s: list of unstable clearing times; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_critical_clearing_time`; baseline: `baselines.critical_clearing_time.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-048; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Literature-derived power-systems task topic converted into a public executable deterministic instance.
  - Bilingual executable benchmark slice requirement; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium; примечание: Supports maintaining English and Russian task presentation for benchmark artifacts.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-048
  - source card: docs/source_cards/critical_clearing_time.md

### dispatch_uncertainty

- Идентификаторы: `dispatch_uncertainty_public_001`, candidate `REL-TASK-015`
- Область: market/dispatch planning & uncertainty
- Назначение: Найти детерминированный график генерации, который покрывает худший сценарий чистой нагрузки с требуемым резервом в каждый момент времени.
- English objective: Find a deterministic schedule that covers the worst net-load scenario plus reserve at every time period.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-015; subdomain: market/dispatch planning & uncertainty; input_fields: список[3]: dispatch_uncertainty_case.generators, dispatch_uncertainty_case.scenarios, dispatch_uncertainty_case.reserve_requirement_mw}; dispatch_uncertainty_case: {time_periods: список[3]: t1, t2, t3; reserve_requirement_mw: 8.0; generators: список[2]: {id: …; pmin_mw: …; pmax_mw: …; … ещё 1}, {id: …; pmin_mw: …; pmax_mw: …; … ещё 1}; scenarios: список[3]: {id: …; load_mw: …; renewable_mw: …}, {id: …; load_mw: …; renewable_mw: …}, {id: …; load_mw: …; renewable_mw: …}}
- Выход: dispatch_mw: object mapping generator id to time-period MW values; worst_case_margin_mw: object mapping time period to total thermal generation minus maximum scenario net load; total_cost: sum of dispatch_mw multiplied by generator variable costs; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_dispatch_uncertainty`; baseline: `baselines.dispatch_uncertainty.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-015; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from market and dispatch planning under uncertainty.
  - Scenario robust economic dispatch; локатор: standard operational model: cover worst-case net load plus reserve while minimizing variable generation cost; доверие: medium; примечание: The public case uses a compact deterministic two-generator instance for executable evaluation.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-015
  - source card: docs/source_cards/dispatch_uncertainty.md

### distance_protection_settings

- Идентификаторы: `distance_protection_settings_public_001`, candidate `REL-TASK-039`
- Область: protection, faults & relay engineering
- Назначение: Рассчитайте уставки срабатывания и выдержки времени зон 1, 2 и 3 по сопротивлениям линии, удалённому резервированию и ограничению от нагрузочного режима.
- English objective: Compute Zone 1, Zone 2, and Zone 3 reach and delay settings from line impedances, remote backup lengths, and load-encroachment limits.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-039; subdomain: protection, faults & relay engineering; input_fields: список[4]: protection_case.protected_line, protection_case.remote_backup_lines, protection_case.maximum_load, protection_case.setting_rules}; protection_case: {voltage_kv: 110.0; protected_line: {id: L_AB; from_bus: A; to_bus: B; length_km: 80.0; … ещё 2}; remote_backup_lines: список[2]: {id: …; from_bus: …; to_bus: …; … ещё 3}, {id: …; from_bus: …; to_bus: …; … ещё 3}; maximum_load: {apparent_power_mva: 80.0; power_factor_lagging: 0.9}; setting_rules: {zone1_fraction: список[2]: …, …; zone1_max_delay_s: 0.05; zone2_backup_fraction: список[2]: …, …; zone2_delay_s: список[2]: …, …; … ещё 3}}
- Выход: zone1_ohm: float primary-ohm reach; zone2_ohm: float primary-ohm reach; zone3_ohm: float primary-ohm reach; zone1_delay_s: float seconds; zone2_delay_s: float seconds; zone3_delay_s: float seconds; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_distance_protection_settings`; baseline: `baselines.distance_protection_settings.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-039; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Balanced-core candidate selected from literature-derived power-systems task taxonomy for protection and relay engineering tasks.
  - Task bank v4 — REL-TASK-039; локатор: literature/task_bank_v4_gap_fill_balanced.md#rel-task-039; доверие: medium; примечание: Identifies distance protection setting calculation for 35–330 kV lines as a benchmarkable relay engineering task.
  - Source card: distance_protection_settings; локатор: docs/source_cards/distance_protection_settings.md; доверие: medium; примечание: Documents the adaptation into an executable relay-zone coordination and load-encroachment task.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-039
  - source_evidence: docs/source_cards/distance_protection_settings.md
  - source card: docs/source_cards/distance_protection_settings.md

### dynamic_thermal_rating

- Идентификаторы: `dynamic_thermal_rating_public_001`, candidate `REL-TASK-014`
- Область: transmission operations & asset ratings
- Назначение: Рассчитать предельный оперативный ток линии по короткому ряду погодных условий.
- English objective: Compute the limiting real-time ampacity over a short weather series.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-014; subdomain: transmission operations & asset ratings; input_fields: список[4]: thermal_rating_case.conductor, thermal_rating_case.thermal_limits, thermal_rating_case.weather_series, thermal_rating_case.scheduled_current_a}; thermal_rating_case: {scheduled_current_a: 520.0; conductor: {type: ACSR compact public case; diameter_mm: 22.4; resistance_ohm_per_km_at_20c: 0.118; resistance_temp_coeff_per_c: 0.00403; … ещё 2}; thermal_limits: {max_conductor_temperature_c: 75.0}; model_constants: {convective_w_per_m_c_at_1ms: 0.72}; weather_series: список[4]: {timestamp: …; ambient_temperature_c: …; wind_speed_m_s: …; … ещё 1}, {timestamp: …; ambient_temperature_c: …; wind_speed_m_s: …; … ещё 1}, {timestamp: …; ambient_temperature_c: …; wind_speed_m_s: …; … ещё 1}, {timestamp: …; ambient_temperature_c: …; wind_speed_m_s: …; … ещё 1}}
- Выход: ampacity_by_timestamp_a: object mapping timestamp to ampacity in amperes; minimum_ampacity_a: minimum ampacity over the weather series; limiting_timestamp: timestamp with the minimum ampacity; overload_timestamps: timestamps where scheduled_current_a exceeds the dynamic rating; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_dynamic_thermal_rating`; baseline: `baselines.dynamic_thermal_rating.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-014; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from the literature-derived transmission operations and asset-ratings taxonomy.
  - IEEE 738-style overhead-conductor heat balance; локатор: standard engineering model: Joule heat plus solar heat equals convective plus radiative cooling; доверие: medium; примечание: The public case uses a compact deterministic version of the standard heat-balance idea for executable evaluation.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-014
  - source card: docs/source_cards/dynamic_thermal_rating.md

### earth_fault_calculation

- Идентификаторы: `earth_fault_calculation_public_001`, candidate `REL-TASK-034`
- Область: protection, faults & relay engineering
- Назначение: Рассчитать токи прямой, обратной и нулевой последовательности, а также остаточный ток при однофазном замыкании на землю по сопротивлениям последовательностей.
- English objective: Calculate the sequence currents and residual current for a single-line-to-ground fault using sequence-network impedances.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-034; subdomain: protection, faults & relay engineering; input_fields: список[4]: earth_fault_case.base_mva, earth_fault_case.voltage_kv, earth_fault_case.sequence_impedances_pu, earth_fault_case.fault_resistance_pu}; earth_fault_case: {base_mva: 50.0; voltage_kv: 13.8; fault_type: single_line_to_ground_phase_a; prefault_phase_voltage_pu: 1.0; fault_resistance_pu: 0.04; sequence_impedances_pu: {positive: {r_pu: …; x_pu: …}; negative: {r_pu: …; x_pu: …}; zero: {r_pu: …; x_pu: …}}}
- Выход: sequence_currents_ka: object with i1, i2, i0; each contains mag_ka and angle_deg; fault_current_ka: object with mag_ka and angle_deg for 3*I0; residual_current_mag_ka: magnitude of 3I0 in kA; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_earth_fault_calculation`; baseline: `baselines.earth_fault_calculation.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-034; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from the literature-derived protection and fault-analysis taxonomy. The public artifact is now an executable sequence-network earth-fault calculation.
  - Symmetrical components method for single-line-to-ground faults; локатор: standard protection-engineering formula I1=I2=I0=V/(Z1+Z2+Z0+3Zf); доверие: medium; примечание: The benchmark instance uses the standard sequence-network relation for compact deterministic evaluation.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-034
  - source card: docs/source_cards/earth_fault_calculation.md

### electric_boiler_capacity_sizing

- Идентификаторы: `electric_boiler_capacity_sizing_public_001`, candidate `REL-TASK-055`
- Область: energy systems beyond electricity / heating
- Назначение: Выбор мощности электрокотла для поддержки теплоснабжения здания
- English objective: Size an electric boiler for building heat support
- Исходные данные: public_inputs: {candidate_id: REL-TASK-055; subdomain: energy systems beyond electricity / heating; input_fields: список[3]: boiler_capacity_case.design_hours, boiler_capacity_case.electric_boiler_efficiency, boiler_capacity_case.sizing_margin_fraction; calculation_spec: For each design hour compute residual_heat_kw_th=max(0, heat_load - heat_pump_heat - waste_heat). Size electric boiler…}; boiler_capacity_case: {electric_boiler_efficiency: 0.98; sizing_margin_fraction: 0.1; capacity_increment_kw: 5; feeder_boiler_capacity_limit_kw: 80; design_hours: {h1: {heat_load_kw_th: …; heat_pump_heat_kw_th: …; waste_heat_kw_th: …; heat_pump_electric_kw: …; … ещё 1}; h2: {heat_load_kw_th: …; heat_pump_heat_kw_th: …; waste_heat_kw_th: …; heat_pump_electric_kw: …; … ещё 1}; h3: {heat_load_kw_th: …; heat_pump_heat_kw_th: …; waste_heat_kw_th: …; heat_pump_electric_kw: …; … ещё 1}}}
- Выход: capacity_kw: electric input capacity of selected boiler; peak_residual_heat_kw_th: maximum residual thermal demand; feeder_peak_kw: peak feeder load with boiler; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_electric_boiler_capacity_sizing`; baseline: `baselines.electric_boiler_capacity_sizing.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-055; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from literature-derived power-systems task taxonomy.
  - Executable public calculation instance; локатор: public task.json calculation_spec and case inputs; доверие: medium; примечание: Compact deterministic instance with independent evaluator and baseline.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-055
  - source card: docs/source_cards/electric_boiler_capacity_sizing.md

### electric_boiler_step_control

- Идентификаторы: `electric_boiler_step_control_public_001`, candidate `REL-TASK-056`
- Область: energy systems beyond electricity / heating
- Назначение: Ступенчатое управление электрокотлом по температуре обратной воды
- English objective: Dispatch stepwise electric-boiler stages from return-water temperature
- Исходные данные: public_inputs: {candidate_id: REL-TASK-056; subdomain: energy systems beyond electricity / heating; input_fields: список[3]: boiler_step_control_case.measurements, boiler_step_control_case.available_stages_kw, boiler_step_control_case.return_temp_setpoint_c; calculation_spec: At each interval compute heat deficit=max(0,(setpoint-return_temp-deadband)*heat_deficit_kw_per_deg_c). Select the…}; boiler_step_control_case: {return_temp_setpoint_c: 55; deadband_c: 0.5; heat_deficit_kw_per_deg_c: 22; available_stages_kw: список[5]: 0, 25, 50, 75, … ещё 1; max_stage_change_per_interval: 2; interval_hours: 0.25; … ещё 1}
- Выход: control_steps: object mapping interval to stage_kw and corrected_return_temp_c; total_energy_kwh: boiler energy over all intervals; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_electric_boiler_step_control`; baseline: `baselines.electric_boiler_step_control.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-056; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from literature-derived power-systems task taxonomy.
  - Executable public calculation instance; локатор: public task.json calculation_spec and case inputs; доверие: medium; примечание: Compact deterministic instance with independent evaluator and baseline.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-056
  - source card: docs/source_cards/electric_boiler_step_control.md

### en50160_voltage_compliance

- Идентификаторы: `en50160_voltage_compliance_public_001`, candidate `REL-TASK-021`
- Область: distribution systems & DER/EV
- Назначение: Проверить, выполняют ли 10-минутные среднеквадратичные значения напряжения нормальные и абсолютные пределы, затем выбрать лучшую из заданных регулировок ответвления трансформатора.
- English objective: Check whether measured 10-minute RMS voltage values satisfy normal and absolute voltage limits, then choose the best listed tap correction.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-021; subdomain: distribution systems & DER/EV; input_fields: список[3]: voltage_compliance_case.voltage_series_pu, voltage_compliance_case.rules, voltage_compliance_case.mitigation_options}; voltage_compliance_case: {nominal_voltage_pu: 1.0; rules: {normal_lower_deviation_pu: -0.1; normal_upper_deviation_pu: 0.1; absolute_lower_deviation_pu: -0.15; absolute_upper_deviation_pu: 0.1; … ещё 1}; mitigation_options: {candidate_tap_changes_pu: список[4]: …, …, …, …}; voltage_series_pu: список[10]: {timestamp: …; voltage_pu: …}, {timestamp: …; voltage_pu: …}, {timestamp: …; voltage_pu: …}, {timestamp: …; voltage_pu: …}, … ещё 6}
- Выход: compliant: boolean compliance decision before mitigation; percent_within_normal_band: percentage of timestamps inside [0.90, 1.10] pu before mitigation; min_voltage_pu: minimum observed voltage; max_voltage_pu: maximum observed voltage; below_normal_timestamps: timestamps with voltage below 0.90 pu; above_normal_timestamps: timestamps with voltage above 1.10 pu; recommended_tap_change_pu: best additive tap correction from the listed options; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_en50160_voltage_compliance`; baseline: `baselines.en50160_voltage_compliance.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-021; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from the literature-derived distribution and power-quality taxonomy.
  - EN 50160 voltage characteristics; локатор: standard practice: 10-minute RMS supply voltage mostly within ±10% of nominal; доверие: medium; примечание: The public case uses a compact EN-50160-style threshold check rather than a full week of measurements.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-021
  - source card: docs/source_cards/en50160_voltage_compliance.md

### ev_v2g_outage_schedule

- Идентификаторы: `ev_v2g_outage_schedule_public_001`, candidate `REL-TASK-020`
- Область: distribution systems & DER/EV
- Назначение: Максимизировать энергию критической нагрузки, покрытую EV-флотом, с учётом ограничений зарядной мощности и резервного SOC.
- English objective: Maximize critical-load energy served by an EV fleet subject to charger power and reserve SOC constraints.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-020; subdomain: distribution systems & DER/EV; input_fields: список[2]: v2g_outage_case.critical_load_kw, v2g_outage_case.evs}; v2g_outage_case: {time_periods: список[3]: t1, t2, t3; interval_hours: 0.5; critical_load_kw: {t1: 10.0; t2: 12.0; t3: 9.0}; evs: {ev_a: {capacity_kwh: …; initial_soc_kwh: …; reserve_soc_kwh: …; charge_max_kw: …; … ещё 4}; ev_b: {capacity_kwh: …; initial_soc_kwh: …; reserve_soc_kwh: …; charge_max_kw: …; … ещё 4}}}
- Выход: dispatch_kw: object mapping timestamp to EV kW commands; served_energy_kwh: critical-load energy served over the event; final_soc_kwh: final EV SOC by ID; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_ev_v2g_outage_schedule`; baseline: `baselines.ev_v2g_outage_schedule.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-020; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from EV/V2G outage scheduling taxonomy.
  - V2G outage support scheduling practice; локатор: standard EV fleet energy-balance model with SOC reserve constraints; доверие: medium; примечание: Public case is a compact deterministic executable instance.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-020
  - source card: docs/source_cards/ev_v2g_outage_schedule.md

### ev_v2g_voltage_support

- Идентификаторы: `ev_v2g_voltage_support_public_001`, candidate `REL-TASK-017`
- Область: distribution systems & DER/EV
- Назначение: Использовать реактивную мощность EV-инверторов для повышения низких напряжений фидера к целевому уровню с учётом ограничений полной мощности.
- English objective: Use EV inverter reactive capability to raise low feeder voltages toward a target while respecting apparent-power limits.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-017; subdomain: distribution systems & DER/EV; input_fields: список[3]: v2g_voltage_support_case.base_voltage_pu, v2g_voltage_support_case.q_sensitivity_pu_per_kvar, v2g_voltage_support_case.evs}; v2g_voltage_support_case: {target_voltage_pu: 0.98; base_voltage_pu: {bus_2: 0.944; bus_3: 0.952}; q_sensitivity_pu_per_kvar: {bus_2: 0.0016; bus_3: 0.0012}; evs: {evse_1: {bus: …; s_rating_kva: …; active_power_kw: …}; evse_2: {bus: …; s_rating_kva: …; active_power_kw: …}; evse_3: {bus: …; s_rating_kva: …; active_power_kw: …}}}
- Выход: q_dispatch_kvar: object mapping bus to aggregate reactive command; corrected_voltage_pu: object mapping bus to voltage after support; total_abs_q_kvar: sum of absolute bus reactive commands; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_ev_v2g_voltage_support`; baseline: `baselines.ev_v2g_voltage_support.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-017; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from EV/V2G voltage support taxonomy.
  - EV inverter voltage support practice; локатор: standard Volt/VAR support with apparent-power capability; доверие: medium; примечание: Public case is a compact deterministic executable instance.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-017
  - source card: docs/source_cards/ev_v2g_voltage_support.md

### fault_section_localization

- Идентификаторы: `fault_section_localization_public_001`, candidate `REL-TASK-052`
- Область: distribution reliability & outage management
- Назначение: Использовать состояния FCI и жалобы об отключениях для определения наиболее вероятного повреждённого участка радиального фидера.
- English objective: Use FCI states and outage complaints to infer the most likely faulted radial feeder section.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-052; subdomain: distribution reliability & outage management; input_fields: список[4]: fault_localization_case.sections, fault_localization_case.fci_locations, fault_localization_case.observed_fci_state, fault_localization_case.outage_complaint_nodes; calculation_spec: For each candidate faulted section, derive which upstream FCI locations should see fault current and which downstream…}; fault_localization_case: {source_node: n0; nodes: список[6]: n0, n1, n2, n3, … ещё 2; customer_nodes: список[4]: n2, n3, n4, n5; sections: {s01: {from: …; to: …}; s12: {from: …; to: …}; s23: {from: …; to: …}; s24: {from: …; to: …}; … ещё 1}; fci_locations: {fci_n1: n1; fci_n2: n2; fci_n4: n4}; observed_fci_state: {fci_n1: True; fci_n2: True; fci_n4: True}; … ещё 1}
- Выход: faulted_section: section ID; affected_customer_nodes: list of downstream customer nodes; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_fault_section_localization`; baseline: `baselines.fault_section_localization.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-052; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from distribution reliability taxonomy.
  - FCI-based fault section localization practice; локатор: radial feeder upstream indicator/downstream complaint model; доверие: medium; примечание: Public case is a compact deterministic executable instance.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-052
  - source card: docs/source_cards/fault_section_localization.md

### fci_placement

- Идентификаторы: `fci_placement_public_001`, candidate `REL-TASK-051`
- Область: distribution reliability & outage management
- Назначение: Выбрать ограниченное бюджетом множество мест установки индикаторов повреждения, чтобы снизить ожидаемые клиент-минуты отключений из-за времени обхода.
- English objective: Select a budgeted set of fault-current-indicator locations to reduce expected customer interruption minutes caused by patrol time.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-051; subdomain: distribution reliability & outage management; input_fields: список[3]: fci_placement_case.budget, fci_placement_case.fault_sections, fci_placement_case.candidate_locations; calculation_spec: Enumerate candidate sets of size budget. For each fault section, take the maximum section_gain_minutes among selected…}; fci_placement_case: {budget: 2; fault_sections: {s12: {annual_fault_rate: …; customers_interrupted: …}; s23: {annual_fault_rate: …; customers_interrupted: …}; s24: {annual_fault_rate: …; customers_interrupted: …}; s45: {annual_fault_rate: …; customers_interrupted: …}}; candidate_locations: {n1: {section_gain_minutes: …}; n2: {section_gain_minutes: …}; n4: {section_gain_minutes: …}; n3: {section_gain_minutes: …}}}
- Выход: selected_locations: list of selected FCI location IDs; expected_customer_minutes_saved: annual customer-minutes saved; section_patrol_time_reduction_min: object mapping section ID to selected patrol-time reduction; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_fci_placement`; baseline: `baselines.fci_placement.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-051; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from distribution reliability taxonomy.
  - FCI placement and patrol-time reduction practice; локатор: customer-weighted reliability planning model; доверие: medium; примечание: Public case is a compact deterministic executable instance.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-051
  - source card: docs/source_cards/fci_placement.md

### fci_saidi_caidi

- Идентификаторы: `fci_saidi_caidi_public_001`, candidate `REL-TASK-053`
- Область: distribution reliability & outage management
- Назначение: Рассчитать показатели надёжности до и после сокращения времени восстановления за счёт FCI.
- English objective: Calculate reliability indices before and after FCI-based restoration-time reductions.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-053; subdomain: distribution reliability & outage management; input_fields: список[4]: fci_reliability_case.total_customers, fci_reliability_case.fault_sections, fci_reliability_case.deployed_fci_locations, fci_reliability_case.fci_locations; calculation_spec: Baseline customer-minutes/year = sum(annual_fault_rate * customers_interrupted * base_restoration_minutes). With FCI,…}; fci_reliability_case: {total_customers: 320; minimum_restoration_minutes: 25; deployed_fci_locations: список[2]: n2, n4; fault_sections: {s12: {annual_fault_rate: …; customers_interrupted: …; base_restoration_minutes: …}; s23: {annual_fault_rate: …; customers_interrupted: …; base_restoration_minutes: …}; s24: {annual_fault_rate: …; customers_interrupted: …; base_restoration_minutes: …}; s45: {annual_fault_rate: …; customers_interrupted: …; base_restoration_minutes: …}}; fci_locations: {n2: {restoration_time_reduction_min: …}; n4: {restoration_time_reduction_min: …}}}
- Выход: baseline: object with SAIDI/CAIDI/SAIFI; with_fci: object with SAIDI/CAIDI/SAIFI after FCI reductions; saidi_improvement_min_per_customer_year: baseline SAIDI minus with-FCI SAIDI; caidi_improvement_min_per_interruption: baseline CAIDI minus with-FCI CAIDI; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_fci_saidi_caidi`; baseline: `baselines.fci_saidi_caidi.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-053; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from distribution reliability taxonomy.
  - Distribution reliability index definitions; локатор: standard SAIDI/SAIFI/CAIDI definitions; доверие: medium; примечание: Public case is a compact deterministic executable instance.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-053
  - source card: docs/source_cards/fci_saidi_caidi.md

### fdi_state_estimation

- Идентификаторы: `fdi_state_estimation_public_001`, candidate `GAP-TASK-006`
- Область: не указана
- Назначение: Обнаружение FDI-атаки в оценивании состояния
- English objective: Identify false-data-injection attacked measurements and provide a corrected DC state estimate with bounded angle error.
- Исходные данные: public_inputs: {residual_threshold: 3.0; state_error_threshold: 0.05; measurements: список[4]: {id: …; residual_norm: …; ground_truth_attack: …}, {id: …; residual_norm: …; ground_truth_attack: …}, {id: …; residual_norm: …; ground_truth_attack: …}, {id: …; residual_norm: …; ground_truth_attack: …}; state_variables: список[2]: theta_2, theta_3}
- Выход: attacked_measurements: List of measurement IDs classified as attacked/corrupted.; corrected_state: Object mapping state-variable names to corrected numeric estimates.; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_fdi_state_estimation`; baseline: `baselines.fdi_state_estimation.baseline`
- Источники:
  - Modeling and performance evaluation of stealthy false data injection attacks on smart grid in the presence of corrupted measurements; локатор: arXiv:1605.06180v1; selected in literature/v0_executable_benchmark_slice.en.md as GAP-TASK-006; доверие: strong; примечание: Primary FDI/state-estimation source motivating corrupted-measurement attack modeling and detection evaluation.
  - Graphical Methods for Defense Against False-data Injection Attacks on Power System State Estimation; локатор: arXiv:1304.4151v4; selected in literature/v0_executable_benchmark_slice.en.md as GAP-TASK-006; доверие: strong; примечание: Classic state-estimation FDI defense source supporting detection/localization style metrics.
  - v0 executable benchmark slice — GAP-TASK-006; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: strong; примечание: Bilingual benchmark planning artifact selecting FDI state-estimation detection for the executable v0 slice.
  - source_evidence: literature/v0_executable_benchmark_slice.en.md#GAP-TASK-006
  - source_evidence: https://arxiv.org/abs/1605.06180v1
  - source_evidence: https://arxiv.org/abs/1304.4151v4

### flisr_restoration

- Идентификаторы: `flisr_restoration_public_001`, candidate `REL-TASK-003`
- Область: не указана
- Назначение: Децентрализованное восстановление сети после короткого замыкания
- English objective: Choose a switching plan that isolates a faulted distribution feeder section, keeps the energized network radial, and restores high-priority load through available tie switches.
- Исходные данные: public_inputs: {source_bus: s; faulted_branches: список[1]: l23; buses: список[5]: {id: …; load_kw: …; priority: …}, {id: …; load_kw: …; priority: …}, {id: …; load_kw: …; priority: …}, {id: …; load_kw: …; priority: …}, … ещё 1; branches: список[5]: {id: …; from_bus: …; to_bus: …; … ещё 2}, {id: …; from_bus: …; to_bus: …; … ещё 2}, {id: …; from_bus: …; to_bus: …; … ещё 2}, {id: …; from_bus: …; to_bus: …; … ещё 2}, … ещё 1}; buses: список[5]: {id: s; load_kw: 0.0; priority: 0}, {id: b1; load_kw: 0.0; priority: 0}, {id: b2; load_kw: 50.0; priority: 3}, {id: b3; load_kw: 80.0; priority: 5}, {id: b4; load_kw: 40.0; priority: 2}; branches: список[5]: {id: l_s1; from_bus: s; to_bus: b1; … ещё 2}, {id: l12; from_bus: b1; to_bus: b2; … ещё 2}, {id: l23; from_bus: b2; to_bus: b3; … ещё 2}, {id: l34; from_bus: b3; to_bus: b4; … ещё 2}, {id: tie_24; from_bus: b2; to_bus: b4; … ещё 2}
- Выход: open_switches: List of branch/switch IDs to open before restoration.; close_switches: List of normally-open tie switch IDs to close for restoration.; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_flisr_restoration`; baseline: `baselines.flisr_restoration.baseline`
- Источники:
  - A Two-Stage Service Restoration Method for Electric Power Distribution Systems; локатор: arXiv:2004.07921v1; selected in literature/v0_executable_benchmark_slice.en.md as GAP-TASK-003; доверие: medium-strong; примечание: Primary source for distribution service-restoration / feeder reconfiguration task structure with switching actions and restored-load objective.
  - v0 executable benchmark slice — GAP-TASK-003; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: strong; примечание: Bilingual benchmark planning artifact selecting FLISR restoration for the executable v0 slice.
  - source_evidence: literature/v0_executable_benchmark_slice.en.md#GAP-TASK-003
  - source_evidence: https://arxiv.org/abs/2004.07921v1

### frt_compliance

- Идентификаторы: `frt_compliance_public_001`, candidate `GAP-TASK-011`
- Область: не указана
- Назначение: Проверка соответствия IBR требованиям FRT сетевого кодекса
- English objective: Check whether an inverter-based resource event trace remains connected inside a voltage/time ride-through envelope and provides required reactive current support during a voltage sag.
- Исходные данные: public_inputs: {ride_through_curve: список[3]: {max_duration_s: …; min_voltage_pu: …}, {max_duration_s: …; min_voltage_pu: …}, {max_duration_s: …; min_voltage_pu: …}; reactive_current_requirement: {voltage_below_pu: 0.9; min_iq_pu: 0.2; response_deadline_s: 0.1}; event_trace: список[5]: {time_s: …; voltage_pu: …; iq_pu: …; … ещё 1}, {time_s: …; voltage_pu: …; iq_pu: …; … ещё 1}, {time_s: …; voltage_pu: …; iq_pu: …; … ещё 1}, {time_s: …; voltage_pu: …; iq_pu: …; … ещё 1}, … ещё 1}
- Выход: declared_compliant: Boolean compliance declaration for the supplied event trace.; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_frt_compliance`; baseline: `baselines.frt_compliance.baseline`
- Источники:
  - Grid-Forming Control Based On Emulated Synchronous Condenser Strategy Compliant With Challenging Grid Code Requirements; локатор: arXiv:2303.00391v2; selected in literature/v0_executable_benchmark_slice.en.md as GAP-TASK-011; доверие: medium-strong; примечание: Source motivating grid-code-compliance checks for inverter-based resources under challenging voltage/frequency events.
  - A Novel Decentralized Inverter Control Algorithm for Loss Minimization and LVRT Improvement; локатор: arXiv:2207.11700v3; selected in literature/v0_executable_benchmark_slice.en.md as GAP-TASK-011; доверие: medium-strong; примечание: Source supporting LVRT/FRT-style inverter response evaluation.
  - v0 executable benchmark slice — GAP-TASK-011; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: strong; примечание: Bilingual benchmark planning artifact selecting grid-code FRT compliance for the executable v0 slice.
  - source_evidence: literature/v0_executable_benchmark_slice.en.md#GAP-TASK-011
  - source_evidence: https://arxiv.org/abs/2303.00391v2
  - source_evidence: https://arxiv.org/abs/2207.11700v3

### hydro_thermal_storage_uc

- Идентификаторы: `hydro_thermal_storage_uc_public_001`, candidate `GAP-TASK-013`
- Область: generation scheduling: hydro, thermal & storage
- Назначение: Решить компактный UC гидро/тепло/накопитель с ограничением выбросов
- English objective: Solve compact hydro/thermal/storage unit commitment with emissions cap
- Исходные данные: public_inputs: {uc_case: {emission_cap_ton: 200; hours: список[3]: …, …, …; thermal_units: список[2]: …, …}}
- Выход: thermal_dispatch_mw: dispatch by hour and unit; total_cost_usd: production cost; emissions_ton: total emissions; emission_cap_satisfied: boolean; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_hydro_thermal_storage_uc`; baseline: `baselines.hydro_thermal_storage_uc.baseline`
- Источники:
  - V4 balanced core shortlist — GAP-TASK-013; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Literature-derived power-systems task topic converted into a public executable deterministic instance.
  - Bilingual executable benchmark slice requirement; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium; примечание: Supports maintaining English and Russian task presentation for benchmark artifacts.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#gap-task-013
  - source card: docs/source_cards/hydro_thermal_storage_uc.md

### ibr_short_circuit_frt

- Идентификаторы: `ibr_short_circuit_frt_public_001`, candidate `GAP-TASK-012`
- Область: grid codes, interconnection & standards compliance
- Назначение: Рассчитать ограниченный по току вклад IBR в КЗ при FRT-управлении
- English objective: Compute current-limited IBR short-circuit response under FRT control
- Исходные данные: public_inputs: {ibr_frt_case: {current_limit_pu: 1.2; prefault_active_current_pu: 0.92; reactive_deadband_pu: 0.9; k_reactive_current_pu_per_pu: 2.0; … ещё 3}}
- Выход: current_profile_pu: object mapping sample_id to id_pu, iq_pu, total_current_pu; min_reactive_current_pu: minimum iq_pu over the samples; max_total_current_pu: maximum current magnitude over the samples; frt_compliant: boolean ride-through/reactive-current compliance result; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_ibr_short_circuit_frt`; baseline: `baselines.ibr_short_circuit_frt.baseline`
- Источники:
  - V4 balanced core shortlist — GAP-TASK-012; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Literature-derived power-systems task topic converted into a public executable deterministic instance.
  - Bilingual executable benchmark slice requirement; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium; примечание: Supports maintaining English and Russian task presentation for benchmark artifacts.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#gap-task-012
  - source card: docs/source_cards/ibr_short_circuit_frt.md

### islanded_microgrid_pq_dispatch

- Идентификаторы: `islanded_microgrid_pq_dispatch_public_001`, candidate `REL-TASK-022`
- Область: microgrids & DER dispatch
- Назначение: Сбалансировать активную и реактивную нагрузку с учётом полной мощности инвертора и допустимых напряжений.
- English objective: Balance active and reactive demand while respecting inverter apparent-power capability and maintaining voltage limits.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-022; subdomain: microgrids & DER dispatch; input_fields: список[4]: islanded_pq_case.load, islanded_pq_case.diesel, islanded_pq_case.inverter, islanded_pq_case.voltage_model}; islanded_pq_case: {load: {p_mw: 34.0; q_mvar: 12.0}; diesel: {pmin_mw: 8.0; pmax_mw: 45.0; qmin_mvar: -10.0; qmax_mvar: 18.0; … ещё 3}; inverter: {p_available_mw: 20.0; s_rating_mva: 24.0}; voltage_model: {base_voltage_pu: 0.965; sensitivity_pu_per_mvar: 0.0025; vmin_pu: 0.95; vmax_pu: 1.05}}
- Выход: dispatch: object with diesel and inverter P/Q values; voltage_pu: computed island voltage; total_cost: diesel active cost plus reactive deviation penalty; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_islanded_microgrid_pq_dispatch`; baseline: `baselines.islanded_microgrid_pq_dispatch.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-022; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from islanded microgrid P/Q dispatch taxonomy.
  - Islanded microgrid P/Q dispatch practice; локатор: standard active/reactive balance with inverter capability and voltage sensitivity; доверие: medium; примечание: Public case is a compact deterministic executable instance.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-022
  - source card: docs/source_cards/islanded_microgrid_pq_dispatch.md

### mas_frequency_handover

- Идентификаторы: `mas_frequency_handover_public_001`, candidate `REL-TASK-001`
- Область: grid operations & control / MAS
- Назначение: Классифицировать состояние частоты MAS и выбрать передачу ведущей станции
- English objective: Classify MAS frequency state and choose lead-station handover
- Исходные данные: public_inputs: {mas_handover_case: {nominal_hz: 50; frequency_hz: 49.82; alert_deviation_hz: 0.1; emergency_deviation_hz: 0.3; … ещё 4}}
- Выход: frequency_state: normal/alert/emergency; lead_agent: selected regulating agent; handover_required: boolean; lead_headroom_mw: available upward/downward headroom; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_mas_frequency_handover`; baseline: `baselines.mas_frequency_handover.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-001; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Literature-derived power-systems task topic converted into a public executable deterministic instance.
  - Bilingual executable benchmark slice requirement; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium; примечание: Supports maintaining English and Russian task presentation for benchmark artifacts.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-001
  - source card: docs/source_cards/mas_frequency_handover.md

### microgrid_economic_dispatch

- Идентификаторы: `microgrid_economic_dispatch_public_001`, candidate `REL-TASK-024`
- Область: microgrids & DER dispatch
- Назначение: Задать дизельную генерацию и батарею для покрытия нагрузки с PV при минимальной стоимости дизеля.
- English objective: Dispatch diesel generation and a battery to serve load with PV at minimum diesel cost.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-024; subdomain: microgrids & DER dispatch; input_fields: список[4]: microgrid_dispatch_case.load_mw, microgrid_dispatch_case.pv_mw, microgrid_dispatch_case.generator, microgrid_dispatch_case.battery}; microgrid_dispatch_case: {time_periods: список[3]: t1, t2, t3; interval_hours: 1.0; load_mw: {t1: 45.0; t2: 62.0; t3: 50.0}; pv_mw: {t1: 10.0; t2: 8.0; t3: 18.0}; generator: {id: diesel; pmin_mw: 15.0; pmax_mw: 70.0; variable_cost_per_mwh: 85.0}; battery: {initial_soc_mwh: 18.0; soc_min_mwh: 6.0; soc_max_mwh: 30.0; charge_pmax_mw: 8.0; … ещё 4}}
- Выход: dispatch: object mapping timestamp to diesel_mw, battery_mw, pv_curtailment_mw, soc_mwh, shed_mw; total_cost: diesel energy cost over the horizon; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_microgrid_economic_dispatch`; baseline: `baselines.microgrid_economic_dispatch.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-024; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from microgrid dispatch taxonomy.
  - Microgrid economic dispatch practice; локатор: standard diesel/PV/battery active-power balance and least-cost scheduling model; доверие: medium; примечание: Public case is a compact executable instance with deterministic enumeration.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-024
  - source card: docs/source_cards/microgrid_economic_dispatch.md

### min_synchronous_share

- Идентификаторы: `min_synchronous_share_public_001`, candidate `REL-TASK-007`
- Область: converter-dominated grids & storage
- Назначение: Найти минимальную долю синхронных машин при ограничениях по инерции и SCR
- English objective: Find the minimum synchronous-machine share satisfying inertia and SCR constraints
- Исходные данные: public_inputs: {synchronous_share_case: {demand_mw: 1000.0; ibr_capacity_mva: 720.0; nominal_frequency_hz: 50.0; largest_loss_mw: 180.0; … ещё 4}}
- Выход: online_units: minimum-share feasible list of synchronous unit IDs; min_synchronous_share_pct: online synchronous MW divided by demand MW; system_inertia_gws: sum(H_s * P_MW) / 1000; rocof_hz_per_s: largest_loss_mw / (2 * inertia_GWs * nominal_frequency_hz * 1000); short_circuit_ratio: (grid base + online unit short-circuit MVA) / IBR MVA; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_min_synchronous_share`; baseline: `baselines.min_synchronous_share.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-007; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Literature-derived power-systems task topic converted into a public executable deterministic instance.
  - Bilingual executable benchmark slice requirement; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium; примечание: Supports maintaining English and Russian task presentation for benchmark artifacts.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-007
  - source card: docs/source_cards/min_synchronous_share.md

### operator_breaker_load_actions

- Идентификаторы: `operator_breaker_load_actions_public_001`, candidate `REL-TASK-050`
- Область: grid operations & control / restoration
- Назначение: Выбрать действия оператора с выключателями/нагрузкой для снятия перегрузок
- English objective: Select operator breaker/load actions that remove overloads with minimal shedding
- Исходные данные: public_inputs: {operator_action_case: {max_actions: 2; max_shed_mw: 25; branches: список[3]: …, …, …; candidate_actions: список[3]: …, …, …}}
- Выход: selected_actions: action ids; load_shed_mw: shed load; post_action_flows_mw: branch flows after actions; all_limits_satisfied: boolean; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_operator_breaker_load_actions`; baseline: `baselines.operator_breaker_load_actions.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-050; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Literature-derived power-systems task topic converted into a public executable deterministic instance.
  - Bilingual executable benchmark slice requirement; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium; примечание: Supports maintaining English and Russian task presentation for benchmark artifacts.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-050
  - source card: docs/source_cards/operator_breaker_load_actions.md

### overcurrent_protection

- Идентификаторы: `overcurrent_protection_public_001`, candidate `REL-TASK-036`
- Область: не указана
- Назначение: Уставки максимальной токовой защиты линии
- English objective: Choose line overcurrent relay pickup current and time delay that avoid load operation, operate for minimum internal faults, and coordinate with downstream protection.
- Исходные данные: public_inputs: {max_load_current_a: 420.0; min_fault_current_a: 1800.0; ct_ratio_primary_per_secondary: 100.0; load_margin_multiplier: 1.2; min_sensitivity_factor: 1.5; downstream_time_delay_s: 0.35; … ещё 3}
- Выход: pickup_current_a: primary pickup current in amperes; time_delay_s: intentional time delay in seconds; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_overcurrent_protection`; baseline: `baselines.overcurrent_protection.baseline`
- Источники:
  - РЕЛЕЙНАЯ ЗАЩИТА В ЗАДАЧАХ С РЕШЕНИЯМИ И ПРИМЕРАМИ; локатор: literature/extracted_text/all_local_archive/РЕЛЕЙНАЯ ЗАЩИТА В ЗАДАЧАХ С РЕШЕНИЯМИ И ПРИМЕРАМИ_bed306ea.txt:548-558; доверие: strong; примечание: The extracted table of contents explicitly identifies maximum non-directional/directional current protections and line-protection sections; task bank REL-TASK-036 maps this to line overcurrent protection setting.
  - Релейная защита. Томск; локатор: literature/extracted_text/all_local_archive/Релейная защита. Томск_3f3d000a.txt:5915-5917,6594-6597,6802-6804; доверие: medium-strong; примечание: Supports current relay pickup conversion through CT ratio, selectivity time-delay requirements, and the distinction between overcurrent protection and current cutoff.
  - v0 executable benchmark slice — REL-TASK-036; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: strong; примечание: Bilingual benchmark planning artifact selecting line overcurrent protection setting for the executable v0 slice.
  - source_evidence: literature/task_bank_v2_reliable_source_mining.md#REL-TASK-036
  - source_evidence: literature/extracted_text/all_local_archive/РЕЛЕЙНАЯ ЗАЩИТА В ЗАДАЧАХ С РЕШЕНИЯМИ И ПРИМЕРАМИ_bed306ea.txt:548-558
  - source_evidence: literature/extracted_text/all_local_archive/Релейная защита. Томск_3f3d000a.txt:5915-5917,6594-6597,6802-6804

### pf_voltage_repair

- Идентификаторы: `pf_voltage_repair_public_001`, candidate `REL-TASK-046`
- Область: не указана
- Назначение: Расчет AC power flow и диагностика нарушений
- English objective: Choose corrective reactive-power actions that remove voltage violations at minimum cost.
- Исходные данные: public_inputs: {base_voltage_pu: {bus_1: 1.0; bus_2: 0.925}; limits: {min_vm_pu: 0.95; max_vm_pu: 1.05}; sensitivities: {bus_2: {q_cap_mvar: …}}; action_bounds: {q_cap_mvar: {min: …; max: …; cost_per_unit: …}}}
- Выход: actions: объект (<bus_id>); rationale: optional string
- Проверка: `prototype.evaluators.evaluate_voltage_repair`; baseline: `baselines.pf_voltage_repair.baseline`
- Источники:
  - Power System Analysis and Design / AC power-flow formulation; локатор: literature/extracted_text/all_local_archive/Power System Analysis and Design_030246bc.txt:2502-2512; literature/v0_executable_benchmark_slice.en.md#REL-TASK-046; доверие: strong; примечание: Supports AC power-flow solve and violation diagnosis as a domain task; public evaluator is a lightweight linear-sensitivity surrogate for the future pandapower hidden evaluator.
  - v0 executable benchmark slice — REL-TASK-046; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: strong; примечание: Bilingual benchmark planning artifact selecting AC PF diagnosis / voltage repair for v0 and recording the source requirement.
  - source_evidence: literature/task_bank_v0_from_local_archive.md#1-ac-load-flow-correction--voltage-violation-repair
  - source_evidence: Power System Analysis and Design
  - source_evidence: Advanced Prediction Techniques Applied to Smart Grids

### power_quality_event_classification

- Идентификаторы: `power_quality_event_classification_public_001`, candidate `GAP-TASK-008`
- Область: power quality & standards
- Назначение: Классифицировать провал напряжения, перенапряжение, прерывание или нормальный режим по ряду среднеквадратичных значений.
- English objective: Classify a voltage sag, swell, interruption, or normal condition from an RMS trace.
- Исходные данные: public_inputs: {candidate_id: GAP-TASK-008; subdomain: power quality & standards; input_fields: список[2]: power_quality_case.rms_trace, power_quality_case.classification_rules}; power_quality_case: {nominal_voltage_pu: 1.0; sample_interval_ms: 20; classification_rules: {interruption_upper_pu: 0.1; sag_lower_pu: 0.1; sag_upper_pu: 0.9; swell_lower_pu: 1.1}; rms_trace: список[8]: {timestamp_ms: …; voltage_pu: …; current_pu: …}, {timestamp_ms: …; voltage_pu: …; current_pu: …}, {timestamp_ms: …; voltage_pu: …; current_pu: …}, {timestamp_ms: …; voltage_pu: …; current_pu: …}, … ещё 4}
- Выход: event_class: one of normal, voltage_sag, voltage_swell, interruption; start_timestamp_ms: first timestamp of the non-normal interval; end_timestamp_ms: last timestamp of the non-normal interval; duration_s: event duration in seconds, inclusive of one sample interval; min_voltage_pu: minimum voltage in the trace; max_current_pu: maximum current in the trace; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_power_quality_event_classification`; baseline: `baselines.power_quality_event_classification.baseline`
- Источники:
  - V4 balanced core shortlist — GAP-TASK-008; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Gap-fill task selected for power-quality event classification.
  - IEC 61000-4-30 / power-quality event threshold practice; локатор: standard engineering categories: sag, swell, and interruption by RMS voltage thresholds; доверие: medium; примечание: The public case uses compact threshold rules for deterministic executable evaluation.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#gap-task-008
  - source card: docs/source_cards/power_quality_event_classification.md

### protected_meter_placement

- Идентификаторы: `protected_meter_placement_public_001`, candidate `GAP-TASK-007`
- Область: OT cybersecurity, state estimation & bad data
- Назначение: Разместить защищенные измерители для максимального покрытия FDI-векторов
- English objective: Place protected meters to maximize FDI attack-vector coverage
- Исходные данные: public_inputs: {meter_placement_case: {budget: 2; candidate_meters: список[4]: …, …, …, …; attack_vectors: список[4]: …, …, …, …}}
- Выход: protected_meters: selected meter ids; covered_attack_vectors: covered attack ids; covered_risk_weight: sum risk weights covered; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_protected_meter_placement`; baseline: `baselines.protected_meter_placement.baseline`
- Источники:
  - V4 balanced core shortlist — GAP-TASK-007; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Literature-derived power-systems task topic converted into a public executable deterministic instance.
  - Bilingual executable benchmark slice requirement; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium; примечание: Supports maintaining English and Russian task presentation for benchmark artifacts.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#gap-task-007
  - source card: docs/source_cards/protected_meter_placement.md

### pv_soft_cost_sobol

- Идентификаторы: `pv_soft_cost_sobol_public_001`, candidate `REL-TASK-058`
- Область: energy economics, planning & policy
- Назначение: Соболевская чувствительность драйверов мягких затрат PV
- English objective: Compute Sobol sensitivity indices for PV soft-cost drivers
- Исходные данные: public_inputs: {candidate_id: REL-TASK-058; subdomain: energy economics, planning & policy; input_fields: список[3]: pv_soft_cost_sobol_case.variables, pv_soft_cost_sobol_case.linear_effect_usd_per_kw, pv_soft_cost_sobol_case.interaction_effect_usd_per_kw; calculation_spec: Enumerate all 0/1 combinations of independent soft-cost drivers. Model output = base + sum(linear_effect_i*x_i) +…}; pv_soft_cost_sobol_case: {variables: список[4]: interconnection, permitting, labor, sales_tax; base_soft_cost_usd_per_kw: 260; linear_effect_usd_per_kw: {interconnection: 85; permitting: 58; labor: 42; sales_tax: 25}; interaction_effect_usd_per_kw: {interconnection*permitting: 18; permitting*labor: 10}}
- Выход: first_order_indices: object mapping variable to first-order Sobol index; total_order_indices: object mapping variable to total-order Sobol index; sensitivity_ranking: variables sorted by descending first-order index; output_variance: population variance of model output; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_pv_soft_cost_sobol`; baseline: `baselines.pv_soft_cost_sobol.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-058; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from literature-derived power-systems task taxonomy.
  - Executable public calculation instance; локатор: public task.json calculation_spec and case inputs; доверие: medium; примечание: Compact deterministic instance with independent evaluator and baseline.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-058
  - source card: docs/source_cards/pv_soft_cost_sobol.md

### pv_volt_var

- Идентификаторы: `pv_volt_var_public_001`, candidate `GAP-TASK-009`
- Область: не указана
- Назначение: Управление реактивной мощностью PV для устранения провалов/повышений напряжения
- English objective: Choose a monotonic PV inverter Volt-VAR curve that mitigates low-voltage sag and high-voltage swell over a short feeder time series without exceeding inverter reactive-power capability.
- Исходные данные: public_inputs: {voltage_limits_pu: {min: 0.95; max: 1.05}; timesteps: список[3]: {id: …; base_voltage_pu: …; pv_kw: …; … ещё 2}, {id: …; base_voltage_pu: …; pv_kw: …; … ещё 2}, {id: …; base_voltage_pu: …; pv_kw: …; … ещё 2}}
- Выход: volt_var_curve: List of points with strictly increasing voltage_pu and monotonic non-increasing q_fraction in [-1, 1]. Positive q_fraction injects reactive power; negative absorbs reactive power.; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_pv_volt_var`; baseline: `baselines.pv_volt_var.baseline`
- Источники:
  - Local Control of Reactive Power by Distributed Photovoltaic Generators; локатор: arXiv:1006.0160v1; selected in literature/v0_executable_benchmark_slice.en.md as GAP-TASK-009; доверие: strong; примечание: Primary PV reactive-power control source motivating local inverter Q control for distribution-voltage regulation.
  - Options for Control of Reactive Power by Distributed Photovoltaic Generators; локатор: arXiv:1008.0878v1; selected in literature/v0_executable_benchmark_slice.en.md as GAP-TASK-009; доверие: strong; примечание: Supports comparing Volt-VAR style local reactive-power control options for PV generators.
  - v0 executable benchmark slice — GAP-TASK-009; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: strong; примечание: Bilingual benchmark planning artifact selecting PV Volt-VAR control for the executable v0 slice.
  - source_evidence: literature/v0_executable_benchmark_slice.en.md#GAP-TASK-009
  - source_evidence: https://arxiv.org/abs/1006.0160v1
  - source_evidence: https://arxiv.org/abs/1008.0878v1

### rolling_microgrid_dispatch

- Идентификаторы: `rolling_microgrid_dispatch_public_001`, candidate `REL-TASK-026`
- Область: microgrids & DER dispatch
- Назначение: Задать батарею и дизельный агрегат на коротких интервалах с сохранением SOC и минимизацией стоимости дизеля.
- English objective: Dispatch a battery and diesel unit across short intervals while preserving SOC and minimizing diesel cost.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-026; subdomain: microgrids & DER dispatch; input_fields: список[4]: rolling_microgrid_dispatch_case.load_mw, rolling_microgrid_dispatch_case.pv_mw, rolling_microgrid_dispatch_case.generator, rolling_microgrid_dispatch_case.battery}; rolling_microgrid_dispatch_case: {time_periods: список[4]: t00, t05, t10, t15; interval_hours: 0.0833333333; load_mw: {t00: 38.0; t05: 42.0; t10: 48.0; t15: 44.0}; pv_mw: {t00: 18.0; t05: 15.0; t10: 11.0; t15: 9.0}; generator: {id: diesel; pmin_mw: 12.0; pmax_mw: 55.0; variable_cost_per_mwh: 92.0}; battery: {initial_soc_mwh: 5.0; soc_min_mwh: 2.5; soc_max_mwh: 8.0; charge_pmax_mw: 6.0; … ещё 4}}
- Выход: dispatch: object mapping timestamp to diesel_mw, battery_mw, pv_curtailment_mw, soc_mwh, shed_mw; total_cost: diesel energy cost over the horizon; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_rolling_microgrid_dispatch`; baseline: `baselines.rolling_microgrid_dispatch.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-026; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from renewable microgrid dispatch taxonomy.
  - Rolling microgrid dispatch practice; локатор: standard short-horizon DER dispatch with SOC constraints; доверие: medium; примечание: Public case is a compact executable instance with deterministic enumeration.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-026
  - source card: docs/source_cards/rolling_microgrid_dispatch.md

### scuc_n1

- Идентификаторы: `scuc_n1_public_001`, candidate `GAP-TASK-001`
- Область: markets, unit commitment, reserves & adequacy
- Назначение: Выбрать минимальный по стоимости N-1 secure unit commitment
- English objective: Choose least-cost N-1 secure unit commitment
- Исходные данные: public_inputs: {scuc_case: {demand_mw: 260; reserve_mw: 40; units: список[4]: …, …, …, …}}
- Выход: committed_units: least-cost feasible unit ids; available_capacity_mw: total committed capacity; n1_secure_capacity_mw: capacity after largest committed-unit loss; reserve_mw: available capacity minus demand; commitment_cost_usd: startup plus no-load cost; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_scuc_n1`; baseline: `baselines.scuc_n1.baseline`
- Источники:
  - V4 balanced core shortlist — GAP-TASK-001; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Literature-derived power-systems task topic converted into a public executable deterministic instance.
  - Bilingual executable benchmark slice requirement; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium; примечание: Supports maintaining English and Russian task presentation for benchmark artifacts.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#gap-task-001
  - source card: docs/source_cards/scuc_n1.md

### three_phase_short_circuit

- Идентификаторы: `three_phase_short_circuit_public_001`, candidate `REL-TASK-033`
- Область: protection, faults & relay engineering
- Назначение: Рассчитать начальный симметричный ток трёхфазного короткого замыкания на шинах 10,5 кВ по сопротивлениям прямой последовательности в относительных единицах.
- English objective: Calculate the initial symmetrical three-phase short-circuit current at a 10.5 kV bus from positive-sequence per-unit impedances.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-033; subdomain: protection, faults & relay engineering; input_fields: список[4]: short_circuit_case.base_mva, short_circuit_case.voltage_kv, short_circuit_case.positive_sequence_impedances_pu, short_circuit_case.fault_resistance_pu}; short_circuit_case: {base_mva: 100.0; voltage_kv: 10.5; fault_location: 10.5 kV switchgear bus downstream of the station transformer; fault_resistance_pu: 0.005; positive_sequence_impedances_pu: список[3]: {id: …; description: …; r_pu: …; … ещё 1}, {id: …; description: …; r_pu: …; … ещё 1}, {id: …; description: …; r_pu: …; … ещё 1}}
- Выход: fault_current_ka: initial symmetrical three-phase RMS short-circuit current in kA; fault_mva: short-circuit apparent power in MVA, sqrt(3)*V_kV*I_kA; z_total_mag_pu: magnitude of the total positive-sequence fault impedance in per unit; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_three_phase_short_circuit`; baseline: `baselines.three_phase_short_circuit.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-033; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from the literature-derived protection and fault-analysis taxonomy. The public artifact is now an executable positive-sequence short-circuit calculation.
  - IEC 60909-style short-circuit calculation practice; локатор: standard engineering formula: initial symmetrical 3-phase current from Thevenin/positive-sequence impedance; доверие: medium; примечание: The executable case uses the common I_k = U/(sqrt(3)*|Z|) relation in per-unit form for a compact benchmark instance.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-033
  - source card: docs/source_cards/three_phase_short_circuit.md

### transient_stability_prediction

- Идентификаторы: `transient_stability_prediction_public_001`, candidate `REL-TASK-008`
- Область: stability & dynamics
- Назначение: Классификация исходов переходной устойчивости для аварий при высокой доле ВИЭ
- English objective: Classify transient-stability outcomes for high-renewable contingencies
- Исходные данные: public_inputs: {transient_stability_cases: {angle_limit_deg: 180.0; voltage_floor_pu: 0.7; min_damping_pct: 3.0; cases: список[3]: …, …, …}}
- Выход: case_results: object mapping case_id to label, risk_score, and clearing_margin_s; stable_case_count: number of stable cases; highest_risk_case: case_id with largest risk_score; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_transient_stability_prediction`; baseline: `baselines.transient_stability_prediction.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-008; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Literature-derived power-systems task topic converted into a public executable deterministic instance.
  - Bilingual executable benchmark slice requirement; локатор: literature/v0_executable_benchmark_slice.en.md and literature/v0_executable_benchmark_slice.ru.md; доверие: medium; примечание: Supports maintaining English and Russian task presentation for benchmark artifacts.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-008
  - source card: docs/source_cards/transient_stability_prediction.md

### wind_power_forecast

- Идентификаторы: `wind_power_forecast_public_001`, candidate `REL-TASK-009`
- Область: forecasting & uncertainty
- Назначение: Спрогнозировать выдачу ветропарка, используя кривую мощности турбины и поправку по исторической ошибке.
- English objective: Forecast wind-farm output by applying the turbine power curve and a historical residual bias correction.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-009; subdomain: forecasting & uncertainty; input_fields: список[4]: wind_forecast_case.turbine, wind_forecast_case.power_curve, wind_forecast_case.history, wind_forecast_case.weather_forecast}; wind_forecast_case: {forecast_step_hours: 1.0; reference_air_density_kg_m3: 1.225; turbine: {count: 8; rated_mw_each: 2.5}; power_curve: {cut_in_m_s: 3.0; rated_m_s: 12.0; cut_out_m_s: 25.0}; history: список[4]: {timestamp: …; wind_speed_m_s: …; air_density_kg_m3: …; … ещё 1}, {timestamp: …; wind_speed_m_s: …; air_density_kg_m3: …; … ещё 1}, {timestamp: …; wind_speed_m_s: …; air_density_kg_m3: …; … ещё 1}, {timestamp: …; wind_speed_m_s: …; air_density_kg_m3: …; … ещё 1}; weather_forecast: список[4]: {timestamp: …; wind_speed_m_s: …; air_density_kg_m3: …}, {timestamp: …; wind_speed_m_s: …; air_density_kg_m3: …}, {timestamp: …; wind_speed_m_s: …; air_density_kg_m3: …}, {timestamp: …; wind_speed_m_s: …; air_density_kg_m3: …}}
- Выход: forecast_mw_by_timestamp: object mapping forecast timestamp to MW; total_forecast_mwh: sum of hourly forecast values in MWh; peak_timestamp: timestamp with the largest forecast power; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_wind_power_forecast`; baseline: `baselines.wind_power_forecast.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-009; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from the forecasting and uncertainty part of the literature-derived taxonomy.
  - Wind-turbine power-curve forecasting practice; локатор: standard engineering model: speed-to-power conversion with density correction and residual bias correction; доверие: medium; примечание: The public case uses a compact deterministic power-curve instance for executable evaluation.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-009
  - source card: docs/source_cards/wind_power_forecast.md

### wind_prediction_interval

- Идентификаторы: `wind_prediction_interval_public_001`, candidate `REL-TASK-012`
- Область: forecasting & uncertainty
- Назначение: Перевести сценарные прогнозы погоды в мощность и указать прогнозные интервалы для каждого горизонта.
- English objective: Convert scenario weather forecasts to power and report prediction intervals for each horizon.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-012; subdomain: forecasting & uncertainty; input_fields: список[3]: wind_interval_case.turbine, wind_interval_case.power_curve, wind_interval_case.horizons}; wind_interval_case: {reference_air_density_kg_m3: 1.225; turbine: {count: 8; rated_mw_each: 2.5}; power_curve: {cut_in_m_s: 3.0; rated_m_s: 12.0; cut_out_m_s: 25.0}; horizons: список[3]: {timestamp: …; scenarios: …}, {timestamp: …; scenarios: …}, {timestamp: …; scenarios: …}}
- Выход: prediction_interval_mw_by_timestamp: object mapping timestamp to {p10, p50, p90}; average_interval_width_mw: mean p90-p10 width over timestamps; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_wind_prediction_interval`; baseline: `baselines.wind_prediction_interval.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-012; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Candidate task selected from the forecasting and uncertainty part of the literature-derived taxonomy.
  - Scenario-based wind-power interval forecasting; локатор: standard practice: transform weather scenarios through a turbine power curve and summarize empirical quantiles; доверие: medium; примечание: The public case uses deterministic scenario quantiles for executable evaluation.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-012
  - source card: docs/source_cards/wind_prediction_interval.md

### ybus_construction

- Идентификаторы: `ybus_construction_public_001`, candidate `REL-TASK-047`
- Область: power flow, modelling & transmission analysis
- Назначение: Постройте матрицу узловых проводимостей по сопротивлениям линий, зарядной проводимости линий и шунтам узлов.
- English objective: Build the bus admittance matrix from line impedances, line charging, and bus shunts.
- Исходные данные: public_inputs: {candidate_id: REL-TASK-047; subdomain: power flow, modelling & transmission analysis; input_fields: список[3]: network.buses, network.branches, network.shunts; complex_entry_format: {re: real part; im: imaginary part}}
- Выход: buses: list of bus ids in the task order; ybus: square matrix; each entry is {"re": float, "im": float}; rationale: optional string
- Проверка: `prototype.evaluators.evaluate_ybus_construction`; baseline: `baselines.ybus_construction.baseline`
- Источники:
  - V4 balanced core shortlist — REL-TASK-047; локатор: literature/metadata/v4_balanced_core_shortlist.md; доверие: medium; примечание: Balanced-core candidate selected from literature-derived power-systems task taxonomy for power-flow/modeling tasks.
  - Task bank v4 — REL-TASK-047; локатор: literature/task_bank_v4_gap_fill_balanced.md#rel-task-047; доверие: medium; примечание: Identifies Ybus construction from network data as a modeling task suitable for deterministic executable evaluation.
  - Source card: ybus_construction; локатор: docs/source_cards/ybus_construction.md; доверие: medium; примечание: Documents the benchmark adaptation from a standard power-flow modeling operation to a concrete JSON-input executable task.
  - source_evidence: literature/metadata/v4_balanced_core_shortlist.md
  - source_evidence: literature/task_bank_v4_gap_fill_balanced.md#rel-task-047
  - source_evidence: docs/source_cards/ybus_construction.md
  - source card: docs/source_cards/ybus_construction.md
