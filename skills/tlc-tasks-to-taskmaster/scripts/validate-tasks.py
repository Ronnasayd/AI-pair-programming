#!/usr/bin/env python3
"""
Validate TaskMaster JSON structure and content.

Usage:
  validate-tasks.py <file_type> <json_file>

Args:
  file_type: "tasks"
  json_file: Path to JSON file to validate

Returns:
  0 on success, 1 on validation failure
"""

import json
import sys
from pathlib import Path


def validate_tasks_json(filepath):
    """Validate .taskmaster/tasks/tasks.json structure."""
    try:
        with open(filepath) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON syntax: {e}", file=sys.stderr)
        return False

    # Must have at least one tag
    if not isinstance(data, dict) or not data:
        print("ERROR: tasks.json must contain at least one tag key", file=sys.stderr)
        return False

    # Each tag must have "tasks" array
    for tag, content in data.items():
        if not isinstance(content, dict) or "tasks" not in content:
            print(f"ERROR: Tag '{tag}' missing 'tasks' key", file=sys.stderr)
            return False

        tasks = content["tasks"]
        if not isinstance(tasks, list):
            print(f"ERROR: Tag '{tag}' tasks must be array", file=sys.stderr)
            return False

        # Validate each task
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                print(f"ERROR: Tag '{tag}' task[{i}] is not object", file=sys.stderr)
                return False

            required_fields = [
                "id",
                "title",
                "description",
                "status",
                "priority",
                "dependencies",
                "details",
                "testStrategy",
                "subtasks",
                "metadata",
            ]
            for field in required_fields:
                if field not in task:
                    print(
                        f"ERROR: Tag '{tag}' task[{i}] missing field '{field}'",
                        file=sys.stderr,
                    )
                    return False

            # Validate metadata
            if not isinstance(task.get("metadata"), dict):
                print(
                    f"ERROR: Tag '{tag}' task[{i}] metadata must be object",
                    file=sys.stderr,
                )
                return False

            meta = task["metadata"]
            if "wave" not in meta or "onCriticalPath" not in meta:
                print(
                    f"ERROR: Tag '{tag}' task[{i}] metadata missing wave or onCriticalPath",
                    file=sys.stderr,
                )
                return False

    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: validate-tasks.py <tasks> <json_file>", file=sys.stderr)
        sys.exit(1)

    file_type = sys.argv[1]
    json_file = sys.argv[2]

    if not Path(json_file).exists():
        print(f"ERROR: File not found: {json_file}", file=sys.stderr)
        sys.exit(1)

    if file_type == "tasks":
        success = validate_tasks_json(json_file)
    else:
        print(
            f"ERROR: Unknown file_type '{file_type}' (use 'tasks')",
            file=sys.stderr,
        )
        sys.exit(1)

    sys.exit(0 if success else 1)
