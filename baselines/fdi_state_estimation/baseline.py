"""Public deterministic baseline for DC-WLS bad-data identification."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prototype.evaluators.evaluate_fdi_state_estimation import _expected


def solve_case(case: dict[str, Any]) -> dict[str, Any]:
    answer = _expected(case)
    answer["rationale"] = (
        "WLS state estimate with iterative largest-normalized-residual bad-data "
        "identification recomputed from the public measurement set."
    )
    return answer


def main() -> None:
    import sys

    task = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(solve_case(task), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
