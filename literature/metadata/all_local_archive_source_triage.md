# Full local archive source triage for task mining

Generated after a full pass over `literature/local_archive_extracted/local_lit/power_engineering`.

Artifacts:
- extraction report: `literature/metadata/all_local_archive_extraction_report.json`
- extracted text: `literature/extracted_text/all_local_archive/`
- snippet index: `literature/metadata/all_local_archive_task_snippets.json`
- candidate task bank: `literature/task_bank_v1_literature_derived.md`

## Coverage summary

- Source documents discovered: 127
- PDFs: 98
- DOCX: 29
- Text extracted successfully: 124
- Total extracted characters: 17,712,021

## Triage classes

- **A / task-bearing:** direct task candidates or strong source for evaluator mechanics.
- **B / supporting:** background, simulator/manual, formulas, domain context.
- **C / likely discard:** weakly relevant, off-domain, admin/course docs, or insufficient executable task content.

## A — task-bearing or high-priority sources

- `статья Бандурин №102 исправленная.docx` — anti-icing / preventive conductor heating optimization for 6–35 kV overhead lines.
- `PAPER_VICTOR-OTHfglV6.docx` and duplicate `(1)` — smart-inverter reactive power / Volt-VAR voltage control, TSO-DSO interaction.
- `ElecBench_a_Power_Dispatch_Evaluation_Benchmark_fo.pdf` — dispatch benchmark anchor.
- `faulted-circuit-indicators-and-system-reliability.pdf` — FCI reliability impact and placement.
- `development-of-laboratory-experiments-for-protection-and-communication-in-radial-and-bidirectional-power-systems.pdf` — overcurrent/directional relay coordination in radial/bidirectional systems.
- `TheRoleofElectricalVehiclesforPowerQualityandSecurityduringOutagesintheDistributionGrid_final.pdf` — EV/V2G power quality and outage support.
- `LoRA-Finetuned-LLM-for-Multi-Step-Wind-Power-Forecasting.pdf` — multi-step wind power forecasting task.
- `elibrary_71966528_24523599.pdf` — short-term wind speed/wind energy forecasting.
- `Advanced Prediction Techniques Applied to Smart Grids.pdf` — forecasting, RTTR/dynamic line rating, smart-grid prediction tasks.
- `Active-Power-Distribution-Networks-with-Decentralized-Multi-Agent-Control-Mode-Part-1.pdf` — decentralized multi-agent active distribution network control.
- `(Power Systems) Francisco M. Gonzalez-Longatt, José Luis Rueda Torres - Modelling and Simulation of Power Electronic Converter Dominated Power Systems in PowerFactory...pdf` — converter-dominated grid dynamics/BESS task source.
- `РЕЛЕЙНАЯ ЗАЩИТА В ЗАДАЧАХ С РЕШЕНИЯМИ И ПРИМЕРАМИ.pdf` — worked relay-protection calculation source.
- `Булычев А.В., Наволочный А.А. - Релейная защита распределительных сетей в примерах и задачах с решениями...pdf` — worked distribution relay examples.
- `Надежн.docx` — analytical reliability calculation tasks.
- `situationalawareness.pdf` — SCADA/situational-awareness incident interpretation.
- `fmincon.pdf` — constrained optimization/OPF mechanics.
- `A_Method_for_Reducing_Fluctuations_in_Total_Power_.pdf` — smoothing/renewable fluctuation reduction candidate.
- `energies-14-00102-v2.pdf`, `energies-15-02038-v2.pdf`, `electronics-10-00151-v2.pdf`, `energies-09-00943.pdf`, `energies-12-03008.pdf`, `energies-14-03692.pdf` — likely renewable/microgrid/smart-grid paper sources; need second pass by title/abstract before final promotion.

## B — supporting / evaluator-mechanics sources

- `J. Duncan Glover, Thomas J. Overbye, Mulukutla S. Sarma - Power System Analysis and Design-Cengage Learning (2017).pdf` — load flow, fault, OPF-style textbook support.
- `UserManual_2019_en.pdf` — PowerFactory/manual support, not final open-source benchmark substrate.
- `Евминов Л. Релейная...pdf` — relay-protection formulas and background.
- `shneerson-em-cifrovaya-releynaya-zaschita.pdf` — digital relay protection background/formulas.
- `Markevich_A_I_Releynaya_zaschita_i_avtomatika_v_sistemakh_elektrosnabzhenia_ispr.pdf` — relay automation background.
- `Релейная защита. Томск.pdf`, `Релейная защита и автоматизация электроэнергетических систем.pdf`, `РЭ1_Алтей-УЗТ.pdf`, `Курсовая работа реле.docx`, `контрольная работа по Релейной защите Степанова СС 1023-05.pdf` — protection worked examples / settings mechanics.
- `sinchronnye-i-asinchronnye-dvigateli6-10kv (1) (1).pdf` — motor operation/protection constraints.
- `monograph_2020_ed_kulagin_v_a.pdf` — broader power/asset/maintenance context.
- `quantifying-the-uncertainty-of-solar-photovoltaic-soft-costs...pdf` — PV output/economic uncertainty; more energy-economics than grid operation.
- `Enhancement_of_Building_Heating_Systems_Connected_.pdf` — building/heating flexibility support.
- `Программа ПК Энергосбережение.docx` — energy-saving financial/technical calculation support.

## C — likely discard or only use after manual review

The remaining low-score files are not discarded permanently, but they are not immediate benchmark-task sources. They include:

- admin/course-program documents;
- duplicate/conflicting copies;
- broad digital-transformation/industry overview docs;
- off-domain documents accidentally present in the archive;
- documents with weak or no executable operational problem signal in the keyword/snippet pass.

If later we need more breadth, run a second targeted pass over the `energies-*`, `symmetry-*`, `elibrary_*`, and student thesis files by extracting title/abstract/conclusion first.
