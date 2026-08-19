#!/usr/bin/python3
"""PreToolUse hook: warn when a .md file is created outside standard
documentation directories, in case it's unintended boilerplate."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("MdLocationCheck")

ALLOWED_PATTERNS = [
    "/docs/",
    "docs/",
    "/documentation/",
    "/commands/",
    "/skills/",
    "/agents/",
    "/rules/",
    ".specs/",
    "/templates/",
    "CLAUDE.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "CODEMAP.md",
    "CONTRIBUTING.md",
    "SKILL.md",
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

    if any(pattern in file_path for pattern in ALLOWED_PATTERNS):
        sys.exit(0)

    file_name = Path(file_path).name
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                f"Creating {file_name} outside of standard documentation "
                "directories. Make sure this file is intentional and not "
                "auto-generated boilerplate."
            ),
        }
    }
    LOG.debug(f"[warning]: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
