#!/usr/bin/env python3
"""
Merge new task tag into existing tasks.json without overwriting other tags.
Preserves all existing tags and adds/updates the specified tag.

Usage:
  merge-tasks.py <tasks_file> <new_tag> <new_tasks_json>

Args:
  tasks_file: Path to existing .taskmaster/tasks/tasks.json
  new_tag: Tag key to add/update (e.g., "master", "feature/auth")
  new_tasks_json: JSON string with tasks array for the new tag
"""

import json
import sys
from pathlib import Path


def merge_tasks(tasks_file, new_tag, new_tasks_json):
    """Merge new tasks under new_tag into existing tasks.json."""
    tasks_path = Path(tasks_file)

    # Read existing file or start fresh
    if tasks_path.exists():
        try:
            with open(tasks_path) as f:
                merged = json.load(f)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {tasks_file}: {e}", file=sys.stderr)
            return False
    else:
        merged = {}

    # Parse new tasks JSON
    try:
        new_tasks = json.loads(new_tasks_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid new_tasks_json: {e}", file=sys.stderr)
        return False

    # Merge: add/update tag without removing others
    merged[new_tag] = {"tasks": new_tasks}

    # Write back
    try:
        with open(tasks_path, "w") as f:
            json.dump(merged, f, indent=2)
        return True
    except Exception as e:
        print(f"ERROR: Failed to write {tasks_file}: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: merge-tasks.py <tasks_file> <new_tag> <new_tasks_json>",
            file=sys.stderr,
        )
        sys.exit(1)

    tasks_file = sys.argv[1]
    new_tag = sys.argv[2]
    new_tasks_json = sys.argv[3]

    success = merge_tasks(tasks_file, new_tag, new_tasks_json)
    sys.exit(0 if success else 1)
