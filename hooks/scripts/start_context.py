#!/usr/bin/python3
# log-tool-calls.py

import json
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("StartContext")

with open(os.path.join(script_dir, "..", "markdown/START.md")) as f:
    RULES = f.read()


def package_json(payload):
    cwd = get_by_key(payload, "cwd")
    package_json_path = os.path.join(cwd, "package.json")
    if not os.path.exists(package_json_path):
        return ""
    with open(package_json_path) as f:
        package_data = json.loads(f.read())
    scripts = package_data.get("scripts", {})
    if not scripts:
        return ""
    return "## package.json scripts\n\n" + "\n".join(
        f"- `{name}`: {cmd}" for name, cmd in scripts.items()
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # erro no parse não bloqueia nada
    additional_context = f"{RULES}"
    package_text = package_json(payload)
    if package_text:
        additional_context += f"\n\n{package_text}"
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context,
        }
    }
    LOG.debug(f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
