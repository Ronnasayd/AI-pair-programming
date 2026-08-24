#!/usr/bin/python3
"""
Incremental Jest coverage hook.

After a JS/TS file is edited, if the project has jest installed, spawns a
detached background process that:
  1. runs jest --coverage scoped to the edited file into a partial dir
  2. merges the partial coverage into the project's existing coverage dir
     (coverage-final.json, coverage-summary.json, and the changed file's
     lcov-report HTML page) so total coverage stays up to date.

Fire-and-forget: does not block the PostToolUse hook response.
"""

import json
import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    acquire_lock,
    find_last_coverage_dir,
    find_project_root,
    get_by_key,
    get_hooks_logger,
    jest_installed,
    lock_path_for,
    spawn_background,
    tmp_project_dir,
)

logger = get_hooks_logger("CoverageIncremental")

_JS_TS_EXTS = {".js", ".jsx", ".ts", ".tsx"}


def maybe_run_incremental_coverage(file_path: str | None) -> None:
    if not file_path:
        return

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        return

    if resolved.suffix.lower() not in _JS_TS_EXTS:
        return

    project_root = find_project_root(str(resolved.parent))

    if not jest_installed(project_root):
        logger.debug("Jest not installed in %s, skipping.", project_root)
        return

    coverage_dir = find_last_coverage_dir(project_root)
    rel_path = os.path.relpath(str(resolved), project_root)
    tmp_dir = tmp_project_dir(project_root, "jest-coverage-incremental")

    lock_file = lock_path_for(tmp_dir, rel_path)
    if not acquire_lock(lock_file):
        logger.debug("Coverage run already in progress for %s, skipping.", rel_path)
        return

    partial_dir = str(tmp_dir / "partials" / rel_path.replace("/", "_"))

    custom_cmd = os.environ.get("JEST_COVERAGE_CMD_INCREMENTAL")
    if custom_cmd:
        jest_cmd = custom_cmd.format(
            rel_path=json.dumps(rel_path),
            coverage_dir=json.dumps(partial_dir),
        )
    else:
        jest_cmd = (
            f"NODE_ENV=test node_modules/.bin/jest --findRelatedTests {json.dumps(rel_path)} "
            f"--coverage --coverageDirectory={json.dumps(partial_dir)} "
            f"--collectCoverageFrom={json.dumps(rel_path)} --passWithNoTests --runInBand"
        )
    merge_cmd = (
        f"{json.dumps(sys.executable)} {json.dumps(str(Path(script_dir) / 'merge_coverage.py'))} "
        f"{json.dumps(partial_dir)} {json.dumps(coverage_dir)} {json.dumps(rel_path)}"
    )

    release_cmd = f"rm -f {json.dumps(str(lock_file))}"
    full_cmd = f"{jest_cmd}; {merge_cmd}; {release_cmd}"
    logger.debug("Spawning background coverage update: %s", full_cmd)
    spawn_background(full_cmd, project_root, tmp_dir / "coverage-incremental.log")


def main() -> None:
    max_stdin = 1024 * 1024
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(max_stdin)
    except OSError:
        pass

    try:
        data = json.loads(stdin_data)
        tool_input = get_by_key(data, "tool_input")
        file_path = get_by_key(tool_input, "file_path") if tool_input else None
        maybe_run_incremental_coverage(file_path)
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.debug("Error parsing stdin: %s", exc)

    sys.stdout.write(stdin_data)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("Error: %s", exc)
        sys.exit(0)
