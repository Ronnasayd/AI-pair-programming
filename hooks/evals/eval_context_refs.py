#!/usr/bin/python3
"""Eval runner for context_refs.py (PreToolUse Edit|Write hook).

Usage:
    python3 eval_context_refs.py <eval.json> [<eval2.json> ...]
    python3 eval_context_refs.py --all

Each case:
    name            str, required
    input           dict, raw stdin payload (e.g. {"tool_name": "Edit", "tool_input": {...}, "session_id": "x"})
    raw_stdin       optional str, sent verbatim instead of json.dumps(input) (for malformed-JSON cases)
    expect_output   bool, required — True if stdout should be non-empty JSON, False if empty
    expect_pattern  optional substr that must appear in stdout when expect_output is True
    reset_cache     optional bool, default True — wipe the session's ref-injection cache before running
"""

import json
import subprocess
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
HOOKS_DIR = EVALS_DIR.parent
REPO_ROOT = HOOKS_DIR.parent
HOOK_PATH = HOOKS_DIR / "scripts" / "context_refs.py"


def run_case(case: dict) -> tuple[bool, str]:
    session_id = case.get("input", {}).get("session_id", "")
    if case.get("reset_cache", True) and session_id:
        short = session_id[:8]
        cache = Path(f"/tmp/context_refs_{short}.json")
        cache.unlink(missing_ok=True)

    stdin_data = (
        case["raw_stdin"] if "raw_stdin" in case else json.dumps(case.get("input", {}))
    )

    try:
        proc = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=stdin_data,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=90,
        )
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"

    if proc.returncode != 0:
        return (
            False,
            f"expected exit 0, got {proc.returncode} (stderr={proc.stderr.strip()!r})",
        )

    stdout = proc.stdout.strip()
    expect_output = case.get("expect_output", False)

    if expect_output and not stdout:
        return (
            False,
            f"expected non-empty stdout, got empty (stderr={proc.stderr.strip()!r})",
        )
    if not expect_output and stdout:
        return False, f"expected empty stdout, got {stdout!r}"

    pattern = case.get("expect_pattern")
    if pattern and pattern not in stdout:
        return False, f"expected stdout to contain {pattern!r}, got {stdout!r}"

    return True, ""


def run_eval_file(eval_path: Path) -> tuple[int, int]:
    spec = json.loads(eval_path.read_text())

    if not HOOK_PATH.exists():
        print(f"[{eval_path.name}] SKIP: hook not found: {HOOK_PATH}")
        return 0, 0

    passed = 0
    failed = 0
    print(f"\n=== {eval_path.name} -> scripts/context_refs.py ===")
    for case in spec.get("cases", []):
        name = case["name"]
        ok, msg = run_case(case)
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
        eval_files = sorted(EVALS_DIR.glob("context_refs*.json"))
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
