"""
my_mcp_server.py

Implements a FastMCP server with tools for code review, context generation,
markdown/JSON conversion, and shell command execution. This module is designed
for extensibility and integration with AI-powered workflows.
"""


import json
import os
import re
import subprocess
from datetime import datetime
from glob import glob
from typing import Any, Dict, List, Optional

import aiohttp
import requests
from markdownify import markdownify as md
from mcp.server.fastmcp import FastMCP

from search_engine import search_codebase

# Properly initializes the MCP server
mcp = FastMCP(name="my-mcp")


def load_instructions(instructions_ref="") -> str:
    with open(
        os.path.join(INSTRUCTIONS_DIR, instructions_ref),
        "r",
        encoding="utf-8",
    ) as f:
        instructions = f.read()
    return instructions


def load_template(template_ref="") -> str:
    with open(
        os.path.join(TEMPLATES_DIR, template_ref),
        "r",
        encoding="utf-8",
    ) as f:
        template = f.read()
    return template

def _format_error(message: str, exc: Exception) -> Dict[str, str]:
    """Helper to format error responses consistently."""
    return {"error": f"{message}: {str(exc)}"}


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



# Constantes para caminhos de arquivos e diretórios
INSTRUCTIONS_DIR = "/home/ronnas/develop/personal/AI-pair-programming/instructions"
TEMPLATES_DIR = "/home/ronnas/develop/personal/AI-pair-programming/templates"
TASKS_DIR = ".taskmaster/tasks"
TASKS_JSON = "tasks.json"
TASKS_MD = "tasks.md"
META_JSON = "meta.json"
REVIEW_INSTRUCTIONS = "review-refactor-specialist.instructions.md"
DEVELOPER_WORKFLOW_INSTRUCTIONS = "developer.instructions.md"
DOCUMENTATION_WORKFLOW_INSTRUCTIONS = "generate-documentation.instructions.md"
GENERATE_PRD_INSTRUCTIONS = "product-owner.instructions.md"
ASK_GUIDELINES_INSTRUCTIONS = "ask-guidelines.instructions.md"
TASK_REVIEWER_INSTRUCTIONS = "task-reviewer.instructions.md"
PRD_TEMPLATE = "PRD-template.json"
VENV_DIRS = ("venv", "env")
BIN_DIR = "bin"
ACTIVATE_SCRIPT = "activate"


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


@mcp.tool()
async def my_mcp_load_page_as_doc(url: str) -> Dict[str, Any]:
    """
    Downloads a web page and returns clean text for documentation purposes.

    Args:
        url (str): The URL to fetch.

    Returns:
        dict: Markdown content or error message.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                html = await resp.text()

        md_html = md(html, heading_style="ATX")
        if not md_html:
            return {"error": "Failed to convert HTML to Markdown."}
        return {"content": md_html}
    except aiohttp.ClientError as e:
        return _format_error("HTTP connection error when loading page", e)


@mcp.tool()
def my_mcp_get_context(
    exclude: str,
    exclude_content: str,
    workers: str,
    llist: bool,
    tree: bool,
    include: str,
    text: str,
    text_full: bool,
    paths: List[str],
) -> Dict[str, Any]:
    """
    Returns context based on the provided parameters.

    Args:
        exclude (str): Patterns to exclude from context generation.
        exclude_content (str): Patterns to exclude from file content.
        workers (str): Number of worker threads for parallel processing (optional).
        llist (bool): If True, lists files instead of generating context.
        tree (bool): If True, outputs directory tree structure.
        include (str): Patterns to include in context generation.
        text (str): Additional text to include in context.
        text_full (bool): If True, includes full text content.
        paths (List[str]): List of file or directory paths to process.

    Returns:
        dict: Context content or error message.
    """
    try:
        command = "python3 /home/ronnas/develop/personal/AI-pair-programming/src/generate-context-ia.py"
        if exclude:
            command += f" --exclude '{exclude}'"
        if exclude_content:
            command += f" --exclude-content '{exclude_content}'"
        if workers:
            command += f" --workers {workers}"
        if llist:
            command += " --list"
        if tree:
            command += " --tree"
        if include:
            command += f" --include '{include}'"
        if text:
            command += f" --text '{text}'"
        if text_full:
            command += " --text-full"
        for path in paths:
            command += f" '{path}'"
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True,  # permite string única como comando
            executable="/bin/zsh",  # garante compatibilidade com zsh
            check=False,
        )
        if result.returncode != 0:
            return {"error": "Failed to execute command"}
        return {"content": result.stdout}
    except FileNotFoundError as e:
        return _format_error("File not found when running command.", e)
    except subprocess.SubprocessError as e:
        return _format_error("Subprocess error when running command", e)


@mcp.tool()
def my_mcp_run_command(command: str, rootProject: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes a shell command in the specified directory (or current directory if not provided).
    If there is a virtual environment (venv/.venv) in the directory, it is automatically activated before the command.

    Args:
        command (str): The shell command to execute.
        rootProject (Optional[str]): Directory to execute the command in.

    Returns:
        dict: stdout, stderr, or error message.
    """
    try:
        workdir = rootProject or os.getcwd()
        result = subprocess.run(
            command,
            cwd=workdir,
            capture_output=True,
            text=True,
            shell=True,  # permite string única como comando
            executable="/bin/zsh",  # garante compatibilidade com zsh
            check=False,
        )
        if result.returncode == 0:
            return {"stdout": result.stdout.strip()}
        else:
            return {
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
            }
    except FileNotFoundError as e:
        return _format_error(
            "File or directory not found when running command.", e
        )
    except subprocess.SubprocessError as e:
        return _format_error("Subprocess error when running command", e)


