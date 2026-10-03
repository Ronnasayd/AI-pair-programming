#!/usr/bin/python3
"""Stop hook.

Blocks the turn from ending when files changed this turn fail lint. The
PostToolUse lint hooks (python_lint.py, typescript_lint.py, golang_lint.py)
are advisory only (always exit 0), so nothing else stops a lint regression
from shipping in a turn's final state.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from golang_lint import maybe_run_golang_lint
from php_lint import maybe_run_php_lint
from python_lint import maybe_run_python_lint
from typescript_lint import maybe_run_typescript_lint
from utils import (
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
    minify_json,
    project_dir,
    run_command_cwd,
    tmp_project_dir,
    truncate_large_output,
)

LOG = get_hooks_logger("StopLintGate")

MAX_FILES = 50
MAX_LOOPS = 5
LINT_EXTS = {".py", ".ts", ".tsx", ".go", ".php"}
_LINT_DISPATCH = {
    ".py": maybe_run_python_lint,
    ".ts": maybe_run_typescript_lint,
    ".tsx": maybe_run_typescript_lint,
    ".go": maybe_run_golang_lint,
    ".php": maybe_run_php_lint,
}


def _loop_count_path(project_root: str, session_id: str) -> Path:
    """Path to this session's stop-loop counter, reset each turn by turn_base_sha.py."""
    return (
        tmp_project_dir(project_root, "stop-loop-count")
        / f"{get_session_id_short(session_id)}.txt"
    )


def _read_loop_count(project_root: str, session_id: str) -> int:
    """Current stop-loop count for this session, defaulting to 0 if absent/invalid."""
    path = _loop_count_path(project_root, session_id)
    if not path.exists():
        return 0
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return 0


def _bump_loop_count(project_root: str, session_id: str, count: int) -> None:
    """Persist the incremented stop-loop count for this session."""
    _loop_count_path(project_root, session_id).write_text(str(count), encoding="utf-8")


def _pinned_sha(project_root: str, session_id: str) -> str | None:
    """Read the turn-start SHA pinned by turn_base_sha.py, if present."""
    sha_path = (
        tmp_project_dir(project_root, "turn-base-sha")
        / f"{get_session_id_short(session_id)}.txt"
    )
    if not sha_path.exists():
        return None
    sha = sha_path.read_text(encoding="utf-8").strip()
    return sha or None


def _porcelain_paths(project_root: str) -> set[str]:
    """Paths from `git status --porcelain`, relative to project_root."""
    result = run_command_cwd("git status --porcelain", cwd=project_root)
    if not result["success"]:
        return set()
    paths = set()
    for line in result["output"].splitlines():
        if len(line) < 4:
            continue
        # porcelain format: "XY path" (renames use "XY old -> new")
        entry = line[3:]
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        paths.add(entry.strip('"'))
    return paths


def _diff_paths(project_root: str, base_sha: str) -> set[str]:
    """Paths changed since base_sha, relative to project_root."""
    result = run_command_cwd(f"git diff --name-only {base_sha}", cwd=project_root)
    if not result["success"]:
        return set()
    return {line for line in result["output"].splitlines() if line}


def changed_files(project_root: str, session_id: str) -> list[str]:
    """Union of pinned-SHA diff and working-tree status, filtered and capped.

    Args:
        project_root: repo root to run git commands in.
        session_id: current session id, used to find the pinned SHA file.

    Returns:
        list[str]: changed paths with a lint-covered extension, capped at
        MAX_FILES.
    """
    base_sha = _pinned_sha(project_root, session_id)
    if base_sha:
        paths = _diff_paths(project_root, base_sha) | _porcelain_paths(project_root)
    else:
        LOG.debug("No pinned SHA for session, falling back to git status alone")
        paths = _porcelain_paths(project_root)

    filtered = sorted(p for p in paths if Path(p).suffix in LINT_EXTS)
    return filtered[:MAX_FILES]


def _lint_failures(project_root: str, files: list[str]) -> dict[str, dict]:
    """Run the matching lint dispatcher per file, keyed by file for failures only."""
    failures: dict[str, dict] = {}
    for rel_path in files:
        maybe_run_lint = _LINT_DISPATCH.get(Path(rel_path).suffix)
        if maybe_run_lint is None:
            continue
        abs_path = str(Path(project_root) / rel_path)
        results = maybe_run_lint(abs_path)
        failed = {
            tool: res
            for tool, res in results.items()
            if res and not res.get("success", True)
        }
        if failed:
            failures[rel_path] = failed
    return failures


def main() -> None:
    """Read the hook payload from stdin, re-run lint on turn-changed files."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse JSON: %s", e)
        sys.exit(0)

    LOG.debug(
        "payload debug: event=%s session_id=%s agent_id=%s",
        get_by_key(payload, "hook_event_name"),
        get_by_key(payload, "session_id"),
        get_by_key(payload, "agent_id"),
    )

    project_root = project_dir(payload)
    session_id = get_by_key(payload, "session_id") or ""

    files = changed_files(project_root, session_id)
    if not files:
        sys.exit(0)

    failures = _lint_failures(project_root, files)
    if not failures:
        sys.exit(0)

    loop_count = _read_loop_count(project_root, session_id) + 1
    if loop_count > MAX_LOOPS:
        LOG.debug("Loop cap hit (%d/%d), letting turn end", loop_count, MAX_LOOPS)
        sys.exit(0)
    _bump_loop_count(project_root, session_id, loop_count)

    reason = truncate_large_output(minify_json(failures), "stop_lint_gate")
    if isinstance(reason, dict):
        reason = minify_json(reason)

    output = {"decision": "block", "reason": reason}
    LOG.debug("[block] (%d/%d): %s", loop_count, MAX_LOOPS, minify_json(output))
    print(minify_json(output))  # noqa: T201 - hook stdout protocol
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        LOG.debug("Error: %s", exc)
        sys.exit(0)
