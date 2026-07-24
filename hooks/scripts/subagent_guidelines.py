#!/usr/bin/python3
"""PreToolUse hook: inject guidelines when a subagent is started."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("SubagentGuidelines")

GUIDELINES = (
    "When starting a new agent/sub-agent, make sure to follow these guidelines:\n\n"
    '- The agent must be instructed to communicate using "caveman full."\n\n'
    "- The agent must have sufficient context to perform its task.\n\n"
    "- Choose the agent model best suited to the task.\n\n"
    "- The agent must not make commits unless the user explicitly authorizes it."
)

AGENT_TOOL_NAMES = {"agent", "task"}


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse JSON: {e}")
        sys.exit(0)

    tool_name = get_by_key(payload, "tool_name")
    if not tool_name or tool_name.lower() not in AGENT_TOOL_NAMES:
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": GUIDELINES,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
