# Source card: minimum synchronous-machine share

Family `min_synchronous_share` (`REL-TASK-007`) models converter-dominated grid adequacy. The executable case enumerates synchronous unit commitments and selects the minimum online synchronous share satisfying RoCoF and short-circuit-ratio constraints.

RoCoF is recomputed from the swing equation, `|df/dt| = dP * f0 / (2 * E_kinetic)` with `E_kinetic = sum(H_i * S_i)` in MW·s (the surrogate uses unit `p_mw` as the MVA base). The 2.0 Hz/s limit follows the ENTSO-E RfG rate-of-change-of-frequency withstand requirement and suits this island-style case where the dimensioning loss is large relative to system kinetic energy.
