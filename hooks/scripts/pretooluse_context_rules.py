#!/usr/bin/python3
"""Generic PreToolUse hook: inject additionalContext when a rule's criteria match.

Each rule declares which tool_name it applies to and a regex tested against
every string value found in tool_input (so it doesn't depend on knowing the
exact field name a given tool uses, e.g. Skill's "command" field).
"""

import json
import re
import sys
from os import path

script_dir = path.dirname(path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)
from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("PreToolUseContextRules")


def read_file(filepath: str):
    with open(filepath) as f:
        return f.read()


# Add new rules here. Each rule: tool_name to match, regex tested against any
# tool_input value, and the additionalContext to inject when both match.
RULES = [
    {
        "name": "tlc-execute-tasks",
        "tool_name": "Skill",
        "pattern": re.compile(r"^tlc-execute-tasks(-adversarial)?$"),
        "additionalContext": read_file(
            path.join(script_dir, "..", "markdown/TASKS.md")
        ),
    },
]


def iterStringValues(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from iterStringValues(v)
    elif isinstance(value, list):
        for v in value:
            yield from iterStringValues(v)


def matchRule(rule, tool_name, tool_input):
    if tool_name != rule["tool_name"]:
        return False
    return any(rule["pattern"].search(v) for v in iterStringValues(tool_input))


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse JSON: {e}")
        sys.exit(0)

    tool_name = get_by_key(payload, "tool_name")
    tool_input = get_by_key(payload, "tool_input") or {}
    if not tool_name:
        sys.exit(0)

    matched = [rule for rule in RULES if matchRule(rule, tool_name, tool_input)]
    if not matched:
        LOG.debug(f"No rule matched tool_name={tool_name!r} input={tool_input!r}")
        sys.exit(0)

    contexts = [rule["additionalContext"] for rule in matched]
    LOG.debug(f"Matched rules: {[r['name'] for r in matched]}")

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "\n\n".join(contexts),
        }
    }
    LOG.debug(f"Output:{json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
