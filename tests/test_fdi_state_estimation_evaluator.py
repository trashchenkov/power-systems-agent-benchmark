import json
import unittest
from pathlib import Path

from baselines.fdi_state_estimation.baseline import solve_case
from prototype.evaluators.evaluate_fdi_state_estimation import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "tasks/fdi_state_estimation/public/case_001/task.json"


class FDIStateEstimationEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))

    def test_public_baseline_is_feasible_for_public_case(self):
        submission = solve_case(self.case)
        result = evaluate_case(self.case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["score"], 1.0)
        self.assertEqual(result["expected_attacked_measurements"], ["inj_b2"])

    def test_identification_flags_injected_measurement_not_smeared_neighbors(self):
        submission = solve_case(self.case)

        # The attacked injection must be identified even though smearing makes
        # the plain weighted residual of flow_l12 large as well.
        self.assertEqual(submission["attacked_measurements"], ["inj_b2"])

    def test_rejects_missed_bad_data_measurement(self):
        submission = solve_case(self.case)
        submission["attacked_measurements"] = []

        result = evaluate_case(self.case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("missed bad-data measurement: inj_b2", result["violations"])
        self.assertEqual(result["score"], 0.0)

    def test_rejects_false_alarm_on_honest_measurement(self):
        submission = solve_case(self.case)
        submission["attacked_measurements"] = ["inj_b2", "flow_l12"]

        result = evaluate_case(self.case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("false bad-data alarm: flow_l12", result["violations"])

    def test_rejects_corrected_state_outside_tolerance(self):
        submission = solve_case(self.case)
        submission["corrected_state"]["theta_2"] += 0.01

        result = evaluate_case(self.case, submission)

        self.assertFalse(result["feasible"])
        self.assertTrue(any("deviates from recomputed WLS estimate" in v for v in result["violations"]))

    def test_rejects_unknown_measurement_id_and_extra_keys(self):
        submission = solve_case(self.case)
        submission["attacked_measurements"] = ["inj_b2", "mystery"]
        submission["answer"] = "leak"

        result = evaluate_case(self.case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("unknown measurement id: mystery", result["violations"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
