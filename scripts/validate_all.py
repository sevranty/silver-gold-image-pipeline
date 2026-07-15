#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "scripts/validate_foundation.py"],
    [sys.executable, "scripts/validate_runtime_contracts.py"],
    [sys.executable, "scripts/validate_policy.py"],
    [sys.executable, "scripts/validate_skill_runtime.py"],
    [sys.executable, "scripts/validate_adapters.py"],
    [sys.executable, "-m", "unittest", "tests/test_validation.py"],
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = []
    failed = False
    env = os.environ.copy()
    env.setdefault("PYTHONPYCACHEPREFIX", str(ROOT / ".validation-pycache"))
    for command in COMMANDS:
        run = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        results.append({"command": command, "exit_code": run.returncode, "stdout": run.stdout, "stderr": run.stderr})
        failed = failed or run.returncode != 0
    payload = {"status": "fail" if failed else "pass", "results": results, "subjective_visual_quality_assessed": False}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        for result in results:
            print(f"$ {' '.join(result['command'])}")
            print(result["stdout"].rstrip())
            if result["stderr"].strip():
                print(result["stderr"].rstrip(), file=sys.stderr)
        print(f"all validation: {payload['status'].upper()}")
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
