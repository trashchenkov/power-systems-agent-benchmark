# Literature-to-benchmark plan

Date: 2026-06-08T06:09:40.671555+00:00

## Revised direction

Do not start by cloning PowerAgentBench's task families. Instead, build a broad task bank from current and canonical power-systems literature, textbooks/manuals, simulator documentation, and benchmark repositories, then compress it into an executable pandapower-first benchmark.

## Source classes

1. Textbooks / practitioner books
   - power-flow, OPF, contingency/security analysis, protection, distribution systems, dynamics/stability, state estimation, restoration, DER/microgrids.
   - Use mostly for task taxonomy and engineering workflow definitions, not for direct data/code.

2. Simulator manuals and examples
   - pandapower, DIgSILENT PowerFactory, OpenDSS, MATPOWER/PYPOWER, PowerModels.jl, Grid2Op, ANDES, PyPSA, PowerWorld/PSS/E when accessible.
   - Use proprietary tools such as DIgSILENT as task inspiration; avoid making them mandatory for open benchmark execution unless licensed access is explicitly part of a track.

3. Recent papers
   - LLM/agent applications in power systems;
   - grid operation/control benchmarks;
   - distribution/DER/microgrid tasks;
   - reliability/security assessment;
   - model/data debugging and state estimation;
   - restoration and outage management.

4. Existing benchmarks/repos
   - PowerAgentBench, EnergyAgentBench, Grid2Op/L2RPN, PGLib-OPF, PowerGym/PowerGridworld, SustainGym/CityLearn.

## Extraction schema for each candidate task

```json
{
  "task_id": "source_slug_task_n",
  "source": "paper/book/manual/repo",
  "domain": "transmission|distribution|DER|microgrid|dynamics|planning|protection|market|data/model-debugging",
  "engineering_workflow": "diagnose|simulate|optimize|rank|repair|explain|operate|plan",
  "original_task": "short description from source",
  "agent_prompt_version": "operator-style task prompt",
  "required_inputs": ["case", "measurements", "event", "constraints"],
  "required_tools": ["runpp", "runopp", "contingency", "timeseries", "short_circuit"],
  "ground_truth_possible": "yes|partial|no",
  "open_substrate": "pandapower|OpenDSS|Grid2Op|ANDES|PyPSA|PowerModels|none",
  "pandapower_mvp_feasible": true,
  "evaluation_contract": "hidden recomputation / injected fault / oracle / rubric",
  "difficulty": "L0|L1|L2|L3",
  "notes": "caveats"
}
```

## Compression pipeline

1. Collect 100-200 raw tasks.
2. Deduplicate into 20-40 normalized task templates.
3. Select 5-8 benchmark families.
4. Pick 2-3 pandapower-feasible MVP families.
5. For each MVP family, define generators, schemas, evaluator, baselines.

## Likely differentiator

The benchmark should be literature-derived and workflow-diverse, not PowerAgentBench-derived. PowerAgentBench remains a reference for mechanics: public/hidden split, tool budget, evidence metrics, hidden recomputation.
