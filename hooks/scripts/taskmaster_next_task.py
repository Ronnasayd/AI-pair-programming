#!/usr/bin/python3
"""SessionStart hook: surface next pending task per taskmaster tag."""

import json
import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger  # noqa: E402

logger = get_hooks_logger("TaskmasterNextTask")

TASKS_PATH = ".taskmaster/tasks/tasks.json"


def find_next_pending(tasks: list) -> dict | None:
    for task in tasks:
        if task.get("status") == "pending":
            return task
    return None


def build_context(workspace_root: str) -> str | None:
    tasks_file = Path(workspace_root) / TASKS_PATH
    if not tasks_file.is_file():
        return None

    try:
        data = json.loads(tasks_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    if not isinstance(data, dict):
        return None

    lines = []
    for tag, tag_data in data.items():
        tasks = tag_data.get("tasks") if isinstance(tag_data, dict) else None
        if not isinstance(tasks, list):
            continue
        next_task = find_next_pending(tasks)
        if next_task is None:
            continue
        lines.append(
            f'- `{tag}`: #{next_task.get("id")} "{next_task.get("title")}"'
            f" (priority: {next_task.get('priority')})"
        )

    if not lines:
        return None

    return "# [SessionStart] Taskmaster — next pending task per tag:\n" + "\n".join(
        lines
    )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        workspace_root = payload.get("cwd", ".")

        context = build_context(workspace_root)
        if context:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            }
            logger.debug("Taskmaster next-task hook produced context.")
            logger.debug(
                f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}"
            )
            print(json.dumps(output, ensure_ascii=False))
        else:
            logger.debug("Taskmaster next-task hook: nothing to report.")

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:  # pylint: disable=broad-exception-caught
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
