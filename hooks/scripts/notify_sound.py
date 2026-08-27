#!/usr/bin/env python3
"""Play alert.mp3 when Claude asks the user a question or needs a permission decision.

Wired to three hook events:
  - PreToolUse (matcher AskUserQuestion): payload has tool_name, no "message" -> always play.
  - PermissionRequest: payload has tool_name, no "message" -> always play.
  - Notification: payload has "message"; play only for permission / input-needed text so
    unrelated notifications stay silent.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

SOUND = (
    Path(__file__).resolve().parents[2] / "hooks" / "assets" / "sounds" / "alert.mp3"
)

# Notification "message" substrings that mean "user action needed".
TRIGGERS = ("permission", "waiting for your input", "needs your input", "wants to")


def play(path: Path) -> None:
    for player, args in (
        ("paplay", [str(path)]),
        ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet", str(path)]),
        ("aplay", [str(path)]),
        ("cvlc", ["--play-and-exit", "--intf", "dummy", str(path)]),
    ):
        if shutil.which(player):
            subprocess.Popen(
                [player, *args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return


def should_play(data: dict) -> bool:
    event = data.get("hook_event_name", "")
    if event == "Notification":
        return any(t in str(data.get("message", "")).lower() for t in TRIGGERS)
    # PreToolUse / PermissionRequest (or anything else it is wired to): always.
    return True


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}
    if SOUND.exists() and should_play(data):
        play(SOUND)


if __name__ == "__main__":
    main()
