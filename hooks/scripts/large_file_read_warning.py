#!/usr/bin/python3
"""
Large-File-Read-Warning Hook

PreToolUse hook for Read. Warns via additionalContext when the target file
has more than LINE_THRESHOLD lines and no offset/limit was given, encouraging
partial reads (offset/limit) or grep-style tools instead of a full read.
"""

import json
import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger  # noqa: E402

logger = get_hooks_logger("LargeFileReadWarning")

MAX_STDIN = 1024 * 1024
LINE_THRESHOLD = 500


def _count_lines(path: Path) -> int:
    count = 0
    with path.open("r", errors="ignore") as f:
        for _ in f:
            count += 1
    return count


def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        pass

    try:
        data = json.loads(stdin_data)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
    except (json.JSONDecodeError, AttributeError):
        logger.debug("Failed to parse stdin JSON, exiting.")
        sys.exit(0)

    if tool_name != "Read":
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    if tool_input.get("offset") or tool_input.get("limit"):
        logger.debug("offset/limit provided, skipping warning.")
        sys.exit(0)

    path = Path(file_path)
    if not path.exists() or not path.is_file():
        sys.exit(0)

    try:
        line_count = _count_lines(path)
    except OSError:
        sys.exit(0)

    logger.debug("file_path=%s line_count=%d", file_path, line_count)

    if line_count <= LINE_THRESHOLD:
        sys.exit(0)

    output = json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    f"File {file_path} has {line_count} lines (>{LINE_THRESHOLD}). "
                    "Prefer reading only the relevant part via `offset`/`limit`, "
                    "or use Grep to locate the section first instead of reading "
                    "the whole file."
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
        sys.exit(0)
