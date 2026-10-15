"""Golden-case validation for fault-section localization and two optimization families.

As in tests/test_golden_physics.py, every expected answer below is derived by hand
from the governing rules and annotated with that derivation; none is produced by
running the families' reference solvers. A reference solver and evaluator that
share a modelling error therefore disagree with these tests.

- Fault-section localization: the fault-current-indicator (FCI) truth table of a
  small radial feeder, including the case that exposed the off-by-one error
  described in the paper.
- Microgrid economic dispatch: an energy-limited battery whose optimum follows
  from the state-of-charge budget, with several equal-cost optima.
- N-1 generation commitment: a case whose least-cost N-1-secure set excludes the
  largest unit, so a capacity-greedy choice is wrong.
"""

import unittest

from prototype.evaluators.evaluate_fault_section_localization import (
    evaluate_case as evaluate_fault_localization,
    solve_case as solve_fault_localization,
)
from prototype.evaluators.evaluate_microgrid_economic_dispatch import (
    evaluate_case as evaluate_microgrid_dispatch,
)
from prototype.evaluators.evaluate_n1_generation_commitment import (
    evaluate_case as evaluate_n1_commitment,
)


def _feeder_task(observed, complaints):
    # Radial feeder  n0 -s01- n1 -s12- n2 -s23- n3
    #                                    \-s24- n4 -s45- n5
    # FCIs at n1, n2, n4; customers at n2..n5.
    return {
        "task_id": "golden_fault_section_localization",
        "fault_localization_case": {
            "source_node": "n0",
            "nodes": ["n0", "n1", "n2", "n3", "n4", "n5"],
            "customer_nodes": ["n2", "n3", "n4", "n5"],
            "sections": {
                "s01": {"from": "n0", "to": "n1"},
                "s12": {"from": "n1", "to": "n2"},
                "s23": {"from": "n2", "to": "n3"},
                "s24": {"from": "n2", "to": "n4"},
                "s45": {"from": "n4", "to": "n5"},
            },
            "fci_locations": {"fci_n1": "n1", "fci_n2": "n2", "fci_n4": "n4"},
            "observed_fci_state": dict(zip(("fci_n1", "fci_n2", "fci_n4"), observed)),
            "outage_complaint_nodes": complaints,
        },
    }


class FaultSectionLocalizationGolden(unittest.TestCase):
    # An FCI registers fault current iff the fault lies strictly downstream of it,
    # i.e. the FCI node is on the source-side path up to and including the
    # faulted section's upstream ("from") node. Its downstream ("to") node is NOT
    # on the fault-current path. The customers de-energized are those downstream
    # of the faulted section.
    #
    #   section  path to "from" node   FCI n1  n2  n4   outaged customers
    #   s01      {n0}                  F       F   F    n2 n3 n4 n5
    #   s12      {n0,n1}               T       F   F    n2 n3 n4 n5
    #   s23      {n0,n1,n2}            T       T   F    n3
    #   s24      {n0,n1,n2}            T       T   F    n4 n5
    #   s45      {n0,n1,n2,n4}         T       T   T    n5
    HAND_TABLE = {
        "s01": ((False, False, False), ["n2", "n3", "n4", "n5"]),
        "s12": ((True, False, False), ["n2", "n3", "n4", "n5"]),
        "s23": ((True, True, False), ["n3"]),
        "s24": ((True, True, False), ["n4", "n5"]),
        "s45": ((True, True, True), ["n5"]),
    }

    def test_every_section_is_recovered_from_its_hand_signature(self):
        for section, (observed, customers) in self.HAND_TABLE.items():
            with self.subTest(section=section):
                answer = solve_fault_localization(_feeder_task(observed, customers))
                self.assertEqual(answer["faulted_section"], section)
                self.assertEqual(answer["affected_customer_nodes"], customers)

    def test_off_by_one_discriminating_case(self):
        # Fault on s24: FCI at n4 (the section's downstream node) stays quiet.
        # The erroneous model put n4 on the fault-current path, predicted
        # (T, T, T) for s24, and so preferred s23 (FCI match, complaint mismatch).
        task = _feeder_task((True, True, False), ["n4", "n5"])
        good = evaluate_fault_localization(task, {"faulted_section": "s24", "affected_customer_nodes": ["n5", "n4"]})
        self.assertTrue(good["feasible"], good["violations"])
        self.assertEqual(good["score"], 1.0)
        wrong = evaluate_fault_localization(task, {"faulted_section": "s23", "affected_customer_nodes": ["n3"]})
        self.assertFalse(wrong["feasible"])


def _dispatch_task():
    return {
        "task_id": "golden_microgrid_economic_dispatch",
        "microgrid_dispatch_case": {
            "time_periods": ["t1", "t2"],
            "interval_hours": 1.0,
            "load_mw": {"t1": 30.0, "t2": 30.0},
            "pv_mw": {"t1": 0.0, "t2": 0.0},
            "generator": {"id": "diesel", "pmin_mw": 5.0, "pmax_mw": 50.0, "variable_cost_per_mwh": 100.0},
            "battery": {
                "initial_soc_mwh": 10.0, "soc_min_mwh": 2.0, "soc_max_mwh": 20.0,
                "charge_pmax_mw": 4.0, "discharge_pmax_mw": 6.0,
                "charge_efficiency": 1.0, "discharge_efficiency": 0.8, "dispatch_step_mw": 2.0,
            },
        },
    }


