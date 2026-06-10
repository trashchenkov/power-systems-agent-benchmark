# Metrics

The benchmark uses layered scoring. Hard safety/physics validity dominates objective quality, and explanation quality is secondary.

## Metric layers

1. **Hard constraints**
   - simulator convergence;
   - voltage/thermal/frequency/protection safety limits;
   - valid action schema and component IDs;
   - resource bounds and operating rules.

2. **Objective quality**
   - action cost;
   - production cost / regret;
   - outage duration / unserved energy;
   - reliability improvement;
   - relay selectivity margin;
   - served load / restoration quality.

3. **Operational quality**
   - number of actions;
   - switching burden;
   - reserve margin;
   - robustness across hidden perturbations;
   - invalid or duplicate tool calls.

4. **Agent behavior diagnostics**
   - schema validity;
   - tool budget use;
   - evidence coverage;
   - explanation-vs-simulator consistency;
   - timeout/refusal rate.

## Normalization

Each evaluator should emit a normalized `score` in `[0, 1]` and raw `metrics` for analysis.

Default convention:

- infeasible due to hard constraints: `score = 0`;
- feasible: `score = max(0, 1 - normalized_cost_penalty - operational_penalties)`;
- family-specific scoring must document units and penalty weights.

## LLM-as-a-judge policy

LLM-as-a-judge must not be the primary score for benchmark ranking. It may be used only for secondary diagnostic fields such as:

- rationale readability;
- report completeness;
- operator-facing explanation quality.

If used, judge prompts, rubrics, models, versions, and calibration examples must be published.

## Reporting recommendations

Leaderboard/report should show at least:

- overall mean score;
- feasibility rate;
- per-family score;
- hard-constraint failure counts;
- invalid action/schema rate;
- timeout/refusal rate;
- cost/regret objective metrics;
- robustness mean/std/worst-case over hidden seeds.
