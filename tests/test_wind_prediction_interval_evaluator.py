import json
import unittest
from pathlib import Path

from baselines.wind_prediction_interval.baseline import solve_case
from prototype.evaluators.evaluate_wind_prediction_interval import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/wind_prediction_interval/public/case_001/task.json"


class WindPredictionIntervalEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_baseline_submission_is_feasible(self) -> None:
        result = evaluate_case(self.task, solve_case(self.task))
        self.assertTrue(result["feasible"], result)

    def test_wrong_quantile_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["prediction_interval_mw_by_timestamp"]["t01"]["p90"] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("p90" in v for v in result["violations"]))

    def test_non_monotonic_interval_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["prediction_interval_mw_by_timestamp"]["t01"] = {"p10": 10.0, "p50": 5.0, "p90": 11.0}
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("p10 <= p50 <= p90" in v for v in result["violations"]))

    def test_wrong_average_width_is_rejected(self) -> None:
        submission = solve_case(self.task)
        submission["average_interval_width_mw"] += 1.0
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertTrue(any("average_interval_width_mw" in v for v in result["violations"]))


if __name__ == "__main__":
    unittest.main()
