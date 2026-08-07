#!/usr/bin/python3
"""
Dir-Context-Refs Hook

PreToolUse hook for Read|Edit|Write. Walks every directory between cwd and the
target file's parent, checking each for CONTEXT.md/CLAUDE.md/AGENTS.md. If any
exist, injects a reference (path only, not contents) into additionalContext so
the agent knows they exist and can read them if useful.

Dedupe: per session, a given directory's set of found files is only
re-announced once NOTIFY_EVERY calls have passed since it was last announced.
"""

import json
import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger, get_session_id_short  # noqa: E402

logger = get_hooks_logger("DirContextRefs")

MAX_STDIN = 1024 * 1024
NOTIFY_EVERY = 25
CANDIDATE_NAMES = ("CONTEXT.md", "CLAUDE.md", "AGENTS.md")


def _cache_path(session_id: str) -> Path:
    return Path(f"/tmp/dir_context_refs_{session_id}.json")


def _load_cache(cache_path: Path) -> dict:
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache_path: Path, cache: dict) -> None:
    try:
        cache_path.write_text(json.dumps(cache))
    except OSError:
        pass


def _intermediate_dirs(cwd: Path, file_path: Path) -> list[Path]:
    """Directories from cwd down to (and including) the file's parent dir."""
    try:
        rel = file_path.resolve().relative_to(cwd.resolve())
    except ValueError:
        return []

    parts = rel.parts[:-1]  # drop filename
    dirs = []
    current = cwd.resolve()
    for part in parts:
        current = current / part
        dirs.append(current)
    return dirs


def main() -> None:
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        sys.exit(0)

    try:
        data = json.loads(stdin_data)
    except (json.JSONDecodeError, TypeError):
        logger.debug("Failed to parse stdin JSON, exiting.")
        sys.exit(0)

    tool_name = get_by_key(data, "tool_name") or ""
    if tool_name not in ("Read", "Edit", "Write"):
        sys.exit(0)

    tool_input = get_by_key(data, "tool_input") or {}
    file_path = get_by_key(tool_input, "file_path")
    if not file_path:
        sys.exit(0)

    cwd = get_by_key(data, "cwd") or str(Path.cwd())
    cwd_path = Path(cwd)
    file_path_obj = Path(file_path)

    dirs = _intermediate_dirs(cwd_path, file_path_obj)
    logger.debug("cwd=%s file_path=%s dirs=%s", cwd, file_path, dirs)
    if not dirs:
        sys.exit(0)

    found: dict[str, list[str]] = {}
    for d in dirs:
        matches = [name for name in CANDIDATE_NAMES if (d / name).is_file()]
        if matches:
            found[str(d)] = matches

    if not found:
        sys.exit(0)

    session_id = get_session_id_short(get_by_key(data, "session_id") or "")
    cache_path = _cache_path(session_id)
    cache = _load_cache(cache_path)

    to_report: list[dict] = []
    for dir_str, names in found.items():
        for name in names:
            key = str(Path(dir_str) / name)
            skip_count = cache.get(key)

            if skip_count is None or skip_count >= NOTIFY_EVERY:
                cache[key] = 0
                to_report.append({"path": key})
            else:
                cache[key] = skip_count + 1

    _save_cache(cache_path, cache)

    if to_report:
        output = json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": json.dumps(
                        {
                            "note": "The following directory-level context files exist. Read them if their content seems relevant.",
                            "files": to_report,
                        }
                    ),
                }
            }
        )
        logger.debug("Output: %s", output)
        sys.stdout.write(output)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("dir_context_refs hook failed")
        sys.exit(0)
