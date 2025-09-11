#!/bin env python3
import subprocess
import aiohttp
from mcp.server.fastmcp import FastMCP
from markdownify import markdownify as md
import os
from glob import glob
from typing import Optional, Dict, Any

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
                "/home/ronnas/develop/personal/prompt-ia/generate-context-ia.py",
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
    Args:
        command (str): The shell command to execute.
        cwd (Optional[str]): Directory to execute the command in.
    Returns:
        dict: stdout, stderr, or error message.
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            shell=True,  # permite string única como comando
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
            f"/home/ronnas/develop/personal/prompt-ia/*{name}*.instructions.md"
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
            "/home/ronnas/develop/personal/prompt-ia/review-refactor-specialist.instructions.md",
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


if __name__ == "__main__":
    mcp.run()  # Inicia o servidor usando stdio por padrão
    # Example test calls (uncomment as needed):
    # import asyncio
    # print(asyncio.run(load_page_as_doc("https://www.prisma.io/docs/guides/management-api-basic")))
    # print(asyncio.run(my_get_context("--list --tree /home/ronnas/develop/personal/prompt-ia/")))
    # print(my_run_command("ls -la"))
    # print(my_code_review("/home/ronnas/develop/personal/prompt-ia/"))
