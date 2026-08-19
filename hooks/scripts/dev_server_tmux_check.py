#!/usr/bin/python3
"""PreToolUse hook: block dev-server commands run outside tmux/screen, to
avoid orphaned background processes."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("DevServerTmuxCheck")

DEV_SERVER_PATTERNS = [
    "npm run dev",
    "npm start",
    "yarn dev",
    "pnpm dev",
    "bun dev",
    "next dev",
    "vite",
    "webpack serve",
    "nodemon",
    "ts-node-dev",
    "python manage.py runserver",
    "flask run",
    "uvicorn",
    "cargo watch",
]


def is_dev_server(command: str) -> bool:
    lowered = command.lower()
    return any(pattern in lowered for pattern in DEV_SERVER_PATTERNS)


def in_multiplexer() -> str | None:
    tmux_val = os.environ.get("TMUX", "")
    if tmux_val and Path(tmux_val.split(",")[0]).exists():
        return "tmux"
    if os.environ.get("STY"):
        return "screen"
    return None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse JSON: {e}")
        sys.exit(0)

    if get_by_key(payload, "tool_name") != "Bash":
        sys.exit(0)

    tool_input = get_by_key(payload, "tool_input") or {}
    command = get_by_key(tool_input, "command") or ""
    if not is_dev_server(command):
        sys.exit(0)

    multiplexer = in_multiplexer()
    if multiplexer:
        LOG.debug(f"dev server command allowed inside {multiplexer}")
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Dev server commands should run inside tmux or screen to "
                "prevent orphaned processes. Start a tmux session first or "
                "run the command in the background."
            ),
        }
    }
    LOG.debug(f"[blocked]: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
