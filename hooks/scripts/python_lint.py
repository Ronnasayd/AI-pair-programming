#!/usr/bin/python3
"""
Python Lint Hook

Runs mypy (type checking) and ruff (linting) on Python files after edit.
- Skips if mypy or ruff not installed locally
- Reports type errors and lint issues
- Falls back to no-op when tools unavailable

Cross-platform (Windows, macOS, Linux)
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    find_project_root,
    get_hooks_logger,
    run_command_cwd,
    run_jscpd,
    run_lint_hook_main,
)

logger = get_hooks_logger("PythonLint")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_STDIN = 1024 * 1024  # 1 MB
_PY_EXTS = {".py"}


def _exec(bin_: str, args: list[str], cwd: str | None = None) -> dict:
    """Wrapper for tool invocations."""
    cmd = " ".join([bin_, *args])
    return run_command_cwd(cmd, cwd=cwd)


def _check_tool_installed(tool: str, project_root: str) -> bool:
    """Check if tool is installed locally via pip."""
    local_bin = Path(project_root) / "venv" / "bin" / tool
    if local_bin.exists():
        return True
    # Also check system PATH
    result = subprocess.run(
        ["which", tool],
        capture_output=True,
        timeout=5,
    )
    return result.returncode == 0


def _run_mypy(resolved: Path, project_root: str) -> dict:
    """Run mypy type checking. Returns {success, output, error}."""
    if not _check_tool_installed("mypy", project_root):
        logger.debug(
            "[PythonLint] mypy not installed, skipping type check for %s",
            resolved,
        )
        return {"success": True, "output": "", "error": "", "installed": False}

    cmd = f"mypy {str(resolved)}"
    logger.info("[PythonLint] Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec("mypy", [str(resolved)], cwd=project_root)
    logger.debug("[PythonLint] mypy result: success=%s", result["success"])
    if result["success"]:
        logger.info("[PythonLint] mypy passed for %s", resolved)
    else:
        logger.warning(
            "[PythonLint] mypy found type errors in %s:\n%s",
            resolved,
            result.get("output", ""),
        )
    if result.get("error"):
        logger.warning("[PythonLint] mypy stderr: %s", result.get("error", ""))
    return {
        "success": result["success"],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def _run_ruff(resolved: Path, project_root: str) -> dict:
    """Run ruff linting. Returns {success, output, error}."""
    if not _check_tool_installed("ruff", project_root):
        logger.debug("[PythonLint] ruff not installed, skipping lint for %s", resolved)
        return {"success": True, "output": "", "error": "", "installed": False}

    cmd = f"ruff check {str(resolved)}"
    logger.info("[PythonLint] Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec("ruff", ["check", str(resolved)], cwd=project_root)
    logger.debug("[PythonLint] ruff result: success=%s", result["success"])
    if result["success"]:
        logger.info("[PythonLint] ruff passed for %s", resolved)
    else:
        logger.warning(
            "[PythonLint] ruff found issues in %s:\n%s",
            resolved,
            result.get("output", ""),
        )
    if result.get("error"):
        logger.warning("[PythonLint] ruff stderr: %s", result.get("error", ""))
    return {
        "success": result["success"],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def maybe_run_python_lint(file_path: str | None) -> dict[str, dict[str, Any] | None]:
    """
    Run mypy, ruff and jscpd checks for Python files.

    Args:
        file_path: Path to the edited file.

    Returns:
        Dict with mypy, ruff and jscpd results.
    """
    result: dict[str, dict[str, Any] | None] = {
        "mypy": None,
        "ruff": None,
        "jscpd": None,
    }

    if not file_path:
        logger.debug("[PythonLint] No file_path provided, skipping.")
        return result

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        logger.debug("[PythonLint] File %s does not exist, skipping.", resolved)
        return result

    ext = resolved.suffix.lower()
    if ext not in _PY_EXTS:
        logger.debug("[PythonLint] File %s not Python, skipping (%s).", resolved, ext)
        return result

    project_root = find_project_root(str(resolved.parent))
    logger.debug("[PythonLint] Project root for %s: %s", resolved, project_root)

    result["mypy"] = _run_mypy(resolved, project_root)
    result["ruff"] = _run_ruff(resolved, project_root)
    result["jscpd"] = run_jscpd(resolved, project_root, logger, "PythonLint")
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    run_lint_hook_main("PythonLint", logger, maybe_run_python_lint)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("[PythonLint] Error: %s", exc)
        sys.exit(0)
