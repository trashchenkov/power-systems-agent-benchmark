# Source card: transformer thermal loading (IEC 60076-7)

Family `transformer_thermal_loading` (`CORE-SWAP-001`) models the loading-guide
thermal calculation for an ONAN transformer over a stepwise load cycle:

- steady-state top-oil rise `dTheta_or * ((1 + R*K^2)/(1 + R))^x`;
- exponential top-oil response between steps with time constant `tau_oil`;
- hot-spot temperature as top-oil plus the rated gradient times `K^y`;
- relative insulation ageing rate `2^((theta_hs - 98)/6)` for non-thermally
  upgraded paper, accumulated into equivalent ageing hours;
- an admissibility verdict against the hot-spot limit (120 C, the IEC 60076-7
  normal-cyclic-loading hot-spot ceiling).

Method reference: IEC 60076-7 loading guide (equivalently IEEE C57.91). Compact
simplifications, stated in the evaluator: end-of-step reporting and a neglected
winding time constant (the hot-spot gradient follows the load instantly).

Replacement note: this family replaces `electric_boiler_capacity_sizing` in the
41-task balanced core. Transformers — the most loaded-and-aged asset class in
any utility — previously had zero coverage, while building-heat boiler sizing
sat outside the power-systems scope of the benchmark.
