"""
MCP Server para conversão de formatos de tarefas.

Funções implementadas:
1. my_convert_markdown_to_tasks - Converte markdown TODO-events para JSON tasks.json
2. my_convert_and_save_markdown_to_tasks - Converte e salva o resultado em arquivo
3. my_convert_tasks_to_markdown - Converte tasks.json para markdown TODO-events
4. validate_tasks_json - Valida estrutura de arquivo tasks.json

Exemplo de uso:
- my_convert_markdown_to_tasks('/path/to/TODO-events.md')
- my_convert_and_save_markdown_to_tasks('/path/to/TODO-events.md', '/path/to/output.json')
- validate_tasks_json('/path/to/tasks.json')
"""

#!/bin/env python3
import json
import os
import subprocess
from glob import glob
from typing import Any, Dict, Optional

import aiohttp
from markdownify import markdownify as md
from mcp.server.fastmcp import FastMCP

# Inicializa o servidor MCP corretamente
mcp = FastMCP(name="my-mcp")


def _format_error(message: str, exc: Exception) -> Dict[str, str]:
    """Helper to format error responses consistently."""
    return {"error": f"{message}: {str(exc)}"}


@mcp.tool()
async def load_page_as_doc(url: str) -> Dict[str, Any]:
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
            return {"error": "Não foi possível converter o HTML para Markdown."}
        return {"content": md_html}
    except aiohttp.ClientError as e:
        return _format_error("Erro de conexão HTTP ao carregar página", e)


