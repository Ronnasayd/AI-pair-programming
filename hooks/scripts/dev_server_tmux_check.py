#!/usr/bin/python3
"""PreToolUse hook: block dev-server commands run outside tmux/screen, to
avoid orphaned background processes."""

import io
import json
import os
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger, split_on_operators  # noqa: E402

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


def _unquoted_text(segment: str) -> str:
    """Reconstruct a command segment keeping only its unquoted tokens.

    Drops any token that came from inside '...' or "..." (e.g. the commit
    message in `git commit -m "npm run dev"`), so quoted text can't trigger
    a false match against DEV_SERVER_PATTERNS.
    """
    stream = io.StringIO(segment)
    lexer = shlex.shlex(stream, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    tokens = []
    try:
        while True:
            start = stream.tell()
            token = lexer.get_token()
            if token is None:
                break
            raw = segment[start : stream.tell()]
            if raw.strip().startswith(("'", '"')):
                continue
            tokens.append(token)
    except ValueError:
        return segment
    return " ".join(tokens)


def is_dev_server(command: str) -> bool:
    """Check whether a shell command starts a long-running dev server.

    Only the text before the first heredoc marker is scanned, split on shell
    operators (&&, ||, ;, |, newlines) and stripped of quoted text, so a
    dev-server pattern occurring inside a quoted string (e.g. a commit
    message) doesn't trigger a false match. Patterns must also match on word
    boundaries: previously any text mentioning "invite" matched "vite" and
    blocked plain file writes.

    Args:
        command: The full shell command line submitted to the Bash tool.

    Returns:
        True when the command line invokes a known dev server.
    """
    head = command.split("<<", 1)[0]
    segments = split_on_operators(head)
    text = " ".join(_unquoted_text(segment) for segment in segments).lower()
    return any(
        re.search(rf"(?<![\w.-]){re.escape(pattern)}(?![\w.-])", text)
        for pattern in DEV_SERVER_PATTERNS
    )


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
