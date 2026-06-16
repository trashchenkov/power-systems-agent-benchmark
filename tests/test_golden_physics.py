"""Golden-case validation of evaluator physics against hand-derived answers.

These tests cross-check selected evaluators against analytic results worked out
by hand from the governing formulas, independently of the families' own baseline
solvers. Because the expected numbers come from an external derivation rather
than from re-running our code, they catch the class of error in which an
evaluator and its baseline share the same physics mistake (e.g. the
faulted-section off-by-one discussed in the paper): a wrong evaluator would
disagree with the hand value here.

Each expected number is annotated with the arithmetic that produces it.
"""

import math
import unittest

from prototype.evaluators.evaluate_three_phase_short_circuit import (
    compute_three_phase_fault,
    evaluate_case as evaluate_short_circuit,
)
from prototype.evaluators.evaluate_earth_fault_calculation import compute_earth_fault
from prototype.evaluators.evaluate_ybus_construction import compute_ybus

SQRT3 = math.sqrt(3.0)


class ThreePhaseShortCircuitGolden(unittest.TestCase):
    # Single positive-sequence reactance x = 0.4 pu, fault resistance r_f = 0.3 pu,
    # base 100 MVA, 10 kV, c_max = 1.1, c_min = 1.0.
    #   I_base = 100 / (sqrt(3) * 10)                 = 5.773503 kA
    #   |Z_bolted| = 0.4 ;  |Z_min| = |0.3 + j0.4|    = 0.5
    #   Ik_max = c_max / |Z_bolted| * I_base = 2.75 * 5.773503 = 15.877133 kA
    #   Sk_max = sqrt(3) * 10 * Ik_max = c_max * 100 / 0.4      = 275.0 MVA
    #   Ik_min = c_min / |Z_min| * I_base = 2.0 * 5.773503      = 11.547005 kA
    def setUp(self):
        self.task = {
            "task_id": "golden_three_phase_short_circuit",
            "short_circuit_case": {
                "base_mva": 100.0, "voltage_kv": 10.0,
                "voltage_factor_cmax": 1.1, "voltage_factor_cmin": 1.0,
                "positive_sequence_impedances_pu": [{"r_pu": 0.0, "x_pu": 0.4}],
                "fault_resistance_pu": 0.3,
            },
        }

    def test_evaluator_physics_matches_hand_derivation(self):
        s = compute_three_phase_fault(self.task)
        self.assertAlmostEqual(s["z_bolted_mag_pu"], 0.4, places=5)
        self.assertAlmostEqual(s["z_min_mag_pu"], 0.5, places=5)
        self.assertAlmostEqual(s["ik_max_ka"], 15.877133, places=4)
        self.assertAlmostEqual(s["sk_max_mva"], 275.0, places=3)
        self.assertAlmostEqual(s["ik_min_ka"], 11.547005, places=4)

    def test_hand_answer_is_accepted_end_to_end(self):
        submission = {
            "ik_max_ka": 15.877133, "sk_max_mva": 275.0, "ik_min_ka": 11.547005,
            "z_bolted_mag_pu": 0.4, "z_min_mag_pu": 0.5,
        }
        result = evaluate_short_circuit(self.task, submission)
        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["score"], 1.0)

    def test_wrong_answer_is_rejected(self):
        # Teeth: a value off by 10% must fail, so the golden check is not vacuous.
        submission = {
            "ik_max_ka": 17.46, "sk_max_mva": 275.0, "ik_min_ka": 11.547005,
            "z_bolted_mag_pu": 0.4, "z_min_mag_pu": 0.5,
        }
        self.assertFalse(evaluate_short_circuit(self.task, submission)["feasible"])


class EarthFaultGolden(unittest.TestCase):
    # Single-line-to-ground fault, Z1 = Z2 = Z0 = j0.5 pu, no fault resistance,
    # base 100 MVA, 10 kV.
    #   I_base = 100 / (sqrt(3) * 10)            = 5.773503 kA
    #   denominator = Z1 + Z2 + Z0 = j1.5  -> |.| = 1.5
    #   I1 = I2 = I0 = 1 / 1.5 = 0.666667 pu, angle -90 deg
    #   |I1| = 0.666667 * 5.773503             = 3.849002 kA
    #   |I_fault| = 3 * |I1| = 3 * 3.849002    = 11.547005 kA, angle -90 deg
    def setUp(self):
        self.task = {
            "task_id": "golden_earth_fault",
            "earth_fault_case": {
                "base_mva": 100.0, "voltage_kv": 10.0,
                "sequence_impedances_pu": {
                    "positive": {"r_pu": 0.0, "x_pu": 0.5},
                    "negative": {"r_pu": 0.0, "x_pu": 0.5},
                    "zero": {"r_pu": 0.0, "x_pu": 0.5},
                },
                "fault_resistance_pu": 0.0,
            },
        }

    def test_evaluator_physics_matches_hand_derivation(self):
        s = compute_earth_fault(self.task)
        self.assertAlmostEqual(s["denominator_x_pu"], 1.5, places=5)
        self.assertAlmostEqual(s["i1_ka"]["mag_ka"], 3.849002, places=4)
        self.assertAlmostEqual(s["i1_ka"]["angle_deg"], -90.0, places=3)
        self.assertAlmostEqual(s["fault_current_mag_ka"], 11.547005, places=4)
        self.assertAlmostEqual(s["fault_current_ka"]["angle_deg"], -90.0, places=3)
        self.assertAlmostEqual(s["residual_current_mag_ka"], 11.547005, places=4)


class YbusGolden(unittest.TestCase):
    # Two buses, one lossless series branch x = 0.5 pu (r = 0, b = 0).
    #   y = 1 / (j0.5) = -j2
    #   Y11 = Y22 = y = -j2 ;  Y12 = Y21 = -y = +j2
    def setUp(self):
        self.task = {
            "task_id": "golden_ybus",
            "network": {
                "buses": ["b1", "b2"],
                "branches": [{"id": "L1", "from_bus": "b1", "to_bus": "b2",
                              "r_pu": 0.0, "x_pu": 0.5, "b_pu": 0.0}],
                "shunts": [],
            },
        }

    def test_evaluator_physics_matches_hand_derivation(self):
        s = compute_ybus(self.task)
        y = s["ybus"]
        self.assertAlmostEqual(y[0][0]["im"], -2.0, places=5)
        self.assertAlmostEqual(y[1][1]["im"], -2.0, places=5)
        self.assertAlmostEqual(y[0][1]["im"], 2.0, places=5)
        self.assertAlmostEqual(y[1][0]["im"], 2.0, places=5)
        for i in range(2):
            for j in range(2):
                self.assertAlmostEqual(y[i][j]["re"], 0.0, places=5)


if __name__ == "__main__":
    unittest.main()
