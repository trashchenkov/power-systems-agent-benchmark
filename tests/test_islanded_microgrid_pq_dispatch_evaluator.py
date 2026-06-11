import json
import unittest
from pathlib import Path

from baselines.islanded_microgrid_pq_dispatch.baseline import solve_case
from prototype.evaluators.evaluate_islanded_microgrid_pq_dispatch import evaluate_case

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/islanded_microgrid_pq_dispatch/public/case_001/task.json"


class IslandedMicrogridPQDispatchEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_unbalanced_dispatch_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['dispatch']['inverter']['q_mvar'] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("reactive power balance" in v for v in result["violations"]))

    def test_wrong_total_or_voltage_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission['voltage_pu'] += 0.1
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("voltage_pu" in v for v in result["violations"]))

    def test_unknown_field_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["answer"] = "leak"
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("unknown answer fields" in v for v in result["violations"]))


    def test_alternative_feasible_dispatch_gets_partial_credit_not_rejection(self):
        import copy
        submission=solve_case(self.task); c=self.task["islanded_pq_case"]
        submission=copy.deepcopy(submission)
        submission["dispatch"]["inverter"]["p_mw"]-=5.0
        submission["dispatch"]["diesel"]["p_mw"]+=5.0
        pd=submission["dispatch"]["diesel"]["p_mw"]; qd=submission["dispatch"]["diesel"]["q_mvar"]
        submission["total_cost"]=round(pd*c["diesel"]["variable_cost_per_h"]+abs(qd-c["diesel"]["q_preferred_mvar"])*c["diesel"]["q_deviation_penalty_per_mvar_h"],3)
        result=evaluate_case(self.task, submission)
        self.assertTrue(result["feasible"], result)
        self.assertLess(result["score"], 1.0)
        self.assertGreater(result["cost_gap"], 0.0)

    def test_capability_circle_violation_is_rejected(self):
        import copy
        submission=copy.deepcopy(solve_case(self.task))
        submission["dispatch"]["inverter"]["q_mvar"]=self.task["islanded_pq_case"]["inverter"]["s_rating_mva"]+5.0
        submission["dispatch"]["diesel"]["q_mvar"]=self.task["islanded_pq_case"]["load"]["q_mvar"]-submission["dispatch"]["inverter"]["q_mvar"]
        result=evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("capability circle" in v for v in result["violations"]))

    def test_power_balance_violation_is_rejected(self):
        import copy
        submission=copy.deepcopy(solve_case(self.task))
        submission["dispatch"]["diesel"]["p_mw"]+=3.0
        result=evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("balance" in v for v in result["violations"]))

if __name__ == "__main__":
    unittest.main()
