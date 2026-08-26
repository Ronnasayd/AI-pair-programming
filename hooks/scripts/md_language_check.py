#!/usr/bin/python3
"""PreToolUse hook: remind the agent to write in English when a .md file is
being written into a directory that requires English-only docs."""

import fnmatch
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("MdLanguageCheck")

# Glob patterns (matched against the file path with fnmatch) whose targets
# require English-only markdown content.
ENGLISH_ONLY_DIRS = [
    "*/.spec/**",
    ".spec/**",
    "*/docs/**",
    "docs/**",
]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse JSON: {e}")
        sys.exit(0)

    tool_input = get_by_key(payload, "tool_input") or {}
    file_path = get_by_key(tool_input, "file_path") or ""

    if not file_path.endswith(".md"):
        sys.exit(0)

    if not any(fnmatch.fnmatch(file_path, pattern) for pattern in ENGLISH_ONLY_DIRS):
        sys.exit(0)

    file_name = Path(file_path).name
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                f"Writing {file_name} into an English-only documentation "
                "directory. Write this file's content in English, "
                "regardless of the conversation language."
            ),
        }
    }
    LOG.debug(f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