@mcp.tool()
def my_mcp_run_prompt(name: str) -> Dict[str, Any]:
    """
    Executes a predefined prompt by loading its instruction file.

    Args:
        name (str): Name pattern for the instruction file.

    Returns:
        dict: File content or error message.
    """
    try:
        filepath = glob(f"{INSTRUCTIONS_DIR}/*{name}*.instructions.md")[0]
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except IndexError as e:
        return _format_error("Instruction file not found.", e)
    except OSError as e:
        return _format_error("System error when opening instruction file", e)


@mcp.tool()
def my_mcp_code_review(
    rootProject: Optional[str] = None, command="git diff"
) -> Dict[str, Any]:
    """
    Gets the git diff in the specified directory (or current directory if not provided) and combines it with the review template for prompt execution.

    Args:
        rootProject (Optional[str]): Directory to run git diff in.
        command (str): Command to execute (default=git diff).

    Returns:
        dict: Combined instructions and git diff, or error message.
    """
    try:
        result = subprocess.run(
            command.split(" "),
            cwd=rootProject or os.getcwd(),
            capture_output=True,
            text=True,
            check=False,
        )
        git_diff = result.stdout

        instructions = load_instructions(REVIEW_INSTRUCTIONS)

        combined_content = f"""
        <system_instructions>{instructions}</system_instructions>
        <diff_in_files>{git_diff}</diff_in_files>
        Based on the modifications made, check if there are any code adjustments or improvements to be made, following the instructions provided. Carefully analyze the problem, write a description of the changes to be made, and save it as {rootProject}/.taskmaster/specs/dd-MM-YYYY-<description>.md, following strictly the format below:
        <format>
        <description>{{DESCRIPTION OF CHABGES HERE}}</description>
        
        <!--- THE FOLLOWING TEXT IS UNCHANGEABLE. --->
        <!--- DO NOT REWRITE, DO NOT CORRECT, DO NOT ADAPT. --->
        <!--- USE IT EXACTLY AS IT IS, CHARACTER BY CHARACTER. --->
        <!--- UNCHANGING_TEXT_START --->
        <workflow>
        - If documentation files or any other type of file are provided, extract relevant links and related files that may assist in implementing the task.
        - When creating a task or subtask, add references to relevant files or links that may assist in implementing the task.
        - Before each implementation step (tasks or subtasks), check relevant references and links. Perform a thorough review of relevant files and documents until you have a complete understanding of what needs to be done.
        - Add relevant code snippets that may assist in implementing the task in markdown format.
        - Check all *.md files starting from SUMMARY.md and docs/ to find relevant documentation.
        - Create and present a detailed action plan for executing the task implementation.
        - Ensure that changes are fully backward compatible and do not affect other system flows.
        - At the end of the implementation, show a summary of what was done and save it as a .md file in docs/features/dd-mm-yyyy-<description>/README.md
        </workflow>
        <!--- UNCHANGING_TEXT_END --->
        </format>
        
        Next, ask the user to review the created document; if they suggest any modifications or extensions, make them. When they say you can proceed, execute these commands sequentially in the terminal:
        task-master add-task --research --prompt="$(cat {rootProject}/.taskmaster/specs/dd-MM-YYYY-<description>.md)" 
        task-master analyze-complexity 
        task-master expand --all  --research  --prompt="$(cat {rootProject}/.taskmaster/specs/dd-MM-YYYY-<description>.md))"
        """
        return {"content": combined_content}

    except FileNotFoundError as e:
        return _format_error("Instruction file not found", e)
    except subprocess.SubprocessError as e:
        return _format_error("Subprocess error when executing git diff", e)