def _dispatch_rows(b1, b2):
    # diesel = load - battery (PV is zero and pmin is never binding here);
    # SOC drops by b / 0.8 per discharged MWh.
    soc1 = 10.0 - b1 / 0.8
    soc2 = soc1 - b2 / 0.8
    return {
        "t1": {"diesel_mw": 30.0 - b1, "battery_mw": b1, "pv_curtailment_mw": 0.0, "soc_mwh": soc1, "shed_mw": 0.0},
        "t2": {"diesel_mw": 30.0 - b2, "battery_mw": b2, "pv_curtailment_mw": 0.0, "soc_mwh": soc2, "shed_mw": 0.0},
    }


class MicrogridEconomicDispatchGolden(unittest.TestCase):
    # Diesel cost is linear (100 $/MWh) and always above pmin, so cost is minimized
    # by maximizing total battery discharge. Charging only loses energy.
    # Usable SOC = 10 - 2 = 8 MWh -> at most 8 * 0.8 = 6.4 MWh delivered; with
    # 2 MW steps and a 6 MW discharge limit the best total is 6 MWh, reached by
    # (6, 0), (4, 2), (2, 4) and (0, 6).
    #   optimal cost = 100 * (30 + 30 - 6) = 5400 $
    # (6, 2) would need 10 MWh of SOC: 10 - 7.5 - 2.5 = 0 < 2 -> infeasible.
    # (2, 2) costs 100 * 56 = 5600 $ -> gap 200 $ -> score 1 - 200/5400 = 0.962963.

    def test_hand_optimum_and_equal_cost_alternatives_score_one(self):
        task = _dispatch_task()
        for b1, b2 in ((6.0, 0.0), (4.0, 2.0), (2.0, 4.0), (0.0, 6.0)):
            with self.subTest(battery=(b1, b2)):
                result = evaluate_microgrid_dispatch(task, {"dispatch": _dispatch_rows(b1, b2), "total_cost": 5400.0})
                self.assertTrue(result["feasible"], result["violations"])
                self.assertEqual(result["optimal_cost"], 5400.0)
                self.assertEqual(result["score"], 1.0)

    def test_soc_violating_schedule_is_rejected(self):
        result = evaluate_microgrid_dispatch(_dispatch_task(), {"dispatch": _dispatch_rows(6.0, 2.0), "total_cost": 5200.0})
        self.assertFalse(result["feasible"])

    def test_suboptimal_schedule_scores_by_hand_gap(self):
        result = evaluate_microgrid_dispatch(_dispatch_task(), {"dispatch": _dispatch_rows(2.0, 2.0), "total_cost": 5600.0})
        self.assertTrue(result["feasible"], result["violations"])
        self.assertAlmostEqual(result["cost_gap_usd"], 200.0, places=3)
        self.assertAlmostEqual(result["score"], 1 - 200 / 5400, places=6)


def _commitment_task():
    return {
        "task_id": "golden_n1_generation_commitment",
        "public_inputs": {
            "commitment_case": {
                "demand_mw": 45.0,
                "reserve_mw": 10.0,
                "units": [
                    {"unit_id": "A", "pmax_mw": 50.0, "startup_cost_usd": 100.0, "no_load_cost_usd": 50.0},
                    {"unit_id": "B", "pmax_mw": 40.0, "startup_cost_usd": 80.0, "no_load_cost_usd": 40.0},
                    {"unit_id": "C", "pmax_mw": 30.0, "startup_cost_usd": 50.0, "no_load_cost_usd": 30.0},
                    {"unit_id": "D", "pmax_mw": 20.0, "startup_cost_usd": 40.0, "no_load_cost_usd": 20.0},
                ],
            }
        },
    }


class N1GenerationCommitmentGolden(unittest.TestCase):
    # Fixed cost per unit (startup + no-load): A 150, B 120, C 80, D 60 $.
    # N-1 secure: capacity left after losing the largest committed unit >= 45 MW;
    # reserve: committed capacity - 45 >= 10 MW.
    #   single units / any pair: largest-unit loss leaves <= 40 MW  -> insecure
    #   A+B+C 120/70 MW, 350 $   A+B+D 110/60 MW, 330 $
    #   A+C+D 100/50 MW, 290 $   B+C+D  90/50 MW, 260 $   A+B+C+D 410 $
    # Least-cost secure set: B+C+D (90 MW, N-1 50 MW, reserve 45 MW, 260 $),
    # which omits the largest unit A.
    HAND = {
        "committed_units": ["D", "B", "C"],
        "available_capacity_mw": 90.0,
        "n1_secure_capacity_mw": 50.0,
        "reserve_mw": 45.0,
        "commitment_cost_usd": 260.0,
    }

    def test_hand_optimum_is_accepted(self):
        result = evaluate_n1_commitment(_commitment_task(), self.HAND)
        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["score"], 1.0)

    def test_capacity_greedy_choice_is_rejected(self):
        greedy = {
            "committed_units": ["A", "C", "D"],
            "available_capacity_mw": 100.0,
            "n1_secure_capacity_mw": 50.0,
            "reserve_mw": 55.0,
            "commitment_cost_usd": 290.0,
        }
        self.assertFalse(evaluate_n1_commitment(_commitment_task(), greedy)["feasible"])


if __name__ == "__main__":
    unittest.main()
