#!/usr/bin/python3
"""PreToolUse hook.

Reminds the agent to write in the configured language when a .md file is
being written into a directory that requires language-controlled docs.
"""

import fnmatch
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger

LOG = get_hooks_logger("MdLanguageCheck")

# Glob patterns (matched against the file path with fnmatch) whose targets
# require language-controlled markdown content.
ENGLISH_ONLY_DIRS = [
    "*/.spec/**",
    ".spec/**",
    "*/docs/**",
    "docs/**",
]

MD_LANGUAGE = os.environ.get("MD_LANGUAGE", "English")


def main() -> None:
    """Read the tool payload from stdin and emit a language reminder."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse JSON: %s", e)
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
                f"Writing {file_name} into a language-controlled documentation "
                f"directory. Write this file's content in {MD_LANGUAGE}, "
                "regardless of the conversation language."
            ),
        }
    }
    LOG.debug("[additionalContext]: %s", json.dumps(output, ensure_ascii=False))
    print(json.dumps(output, ensure_ascii=False))  # noqa: T201
    sys.exit(0)


if __name__ == "__main__":
    main()
