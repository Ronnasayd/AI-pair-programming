"""
my_mcp_server.py

Implements a FastMCP server with tools for code review, context generation,
markdown/JSON conversion, and shell command execution. This module is designed
for extensibility and integration with AI-powered workflows.
"""


import os
import subprocess
from glob import glob
from typing import Any, Dict, List, Optional

import aiohttp
import requests
from markdownify import markdownify as md
from mcp.server.fastmcp import FastMCP

from search_engine import search_codebase

# Properly initializes the MCP server
mcp = FastMCP(name="my-mcp")

def run(cmd, cwd=None):
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()

def load_instructions(instructions_ref="") -> str:
    with open(
        os.path.join(AGENTS_DIR, instructions_ref),
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




# Constantes para caminhos de arquivos e diretórios
AGENTS_DIR = "/home/ronnas/develop/personal/AI-pair-programming/agents"
TEMPLATES_DIR = "/home/ronnas/develop/personal/AI-pair-programming/templates"
TASKS_DIR = ".taskmaster/tasks"
TASKS_JSON = "tasks.json"
TASKS_MD = "tasks.md"
META_JSON = "meta.json"
REVIEW_INSTRUCTIONS = "review-refactor-specialist.agent.md"
DEVELOPER_WORKFLOW_INSTRUCTIONS = "developer-specialist.agent.md"
DOCUMENTATION_WORKFLOW_INSTRUCTIONS = "documentation-specialist.agent.md"
GENERATE_PRD_INSTRUCTIONS = "product-owner-specialist.agent.md"
ASK_GUIDELINES_INSTRUCTIONS = "ask-guidelines-specialist.agent.md"
TASK_REVIEWER_INSTRUCTIONS = "task-reviewer-specialist.agent.md"
PRD_TEMPLATE = "PRD-template.json"
VENV_DIRS = ("venv", "env")
BIN_DIR = "bin"
ACTIVATE_SCRIPT = "activate"




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
def my_mcp_run_prompt(name: str) -> Dict[str, Any]:
    """
    Executes a predefined prompt by loading its instruction file.

    Args:
        name (str): Name pattern for the instruction file.

    Returns:
        dict: File content or error message.
    """
    try:
        filepath = glob(f"{AGENTS_DIR}/*{name}*.agent.md")[0]
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except IndexError as e:
        return _format_error("Instruction file not found.", e)
    except OSError as e:
        return _format_error("System error when opening instruction file", e)


@mcp.tool()
def my_mcp_generate_docs_sync(rootProject: Optional[str] = None, filter:str="") -> Dict[str, Any]:
    """
    Generates a documentation update context by computing the git diff from the
    oldest commit that modified the `docs/` directory up to the current HEAD.

    The function:
    1. Finds the oldest git commit that changed any file inside `docs/`.
    2. Computes the diff between that commit and the current HEAD.
    3. Combines the diff with documentation workflow instructions to build a prompt
       for documentation synchronization.

    Args:
        rootProject (Optional[str]): Path to the project root directory where git commands
            will be executed. If not provided, the current working directory is used.
        filter (str): Optional filter pattern to limit the git diff to specific files or paths
            (e.g., "docs/*.md"). If not provided, the entire diff is included.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - "content": The combined instructions and git diff for documentation updates.
            - "error": An error message if the process fails.
    """
    try:
        cwd = rootProject or os.getcwd()

        # 1) Commit mais antigo que mexeu em docs/
        oldest_docs_commit = run(
            ["bash", "-c", "git log --reverse --format='%H' -- docs/ | head -n 1"],
            cwd,
        )

        if not oldest_docs_commit:
            return {"error": "No commits found in docs/"}

        # 2) Diff desde o commit mais antigo até HEAD
        if filter:
            git_diff = run(
                ["bash", "-c", f"git diff {oldest_docs_commit}..HEAD -- {filter}"],
                cwd,
            )
        else:
            git_diff = run(["git", "diff", f"{oldest_docs_commit}..HEAD"], cwd)

        combined_content = f"""
        MANDATORY: Use documentations-specialist agent
        <oldest_docs_commit>{oldest_docs_commit}</oldest_docs_commit>
        <diff_in_files>
        {git_diff}
        </diff_in_files>
        <task>
        Based on the modifications and instructions provided, adjust the documentation accordingly.
        Review existing documentation files (docs/ and SUMMARY.md).
        Update only relevant files. Before any modification, show what will be added and ask if you should proceed.
        </task>
        """

        return {"content": combined_content}

    except Exception as e:
        return {"error": str(e)}


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
