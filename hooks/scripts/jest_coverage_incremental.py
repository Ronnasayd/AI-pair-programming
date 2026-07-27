#!/usr/bin/python3
"""
Incremental Jest coverage hook.

After a JS/TS file is edited, if the project has jest installed, spawns a
detached background process that:
  1. runs jest --coverage scoped to the edited file into a partial dir
  2. merges the partial coverage-final.json into the project's existing
     coverage dir (via nyc merge) so total coverage stays up to date.

Fire-and-forget: does not block the PostToolUse hook response.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import find_project_root, get_by_key, get_hooks_logger  # noqa: E402

logger = get_hooks_logger("CoverageIncremental")

_JS_TS_EXTS = {".js", ".jsx", ".ts", ".tsx"}


def _jest_installed(project_root: str) -> bool:
    return (Path(project_root) / "node_modules" / ".bin" / "jest").exists()


def _find_last_coverage_dir(project_root: str) -> str:
    """Return existing coverage dir if present, else default 'coverage'."""
    default_dir = Path(project_root) / "coverage"
    if default_dir.exists():
        return str(default_dir)
    for candidate in Path(project_root).glob("**/coverage-final.json"):
        return str(candidate.parent)
    return str(default_dir)


def _tmp_project_dir(project_root: str) -> Path:
    """Per-project scratch dir under the OS tmp dir, keyed by project path hash."""
    key = hashlib.sha1(project_root.encode()).hexdigest()[:12]
    tmp_dir = Path(tempfile.gettempdir()) / "jest-coverage-incremental" / key
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


def _spawn_background(cmd: str, cwd: str, tmp_dir: Path) -> None:
    """Detach a shell command so it survives after this hook process exits."""
    log_path = tmp_dir / "coverage-incremental.log"
    with open(log_path, "ab") as log_file:
        subprocess.Popen(
            ["nohup", "bash", "-c", cmd],
            cwd=cwd,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )


def maybe_run_incremental_coverage(file_path: str | None) -> None:
    if not file_path:
        return

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        return

    if resolved.suffix.lower() not in _JS_TS_EXTS:
        return

    project_root = find_project_root(str(resolved.parent))

    if not _jest_installed(project_root):
        logger.debug("Jest not installed in %s, skipping.", project_root)
        return

    coverage_dir = _find_last_coverage_dir(project_root)
    rel_path = os.path.relpath(str(resolved), project_root)
    tmp_dir = _tmp_project_dir(project_root)
    partial_dir = str(tmp_dir / "partials" / rel_path.replace("/", "_"))

    jest_cmd = (
        f"node_modules/.bin/jest --findRelatedTests {json.dumps(rel_path)} "
        f"--coverage --coverageDirectory={json.dumps(partial_dir)} "
        f"--collectCoverageFrom={json.dumps(rel_path)} --passWithNoTests"
    )
    merge_cmd = (
        f"npx nyc merge {json.dumps(partial_dir)} {json.dumps(coverage_dir)}/coverage-final.json.tmp "
        f"&& mv {json.dumps(coverage_dir)}/coverage-final.json.tmp {json.dumps(coverage_dir)}/coverage-final.json"
    )
    report_cmd = (
        f"npx nyc report --temp-dir={json.dumps(coverage_dir)} "
        f"--reporter=html --reporter=json --reporter=text-summary --report-dir={json.dumps(coverage_dir)}"
    )

    full_cmd = f"{jest_cmd}; {merge_cmd} && {report_cmd}"
    logger.debug("Spawning background coverage update: %s", full_cmd)
    _spawn_background(full_cmd, project_root, tmp_dir)


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
