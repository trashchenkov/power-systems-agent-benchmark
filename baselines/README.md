# Baselines

Baseline agents are used to calibrate evaluator difficulty and catch scoring regressions.

Planned baselines:

- `random`: emits valid but naive actions within bounds.
- `do_nothing`: submits an empty/no-op response where allowed.
- `scripted`: uses simple domain heuristics or solver calls.
- `oracle_dev`: development-only baseline with access to public evaluator details; not for sealed leaderboard comparison.

All baselines must write the same JSON submission shape as external agents and must be scored by the same evaluator CLI.
