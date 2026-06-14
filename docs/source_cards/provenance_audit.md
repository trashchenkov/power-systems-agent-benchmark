# Provenance audit


Scope: 41 public benchmark families. Only `source_evidence`, `source_provenance`, and `docs/source_cards/*` were changed. Full copyrighted sources are not redistributed.


## Family-by-family audit


| family | candidate_id | primary source locator | confidence | library match / status | mapping note |
|---|---|---|---|---|---|
| `bess_ancillary_response` | `REL-TASK-004` | DOI:10.1007/978-3-030-54124-8 | `medium` | found in private library | Grounds converter/BESS ancillary-response modelling; the benchmark uses a compact droop-response instance. |
| `breaker_relay_short_circuit` | `REL-TASK-045` | Cengage Learning, 2017; short-circuit programs for breaker and relay settings | `high` | found in private library | Canonical textbook source for short-circuit studies used for breaker adequacy and relay setting inputs. |
| `cable_ampacity_sizing` | `CORE-SWAP-002` | IEC 60364-5-52 ampacity and voltage-drop checks; IEC 60949 adiabatic short-circuit withstand | `high` | standard_not_redistributed | The executable case follows standard derated ampacity, voltage-drop and adiabatic withstand checks; standards are cited, not redistributed. |
| `commercial_pv_lcoe_uncertainty` | `REL-TASK-059` | DOI:10.1017/dsd.2020.171 | `medium` | found in private library | Primary source for PV soft-cost uncertainty and LCOE/CREST framing; the task is a compact deterministic scenario-quantile calculation. |
| `contingency_screening` | `GAP-TASK-005` | arXiv:1904.00044v1 and arXiv:1904.03587v1 | `medium` | external_arxiv_not_in_private_pdf_corpus | Grounds fast N-1 contingency screening and grid-splitting detection; the benchmark uses precomputed compact flows. |
| `corrective_transmission_switching` | `GAP-TASK-002` | arXiv:2001.00597v1 | `medium` | external_arxiv_not_in_private_pdf_corpus | Primary source for post-contingency corrective switching; public case is a compact DC-flow adaptation, not the full SCUC MILP. |
| `critical_clearing_time` | `REL-TASK-048` | Kundur, Power System Stability and Control; also supported by Glover/Overbye/Sarma stability-program discussion | `high` | found in private library | Canonical equal-area method; the executable case directly computes critical angle/time from the stated swing-equation parameters. |
| `dispatch_uncertainty` | `REL-TASK-015` | local archive; dispatch under renewable forecast uncertainty sections | `medium` | found in private library | Grounds uncertainty-aware dispatch framing; the executable case uses explicit robust-dispatch equations. |
| `distance_protection_settings` | `REL-TASK-039` | local archive text lines around REL-TASK-039 distance-protection sections | `medium` | found in private library | Identifies distance protection settings for 35–330 kV lines; the task is a compact zone-setting and load-encroachment instance. |
| `dynamic_thermal_rating` | `REL-TASK-014` | local archive dynamic-line-rating / weather-uncertainty sections | `medium` | found in private library | Grounds weather-dependent rating and operational uncertainty; the task implements an IEEE-738-style heat-balance surrogate. |
| `earth_fault_calculation` | `REL-TASK-034` | local archive; symmetrical components and earth-fault calculation sections | `medium` | found in private library | Grounds unsymmetrical/earth-fault calculations; the executable case follows standard sequence-network equations. |
| `en50160_voltage_compliance` | `REL-TASK-021` | EN 50160 supply-voltage characteristics; 10-minute RMS voltage limits | `high` | standard_not_redistributed | The executable case directly applies EN-50160-style voltage compliance thresholds; the standard itself is not redistributed. |
| `ev_v2g_outage_schedule` | `REL-TASK-020` | DOI:10.1109/RTUCON51174.2020.9316604 | `medium` | found in private library | Grounds EV/V2G outage-support scheduling; the task uses explicit energy/SOC constraints. |
| `ev_v2g_voltage_support` | `REL-TASK-017` | DOI:10.1109/RTUCON51174.2020.9316604 | `medium` | found in private library | Grounds EV inverter support for distribution voltage during outages; the task uses compact Volt/VAR capability checks. |
| `fault_section_localization` | `REL-TASK-052` | DOI:10.1109/REPCON.2000.848037 | `medium` | found in private library | Grounds FCI indications, patrol direction and outage localization; the case is a compact radial-feeder graph instance. |
| `fci_placement` | `REL-TASK-051` | DOI:10.1109/REPCON.2000.848037 | `medium` | found in private library | Grounds placement of FCIs to reduce patrol time; the case implements a small budgeted placement problem. |
| `fci_saidi_caidi` | `REL-TASK-053` | DOI:10.1109/REPCON.2000.848037 | `medium` | found in private library | Grounds reliability-index effects of FCI deployment; the case computes SAIDI/CAIDI changes deterministically. |
| `fdi_state_estimation` | `GAP-TASK-006` | largest-normalized-residual bad-data test | `high` | canonical_textbook_not_redistributed | The executable case directly implements the textbook WLS/LNR bad-data identification method. |
| `flisr_restoration` | `REL-TASK-003` | arXiv:2004.07921v1 | `medium` | external_arxiv_not_in_private_pdf_corpus | Primary source for distribution service restoration and feeder switching; task is a compact restored-load optimization instance. |
| `frt_compliance` | `GAP-TASK-011` | arXiv:2303.00391v2; arXiv:2207.11700v3 | `medium` | external_arxiv_not_in_private_pdf_corpus | Grounds inverter FRT/LVRT compliance checks; public case applies an explicit voltage-time ride-through curve. |
| `harmonic_ieee519_compliance` | `CORE-SWAP-003` | IEEE 519-2014 current-distortion and voltage-distortion limits | `high` | standard_not_redistributed | The executable case directly applies IEEE-519-style TDD/THD limit-table logic; the standard is cited, not redistributed. |
| `hydro_thermal_storage_uc` | `GAP-TASK-013` | arXiv:2012.07118v1; arXiv:2311.13438v1 | `medium` | external_arxiv_not_in_private_pdf_corpus | Grounds UC with emissions/ramping constraints; hydro/storage terms are compact benchmark extensions. |
| `ibr_short_circuit_frt` | `GAP-TASK-012` | arXiv:2504.10181v1 | `medium` | external_arxiv_not_in_private_pdf_corpus | Primary source for IBR short-circuit contribution modelling; the case applies explicit current-limit and FRT strategy rules. |
| `islanded_microgrid_pq_dispatch` | `REL-TASK-022` | local archive fmincon / microgrid dispatch source | `medium` | found in private library | Grounds joint P/Q dispatch with inverter capability; the task uses explicit balance, voltage-sensitivity and capability constraints. |
| `mas_frequency_handover` | `REL-TASK-001` | DOI:10.24160/0013-5380-2022-10-14-24 | `medium` | found in private library | Grounds frequency/power regulation states and multi-agent handover rules; the task is a compact state-classification case. |
| `microgrid_economic_dispatch` | `REL-TASK-024` | local archive fmincon / microgrid dispatch source | `medium` | found in private library | Grounds constrained microgrid dispatch; the task implements an explicit diesel/PV/battery cost-minimization instance. |
| `min_synchronous_share` | `REL-TASK-007` | local archive; minimum synchronous-generator share and converter-dominated stability sections | `medium` | found in private library | Grounds converter-dominated stability / synchronous-share analysis; evaluator recomputes RoCoF with explicit swing-equation formula. |
| `n1_generation_commitment` | `GAP-TASK-001` | arXiv:2001.00597v1 | `medium` | external_arxiv_not_in_private_pdf_corpus | Primary source for N-1/security-constrained UC framing; case is a small deterministic commitment feasibility problem. |
| `operator_breaker_load_actions` | `REL-TASK-050` | Cengage Learning, 2017; interactive one-line/breaker/load-action discussion | `medium` | found in private library | Grounds breaker/load operator actions in a one-line model; task uses graph connectivity and voltage checks. |
| `overcurrent_protection` | `REL-TASK-036` | local archive protection-setting sections for maximum-current protection and CT/selectivity checks | `medium` | found in private library | Grounds line overcurrent pickup, sensitivity and selectivity requirements; the task is a compact relay-setting calculation. |
| `pf_voltage_repair` | `REL-TASK-046` | Cengage Learning, 2017; AC power-flow solve and violation diagnosis | `high` | found in private library | Canonical textbook grounding for AC power-flow variables/violations; public case is a compact voltage-repair surrogate. |
| `power_quality_event_classification` | `GAP-TASK-008` | IEC 61000-4-30 measurement classes; sag/swell/interruption RMS thresholds | `high` | standard_not_redistributed | The executable case directly applies standard power-quality event threshold categories to RMS windows. |
| `protected_meter_placement` | `GAP-TASK-007` | arXiv:1304.4151v4 | `medium` | external_arxiv_not_in_private_pdf_corpus | Primary source for protected-meter placement against FDI attacks; the case is a compact graph-coverage instance. |
| `pv_volt_var` | `GAP-TASK-009` | arXiv:1006.0160v1; arXiv:1008.0878v1 | `medium` | external_arxiv_not_in_private_pdf_corpus | Primary PV reactive-power-control sources; the task selects a Volt-VAR curve under capability and voltage constraints. |
| `rolling_microgrid_dispatch` | `REL-TASK-026` | local archive fmincon / microgrid dispatch source | `medium` | found in private library | Grounds short-horizon renewable microgrid dispatch; the case uses explicit five-minute-style rolling-horizon constraints. |
| `three_phase_short_circuit` | `REL-TASK-033` | IEC 60909 max/min three-phase short-circuit current method | `high` | standard_not_redistributed; also local relay-protection worked examples | The executable case directly applies IEC-60909-style max/min short-circuit current calculations. |
| `transformer_thermal_loading` | `CORE-SWAP-001` | IEC 60076-7 top-oil / hot-spot exponential thermal model; IEEE C57.91 comparable practice | `high` | standard_not_redistributed | The executable case directly implements the standard top-oil/hot-spot and ageing-factor method in compact form. |
| `transient_stability_prediction` | `REL-TASK-008` | local archive transient-stability prediction with high wind penetration sections | `medium` | found in private library | Grounds transient-stability prediction features and stability index; the task is a compact classification instance. |
| `wind_power_forecast` | `REL-TASK-009` | DOI:10.13140/RG.2.2.33696.34561 | `medium` | found in private library | Grounds multi-step wind-power forecasting; the case uses deterministic power-curve and residual-bias calculations. |
| `wind_prediction_interval` | `REL-TASK-012` | local archive prediction-interval reliability/sharpness sections | `medium` | found in private library | Grounds prediction-interval coverage and sharpness; the case computes empirical wind-power quantiles. |
| `ybus_construction` | `REL-TASK-047` | Cengage Learning, 2017; bus admittance matrix construction | `high` | found in private library | Canonical textbook grounding for Ybus diagonal/off-diagonal construction; executable case follows the method directly. |

## Families left at low confidence

- None. All families now have a normalized `medium` or `high` primary-source provenance confidence. Internal task-bank records are retained only in `source_evidence` as derived traceability breadcrumbs, not as primary sources.

## Private library roots used

- `/root/investigation-runs/power-systems-agent-benchmark/literature/local_archive_extracted/local_lit/power_engineering/`
- `/root/investigation-runs/power-systems-agent-benchmark/literature/extracted_text/all_local_archive/`
- `/root/investigation-runs/power-systems-agent-benchmark/literature/curated_drive_corpus/`
