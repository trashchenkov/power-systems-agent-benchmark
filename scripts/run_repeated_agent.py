"""Run the same agent command k independent times over a subset of task packets.

Each repeat is an ordinary `run_agent_command` run written to `<out>/rep_<r>/`, so the
per-run protocol (sandbox relocation, retry policy, logs, scoring) is unchanged. Repeats
are independent draws of the agent; they are never merged into best-of-N inside a run.
Use `scripts/summarize_repeats.py` to compute run-to-run statistics.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[1]
if str(ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(ROOT_FOR_IMPORTS))

from scripts.run_agent_command import PACKET_FILES, run_agent_command


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def subset_packets(packets_dir: Path, out_dir: Path, families: list[str] | None, splits: list[str] | None) -> Path:
    """Write a manifest restricted to the requested families/splits; packet dirs are reused."""
    manifest = json.loads((packets_dir / "manifest.json").read_text(encoding="utf-8"))
    packets = [
        p
        for p in manifest.get("packets", [])
        if (not families or p["family"] in families) and (not splits or p.get("split", "public") in splits)
    ]
    if families:
        missing = sorted(set(families) - {p["family"] for p in packets})
        if missing:
            raise SystemExit(f"families not found in packets: {missing}")
    subset_dir = out_dir / "packets_subset"
    _write_json(subset_dir / "manifest.json", {**manifest, "packets": packets, "packet_count": len(packets)})
    return subset_dir


def private_packet_copy(subset_dir: Path, rep_dir: Path) -> Path:
    """Give one repeat its own pristine packet copy, so files an agent writes into a
    packet (e.g. through the absolute path in instructions.md) cannot reach other repeats."""
    manifest = json.loads((subset_dir / "manifest.json").read_text(encoding="utf-8"))
    copy_root = rep_dir / "packets"
    packets = []
    for p in manifest["packets"]:
        src = Path(p["packet_dir"])
        dst = copy_root / src.name
        dst.mkdir(parents=True, exist_ok=True)
        for name in PACKET_FILES:
            shutil.copyfile(src / name, dst / name)
        # instructions.md names the packet's own submission path; point it at this copy.
        text = (dst / "instructions.md").read_text(encoding="utf-8")
        (dst / "instructions.md").write_text(text.replace(str(src), str(dst)), encoding="utf-8")
        packets.append({**p, "packet_dir": str(dst), "task_path": str(dst / "task.json"),
                        "expected_submission_path": str(dst / "submission.json")})
    _write_json(copy_root / "manifest.json", {**manifest, "packets": packets})
    return copy_root


def stray_packet_files(packets_dir: Path) -> list[str]:
    """Files an agent wrote into its packet copy instead of the sandbox (diagnostic only)."""
    return sorted(str(f.relative_to(packets_dir)) for f in packets_dir.glob("*/*")
                  if f.is_file() and f.name not in PACKET_FILES)


def _one_repeat(args: tuple) -> dict[str, Any]:
    root, packets, out, agent, command, timeout_s, max_attempts, backoff = args
    own_packets = private_packet_copy(packets, out)
    summary = run_agent_command(root, own_packets, out, agent, command, timeout_s, max_attempts=max_attempts,
                                retry_backoff_s=backoff)
    summary["files_written_into_packets"] = stray_packet_files(own_packets)
    _write_json(out / "summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Benchmark repository root")
    parser.add_argument("--packets", type=Path, required=True, help="Directory created by scripts/prepare_agent_tasks.py")
    parser.add_argument("--out", type=Path, required=True, help="Output directory; repeats go to rep_<r>/")
    parser.add_argument("--agent-name", required=True)
    parser.add_argument("--command", required=True, help="Shell command to run once per packet")
    parser.add_argument("--families", nargs="*", default=None, help="Family subset (default: all packets)")
    parser.add_argument("--splits", nargs="*", default=None, help="Split subset (default: all packets)")
    parser.add_argument("--repeats", type=int, required=True, help="Number of independent repeats k")
    parser.add_argument("--first-repeat", type=int, default=1, help="Index of the first repeat (to extend a run)")
    parser.add_argument("--parallel", type=int, default=1, help="Repeats executed concurrently")
    parser.add_argument("--timeout-s", type=int, default=600)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--retry-backoff-s", type=float, default=30.0)
    args = parser.parse_args(argv)

    args.out.mkdir(parents=True, exist_ok=True)
    packets = subset_packets(args.packets, args.out, args.families, args.splits)
    reps = range(args.first_repeat, args.first_repeat + args.repeats)
    jobs = [
        (args.root, packets, args.out / f"rep_{r}", args.agent_name, args.command, args.timeout_s,
         args.max_attempts, args.retry_backoff_s)
        for r in reps
    ]
    summaries: dict[int, dict[str, Any]] = {}
    with ProcessPoolExecutor(max_workers=max(1, args.parallel)) as pool:
        futures = {pool.submit(_one_repeat, job): r for r, job in zip(reps, jobs)}
        for future in as_completed(futures):
            r = futures[future]
            summaries[r] = future.result()
            print(f"repeat {r}: mean={summaries[r]['mean_score']} feasible={summaries[r]['feasible_count']}"
                  f"/{summaries[r]['case_count']}", flush=True)
    _write_json(args.out / f"repeats_{args.first_repeat}-{reps[-1]}.json", {
        "agent": args.agent_name,
        "command": args.command,
        "families": args.families,
        "splits": args.splits,
        "repeats": {str(r): summaries[r] for r in sorted(summaries)},
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
