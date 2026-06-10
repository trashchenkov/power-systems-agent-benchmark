# Public/hidden split

The benchmark should support open development and sealed evaluation without changing the task interface.

## Public split

Public artifacts are safe to commit and distribute:

```text
tasks/<family>/public/<case_id>/
  task.json
  prompt.md                 # optional natural-language operator prompt
  assets/                   # public network/data files
  sample_submission.json    # public example only
```

Public cases should be:

- small enough for local debugging;
- deterministic;
- representative of the task schema;
- not reused as leaderboard hidden cases;
- accompanied by at least one sample submission when possible.

## Hidden split

Hidden artifacts must not be committed to the public benchmark repo unless explicitly released as an open split:

```text
hidden/<family>/<case_id>/
  evaluator_config.json
  perturbations.json
  expected_ranges.json
  seeds.json
```

Hidden cases should:

- use the same task/submission/evaluator interface as public cases;
- include versioned seeds and perturbation recipes;
- avoid leaking oracle rankings, optimal placements, or final metrics;
- be reproducible by benchmark maintainers;
- support stress evaluation over multiple hidden realizations.

## Sealed evaluation rule

Agents see:

- task statement;
- public inputs;
- allowed action schema;
- budget/tool constraints;
- previous public examples.

Agents do not see:

- hidden perturbation seeds;
- oracle solution;
- exact hidden score distribution;
- hidden evaluator config beyond published metric definitions.

## Leakage guardrails

- Keep hidden directories ignored by default.
- Do not embed hidden answers in public tests.
- Public sample submissions should demonstrate format, not optimal policy.
- If hidden data is generated from public seeds, treat those seeds as hidden until release.
- Baselines should be run through the same sealed evaluator as agents.
