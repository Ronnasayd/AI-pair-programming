
import os
from typing import Any, Dict
import re
from datetime import datetime
import json
import sys


TASKS_DIR = ".taskmaster/tasks"
TASKS_JSON = "tasks.json"
TASKS_MD = "tasks.md"
META_JSON = "meta.json"

def _merge_tasks_with_meta(
    tasks_json: Dict[str, Any], meta: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fills tasks.json (after parsing markdown) with extra fields from meta.json.

    Args:
        tasks_json: Task structure converted from markdown.
        meta: Extra metadata indexed by id.

    Returns:
        dict: Task structure enriched with metadata.
    """
    for _, context_data in tasks_json.items():
        if "tasks" not in context_data:
            continue
        for task in context_data["tasks"]:
            task_id = str(task.get("id"))
            if task_id in meta:
                for k, v in meta[task_id].items():
                    task[k] = v
            # Subtasks
            for subtask in task.get("subtasks", []):
                sub_id = f"{task_id}.{subtask.get('id')}"
                if sub_id in meta:
                    for k, v in meta[sub_id].items():
                        subtask[k] = v
    return tasks_json



def _symbol_to_status(symbol: str) -> str:
    """
    Converts markdown checkbox symbol to status string.

    Args:
        symbol: Checkbox symbol (space, /, x, -)

    Returns:
        str: Corresponding status string
    """
    symbol_map = {
        " ": "pending",
        "/": "in-progress",
        "x": "done",
        "-": "cancelled",
    }
    return symbol_map.get(symbol, "pending")




def _format_error(message: str, exc: Exception) -> Dict[str, str]:
    """Helper to format error responses consistently."""
    return {"error": f"{message}: {str(exc)}"}



def _extract_meta_from_tasks(tasks_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts extra fields from tasks.json to meta.json, indexing by id (and composite id for subtasks).

    Args:
        tasks_data: Dictionary with task data.

    Returns:
        dict: Extra metadata indexed by id.
    """
    meta = {}
    for _, context_data in tasks_data.items():
        if "tasks" not in context_data:
            continue
        for task in context_data["tasks"]:
            task_id = str(task.get("id"))
            meta[task_id] = {
                k: v
                for k, v in task.items()
                if k not in ("id", "title", "status", "subtasks")
            }
            # Subtasks
            for subtask in task.get("subtasks", []):
                sub_id = f"{task_id}.{subtask.get('id')}"
                meta[sub_id] = {
                    k: v
                    for k, v in subtask.items()
                    if k not in ("id", "title", "status")
                }
    return meta




def _get_status_symbol(status: str) -> str:
    """
    Converts status string to markdown checkbox symbol.

    Args:
        status: Status string (pending, in-progress, done, cancelled)

    Returns:
        str: Corresponding checkbox symbol
    """
    status_map = {
        "pending": "[ ]",
        "in-progress": "[/]",
        "done": "[x]",
        "cancelled": "[-]",
    }
    return status_map.get(status.lower(), "[ ]")



def _generate_markdown_from_tasks(tasks_data: Dict[str, Any]) -> str:
    """
    Generates markdown content from tasks JSON data.

    Args:
        tasks_data: Dictionary containing tasks data

    Returns:
        str: Formatted markdown content
    """
    markdown_lines = []

    # Header
    markdown_lines.extend(
        [
            "## Legenda:",
            "",
            "- [ ] = pending",
            "- [/] = in-progress",
            "- [-] = cancelled",
            "- [x] = done",
            "",
            "---",
            "",
            "",
            "# Tasks",
            "",
        ]
    )

    # Process each context (e.g., "master")
    for _, context_data in tasks_data.items():
        if "tasks" not in context_data:
            continue

        tasks = context_data["tasks"]

        # Sort tasks by id for consistent output
        sorted_tasks = sorted(tasks, key=lambda x: x.get("id", 0))

        for task in sorted_tasks:
            # Skip empty tasks or tasks without proper structure
            if not task or not task.get("title"):
                continue

            # Convert status to markdown checkbox
            status_symbol = _get_status_symbol(task.get("status", "pending"))

            # Main task
            task_id = task.get("id", "")
            title = task.get("title", "Untitled Task")
            description = task.get("description", "").strip()

            markdown_lines.append(f"- {status_symbol} {task_id} - {title}")
            # Include description as a field (two-space indent) if present
            if description:
                # Normalize newlines to a single line to keep markdown parsing simple
                desc_single = " ".join(description.splitlines()).strip()
                if desc_single and desc_single != title:
                    markdown_lines.append(f"  - **Description**: {desc_single}")

            # Process subtasks if they exist
            subtasks = task.get("subtasks", [])
            if subtasks:
                # Sort subtasks by id if they have one
                try:
                    sorted_subtasks = sorted(subtasks, key=lambda x: x.get("id", 0))
                except (TypeError, KeyError):
                    sorted_subtasks = subtasks

                for subtask in sorted_subtasks:
                    if not subtask or not subtask.get("title"):
                        continue

                    subtask_status_symbol = _get_status_symbol(
                        subtask.get("status", "pending")
                    )
                    subtask_id = subtask.get("id", "")
                    subtask_title = subtask.get("title", "Untitled Subtask")
                    subtask_description = subtask.get("description", "").strip()

                    markdown_lines.append(
                        f"  - {subtask_status_symbol} {subtask_id} - {subtask_title}"
                    )
                    # Include subtask description as a deeper-indented field (4 spaces)
                    if subtask_description:
                        sub_desc_single = " ".join(subtask_description.splitlines()).strip()
                        if sub_desc_single and sub_desc_single != subtask_title:
                            markdown_lines.append(f"    - **Description**: {sub_desc_single}")

            markdown_lines.append("")
            markdown_lines.append("---")  # Separator between main tasks

    return "\n".join(markdown_lines)



def _parse_markdown_to_tasks(markdown_content: str) -> Dict[str, Any]:
    """
    Parses markdown content in TODO-events format and converts to tasks.json structure.

    Args:
        markdown_content: Markdown content string

    Returns:
        dict: Tasks JSON structure
    """

    lines = markdown_content.split("\n")
    tasks = []
    current_task = None
    current_subtask = None
    task_id_counter = 1
    subtask_id_counter = 1

    # Patterns for parsing
    main_task_pattern = r"^- \[(.)\] (\d+) - (.+)$"
    subtask_pattern = r"^  - \[(.)\] (\d+) - (.+)$"
    field_pattern = r"^  - \*\*([^*]+)\*\*: (.+)$"
    subtask_field_pattern = r"^    - \*\*([^*]+)\*\*: (.+)$"

    for line in lines:
        line = line.rstrip()

        # Skip empty lines and separators
        if not line or line == "---" or line.startswith("#") or "Legenda:" in line:
            continue

        # Check for main task
        main_task_match = re.match(main_task_pattern, line)
        if main_task_match:
            # Save previous task if exists
            if current_task:
                tasks.append(current_task)

            status_symbol, task_id, title = main_task_match.groups()
            status = _symbol_to_status(status_symbol)

            current_task = {
                "id": int(task_id) if task_id.isdigit() else task_id_counter,
                "title": f"{title.strip()}",
                "description": f"{title.strip()}",
                "details": "",
                "testStrategy": "",
                "priority": "medium",
                "dependencies": [],
                "status": status,
                "subtasks": [],
            }
            task_id_counter = (
                max(task_id_counter, int(task_id) + 1)
                if task_id.isdigit()
                else task_id_counter + 1
            )
            subtask_id_counter = 1
            current_subtask = None
            continue

        # Check for subtask
        subtask_match = re.match(subtask_pattern, line)
        if subtask_match and current_task:
            status_symbol, subtask_id, title = subtask_match.groups()
            status = _symbol_to_status(status_symbol)

            current_subtask = {
                "id": int(subtask_id) if subtask_id.isdigit() else subtask_id_counter,
                "title": f"{title.strip()}",
                "description": f"{title.strip()}",
                "details": "",
                "testStrategy": "",
                "priority": "medium",
                "dependencies": [],
                "status": status,
            }
            current_task["subtasks"].append(current_subtask)
            subtask_id_counter = (
                max(subtask_id_counter, int(subtask_id) + 1)
                if subtask_id.isdigit()
                else subtask_id_counter + 1
            )
            continue

        # Check for subtask field
        subtask_field_match = re.match(subtask_field_pattern, line)
        if subtask_field_match and current_subtask:
            field_name, field_value = subtask_field_match.groups()
            field_name = field_name.strip()
            field_value = field_value.strip()

            # Map known fields into the current subtask
            key = field_name.lower()
            if key == "description":
                current_subtask["description"] = field_value
            elif key == "details":
                current_subtask["details"] = field_value
            elif key == "priority":
                current_subtask["priority"] = field_value
            elif key == "status":
                # Allow overriding status via field
                current_subtask["status"] = _symbol_to_status(field_value) if len(field_value) == 1 else field_value

            continue

        # Check for main task field
        field_match = re.match(field_pattern, line)
        if field_match and current_task:
            field_name, field_value = field_match.groups()
            field_name = field_name.strip()
            field_value = field_value.strip()
            # Map known fields into the current main task
            key = field_name.lower()
            if key == "description":
                current_task["description"] = field_value
            elif key == "details":
                current_task["details"] = field_value
            elif key == "priority":
                current_task["priority"] = field_value
            elif key == "status":
                current_task["status"] = _symbol_to_status(field_value) if len(field_value) == 1 else field_value

    # Don't forget the last task
    if current_task:
        tasks.append(current_task)

    # Create the complete structure
    current_time = datetime.now().isoformat() + "Z"

    tasks_json = {
        "master": {
            "tasks": tasks,
            "metadata": {
                "created": current_time,
                "updated": current_time,
                "description": "Tasks converted from markdown format",
            },
        }
    }

    return tasks_json




def convert_tasks_to_markdown(
) -> Dict[str, Any]:
    """
    Converts a .taskmaster/tasks/tasks.json file to markdown format similar to TODO-events.md.
    Also generates meta.json with the extra fields of tasks/subtasks.

    Args:
        rootProject: Project root directory (optional).

    Returns:
        dict: Success or error message.
    """
    try:
        tasks_file_path = os.path.join(TASKS_DIR, TASKS_JSON)
        if not os.path.isfile(tasks_file_path):
            return {"error": f"tasks.json file not found at: {tasks_file_path}"}
        with open(tasks_file_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
        markdown_content = _generate_markdown_from_tasks(tasks_data)
        tasks_dir_path = os.path.join( TASKS_DIR)
        if not os.path.exists(tasks_dir_path):
            os.makedirs(tasks_dir_path)
        with open(os.path.join(tasks_dir_path, TASKS_MD), "w", encoding="utf-8") as f:
            f.write(markdown_content)
        # Gera meta.json
        meta = _extract_meta_from_tasks(tasks_data)
        with open(os.path.join(tasks_dir_path, META_JSON), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        return {"content": "Files tasks.md and meta.json created successfully."}
    except json.JSONDecodeError as e:
        return _format_error("Error decoding JSON", e)
    except OSError as e:
        return _format_error("System error when opening file", e)
    except Exception as e:
        return _format_error("Unexpected error processing tasks", e)



def convert_markdown_to_tasks() -> Dict[str, Any]:
    """
    Converts a markdown file in TODO-events format to tasks.json format.
    Uses meta.json to restore extra fields, if available.

    Args:
        rootProject: Project root directory (optional).

    Returns:
        dict: Success or error message.
    """
    try:
        markdown_file_path = os.path.join( TASKS_DIR, TASKS_MD)
        meta_file_path = os.path.join( TASKS_DIR, META_JSON)
        if not os.path.isfile(markdown_file_path):
            return {
                "error": f"Markdown file not found at: {markdown_file_path}"
            }
        with open(markdown_file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()
        tasks_json = _parse_markdown_to_tasks(markdown_content)
        # If meta.json exists, restore extra fields
        if os.path.isfile(meta_file_path):
            with open(meta_file_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            tasks_json = _merge_tasks_with_meta(tasks_json, meta)
        tasks_json_str = json.dumps(tasks_json, ensure_ascii=False, indent=2)
        with open(
            os.path.join( TASKS_DIR, TASKS_JSON), "w", encoding="utf-8"
        ) as f:
            f.write(tasks_json_str)
        return {"content": f"{TASKS_DIR}/{TASKS_JSON} created successfully."}
    except OSError as e:
        return _format_error("System error when opening markdown file", e)
    except Exception as e:
        return _format_error("Unexpected error processing markdown", e)


if __name__ == "__main__":
    # Example usage:
    if len(sys.argv) < 2:
        print("Usage: python convert_tasks.py [--to_markdown|--to_tasks]")
        sys.exit(1)

    if sys.argv[1] == "--to_markdown":
        print(convert_tasks_to_markdown())
    elif sys.argv[1] == "--to_tasks":
        print(convert_markdown_to_tasks())
    else:
        print("Invalid option. Use '--to_markdown' or '--to_tasks'.")
        sys.exit(1)