@mcp.tool()
def my_get_context(command: str) -> Dict[str, Any]:
    """
    Returns context based on the provided command.
    Args:
        command (str): Command-line arguments for context generation script.
    Returns:
        dict: Context content or error message.
    """
    try:
        result = subprocess.run(
            [
                "python3",
                "/home/ronnas/develop/personal/AI-pair-programming/src/generate-context-ia.py",
            ]
            + command.split(" "),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return {"error": "Não foi possível executar o command"}
        return {"content": result.stdout}
    except FileNotFoundError as e:
        return _format_error("Arquivo não encontrado ao executar comando", e)
    except subprocess.SubprocessError as e:
        return _format_error("Erro de subprocesso ao executar comando", e)


@mcp.tool()
def my_run_command(command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes a shell command in the specified directory (or current directory if not provided).
    Se houver ambiente virtual (venv/.venv) no diretório, ativa automaticamente antes do comando.
    Args:
        command (str): The shell command to execute.
        cwd (Optional[str]): Directory to execute the command in.
    Returns:
        dict: stdout, stderr, or error message.
    """
    try:
        workdir = cwd or os.getcwd()
        venv_path = None
        # Detecta venv ou .venv
        for venv_candidate in ["venv", "env"]:
            candidate_path = os.path.join(workdir, venv_candidate, "bin", "activate")
            if os.path.isfile(candidate_path):
                venv_path = candidate_path
                break
        # Só prefixa se não houver ativação explícita no comando
        if venv_path and not ("activate" in command or "source" in command):
            # Usa 'source' para ativar o venv antes do comando
            command = f"source '{venv_path}' && {command}"
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
            "Arquivo ou diretório não encontrado ao executar comando", e
        )
    except subprocess.SubprocessError as e:
        return _format_error("Erro de subprocesso ao executar comando", e)


def mostrar_menu(opcoes: list[str]) -> None:
    """
    Prints a menu of options to the console.
    Args:
        opcoes (list[str]): List of option strings.
    """
    print("\nEscolha uma opção:")
    for i, opcao in enumerate(opcoes, start=1):
        print(f"{i}. {opcao}")
    print("0. Sair")


@mcp.tool()
def my_run_prompt(name: str) -> Dict[str, Any]:
    """
    Executes a predefined prompt by loading its instruction file.
    Args:
        name (str): Name pattern for the instruction file.
    Returns:
        dict: File content or error message.
    """
    try:
        filepath = glob(
            f"/home/ronnas/develop/personal/AI-pair-programming/instructions/*{name}*.instructions.md"
        )[0]
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except IndexError as e:
        return _format_error("Arquivo de instruções não encontrado", e)
    except OSError as e:
        return _format_error("Erro de sistema ao abrir arquivo de instruções", e)


@mcp.tool()
def my_code_review(cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Gets the git diff in the specified directory (or current directory if not provided) and combines it with the review template for prompt execution.
    Args:
        cwd (Optional[str]): Directory to run git diff in.
    Returns:
        dict: Combined instructions and git diff, or error message.
    """
    try:
        result = subprocess.run(
            ["git", "diff"],
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            check=False,
        )
        git_diff = result.stdout

        with open(
            "/home/ronnas/develop/personal/AI-pair-programming/instructions/review-refactor-specialist.instructions.md",
            "r",
            encoding="utf-8",
        ) as f:
            instructions = f.read()

        combined_content = f"{instructions}\n\nGit Diff:\n{git_diff}"
        return {"content": combined_content}

    except FileNotFoundError as e:
        return _format_error("Arquivo de instruções não encontrado", e)
    except subprocess.SubprocessError as e:
        return _format_error("Erro de subprocesso ao executar git diff", e)


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
    for context_name, context_data in tasks_data.items():
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
            description = task.get("description", "")

            markdown_lines.append(f"- {status_symbol} {task_id} - {title}")

            if description:
                clean_description = _clean_text(description)
                markdown_lines.append(f"  - **Description**: {clean_description}")

            # Add task details if present
            details = task.get("details", "")
            if details:
                clean_details = _clean_text(details)
                markdown_lines.append(f"  - **Details**: {clean_details}")

            # Add test strategy if present
            test_strategy = task.get("testStrategy", "")
            if test_strategy:
                clean_test_strategy = _clean_text(test_strategy)
                markdown_lines.append(f"  - **Test Strategy**: {clean_test_strategy}")

            # Add priority if present
            priority = task.get("priority", "")
            if priority:
                markdown_lines.append(f"  - **Priority**: {priority}")

            # Add dependencies if present for main tasks
            dependencies = task.get("dependencies", [])
            if dependencies:
                deps_str = ", ".join(str(dep) for dep in dependencies)
                markdown_lines.append(f"  - **Dependencies**: {deps_str}")

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
                    subtask_description = subtask.get("description", "")

                    markdown_lines.append(
                        f"  - {subtask_status_symbol} {subtask_id} - {subtask_title}"
                    )

                    if subtask_description:
                        clean_subtask_description = _clean_text(subtask_description)
                        markdown_lines.append(
                            f"    - **Description**: {clean_subtask_description}"
                        )

                    # Add subtask details if present
                    subtask_details = subtask.get("details", "")
                    if subtask_details:
                        clean_subtask_details = _clean_text(subtask_details)
                        markdown_lines.append(
                            f"    - **Details**: {clean_subtask_details}"
                        )

                    # Add dependencies if present
                    dependencies = subtask.get("dependencies", [])
                    if dependencies:
                        deps_str = ", ".join(str(dep) for dep in dependencies)
                        markdown_lines.append(f"    - **Dependencies**: {deps_str}")

                    # Add test strategy if present
                    test_strategy = subtask.get("testStrategy", "")
                    if test_strategy:
                        clean_subtask_test_strategy = _clean_text(test_strategy)
                        markdown_lines.append(
                            f"    - **Test Strategy**: {clean_subtask_test_strategy}"
                        )

                    # Add priority if present
                    priority = subtask.get("priority", "")
                    if priority:
                        markdown_lines.append(f"    - **Priority**: {priority}")

            markdown_lines.append("")
            markdown_lines.append("---")  # Separator between main tasks

    return "\n".join(markdown_lines)


def _clean_text(text: str) -> str:
    """
    Cleans text by removing XML-like tags and normalizing whitespace.

    Args:
        text: Text string to clean

    Returns:
        str: Cleaned text
    """
    import re

    if not text:
        return ""

    # Remove XML-like tags (e.g., <info added on...>...</info>)
    cleaned = re.sub(r"<[^>]+>[^<]*</[^>]+>", "", text)

    # Remove standalone XML-like tags
    cleaned = re.sub(r"<[^>]+>", "", cleaned)

    # Normalize whitespace and line breaks
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip()

    return cleaned


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


@mcp.tool()
def my_convert_tasks_to_markdown(
    tasks_file_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Converts a .taskmaster/tasks/tasks.json file to markdown format similar to TODO-events.md.

    Args:
        tasks_file_path (Optional[str]): Path to the tasks.json file. If not provided, looks for .taskmaster/tasks/tasks.json in current directory.

    Returns:
        dict: Markdown content or error message.
    """
    try:
        # Default path if not provided
        if not tasks_file_path:
            tasks_file_path = os.path.join(
                os.getcwd(), ".taskmaster", "tasks", "tasks.json"
            )

        # Check if file exists
        if not os.path.isfile(tasks_file_path):
            return {"error": f"Arquivo tasks.json não encontrado em: {tasks_file_path}"}

        # Load JSON content
        with open(tasks_file_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        # Generate markdown content
        markdown_content = _generate_markdown_from_tasks(tasks_data)

        return {"content": markdown_content}

    except json.JSONDecodeError as e:
        return _format_error("Erro ao decodificar JSON", e)
    except OSError as e:
        return _format_error("Erro de sistema ao abrir arquivo", e)
    except Exception as e:
        return _format_error("Erro inesperado ao processar tasks", e)


@mcp.tool()
def my_convert_markdown_to_tasks(markdown_file_path: str) -> Dict[str, Any]:
    """
    Converts a markdown file in TODO-events format to tasks.json format.

    Args:
        markdown_file_path (str): Path to the markdown file to convert.

    Returns:
        dict: Tasks JSON content or error message.
    """
    try:
        # Check if file exists
        if not os.path.isfile(markdown_file_path):
            return {
                "error": f"Arquivo markdown não encontrado em: {markdown_file_path}"
            }

        # Read markdown content
        with open(markdown_file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Parse markdown and convert to tasks JSON
        tasks_json = _parse_markdown_to_tasks(markdown_content)

        return {"content": tasks_json}

    except OSError as e:
        return _format_error("Erro de sistema ao abrir arquivo markdown", e)
    except Exception as e:
        return _format_error("Erro inesperado ao processar markdown", e)


def _parse_markdown_to_tasks(markdown_content: str) -> Dict[str, Any]:
    """
    Parses markdown content in TODO-events format and converts to tasks.json structure.

    Args:
        markdown_content: Markdown content string

    Returns:
        dict: Tasks JSON structure
    """
    import re
    from datetime import datetime

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
                "title": title.strip(),
                "description": "",
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
                "title": title.strip(),
                "description": "",
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

            if field_name == "Description":
                current_subtask["description"] = field_value
            elif field_name == "Details":
                current_subtask["details"] = field_value
            elif field_name == "Test Strategy":
                current_subtask["testStrategy"] = field_value
            elif field_name == "Priority":
                current_subtask["priority"] = field_value.lower()
            elif field_name == "Dependencies":
                # Parse dependencies (comma-separated)
                deps = [dep.strip() for dep in field_value.split(",") if dep.strip()]
                # Convert to integers if possible
                current_subtask["dependencies"] = [
                    int(dep) if dep.isdigit() else dep for dep in deps
                ]
            continue

        # Check for main task field
        field_match = re.match(field_pattern, line)
        if field_match and current_task:
            field_name, field_value = field_match.groups()
            field_name = field_name.strip()
            field_value = field_value.strip()

            if field_name == "Description":
                current_task["description"] = field_value
            elif field_name == "Details":
                current_task["details"] = field_value
            elif field_name == "Test Strategy":
                current_task["testStrategy"] = field_value
            elif field_name == "Priority":
                current_task["priority"] = field_value.lower()
            elif field_name == "Dependencies":
                # Parse dependencies (comma-separated)
                deps = [dep.strip() for dep in field_value.split(",") if dep.strip()]
                # Convert to integers if possible
                current_task["dependencies"] = [
                    int(dep) if dep.isdigit() else dep for dep in deps
                ]

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


@mcp.tool()
def my_convert_and_save_markdown_to_tasks(
    markdown_file_path: str, output_file_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Converts a markdown file in TODO-events format to tasks.json format and optionally saves it.

    Args:
        markdown_file_path (str): Path to the markdown file to convert.
        output_file_path (Optional[str]): Path to save the JSON file. If not provided, returns content only.

    Returns:
        dict: Success message with file path or JSON content, or error message.
    """
    try:
        # First convert the markdown
        result = my_convert_markdown_to_tasks(markdown_file_path)

        if "error" in result:
            return result

        tasks_json = result["content"]

        # If output path provided, save to file
        if output_file_path:
            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(tasks_json, f, indent=2, ensure_ascii=False)

            return {
                "success": f"Arquivo convertido e salvo em: {output_file_path}",
                "tasks_count": len(tasks_json.get("master", {}).get("tasks", [])),
                "file_path": output_file_path,
            }
        else:
            return {"content": tasks_json}

    except OSError as e:
        return _format_error("Erro de sistema ao salvar arquivo", e)
    except Exception as e:
        return _format_error("Erro inesperado ao converter e salvar", e)


def _validate_tasks_json(tasks_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates the structure of tasks.json to ensure it follows the expected format.

    Args:
        tasks_json: Dictionary containing tasks data

    Returns:
        dict: Validation result with status and details
    """
    try:
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {},
        }

        # Check if master context exists
        if "master" not in tasks_json:
            validation_result["errors"].append("Missing 'master' context")
            validation_result["valid"] = False
            return validation_result

        master_context = tasks_json["master"]

        # Check if tasks array exists
        if "tasks" not in master_context:
            validation_result["errors"].append(
                "Missing 'tasks' array in master context"
            )
            validation_result["valid"] = False
            return validation_result

        tasks = master_context["tasks"]

        if not isinstance(tasks, list):
            validation_result["errors"].append("'tasks' should be an array")
            validation_result["valid"] = False
            return validation_result

        # Validate each task
        task_ids = set()
        total_subtasks = 0
        status_counts = {"pending": 0, "in-progress": 0, "done": 0, "cancelled": 0}

        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                validation_result["errors"].append(
                    f"Task at index {i} is not an object"
                )
                continue

            # Check required fields
            required_fields = ["id", "title", "status"]
            for field in required_fields:
                if field not in task:
                    validation_result["errors"].append(
                        f"Task {i}: Missing required field '{field}'"
                    )

            # Check for duplicate IDs
            task_id = task.get("id")
            if task_id in task_ids:
                validation_result["errors"].append(f"Duplicate task ID: {task_id}")
            task_ids.add(task_id)

            # Count status
            task_status = task.get("status", "pending")
            if task_status in status_counts:
                status_counts[task_status] += 1
            else:
                validation_result["warnings"].append(
                    f"Task {task_id}: Unknown status '{task_status}'"
                )

            # Validate subtasks if present
            subtasks = task.get("subtasks", [])
            if subtasks:
                subtask_ids = set()
                for j, subtask in enumerate(subtasks):
                    total_subtasks += 1

                    if not isinstance(subtask, dict):
                        validation_result["errors"].append(
                            f"Task {task_id}: Subtask at index {j} is not an object"
                        )
                        continue

                    # Check subtask required fields
                    for field in required_fields:
                        if field not in subtask:
                            validation_result["errors"].append(
                                f"Task {task_id}: Subtask {j} missing required field '{field}'"
                            )

                    # Check for duplicate subtask IDs within task
                    subtask_id = subtask.get("id")
                    if subtask_id in subtask_ids:
                        validation_result["errors"].append(
                            f"Task {task_id}: Duplicate subtask ID: {subtask_id}"
                        )
                    subtask_ids.add(subtask_id)

        # Check metadata
        if "metadata" not in master_context:
            validation_result["warnings"].append("Missing metadata in master context")
        else:
            metadata = master_context["metadata"]
            metadata_fields = ["created", "updated", "description"]
            for field in metadata_fields:
                if field not in metadata:
                    validation_result["warnings"].append(
                        f"Missing metadata field: '{field}'"
                    )

        # Set validation status
        validation_result["valid"] = len(validation_result["errors"]) == 0

        # Statistics
        validation_result["statistics"] = {
            "total_tasks": len(tasks),
            "total_subtasks": total_subtasks,
            "status_distribution": status_counts,
            "unique_task_ids": len(task_ids),
        }

        return validation_result

    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Validation error: {str(e)}"],
            "warnings": [],
            "statistics": {},
        }


@mcp.tool()
def validate_tasks_json(tasks_file_path: str) -> Dict[str, Any]:
    """
    Validates a tasks.json file structure and content.

    Args:
        tasks_file_path (str): Path to the tasks.json file to validate.

    Returns:
        dict: Validation result with status, errors, warnings and statistics.
    """
    try:
        # Check if file exists
        if not os.path.isfile(tasks_file_path):
            return {"error": f"Arquivo tasks.json não encontrado em: {tasks_file_path}"}

        # Load JSON content
        with open(tasks_file_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        # Validate structure
        validation_result = _validate_tasks_json(tasks_data)
        validation_result["file_path"] = tasks_file_path

        return validation_result

    except json.JSONDecodeError as e:
        return _format_error("Erro ao decodificar JSON", e)
    except OSError as e:
        return _format_error("Erro de sistema ao abrir arquivo", e)
    except Exception as e:
        return _format_error("Erro inesperado ao validar tasks", e)


if __name__ == "__main__":
    mcp.run()  # Inicia o servidor usando stdio por padrão
    # Example test calls (uncomment as needed):
    # import asyncio
    # print(asyncio.run(load_page_as_doc("https://www.prisma.io/docs/guides/management-api-basic")))
    # print(asyncio.run(my_get_context("--list --tree /home/ronnas/develop/personal/prompt-ia/")))
    # print(my_run_command("ls -la"))
    # print(my_code_review("/home/ronnas/develop/personal/prompt-ia/"))