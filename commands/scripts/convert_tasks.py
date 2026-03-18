
import glob
import os
from typing import Any, Dict, List, Optional, Tuple
import re
from datetime import datetime
import json
import sys


TASKS_DIR = ".taskmaster/tasks"
TASKS_JSON = "tasks.json"
TASKS_MD = "tasks.md"
META_JSON = "meta.json"


def _get_tags_from_json(tasks_json: Dict[str, Any]) -> List[str]:
    """
    Extracts all top-level tag keys from tasks.json.

    Args:
        tasks_json: Full tasks JSON structure.

    Returns:
        list: List of tag names (e.g., ["master", "review-1"]).
    """
    return list(tasks_json.keys())


def _generate_tag_filename(tag_name: str, file_type: str) -> str:
    """
    Maps a tag name to its corresponding filename.

    Args:
        tag_name: Tag identifier (e.g., "master", "review-1").
        file_type: File extension ("md" or "json").

    Returns:
        str: Filename (e.g., "tasks-master.md", "meta-review-1.json").
    """
    if file_type == "md":
        return f"tasks-{tag_name}.md"
    return f"meta-{tag_name}.json"


def _discover_tag_files(tasks_dir: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Scans the tasks directory for all tasks-*.md files and returns discovered tags.

    Args:
        tasks_dir: Path to the tasks directory.

    Returns:
        Tuple of (list of tag names, mapping of tag -> filepath).
    """
    pattern = os.path.join(tasks_dir, "tasks-*.md")
    files = sorted(glob.glob(pattern))
    tags: List[str] = []
    tag_to_file: Dict[str, str] = {}
    for filepath in files:
        filename = os.path.basename(filepath)
        match = re.match(r"^tasks-(.+)\.md$", filename)
        if match:
            tag_name = match.group(1)
            tags.append(tag_name)
            tag_to_file[tag_name] = filepath
    return tags, tag_to_file


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


def _extract_meta_from_tag_data(tag_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts extra fields from a single tag's task data, indexed by id.

    Args:
        tag_data: Single tag data dict (e.g., tasks_json["master"]).

    Returns:
        dict: Extra metadata indexed by id and composite sub-id.
    """
    meta: Dict[str, Any] = {}
    if "tasks" not in tag_data:
        return meta
    for task in tag_data["tasks"]:
        task_id = str(task.get("id"))
        meta[task_id] = {
            k: v
            for k, v in task.items()
            if k not in ("id", "title", "status", "subtasks")
        }
        for subtask in task.get("subtasks", []):
            sub_id = f"{task_id}.{subtask.get('id')}"
            meta[sub_id] = {
                k: v
                for k, v in subtask.items()
                if k not in ("id", "title", "status")
            }
    return meta


def _merge_tag_with_meta(
    tag_data: Dict[str, Any], meta: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fills a single tag's task data with extra fields from a per-tag meta dict.

    Args:
        tag_data: Single tag data dict (e.g., tasks_json["master"]).
        meta: Extra metadata indexed by id.

    Returns:
        dict: Tag data enriched with metadata.
    """
    if "tasks" not in tag_data:
        return tag_data
    for task in tag_data["tasks"]:
        task_id = str(task.get("id"))
        if task_id in meta:
            for k, v in meta[task_id].items():
                task[k] = v
        for subtask in task.get("subtasks", []):
            sub_id = f"{task_id}.{subtask.get('id')}"
            if sub_id in meta:
                for k, v in meta[sub_id].items():
                    subtask[k] = v
    return tag_data


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



def _generate_markdown_for_tag(tag_name: str, tag_data: Dict[str, Any]) -> str:
    """
    Generates complete markdown content for a single tag's task data.

    Args:
        tag_name: Tag identifier (e.g., "master", "review-1").
        tag_data: Single tag data dict (e.g., tasks_json["master"]).

    Returns:
        str: Formatted markdown content for that tag.
    """
    markdown_lines: List[str] = []

    # Header / legend
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

    if "tasks" not in tag_data:
        return "\n".join(markdown_lines)

    tasks = tag_data["tasks"]

    # Sort tasks by id for consistent output
    sorted_tasks = sorted(tasks, key=lambda x: x.get("id", 0))

    for task in sorted_tasks:
        # Skip empty tasks or tasks without proper structure
        if not task or not task.get("title"):
            continue

        status_symbol = _get_status_symbol(task.get("status", "pending"))
        task_id = task.get("id", "")
        title = task.get("title", "Untitled Task")
        description = task.get("description", "").strip()

        markdown_lines.append(f"- {status_symbol} {task_id} - {title}")
        if description:
            # Normalize newlines to a single line to keep markdown parsing simple
            desc_single = " ".join(description.splitlines()).strip()
            if desc_single and desc_single != title:
                markdown_lines.append(f"  - **Description**: {desc_single}")

        subtasks = task.get("subtasks", [])
        if subtasks:
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
                if subtask_description:
                    sub_desc_single = " ".join(subtask_description.splitlines()).strip()
                    if sub_desc_single and sub_desc_single != subtask_title:
                        markdown_lines.append(f"    - **Description**: {sub_desc_single}")

        markdown_lines.append("")
        markdown_lines.append("---")  # Separator between main tasks

    return "\n".join(markdown_lines)


def _generate_markdown_from_tasks(tasks_data: Dict[str, Any]) -> str:
    """
    Generates markdown content from tasks JSON data (all tags merged, backward-compatible).

    Iterates every tag and delegates to _generate_markdown_for_tag(); the results are
    concatenated so the legacy single-file output is preserved.

    Args:
        tasks_data: Full tasks JSON structure (all tags).

    Returns:
        str: Formatted markdown content for all tags.
    """
    parts: List[str] = []
    for tag_name, context_data in tasks_data.items():
        parts.append(_generate_markdown_for_tag(tag_name, context_data))
    return "\n".join(parts)



def _parse_markdown_to_tasks(
    markdown_content: str, tag_name: str = "master"
) -> Dict[str, Any]:
    """
    Parses markdown content in TODO-events format and converts to tasks.json structure.

    Args:
        markdown_content: Markdown content string.
        tag_name: Tag key to use in the output JSON (default: "master").

    Returns:
        dict: Tasks JSON structure keyed by tag_name.
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
        tag_name: {
            "tasks": tasks,
            "metadata": {
                "created": current_time,
                "updated": current_time,
                "description": "Tasks converted from markdown format",
            },
        }
    }

    return tasks_json


def _parse_all_tag_files(tasks_dir: str) -> Dict[str, Any]:
    """
    Discovers all tasks-*.md files in tasks_dir and parses them into a consolidated
    tasks.json structure keyed by tag name.

    For each discovered tag, the corresponding meta-{tag}.json is loaded (if present)
    and merged back into the task objects.

    Args:
        tasks_dir: Path to the tasks directory.

    Returns:
        dict: Consolidated tasks JSON structure (all tags).
    """
    tags, tag_to_file = _discover_tag_files(tasks_dir)
    result: Dict[str, Any] = {}
    for tag_name in tags:
        filepath = tag_to_file[tag_name]
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            print(f"Warning: could not read {filepath}: {e}", file=sys.stderr)
            continue

        tag_json = _parse_markdown_to_tasks(content, tag_name)
        tag_data = tag_json[tag_name]

        # Restore metadata from meta-{tag}.json if present
        meta_path = os.path.join(tasks_dir, f"meta-{tag_name}.json")
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                tag_data = _merge_tag_with_meta(tag_data, meta)
            except (OSError, json.JSONDecodeError) as e:
                print(
                    f"Warning: could not load meta for tag '{tag_name}': {e}",
                    file=sys.stderr,
                )

        result[tag_name] = tag_data
    return result


def convert_tasks_to_markdown(
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Converts tasks.json to per-tag markdown files.

    For each tag discovered in tasks.json a separate ``tasks-{tag}.md`` and
    ``meta-{tag}.json`` are written to TASKS_DIR.  An optional *tags* filter
    restricts processing to a specific subset of tags.

    Args:
        tags: Optional list of tag names to process.  When *None* (default)
              all tags present in tasks.json are processed.

    Returns:
        dict: Success message listing generated files, or error details.
    """
    try:
        tasks_file_path = os.path.join(TASKS_DIR, TASKS_JSON)
        if not os.path.isfile(tasks_file_path):
            return {"error": f"tasks.json file not found at: {tasks_file_path}"}

        with open(tasks_file_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        all_tags = _get_tags_from_json(tasks_data)
        tags_to_process = [t for t in all_tags if t in tags] if tags else all_tags

        if not os.path.exists(TASKS_DIR):
            os.makedirs(TASKS_DIR)

        generated_files: List[str] = []
        for tag_name in tags_to_process:
            tag_data = tasks_data[tag_name]

            # Generate per-tag markdown
            markdown_content = _generate_markdown_for_tag(tag_name, tag_data)
            md_filename = _generate_tag_filename(tag_name, "md")
            md_path = os.path.join(TASKS_DIR, md_filename)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            generated_files.append(md_filename)

            # Generate per-tag meta JSON
            meta = _extract_meta_from_tag_data(tag_data)
            meta_filename = _generate_tag_filename(tag_name, "json")
            meta_path = os.path.join(TASKS_DIR, meta_filename)
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
            generated_files.append(meta_filename)

        tag_count = len(tags_to_process)
        return {
            "content": (
                f"Generated {', '.join(generated_files)} ({tag_count} tag(s) processed)"
            )
        }
    except json.JSONDecodeError as e:
        return _format_error("Error decoding JSON", e)
    except OSError as e:
        return _format_error("System error when opening file", e)
    except Exception as e:
        return _format_error("Unexpected error processing tasks", e)


def convert_markdown_to_tasks() -> Dict[str, Any]:
    """
    Converts per-tag markdown files back to a consolidated tasks.json.

    Discovers all ``tasks-*.md`` files in TASKS_DIR and merges them into a
    single ``tasks.json``.  Falls back to the legacy ``tasks.md`` if no
    per-tag files are found (backward compatibility).

    Returns:
        dict: Success or error message.
    """
    try:
        tags, _ = _discover_tag_files(TASKS_DIR)

        if tags:
            # Multi-tag flow: parse all discovered tag files
            tasks_json = _parse_all_tag_files(TASKS_DIR)
            if not tasks_json:
                return {"error": "No tasks could be parsed from the discovered markdown files"}
        else:
            # Backward-compatibility: fall back to legacy tasks.md
            markdown_file_path = os.path.join(TASKS_DIR, TASKS_MD)
            meta_file_path = os.path.join(TASKS_DIR, META_JSON)
            if not os.path.isfile(markdown_file_path):
                return {
                    "error": (
                        f"No per-tag markdown files found and legacy "
                        f"{markdown_file_path} does not exist"
                    )
                }
            with open(markdown_file_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()
            tasks_json = _parse_markdown_to_tasks(markdown_content)
            if os.path.isfile(meta_file_path):
                with open(meta_file_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                tasks_json = _merge_tasks_with_meta(tasks_json, meta)

        tasks_json_str = json.dumps(tasks_json, ensure_ascii=False, indent=2)
        output_path = os.path.join(TASKS_DIR, TASKS_JSON)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(tasks_json_str)
        return {"content": f"{output_path} created successfully."}
    except OSError as e:
        return _format_error("System error when opening markdown file", e)
    except Exception as e:
        return _format_error("Unexpected error processing markdown", e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python convert_tasks.py [--to_markdown|--to_tasks] "
            "[--tags=tag1,tag2|all]"
        )
        sys.exit(1)

    # Parse optional --tags flag (only relevant for --to_markdown)
    tags_filter: Optional[List[str]] = None
    for arg in sys.argv[2:]:
        if arg.startswith("--tags="):
            tags_value = arg.split("=", 1)[1]
            if tags_value.lower() != "all":
                tags_filter = [t.strip() for t in tags_value.split(",") if t.strip()]

    if sys.argv[1] == "--to_markdown":
        print(convert_tasks_to_markdown(tags=tags_filter))
    elif sys.argv[1] == "--to_tasks":
        print(convert_markdown_to_tasks())
    else:
        print("Invalid option. Use '--to_markdown' or '--to_tasks'.")
        sys.exit(1)

