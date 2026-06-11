# Source card: cable cross-section selection

Family `cable_ampacity_sizing` (`CORE-SWAP-002`) models routine LV feeder design:
choose the smallest catalog cable cross-section that passes three independent
checks —

1. continuous current: catalog ampacity derated by ambient and grouping
   correction factors must cover the design current (IEC 60364-5-52 practice);
2. voltage drop: `dU = sqrt(3) * I * L * (R*cos(phi) + X*sin(phi))` within a
   percentage limit of system voltage;
3. short-circuit withstand: the adiabatic criterion `k*S >= I_fault*sqrt(t)`
   (IEC 60949), i.e. `S_min = I_fault*sqrt(t)/k`, with k = 143 A·sqrt(s)/mm2 for
   copper/XLPE.

The public case is constructed so the checks interact: the 70 mm2 candidate
passes derated ampacity but fails the 5 % voltage-drop limit on a 250 m run, so
the correct selection is 95 mm2. Catalog ampacities and impedances are
representative copper/XLPE values.

Replacement note: this family replaces `electric_boiler_step_control` in the
41-task balanced core; cable design had no coverage while boiler staging sat
outside the power-systems scope.
