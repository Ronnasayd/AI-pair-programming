#!/usr/bin/python3
"""Generic hook: inject additionalContext when a rule's `match(payload)` returns True.

Each rule gets the full raw hook payload, so matching logic isn't limited to
a fixed set of fields (event/tool_name/tool_input/...) — add whatever check
you need directly in the rule's `match` lambda/function.
"""

import json
import re
import sys
from os import path

script_dir = path.dirname(path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)
from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("ToolUseContextRules")


def read_file(filepath: str):
    with open(filepath) as f:
        return f.read()


def iterStringValues(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from iterStringValues(v)
    elif isinstance(value, list):
        for v in value:
            yield from iterStringValues(v)


def toolInputMatches(payload, pattern: re.Pattern):
    tool_input = get_by_key(payload, "tool_input") or {}
    return any(pattern.search(v) for v in iterStringValues(tool_input))


# Add new rules here. Each rule: a name, and a `match(payload)` predicate that
# decides whether `additionalContext` gets injected for this hook call.
RULES = [
    {
        "name": "plan-mode-ask-user-question-grilling",
        "match": lambda payload: (
            get_by_key(payload, "hook_event_name") == "PreToolUse"
            and (
                get_by_key(payload, "tool_name") == "AskUserQuestion"
                or get_by_key(payload, "tool_name") == "UserPromptSubmit"
            )
            and get_by_key(payload, "permission_mode") == "plan"
        ),
        "additionalContext": (
            "use the skill `grilling` for Grill the user relentlessly about "
            "a plan or design. Use when the user wants to stress-test a plan "
            "before building, or uses any 'grill' trigger phrases."
        ),
    },
]


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse JSON: {e}")
        sys.exit(0)

    hook_event_name = get_by_key(payload, "hook_event_name")
    tool_name = get_by_key(payload, "tool_name")
    if not tool_name or not hook_event_name:
        sys.exit(0)

    matched = [rule for rule in RULES if rule["match"](payload)]
    if not matched:
        # LOG.debug(f"No rule matched payload={payload!r}")
        sys.exit(0)

    contexts = [rule["additionalContext"] for rule in matched]
    LOG.debug(f"Matched rules: {[r['name'] for r in matched]}")

    output = {
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
            "additionalContext": "\n\n".join(contexts),
        }
    }
    LOG.debug(f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