@mcp.tool()
def my_mcp_generate_docs_update(
    rootProject: Optional[str] = None, command="git diff"
) -> Dict[str, Any]:
    """
    Gets the git diff or similar command in the specified directory (or current directory if not provided) and combines it with the documentation template for prompt execution.

    Args:
        rootProject (Optional[str]): Directory to run git diff in.
        command (str): Command to execute (default=git diff).

    Returns:
        dict: Combined instructions and git diff, or error message.
    """
    try:
        result = subprocess.run(
            command.split(" "),
            cwd=rootProject or os.getcwd(),
            capture_output=True,
            text=True,
            check=False,
        )
        git_diff = result.stdout
        instructions = load_instructions(DOCUMENTATION_WORKFLOW_INSTRUCTIONS)
        combined_content = f"<system_instructions>\n{instructions}\n</system_instructions>\n<diff_in_files>\n{git_diff}\n</diff_in_files>\n<task>\nBased on the modifications and instructions provided, adjust the documentation accordingly. Review existing documentation files (check the docs/ folder and SUMMARY.md if they exist) and see which ones need updating based on the changes made. Preferably update existing files, but create new ones if necessary. Only update files if the changes are relevant to the file's content type. Don't add text just for the sake of adding it. Before any modification, show what will be added and ask if you should proceed.\n</task>\n"
        return {"content": combined_content}

    except FileNotFoundError as e:
        return _format_error("Instruction file not found", e)
    except subprocess.SubprocessError as e:
        return _format_error("Subprocess error when executing git diff", e)


@mcp.tool()
def my_mcp_developer_instructions() -> Dict[str, Any]:
    """
    Loads and returns the developer instructions that must be followed by the agent.

    Returns:
        dict: The content of the instructions or an error message.
    """
    try:
        instructions = load_instructions(DEVELOPER_WORKFLOW_INSTRUCTIONS)
        combined_content = f"""
        <system_instructions>{instructions}</system_instructions>
        <task>Follow the instructions provided for code development in any implementation or adjustment requested.</task>"""
        return {"content": combined_content}

    except FileNotFoundError as e:
        return _format_error("Instruction file not found", e)
    except subprocess.SubprocessError as e:
        return _format_error("Subprocess error when executing git diff", e)


@mcp.tool()
def my_mcp_generate_prd() -> Dict[str, Any]:
    """
    return instructions for generating PRD file.

    Returns:
        dict: The content of the instructions or an error message.
    """
    try:
        instructions = load_instructions(GENERATE_PRD_INSTRUCTIONS)
        template = load_template(PRD_TEMPLATE)
        combined_content = f"""
        <prd_template>{template}</prd_template>
        <system_instructions>{instructions}</system_instructions>
        <task>Follow the workflow provided in `system_instructions`. The format to be used is defined in `prd_template`. Ask the user questions that help in the elaboration of the PRD. Wait for the user's response to each question before proceeding to the next. Think deeply about the problem resolution and conduct research if necessary. At the end of the process, save the generated file in `docs/PRD.json`.</task>
        """
        return {"content": combined_content}

    except FileNotFoundError as e:
        return _format_error("Instruction file not found", e)

