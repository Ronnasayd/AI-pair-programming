#!/usr/bin/python3
"""
Jest coverage report hook.

After a JS/TS file is edited/created, if the project has jest and an existing
coverage-final.json, computes that file's per-file coverage summary and
surfaces it via additionalContext so the model sees current line/branch/
function coverage for the file it just touched.

Read-only: does not run jest, just reads whatever coverage data already
exists on disk (populated by jest_coverage_incremental.py / session-end runs).
"""

import json
import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    build_coverage_summary,
    find_last_coverage_dir,
    find_project_root,
    get_by_key,
    get_hooks_logger,
    jest_installed,
    lock_path_for,
    tmp_project_dir,
)

logger = get_hooks_logger("CoverageReport")

_JS_TS_EXTS = {".js", ".jsx", ".ts", ".tsx"}


def _load_final_json(coverage_dir: str) -> dict | None:
    final_file = Path(coverage_dir) / "coverage-final.json"
    if not final_file.exists():
        return None
    try:
        return json.loads(final_file.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        logger.debug("Error reading %s: %s", final_file, exc)
        return None


def _load_summary_entry(final: dict, resolved: Path, project_root: str) -> dict | None:
    candidates = {str(resolved), os.path.relpath(str(resolved), project_root)}
    for key, file_coverage in final.items():
        if key in candidates or key.endswith(str(resolved)):
            logger.debug("Matched coverage entry for %s via key %s", resolved, key)
            return build_coverage_summary({key: file_coverage})[key]
    logger.debug("No coverage entry found for %s", resolved)
    return None


def _format_line_ranges(lines: list[int]) -> str:
    if not lines:
        return ""
    lines = sorted(set(lines))
    ranges = []
    start = prev = lines[0]
    for n in lines[1:]:
        if n == prev + 1:
            prev = n
            continue
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = n
    ranges.append(str(start) if start == prev else f"{start}-{prev}")
    return ",".join(ranges)


def _load_uncovered_lines(
    final: dict, resolved: Path, project_root: str
) -> list[int] | None:
    candidates = {str(resolved), os.path.relpath(str(resolved), project_root)}
    file_entry = None
    for key, entry in final.items():
        if key in candidates or key.endswith(str(resolved)):
            file_entry = entry
            break
    if not file_entry:
        return None

    statement_map = file_entry.get("statementMap", {})
    hits = file_entry.get("s", {})
    uncovered = []
    for stmt_id, count in hits.items():
        if count:
            continue
        stmt = statement_map.get(stmt_id)
        if stmt:
            uncovered.append(stmt["start"]["line"])
    return uncovered


def _format_message(
    file_path: str, entry: dict, uncovered_lines: list[int] | None
) -> str:
    lines_ = entry.get("lines", {})
    stmts = entry.get("statements", {})
    funcs = entry.get("functions", {})
    branches = entry.get("branches", {})
    message = (
        f"Jest coverage for {file_path}: "
        f"lines {lines_.get('pct', '?')}% ({lines_.get('covered', '?')}/{lines_.get('total', '?')}), "
        f"functions {funcs.get('pct', '?')}% ({funcs.get('covered', '?')}/{funcs.get('total', '?')}), "
        f"branches {branches.get('pct', '?')}% ({branches.get('covered', '?')}/{branches.get('total', '?')}), "
        f"statements {stmts.get('pct', '?')}% ({stmts.get('covered', '?')}/{stmts.get('total', '?')})."
    )
    if uncovered_lines:
        message += f" Uncovered lines: {_format_line_ranges(uncovered_lines)}."
    return message


def build_coverage_context(file_path: str | None) -> str | None:
    if not file_path:
        logger.debug("No file_path in tool_input, skipping.")
        return None

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        logger.debug("File does not exist: %s", resolved)
        return None
    if resolved.suffix.lower() not in _JS_TS_EXTS:
        logger.debug("Not a JS/TS file, skipping: %s", resolved)
        return None

    project_root = find_project_root(str(resolved.parent))
    logger.debug("Resolved project root: %s", project_root)
    if not jest_installed(project_root):
        logger.debug("Jest not installed in %s, skipping.", project_root)
        return None

    rel_path_for_lock = os.path.relpath(str(resolved), project_root)
    tmp_dir = tmp_project_dir(project_root, "jest-coverage-incremental")
    lock_file = lock_path_for(tmp_dir, rel_path_for_lock)
    stale = lock_file.exists()
    if stale:
        logger.debug(
            "Incremental coverage run still in progress for %s, showing last known coverage.",
            rel_path_for_lock,
        )

    coverage_dir = find_last_coverage_dir(project_root)
    logger.debug("Using coverage dir: %s", coverage_dir)
    final = _load_final_json(coverage_dir)
    if not final:
        logger.debug("No coverage-final.json available in %s.", coverage_dir)
        return None

    entry = _load_summary_entry(final, resolved, project_root)
    if not entry:
        logger.debug("No coverage entry available for %s.", resolved)
        return None

    uncovered_lines = _load_uncovered_lines(final, resolved, project_root)
    rel_path = os.path.relpath(str(resolved), project_root)
    message = _format_message(rel_path, entry, uncovered_lines)
    if stale:
        message += (
            " (incremental run in progress; values may not reflect the latest edit)"
        )
    logger.debug("Built coverage context: %s", message)
    return message


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
        logger.debug("Received tool_input file_path: %s", file_path)
        context = build_coverage_context(file_path)
        if context:
            output = json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": context,
                    }
                }
            )
            logger.debug(f"[additionalContext]: {output}")
            print(output)
        else:
            logger.debug("No coverage context produced for %s", file_path)
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.debug("Error parsing stdin: %s", exc)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("Error: %s", exc)
        sys.exit(0)
