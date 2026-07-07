#!/usr/bin/env python3
"""Run the self-contained Agent Swarm contract validation suite."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=ROOT, text=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def validate_json_files() -> None:
    for folder in ("schemas", "verification"):
        for path in sorted((ROOT / folder).glob("*.json")):
            json.loads(path.read_text(encoding="utf-8"))
            print(f"json-ok {path.relative_to(ROOT)}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-git-check", action="store_true")
    args = parser.parse_args()

    validate_json_files()
    run([sys.executable, "scripts/validate_skills.py"])
    run([sys.executable, "scripts/verify_witness.py"])
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    if not args.skip_git_check:
        run(["git", "diff", "--check"])
    print("contract-validation-ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
