import json
import unittest
from pathlib import Path

from baselines.corrective_transmission_switching.baseline import solve_case
from prototype.evaluators.evaluate_corrective_transmission_switching import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_CASE = ROOT / "tasks/corrective_transmission_switching/public/case_001/task.json"


class CorrectiveTransmissionSwitchingEvaluatorTests(unittest.TestCase):
    def public_case(self):
        return json.loads(PUBLIC_CASE.read_text(encoding="utf-8"))

    def test_public_baseline_closes_tie_and_is_feasible(self):
        case = self.public_case()
        submission = solve_case(case)

        result = evaluate_case(case, submission)

        self.assertTrue(result["feasible"], result["violations"])
        self.assertEqual(result["close_branches"], ["l14"])
        self.assertEqual(result["open_branches"], [])
        self.assertLessEqual(result["max_loading_pct"], 100.0)
        self.assertGreaterEqual(result["score"], 0.99)

    def test_no_action_keeps_l12_overloaded(self):
        result = evaluate_case(self.public_case(), {"close_branches": [], "open_branches": []})

        self.assertFalse(result["feasible"])
        self.assertIn("post-switching overloads remain", "\n".join(result["violations"]))
        self.assertEqual(result["score"], 0.0)

    def test_rejects_non_candidate_switch(self):
        result = evaluate_case(self.public_case(), {"close_branches": ["l13"], "open_branches": []})

        self.assertFalse(result["feasible"])
        self.assertIn("non-candidate", "\n".join(result["violations"]))

    def test_rejects_islanding_or_overloading_open_action(self):
        result = evaluate_case(self.public_case(), {"close_branches": [], "open_branches": ["l23"]})

        self.assertFalse(result["feasible"])
        self.assertIn("post-switching overloads remain", "\n".join(result["violations"]))

    def test_rejects_switching_budget_excess(self):
        result = evaluate_case(self.public_case(), {"close_branches": ["l14"], "open_branches": ["l23"]})

        self.assertFalse(result["feasible"])
        self.assertIn("switching budget exceeded", "\n".join(result["violations"]))


if __name__ == "__main__":
    unittest.main()
