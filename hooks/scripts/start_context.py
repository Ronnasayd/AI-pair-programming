#!/usr/bin/python3
# log-tool-calls.py

import json
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("StartContext")

with open(os.path.join(script_dir, "..", "markdown/START.md")) as f:
    RULES = f.read()


def main():
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": RULES,
        }
    }
    LOG.debug(f"Output: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
