#!/usr/bin/python3
"""PreToolUse hook: inject guidelines on the first subagent start per session."""

import contextlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger, get_session_id_short, minify_markdown

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

LOG = get_hooks_logger("SubagentGuidelines")
with open(
    os.path.join(script_dir, "..", "markdown/SUBAGENT-GUIDELINES.md"), encoding="utf-8"
) as f:
    GUIDELINES = f.read()
_response_template_path = os.path.join(
    script_dir, "..", "markdown/SUBAGENT-RESPONSE-TEMPLATE.md"
)
with open(_response_template_path, encoding="utf-8") as f:
    RESPONSE_TEMPLATE = f.read()

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

    session_id = get_session_id_short(get_by_key(payload, "session_id") or "")
    marker = Path(f"/tmp/subagent_guidelines_{session_id}")  # noqa: S108
    if marker.exists():
        sys.exit(0)
    with contextlib.suppress(OSError):
        marker.touch()

    combined = f"{GUIDELINES}\n\n{RESPONSE_TEMPLATE}"
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": minify_markdown(combined),
        }
    }
    LOG.debug("[additionalContext]: %s", json.dumps(output, ensure_ascii=False))
    print(json.dumps(output, ensure_ascii=False))  # noqa: T201 - hook stdout protocol
    sys.exit(0)


if __name__ == "__main__":
    main()
