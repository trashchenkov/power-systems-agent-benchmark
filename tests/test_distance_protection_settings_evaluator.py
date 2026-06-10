import json
import unittest
from pathlib import Path

from baselines.distance_protection_settings.baseline import solve_case
from prototype.evaluators.evaluate_distance_protection_settings import evaluate_case, expected_windows


ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / "tasks/distance_protection_settings/public/case_001/task.json"


class DistanceProtectionSettingsEvaluatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task = json.loads(TASK_PATH.read_text(encoding="utf-8"))

    def test_public_baseline_is_feasible(self) -> None:
        submission = solve_case(self.task)
        result = evaluate_case(self.task, submission)
        self.assertTrue(result["feasible"], result)
        self.assertEqual(result["score"], 1.0)

    def test_rejects_zone1_overreach(self) -> None:
        submission = solve_case(self.task)
        windows = expected_windows(self.task)
        submission["zone1_ohm"] = windows["zone1"]["max"] + 0.1
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("zone1_ohm above maximum reach", result["violations"])

    def test_rejects_zone2_insufficient_backup_coverage(self) -> None:
        submission = solve_case(self.task)
        windows = expected_windows(self.task)
        submission["zone2_ohm"] = windows["zone2"]["min"] - 0.1
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("zone2_ohm below minimum reach", result["violations"])

    def test_rejects_zone3_load_encroachment_or_overreach(self) -> None:
        submission = solve_case(self.task)
        windows = expected_windows(self.task)
        submission["zone3_ohm"] = windows["zone3"]["max"] + 0.1
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("zone3_ohm above maximum reach", result["violations"])

    def test_rejects_uncoordinated_delays(self) -> None:
        submission = solve_case(self.task)
        submission["zone2_delay_s"] = 0.1
        result = evaluate_case(self.task, submission)
        self.assertFalse(result["feasible"])
        self.assertIn("zone2_delay_s outside coordination window", result["violations"])


if __name__ == "__main__":
    unittest.main()