@mcp.tool()
def my_mcp_aks_guidelines() -> Dict[str, Any]:
    """
    return a group of guidelines for asking questions that the agent must respond to.
    Returns:
        dict: The content of the instructions or an error message.
    """
    try:
        instructions = load_instructions(ASK_GUIDELINES_INSTRUCTIONS)
        combined_content = f"""<system_instructions>{instructions}</system_instructions> answer the questions."""
        return {"content": combined_content}

    except FileNotFoundError as e:
        return _format_error("Instruction file not found", e)

@mcp.tool()
def my_mcp_generate_docs_init() -> Dict[str, Any]:
    """
    return instructions for generating initial project documentation from a predefined instructions file.

    Returns:
        dict: The content of the instructions or an error message.
    """
    try:
        instructions = load_instructions(DOCUMENTATION_WORKFLOW_INSTRUCTIONS)
        combined_content = f"""
        <system_instructions>{instructions}</system_instructions>
        <task>
        Follow the instructions provided to generate the workspace documentation in the described format. Perform the generation of this documentation incrementally. Analyze the tree structure of the workspace and break it down into smaller parts (modules, folders, files). As you iterate over each part, show which file, module, or folder of the workspace will be analyzed next and after analysis, perform the generation of the documentation incrementally as described in the instructions.
        </task>
        """
        return {"content": combined_content}

    except FileNotFoundError as e:
        return _format_error("Instruction file not found", e)

@mcp.tool()
def my_mcp_convert_tasks_to_markdown(
    rootProject: Optional[str] = None,
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
        if not rootProject:
            rootProject = os.getcwd()
        tasks_file_path = os.path.join(rootProject, TASKS_DIR, TASKS_JSON)
        if not os.path.isfile(tasks_file_path):
            return {"error": f"tasks.json file not found at: {tasks_file_path}"}
        with open(tasks_file_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)
        markdown_content = _generate_markdown_from_tasks(tasks_data)
        tasks_dir_path = os.path.join(rootProject, TASKS_DIR)
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


@mcp.tool()
def my_mcp_convert_markdown_to_tasks(rootProject: Optional[str] = None) -> Dict[str, Any]:
    """
    Converts a markdown file in TODO-events format to tasks.json format.
    Uses meta.json to restore extra fields, if available.

    Args:
        rootProject: Project root directory (optional).

    Returns:
        dict: Success or error message.
    """
    try:
        if not rootProject:
            rootProject = os.getcwd()
        markdown_file_path = os.path.join(rootProject, TASKS_DIR, TASKS_MD)
        meta_file_path = os.path.join(rootProject, TASKS_DIR, META_JSON)
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
            os.path.join(rootProject, TASKS_DIR, TASKS_JSON), "w", encoding="utf-8"
        ) as f:
            f.write(tasks_json_str)
        return {"content": f"{TASKS_DIR}/{TASKS_JSON} created successfully."}
    except OSError as e:
        return _format_error("System error when opening markdown file", e)
    except Exception as e:
        return _format_error("Unexpected error processing markdown", e)

@mcp.tool()
def my_mcp_styleguide(language: str = "python") -> Dict[str, Any]:
    """
    Returns a style guide for the specified programming language.

    Args:
        language (str): Programming language (default: Python).

    Returns:
        dict: Style guide content or error message.
    """
    try:
        mapper = {
            "golang": "https://google.github.io/styleguide/go/index.html",
            "html": "https://google.github.io/styleguide/htmlcssguide.html",
            "css": "https://google.github.io/styleguide/htmlcssguide.html",
            "python": "https://google.github.io/styleguide/pyguide.html",
            "typescript": "https://google.github.io/styleguide/tsguide.html",
            "javascript": "https://google.github.io/styleguide/jsguide.html",
            "markdown": "https://google.github.io/styleguide/docguide/style.html",
        }
        response = requests.get(mapper[language], timeout=5)
        if response.status_code == 200:
            return {
                "content": f"{response.text}\n use this styleguide for code related to the {language} language"
            }
        else:
            return _format_error("Error fetching styleguide", response.status_code)
    except OSError as e:
        return _format_error("System error when opening styleguide file", e)


