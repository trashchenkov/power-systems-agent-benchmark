import json
import unittest
from pathlib import Path

from baselines.flisr_restoration.baseline import solve_case
from prototype.evaluators.evaluate_flisr_restoration import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "tasks/flisr_restoration/public/case_001/task.json"


class FLISRRestorationEvaluatorTests(unittest.TestCase):
    def small_case(self):
        return {
            "task_id": "flisr_restoration_public_001",
            "source_bus": "s",
            "faulted_branches": ["l23"],
            "buses": [
                {"id": "s", "load_kw": 0.0, "priority": 0},
                {"id": "b1", "load_kw": 0.0, "priority": 0},
                {"id": "b2", "load_kw": 50.0, "priority": 3},
                {"id": "b3", "load_kw": 80.0, "priority": 5},
                {"id": "b4", "load_kw": 40.0, "priority": 2},
            ],
            "branches": [
                {"id": "l_s1", "from_bus": "s", "to_bus": "b1", "normally_closed": True, "capacity_kw": 250.0},
                {"id": "l12", "from_bus": "b1", "to_bus": "b2", "normally_closed": True, "capacity_kw": 160.0},
                {"id": "l23", "from_bus": "b2", "to_bus": "b3", "normally_closed": True, "capacity_kw": 120.0},
                {"id": "l34", "from_bus": "b3", "to_bus": "b4", "normally_closed": True, "capacity_kw": 130.0},
                {"id": "tie_24", "from_bus": "b2", "to_bus": "b4", "normally_closed": False, "capacity_kw": 120.0},
            ],
        }

    def test_accepts_radial_plan_that_isolates_fault_and_restores_load(self):
        submission = {"open_switches": ["l23"], "close_switches": ["tie_24"]}

        result = evaluate_case(self.small_case(), submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["restored_buses"], ["b2", "b3", "b4"])
        self.assertAlmostEqual(result["restored_load_kw"], 170.0)
        self.assertAlmostEqual(result["priority_restored"], 10.0)
        self.assertGreater(result["score"], 0.9)
        self.assertLessEqual(result["score"], 1.0)

    def test_rejects_plan_that_reenergizes_faulted_branch(self):
        submission = {"open_switches": [], "close_switches": ["tie_24"]}

        result = evaluate_case(self.small_case(), submission)

        self.assertFalse(result["feasible"])
        self.assertIn("faulted branch must be open: l23", result["violations"])
        self.assertEqual(result["score"], 0.0)

    def test_rejects_meshed_switching_plan(self):
        case = self.small_case()
        case["faulted_branches"] = []
        submission = {"open_switches": [], "close_switches": ["tie_24"]}

        result = evaluate_case(case, submission)

        self.assertFalse(result["feasible"])
        self.assertIn("energized network must be radial", result["violations"])

    def test_public_baseline_is_feasible_for_public_case(self):
        case = json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))

        submission = solve_case(case)
        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["violations"], [])


if __name__ == "__main__":
    unittest.main()
