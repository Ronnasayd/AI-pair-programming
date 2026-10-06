#!/usr/bin/python3
"""Run tests related to changed files in the working tree; exit 1 if any fail.

Standalone entry for harness `grind.testCommand` / lefthook. Sibling of
lint_changed.py: same changed-file discovery, same `--staged` / `--ignore`
flags. No-op (exit 0) when no supported runner is installed locally.
"""

from pathlib import Path
import shlex
import sys

sys.path.insert(0, str(Path(__file__).parent))
from lint_changed import (
    DEFAULT_IGNORE,
    _ignore_globs,
    _is_ignored,
    _porcelain_paths,
    _staged_paths,
)
from utils import minify_json, run_command_cwd, truncate_large_output

MAX_FILES = 50
TIMEOUT_S = 600
_JS_EXTS = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}
# runner bin in node_modules/.bin -> command prefix; first installed wins.
# why: `related` mode maps changed sources to the tests that import them,
# so only affected tests run.
_RUNNERS = {
    "jest": "--findRelatedTests --passWithNoTests --bail",
    "vitest": "related --run --passWithNoTests",
}


def _installed_runner(root: str) -> str | None:
    """First of _RUNNERS present in root's node_modules/.bin, else None."""
    return next(
        (r for r in _RUNNERS if (Path(root) / "node_modules" / ".bin" / r).exists()),
        None,
    )


def main() -> int:
    """Run related tests for changed JS/TS files and print failures as JSON.

    Returns:
        int: 1 if the related tests fail, else 0.
    """
    argv = sys.argv[1:]
    root = str(Path.cwd())
    runner = _installed_runner(root)
    if runner is None:
        return 0
    changed = _staged_paths(root) if "--staged" in argv else _porcelain_paths(root)
    ignore = [*DEFAULT_IGNORE, *_ignore_globs(argv)]
    files = sorted(
        p
        for p in changed
        if Path(p).suffix in _JS_EXTS
        and (Path(root) / p).is_file()
        and not _is_ignored(p, ignore)
    )[:MAX_FILES]
    if not files:
        return 0
    cmd = f"node_modules/.bin/{runner} {_RUNNERS[runner]} " + shlex.join(files)
    result = run_command_cwd(cmd, cwd=root, timeout=TIMEOUT_S)
    if result["success"]:
        return 0
    # jest/vitest print failures on stderr
    out = result["error"] or result["output"]
    print(minify_json({runner: truncate_large_output(out, runner)}))
    return 1


if __name__ == "__main__":
    sys.exit(main())