@mcp.tool()
def my_mcp_search_references(query: str, rootProject: Optional[str] = None,globs=["*.*"], top_n: int = 10) -> Dict[str, Any]:
    """
    Returns relevant references from the codebase based on the search query.

    Args:
        query (str): The search query.
        rootProject (str): The root project directory.
        globs (List[str]): List of glob patterns to filter files.
        top_n (int): Number of top results to return.

    Returns:
        dict: Search results.
    """
    if not rootProject:
        rootProject = os.getcwd()
    results = search_codebase(query, rootProject, globs,top_n)
    return {"query": query, "results": results}

@mcp.tool()
def my_mcp_task_create(rootProject: Optional[str] = None,task_description: str = "") -> Dict[str, Any]:
    """
    Generate task description to be added to taskmaster based on project analysis.

    Args:
        rootProject (str): The root project directory.
        task_description (str): Description of the task to be created.

    Returns:
        dict: The content of the instructions or an error message.
    """
    try:
        instructions = load_instructions(TASK_REVIEWER_INSTRUCTIONS)
        combined_content = f"""
        <system_instructions>{instructions}</system_instructions>
        <task_description>{task_description}</task_description>
        Search on the @workspace of {rootProject} for files relevants to the implementation of the task. Search on the web if necessary for any docs that helps in the implementation of the task. Deep think about the problem and generate a description of the task and save it as {rootProject}/.taskmaster/specs/dd-MM-YYYY-<description>.md, following strictly the format below:
        <format>
        <description>{{DESCRIPTION OF TASK HERE}}</description>
        
        <!--- THE FOLLOWING TEXT IS UNCHANGEABLE. --->
        <!--- DO NOT REWRITE, DO NOT CORRECT, DO NOT ADAPT. --->
        <!--- USE IT EXACTLY AS IT IS, CHARACTER BY CHARACTER. --->
        <!--- UNCHANGING_TEXT_START --->
        <workflow>
        - If documentation files or any other type of file are provided, extract relevant links and related files that may assist in implementing the task.
        - When creating a task or subtask, add references to relevant files or links that may assist in implementing the task.
        - Before each implementation step (tasks or subtasks), check relevant references and links. Perform a thorough review of relevant files and documents until you have a complete understanding of what needs to be done.
        - Add relevant code snippets that may assist in implementing the task in markdown format.
        - Check all *.md files starting from SUMMARY.md and docs/ to find relevant documentation.
        - Create and present a detailed action plan for executing the task implementation.
        - Ensure that changes are fully backward compatible and do not affect other system flows.
        - At the end of the implementation, show a summary of what was done and save it as a .md file in docs/features/dd-mm-yyyy-<description>/README.md
        </workflow>
        <!--- UNCHANGING_TEXT_END --->
        </format>
        
        Next, ask the user to review the created document; if they suggest any modifications or extensions, make them. When they say you can proceed, execute these commands sequentially in the terminal:
        task-master add-task --research --prompt="$(cat {rootProject}/.taskmaster/specs/dd-MM-YYYY-<description>.md)" 
        task-master analyze-complexity 
        task-master expand --all  --research  --prompt="$(cat {rootProject}/.taskmaster/specs/dd-MM-YYYY-<description>.md))"
        """
        return {"content": combined_content}

    except FileNotFoundError as e:
        return _format_error("Instruction file not found", e)


if __name__ == "__main__":
    mcp.run()  # Starts the server using stdio by default
    # Example test calls (uncomment as needed):
    # import asyncio
    # print(asyncio.run(my_load_page_as_doc(
    #     "https://www.prisma.io/docs/guides/management-api-basic")))
    # print(asyncio.run(my_get_context(
    #     "--list --tree /home/ronnas/develop/personal/prompt-ia/")))
    # print(my_run_command("ls -la"))
    # print(my_code_review("/home/ronnas/develop/personal/prompt-ia/"))
