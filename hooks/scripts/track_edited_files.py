#!/usr/bin/python3
"""
Track Edited Files Hook

Appends every file_path touched by Edit/Write to a per-session tmp list,
so format_on_session_end.py can format them once, at session end, instead
of reformatting on every single edit.

Cross-platform (Windows, macOS, Linux)
"""

import json
import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
)

logger = get_hooks_logger("TrackEditedFiles")

MAX_STDIN = 1024 * 1024  # 1 MB


def tracked_files_path(session_id: str) -> Path:
    return Path(f"/tmp/edited-files-{get_session_id_short(session_id)}.json")


def append_file(path: Path, file_path: str) -> None:
    files: list[str] = []
    if path.exists():
        try:
            files = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            files = []

    if file_path not in files:
        files.append(file_path)
        path.write_text(json.dumps(files), encoding="utf-8")
        logger.debug("Tracked %s (session file: %s)", file_path, path)
    else:
        logger.debug("Already tracked %s", file_path)


def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        pass

    try:
        data = json.loads(stdin_data)
        tool_input = get_by_key(data, "tool_input")
        file_path = get_by_key(tool_input, "file_path") if tool_input else None
        session_id = get_by_key(data, "session_id") or ""
        if file_path:
            append_file(tracked_files_path(session_id), file_path)
    except (json.JSONDecodeError, AttributeError):
        pass

    sys.stdout.write(stdin_data)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("Error: %s", exc)
        sys.exit(0)
