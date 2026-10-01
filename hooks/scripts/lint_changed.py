#!/usr/bin/python3
"""Lint every changed file in the working tree; exit 1 if any fails.

Standalone entry for harness `grind.lintCommand`: no hook payload on stdin,
no loop counter, no pinned turn SHA (the harness owns those).
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from golang_lint import maybe_run_golang_lint
from php_lint import maybe_run_php_lint
from python_lint import maybe_run_python_lint
from typescript_lint import maybe_run_typescript_lint
from utils import minify_json, run_command_cwd

MAX_FILES = 50
_LINT_DISPATCH = {
    ".py": maybe_run_python_lint,
    ".ts": maybe_run_typescript_lint,
    ".tsx": maybe_run_typescript_lint,
    ".go": maybe_run_golang_lint,
    ".php": maybe_run_php_lint,
}


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


def _lint_failures(project_root: str, files: list[str]) -> dict[str, dict]:
    """Run the matching lint dispatcher per file, keyed by file for failures only."""
    failures: dict[str, dict] = {}
    for rel_path in files:
        maybe_run_lint = _LINT_DISPATCH[Path(rel_path).suffix]
        results = maybe_run_lint(str(Path(project_root) / rel_path))
        failed = {
            tool: res
            for tool, res in results.items()
            if res and not res.get("success", True)
        }
        if failed:
            failures[rel_path] = failed
    return failures


def main() -> int:
    """Lint changed files under cwd and print failures as JSON.

    Returns:
        int: 1 if any file fails lint, else 0.
    """
    root = str(Path.cwd())
    changed = _porcelain_paths(root)
    files = sorted(p for p in changed if Path(p).suffix in _LINT_DISPATCH)
    failures = _lint_failures(root, files[:MAX_FILES])
    if failures:
        print(minify_json(failures))  # noqa: T201 - CLI output
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
