#!/usr/bin/python3
"""Python Lint Hook.

Runs mypy (type checking) and ruff (linting) on Python files after edit.
- Skips if mypy or ruff not installed locally
- Reports type errors and lint issues
- Falls back to no-op when tools unavailable

Cross-platform (Windows, macOS, Linux)
"""

import os
from pathlib import Path
import shutil
import sys
from typing import Any

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    find_project_root,
    get_hooks_logger,
    parse_json_output,
    parse_jsonlines_output,
    run_command_cwd,
    run_jscpd,
    run_lint_hook_main,
    truncate_large_output,
)

logger = get_hooks_logger("PythonLint")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_STDIN = 1024 * 1024  # 1 MB
_PY_EXTS = {".py"}


def _exec(bin_: str, args: list[str], cwd: str | None = None) -> dict:
    """Wrapper for tool invocations. Prefers the project venv's binary if present."""
    resolved_bin = _resolve_tool_bin(bin_, cwd) if cwd else bin_
    cmd = " ".join([resolved_bin, *args])
    return run_command_cwd(cmd, cwd=cwd)


_VENV_DIRS = (".venv", "venv")


def _venv_tool_bin(tool: str, project_root: str) -> Path | None:
    """Return first existing venv binary for `tool`, checking .venv then venv."""
    for venv_dir in _VENV_DIRS:
        candidate = Path(project_root) / venv_dir / "bin" / tool
        if candidate.exists():
            return candidate
    return None


def _resolve_tool_bin(tool: str, project_root: str) -> str:
    """Return project venv's binary path for `tool` if present, else `tool` bare."""
    local_bin = _venv_tool_bin(tool, project_root)
    return str(local_bin) if local_bin else tool


def _check_tool_installed(tool: str, project_root: str) -> bool:
    """Check if tool is installed locally via pip."""
    if _venv_tool_bin(tool, project_root):
        return True
    return shutil.which(tool) is not None


def _run_mypy(resolved: Path, project_root: str) -> dict:
    """Run mypy type checking. Returns {success, output, error}.

    `output` is parsed from mypy's `--output json` jsonlines format (one
    JSON object per error) since agents parse structured data far more
    reliably than mypy's default text output.
    """
    if not _check_tool_installed("mypy", project_root):
        logger.debug(
            "mypy not installed, skipping type check for %s",
            resolved,
        )
        return {"success": True, "output": "", "error": "", "installed": False}

    cmd = f"mypy --output json {resolved!s}"
    logger.debug("Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec("mypy", ["--output", "json", str(resolved)], cwd=project_root)
    logger.debug("mypy result: success=%s", result["success"])
    output = parse_jsonlines_output(
        result.get("output", ""), "PythonLint", "mypy", logger
    )
    if result["success"]:
        logger.debug("mypy passed for %s", resolved)
    else:
        logger.warning("mypy found type errors in %s:\n%s", resolved, output)
    if result.get("error"):
        logger.warning("mypy stderr: %s", result.get("error", ""))
    output = truncate_large_output(output, "mypy")
    return {
        "success": result["success"],
        "output": output,
        "error": result.get("error", ""),
        "installed": True,
    }


def _run_ruff(resolved: Path, project_root: str) -> dict:
    """Run ruff linting. Returns {success, output, error}.

    `output` is parsed from ruff's `--output-format json` (structured
    violations list) since agents parse structured data far more reliably
    than the default text output.
    """
    if not _check_tool_installed("ruff", project_root):
        logger.debug("ruff not installed, skipping lint for %s", resolved)
        return {"success": True, "output": "", "error": "", "installed": False}

    cmd = f"ruff check --output-format json {resolved!s}"
    logger.debug("Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec(
        "ruff", ["check", "--output-format", "json", str(resolved)], cwd=project_root
    )
    logger.debug("ruff result: success=%s", result["success"])
    output = parse_json_output(result.get("output", ""), "PythonLint", "ruff", logger)
    if result["success"]:
        logger.debug("ruff passed for %s", resolved)
    else:
        logger.warning("ruff found issues in %s:\n%s", resolved, output)
    if result.get("error"):
        logger.warning("ruff stderr: %s", result.get("error", ""))
    output = truncate_large_output(output, "ruff")
    return {
        "success": result["success"],
        "output": output,
        "error": result.get("error", ""),
        "installed": True,
    }


def _run_pylint(resolved: Path, project_root: str) -> dict:
    """Run pylint linting. Returns {success, output, error}.

    `output` is parsed from pylint's `--output-format=json` (structured
    violations list) since agents parse structured data far more reliably
    than the default text output.
    """
    if not _check_tool_installed("pylint", project_root):
        logger.debug("pylint not installed, skipping lint for %s", resolved)
        return {"success": True, "output": "", "error": "", "installed": False}

    cmd = f"pylint --output-format=json {resolved!s}"
    logger.debug("Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec("pylint", ["--output-format=json", str(resolved)], cwd=project_root)
    logger.debug("pylint result: success=%s", result["success"])
    output = parse_json_output(result.get("output", ""), "PythonLint", "pylint", logger)
    if result["success"]:
        logger.debug("pylint passed for %s", resolved)
    else:
        logger.warning("pylint found issues in %s:\n%s", resolved, output)
    if result.get("error"):
        logger.warning("pylint stderr: %s", result.get("error", ""))
    output = truncate_large_output(output, "pylint")
    return {
        "success": result["success"],
        "output": output,
        "error": result.get("error", ""),
        "installed": True,
    }


def maybe_run_python_lint(file_path: str | None) -> dict[str, dict[str, Any] | None]:
    """Run mypy, ruff, pylint and jscpd checks for Python files.

    Args:
        file_path: Path to the edited file.

    Returns:
        Dict with mypy, ruff, pylint and jscpd results.
    """
    result: dict[str, dict[str, Any] | None] = {
        "mypy": None,
        "ruff": None,
        "pylint": None,
        "jscpd": None,
    }

    if not file_path:
        logger.debug("No file_path provided, skipping.")
        return result

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        logger.debug("File %s does not exist, skipping.", resolved)
        return result

    ext = resolved.suffix.lower()
    if ext not in _PY_EXTS:
        logger.debug("File %s not Python, skipping (%s).", resolved, ext)
        return result

    project_root = find_project_root(str(resolved.parent))
    logger.debug("Project root for %s: %s", resolved, project_root)

    result["mypy"] = _run_mypy(resolved, project_root)
    result["ruff"] = _run_ruff(resolved, project_root)
    result["pylint"] = _run_pylint(resolved, project_root)
    result["jscpd"] = run_jscpd(resolved, project_root, logger, "PythonLint")
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: run mypy/ruff/pylint/jscpd against the changed Python file."""
    run_lint_hook_main("PythonLint", logger, maybe_run_python_lint)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("Error: %s", exc)
        sys.exit(0)
