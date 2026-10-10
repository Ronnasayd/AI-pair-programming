#!/usr/bin/python3
"""PreToolUse hook: deny creating .md files outside standard documentation dirs.

Guards against unintended boilerplate. Overwriting existing files and allowed
locations stay silent.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger

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
    "README.md",
]


def main() -> None:
    """Check if .md file creation is outside allowed documentation directories."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse JSON: %s", e)
        sys.exit(0)

    tool_input = get_by_key(payload, "tool_input") or {}
    file_path = get_by_key(tool_input, "file_path") or ""

    if not file_path.endswith(".md"):
        sys.exit(0)

    if any(pattern in file_path for pattern in ALLOWED_PATTERNS):
        sys.exit(0)

    if Path(file_path).exists():
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"Creating {Path(file_path).name} outside standard documentation "
                "directories (docs/, skills/, agents/, commands/, .specs/, ...). "
                "Move it there, or ask the user if this location is intentional."
            ),
        }
    }
    LOG.debug("[blocked]: %s", json.dumps(output, ensure_ascii=False))
    print(json.dumps(output, ensure_ascii=False))  # noqa: T201
    sys.exit(0)


if __name__ == "__main__":
    main()
