# Source card: DC-WLS bad-data identification (non-stealthy FDI)

Family `fdi_state_estimation` (`GAP-TASK-007`) models bad-data analysis in a DC
state estimator. The public case publishes a 3-bus DC network and five raw
measurements (three flows, two injections) where one injection carries a large
non-stealthy false-data bias. The agent must run the weighted least-squares
estimate, apply the iterative largest-normalized-residual (LNR) test, and report
the flagged measurement set plus the corrected state.

Method reference: Abur & Exposito, *Power System State Estimation: Theory and
Implementation* — normalized residuals `r_i / sqrt(Omega_ii)` with
`Omega = R - H G^-1 H^T`, `G = H^T W H`, iterative removal above a 3.0 threshold.
The case is deliberately constructed so that residual smearing makes the plain
weighted residual of an honest flow measurement large; only the properly
normalized residual identifies the attacked injection.

Honest scope limitation: coordinated stealthy FDI attacks (Liu, Ning & Reiter,
2009) are constructed to leave residuals unchanged and are undetectable by any
residual-based test. This family covers the naive detectable-injection case;
stealthy-FDI detectability would require a different task design (e.g., secured
measurement subsets or moving-target defenses) and is out of scope for this
surrogate.
