#!/usr/bin/python3
"""Central eval runner for Claude Code hook scripts.

Usage:
    python3 eval.py                # run every *.json in this dir
    python3 eval.py <eval.json> ...

Each eval JSON: {"hook": "scripts/x.py", "mode": "exit_code"|"stdout", "cases": [...]}

mode "exit_code" (PreToolUse allow/deny hooks):
    tool_name       str, default "Bash"
    tool_input      dict
    cwd             optional, default repo root
    expect          "allow" | "deny"   (deny == exit code 2)
    expect_pattern  optional substr required in stderr

mode "stdout" (hooks that print JSON/context to stdout, always exit 0):
    input           dict, raw stdin payload
    raw_stdin       optional str sent verbatim instead of json.dumps(input)
    expect_output   bool, required
    expect_pattern  optional substr required in stdout
    cache_files     optional list[str] of cache file paths (supports "{session_id}"
                     and "{short_id}" placeholders) to delete before running
"""

import json
import os
import subprocess
import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
HOOKS_DIR = EVALS_DIR.parent
REPO_ROOT = HOOKS_DIR.parent

ENV = {**os.environ, "AI_PROJECT_DIR": os.environ.get("AI_PROJECT_DIR", str(REPO_ROOT))}


def run_exit_code_case(hook_path: Path, case: dict) -> tuple[bool, str]:
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
            env=ENV,
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


def run_stdout_case(hook_path: Path, case: dict) -> tuple[bool, str]:
    session_id = case.get("input", {}).get("session_id", "")
    for template in case.get("cache_files", []):
        path = Path(template.format(session_id=session_id, short_id=session_id[:8]))
        path.unlink(missing_ok=True)

    stdin_data = (
        case["raw_stdin"] if "raw_stdin" in case else json.dumps(case.get("input", {}))
    )

    try:
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=stdin_data,
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=ENV,
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


RUNNERS = {"exit_code": run_exit_code_case, "stdout": run_stdout_case}


def run_eval_file(eval_path: Path) -> tuple[int, int]:
    spec = json.loads(eval_path.read_text())
    hook_path = HOOKS_DIR / spec["hook"]
    mode = spec.get("mode", "exit_code")
    runner = RUNNERS[mode]

    if not hook_path.exists():
        print(f"[{eval_path.name}] SKIP: hook not found: {hook_path}")
        return 0, 0

    passed = 0
    failed = 0
    print(f"\n=== {eval_path.name} -> {spec['hook']} ({mode}) ===")
    for case in spec.get("cases", []):
        name = case["name"]
        ok, msg = runner(hook_path, case)
        if ok:
            passed += 1
            print(f"  PASS  {name}")
        else:
            failed += 1
            print(f"  FAIL  {name}: {msg}")

    return passed, failed


def main() -> None:
    args = sys.argv[1:]
    eval_files = (
        sorted(EVALS_DIR.glob("*.json")) if not args else [Path(a) for a in args]
    )

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
