import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.prepare_agent_tasks import prepare_agent_tasks
from scripts.run_agent_command import run_agent_command


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class RunnerTimeoutTest(unittest.TestCase):
    def test_timeout_kills_the_whole_agent_process_tree(self) -> None:
        # The "agent" leaves a child process running and then hangs past the budget.
        # Killing only the shell wrapper would orphan the child.
        family = "three_phase_short_circuit"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prepare_agent_tasks(ROOT, tmp_path / "packets")
            manifest = json.loads((tmp_path / "packets" / "manifest.json").read_text())
            manifest["packets"] = [p for p in manifest["packets"] if p["family"] == family]
            (tmp_path / "packets" / "manifest.json").write_text(json.dumps(manifest))
            pid_file = tmp_path / "child.pid"
            command = f"sleep 60 & echo $! > '{pid_file}'; sleep 60"
            started = time.time()
            summary = run_agent_command(ROOT, tmp_path / "packets", tmp_path / "run", "hang", command, timeout_s=2)
            self.assertLess(time.time() - started, 30)
            self.assertEqual(summary["feasible_count"], 0)
            row = json.loads((tmp_path / "run" / "results.jsonl").read_text().splitlines()[0])
            self.assertEqual(row["returncode"], 124)
            self.assertEqual(row["failure_class_initial"], "timeout_budget")
            child = int(pid_file.read_text())
            for _ in range(20):
                if not _alive(child):
                    break
                time.sleep(0.1)
            self.assertFalse(_alive(child), "agent child process survived the timeout")


if __name__ == "__main__":
    unittest.main()
