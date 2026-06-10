import json
import unittest
from pathlib import Path

from baselines.contingency_screening.baseline import solve_case
from prototype.evaluators.evaluate_contingency_screening import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "tasks/contingency_screening/public/case_001/task.json"


class ContingencyScreeningEvaluatorTests(unittest.TestCase):
    def small_case(self):
        return {
            "task_id": "contingency_screening_public_001",
            "branches": [
                {"id": "l12", "from_bus": "b1", "to_bus": "b2", "base_flow_mw": 80, "rating_mw": 100},
                {"id": "l23", "from_bus": "b2", "to_bus": "b3", "base_flow_mw": 60, "rating_mw": 100},
                {"id": "l13", "from_bus": "b1", "to_bus": "b3", "base_flow_mw": 40, "rating_mw": 70},
            ],
            "contingencies": [
                {"id": "out_l12", "outaged_branch": "l12", "post_flows_mw": {"l23": 95, "l13": 88}},
                {"id": "out_l23", "outaged_branch": "l23", "post_flows_mw": {"l12": 91, "l13": 55}},
                {"id": "out_l13", "outaged_branch": "l13", "post_flows_mw": {"l12": 99, "l23": 80}},
            ],
            "critical_loading_threshold_pct": 100.0,
        }

    def test_flags_islanding_contingency(self):
        case = {
            "task_id": "contingency_screening_public_001",
            "branches": [
                {"id": "l12", "from_bus": "b1", "to_bus": "b2", "base_flow_mw": 50, "rating_mw": 100},
                {"id": "l23", "from_bus": "b2", "to_bus": "b3", "base_flow_mw": 50, "rating_mw": 100},
            ],
            "contingencies": [
                {"id": "out_l12", "outaged_branch": "l12", "post_flows_mw": {"l23": 50}},
            ],
            "critical_loading_threshold_pct": 100.0,
        }
        submission = {"ranking": ["out_l12"], "islanding_flags": {"out_l12": True}}

        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"])
        self.assertEqual(result["missed_islanding"], [])
        self.assertEqual(result["violations"], [])

    def test_penalizes_missed_critical_overload(self):
        case = self.small_case()
        submission = {"ranking": ["out_l23", "out_l13"], "islanding_flags": {}}

        result = evaluate_case(case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("out_l12", result["missed_critical_contingencies"])
        self.assertEqual(result["score"], 0.0)

    def test_rewards_correct_critical_ranking(self):
        case = self.small_case()
        submission = {"ranking": ["out_l12", "out_l13", "out_l23"], "islanding_flags": {}}

        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["missed_critical_contingencies"], [])
        self.assertGreater(result["score"], 0.9)
        self.assertLessEqual(result["score"], 1.0)
        self.assertAlmostEqual(result["contingency_results"]["out_l12"]["max_loading_pct"], 125.714286, places=5)

    def test_public_baseline_is_feasible_for_public_case(self):
        case = json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))

        submission = solve_case(case)
        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["missed_critical_contingencies"], [])
        self.assertEqual(result["missed_islanding"], [])


if __name__ == "__main__":
    unittest.main()
