#!/usr/bin/python3
"""Generic eval runner for Claude Code hook scripts.

Usage:
    python3 eval.py <eval.json> [<eval2.json> ...]
    python3 eval.py --all              # run every *.json in this dir

Each eval file: {"hook": "scripts/x.py", "cases": [...]}
Case fields:
    name            str, required
    tool_name       str, sent as payload.tool_name
    tool_input      dict, sent as payload.tool_input
    expect          "allow" | "deny"
    expect_pattern  optional substr that must appear in stderr JSON reason/file/pattern
    cwd             optional, working dir to run hook from (default: repo root)
"""

import json
import subprocess
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
HOOKS_DIR = EVALS_DIR.parent
REPO_ROOT = HOOKS_DIR.parent


def run_case(hook_path: Path, case: dict) -> tuple[bool, str]:
    payload = {
        "tool_name": case.get("tool_name", "Bash"),
        "tool_input": case.get("tool_input", {}),
    }
    cwd = case.get("cwd", str(REPO_ROOT))

    try:
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"

    decision = "deny" if proc.returncode == 2 else "allow"
    expect = case.get("expect", "allow")

    if decision != expect:
        return False, (
            f"expected '{expect}' got '{decision}' "
            f"(exit={proc.returncode}, stderr={proc.stderr.strip()!r})"
        )

    pattern = case.get("expect_pattern")
    if pattern and pattern not in proc.stderr:
        return (
            False,
            f"expected stderr to contain {pattern!r}, got {proc.stderr.strip()!r}",
        )

    return True, ""


def run_eval_file(eval_path: Path) -> tuple[int, int]:
    spec = json.loads(eval_path.read_text())
    hook_path = HOOKS_DIR / spec["hook"]

    if not hook_path.exists():
        print(f"[{eval_path.name}] SKIP: hook not found: {hook_path}")
        return 0, 0

    passed = 0
    failed = 0
    print(f"\n=== {eval_path.name} -> {spec['hook']} ===")
    for case in spec.get("cases", []):
        name = case["name"]
        ok, msg = run_case(hook_path, case)
        if ok:
            passed += 1
            print(f"  PASS  {name}")
        else:
            failed += 1
            print(f"  FAIL  {name}: {msg}")

    return passed, failed


def main() -> None:
    args = sys.argv[1:]

    if not args or args == ["--all"]:
        eval_files = sorted(p for p in EVALS_DIR.glob("*.json"))
    else:
        eval_files = [Path(a) for a in args]

    if not eval_files:
        print("No eval files found.")
        sys.exit(1)

    total_passed = 0
    total_failed = 0
    for eval_path in eval_files:
        p, f = run_eval_file(eval_path)
        total_passed += p
        total_failed += f

    print(f"\n{'=' * 40}")
    print(f"TOTAL: {total_passed} passed, {total_failed} failed")
    sys.exit(1 if total_failed else 0)


if __name__ == "__main__":
    main()
