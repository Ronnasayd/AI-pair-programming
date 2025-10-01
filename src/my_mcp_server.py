#!/bin/env python3
import json
import os
import re
import subprocess
from datetime import datetime
from glob import glob
from typing import Any, Dict, Optional

import aiohttp
import requests
from markdownify import markdownify as md
from mcp.server.fastmcp import FastMCP

# Inicializa o servidor MCP corretamente
mcp = FastMCP(name="my-mcp")


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

            markdown_lines.append(f"- {status_symbol} {task_id} - {title}")

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

                    markdown_lines.append(
                        f"  - {subtask_status_symbol} {subtask_id} - {subtask_title}"
                    )

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

            continue

        # Check for main task field
        field_match = re.match(field_pattern, line)
        if field_match and current_task:
            field_name, field_value = field_match.groups()
            field_name = field_name.strip()
            field_value = field_value.strip()

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
async def my_load_page_as_doc(url: str) -> Dict[str, Any]:
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
def my_code_review(
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


@mcp.tool()
def my_convert_tasks_to_markdown(
    rootProject: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Converts a .taskmaster/tasks/tasks.json file to markdown format similar to TODO-events.md.

    Args:
        rootProject (Optional[str]): root of the project, looks for .taskmaster/tasks/tasks.json in current directory.

    Returns:
        dict: Markdown content or error message.
    """
    try:
        # Default path if not provided
        if not rootProject:
            rootProject = os.getcwd()

        tasks_file_path = os.path.join(
            rootProject, ".taskmaster", "tasks", "tasks.json"
        )

        # Check if file exists
        if not os.path.isfile(tasks_file_path):
            return {"error": f"Arquivo tasks.json não encontrado em: {tasks_file_path}"}

        # Load JSON content
        with open(tasks_file_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        # Generate markdown content
        markdown_content = _generate_markdown_from_tasks(tasks_data)

        if not os.path.exists(os.path.join(rootProject, ".taskmaster", "tasks")):
            os.makedirs(os.path.join(rootProject, ".taskmaster", "tasks"))

        with open(
            os.path.join(rootProject, ".taskmaster", "tasks", "tasks.md"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(markdown_content)

        return {"content": "Arquivo criado com sucesso."}

    except json.JSONDecodeError as e:
        return _format_error("Erro ao decodificar JSON", e)
    except OSError as e:
        return _format_error("Erro de sistema ao abrir arquivo", e)
    except Exception as e:
        return _format_error("Erro inesperado ao processar tasks", e)


@mcp.tool()
def my_convert_markdown_to_tasks(rootProject: Optional[str] = None) -> Dict[str, Any]:
    """
    Converts a markdown file in TODO-events format to tasks.json format.

    Args:
        rootProject (Optional[str]): root of the project, looks for .taskmaster/tasks/tasks.md in current directory.

    Returns:
        dict: Tasks JSON content or error message.
    """
    try:
        if not rootProject:
            rootProject = os.getcwd()
        # Check if file exists
        markdown_file_path = os.path.join(
            rootProject, ".taskmaster", "tasks", "tasks.md"
        )

        if not os.path.isfile(markdown_file_path):
            return {
                "error": f"Arquivo markdown não encontrado em: {markdown_file_path}"
            }

        # Read markdown content
        with open(markdown_file_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Parse markdown and convert to tasks JSON
        tasks_json = _parse_markdown_to_tasks(markdown_content)
        tasks_json_str = json.dumps(tasks_json, ensure_ascii=False)

        with open(
            os.path.join(rootProject, ".taskmaster", "tasks", "tasks.json"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(tasks_json_str)

        return {"content": ".taskmaster/tasks/tasks.json criado com sucesso."}

    except OSError as e:
        return _format_error("Erro de sistema ao abrir arquivo markdown", e)
    except Exception as e:
        return _format_error("Erro inesperado ao processar markdown", e)


@mcp.tool()
def my_styleguide(language: str = "python") -> Dict[str, Any]:
    """
    Returns a style guide for the specified programming language.
    Args:
        language (str): Programming language (default: Python).
    Returns:
        dict: Style guide content or error message.
    """
    try:
        mapper = {
            "python": "https://raw.githubusercontent.com/google/styleguide/refs/heads/gh-pages/pyguide.md",
            "javascript": "https://raw.githubusercontent.com/google/styleguide/refs/heads/gh-pages/jsguide.html",
            "go": "https://raw.githubusercontent.com/google/styleguide/refs/heads/gh-pages/go/guide.md",
        }
        response = requests.get(mapper[language], timeout=5)
        if response.status_code == 200:
            return {
                "content": f"{response.text}\n utilize esse styleguide para código referente a linguagem {language}"
            }
        else:
            return _format_error("Erro ao buscar styleguide", response.status_code)
    except OSError as e:
        return _format_error("Erro de sistema ao abrir arquivo de styleguide", e)


if __name__ == "__main__":
    mcp.run()  # Inicia o servidor usando stdio por padrão
    # Example test calls (uncomment as needed):
    # import asyncio
    # print(asyncio.run(my_load_page_as_doc("https://www.prisma.io/docs/guides/management-api-basic")))
    # print(asyncio.run(my_get_context("--list --tree /home/ronnas/develop/personal/prompt-ia/")))
    # print(my_run_command("ls -la"))
    # print(my_code_review("/home/ronnas/develop/personal/prompt-ia/"))
