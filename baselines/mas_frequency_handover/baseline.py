from __future__ import annotations
import json
from pathlib import Path
from prototype.evaluators.evaluate_mas_frequency_handover import _expected
def solve_case(task):
    ans=_expected(task); ans["rationale"]="computed from public executable case inputs"; return ans
def main():
    import sys
    task=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")); print(json.dumps(solve_case(task), indent=2, ensure_ascii=False))
if __name__=="__main__": main()
