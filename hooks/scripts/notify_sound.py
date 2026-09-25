#!/usr/bin/env python3
"""Play alert.mp3 when Claude asks the user a question or needs a permission decision.

Wired to three hook events:
  - PreToolUse (matcher AskUserQuestion): payload has tool_name, no "message"
    -> always play.
  - PermissionRequest: payload has tool_name, no "message" -> always play.
  - Notification: payload has "message"; play only for permission / input-needed
    text so unrelated notifications stay silent.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys

SOUND = (
    Path(__file__).resolve().parents[2] / "hooks" / "assets" / "sounds" / "alert.mp3"
)

# Notification "message" substrings that mean "user action needed".
TRIGGERS = ("permission", "waiting for your input", "needs your input", "wants to")


def play(path: Path) -> None:
    """Play sound file using available system player.

    Args:
        path: Path to the audio file.
    """
    for player, args in (
        ("paplay", [str(path)]),
        ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet", str(path)]),
        ("aplay", [str(path)]),
        ("cvlc", ["--play-and-exit", "--intf", "dummy", str(path)]),
    ):
        if shutil.which(player):
            subprocess.Popen(  # noqa: S603
                [player, *args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return


def should_play(data: dict) -> bool:
    """Check if notification should trigger sound.

    Args:
        data: Hook payload dictionary.

    Returns:
        True if sound should play, False otherwise.
    """
    event = data.get("hook_event_name", "")
    if event == "Notification":
        return any(t in str(data.get("message", "")).lower() for t in TRIGGERS)
    # PreToolUse / PermissionRequest (or anything else it is wired to): always.
    return True


def main() -> None:
    """Load hook payload from stdin and play alert if criteria are met."""
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        data = {}
    if SOUND.exists() and should_play(data):
        play(SOUND)


if __name__ == "__main__":
    main()
