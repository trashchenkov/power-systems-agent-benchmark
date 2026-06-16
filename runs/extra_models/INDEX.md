# Extra models on the Power Systems Agent Benchmark (public split)

Harness: opencode (model-agnostic), one run per model. Scores recomputed from the saved
submissions against the benchmark's final, optimum-normalized evaluators. `no_submission`
= the model/harness wrote no submission.json (infrastructure miss, counted as infeasible).

| model | size | feasible/41 | perfect/41 | mean | no_submission |
|---|---|---:|---:|---:|---:|
| Kimi K2.5 | ~1.04T total, 32B active (MoE, open weights) | 38/41 | 37/41 | 0.927 | 0 |
| GLM-4.6 | 357B total, 32B active (MoE, open weights) | 32/41 | 31/41 | 0.780 | 0 |
| Claude Haiku 4.5 | proprietary, size undisclosed | 29/41 | 27/41 | 0.706 | 5 |
| Qwen3-Coder-Next | 80B total, 3B active (MoE, open weights) | 27/41 | 27/41 | 0.659 | 2 |

For reference (canonical round, same evaluators): codex/gpt-5.5 0.973, cursor/composer-2.5
0.973, opencode/deepseek-v4-flash-free 0.951 (public mean).
