#!/usr/bin/python3
"""PreToolUse hook: inject guidelines when a subagent is started."""

import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger, minify_markdown

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

LOG = get_hooks_logger("SubagentGuidelines")
with open(
    os.path.join(script_dir, "..", "markdown/SUBAGENT-GUIDELINES.md"), encoding="utf-8"
) as f:
    GUIDELINES = f.read()

AGENT_TOOL_NAMES = {"agent", "task"}


def main() -> None:
    """Execute the subagent guidelines hook."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse JSON: %s", e)
        sys.exit(0)

    tool_name = get_by_key(payload, "tool_name")
    if not tool_name or tool_name.lower() not in AGENT_TOOL_NAMES:
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": minify_markdown(GUIDELINES),
        }
    }
    LOG.debug("[additionalContext]: %s", json.dumps(output, ensure_ascii=False))
    LOG.info("%s", json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
