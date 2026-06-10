# Source card: critical clearing time

Family `critical_clearing_time` (`REL-TASK-048`) models first-swing transient
stability for a single machine connected to an infinite bus. The executable case
publishes machine data only (H, f0, Pm, pre-/during-/post-fault transfer
capability); the agent computes the critical clearing angle from the equal-area
criterion and the critical clearing time from the closed-form swing-equation
solution valid for zero during-fault power transfer:

    delta_0   = asin(Pm / Pmax_pre)
    delta_max = pi - asin(Pm / Pmax_post)
    cos(delta_cr) = (Pm * (delta_max - delta_0) + Pmax_post * cos(delta_max)) / Pmax_post
    t_cr = sqrt(4 * H * (delta_cr - delta_0) / (2 * pi * f0 * Pm))

Method reference: standard textbook treatment (e.g. Kundur, *Power System
Stability and Control*). This replaces the earlier sweep-table surrogate whose
inputs carried precomputed stable/unstable labels and reduced the task to table
lookup; the agent now performs the stability computation itself. Multi-machine
or non-zero during-fault transfer variants require numerical integration and are
candidates for simulator-backed hidden cases.
