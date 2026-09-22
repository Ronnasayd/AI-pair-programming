#!/usr/bin/python3
"""UserPromptSubmit hook.

Pins the turn's starting commit SHA to a per-session file, so the Stop-time
lint gate can diff against a fixed point even if the agent commits mid-turn
(diffing live HEAD against itself always shows nothing after a commit).
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
    project_dir,
    run_command_cwd,
    tmp_project_dir,
)

LOG = get_hooks_logger("TurnBaseSha")


def main() -> None:
    """Read the hook payload from stdin, pin HEAD's SHA, pass stdin through."""
    stdin_data = sys.stdin.read()

    try:
        payload = json.loads(stdin_data)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse JSON: %s", e)
        sys.stdout.write(stdin_data)
        sys.exit(0)

    project_root = project_dir(payload)
    session_id = get_by_key(payload, "session_id") or ""

    result = run_command_cwd("git rev-parse HEAD", cwd=project_root)
    if result["success"] and result["output"]:
        sha_path = (
            tmp_project_dir(project_root, "turn-base-sha")
            / f"{get_session_id_short(session_id)}.txt"
        )
        sha_path.write_text(result["output"], encoding="utf-8")
        LOG.debug("Pinned turn-base SHA %s to %s", result["output"], sha_path)
    else:
        LOG.debug("git rev-parse HEAD failed, skipping SHA pin: %s", result)

    sys.stdout.write(stdin_data)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        LOG.debug("Error: %s", exc)
        sys.exit(0)
