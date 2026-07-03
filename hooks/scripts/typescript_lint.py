#!/usr/bin/python3
"""
TypeScript/ESLint Lint Hook

Runs TypeScript and ESLint checks on JS/TS files after edit.
- Skips if typescript or eslint not installed locally
- Reports type errors and lint issues
- Falls back to no-op when tools unavailable

Cross-platform (Windows, macOS, Linux)
"""

import json
import os
import subprocess
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    find_project_root,
    get_by_key,
    get_hooks_logger,
)

logger = get_hooks_logger("TypeScriptLint")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_STDIN = 1024 * 1024  # 1 MB
_TS_JS_EXTS = {".ts", ".tsx"}


def run_command(cmd: str, cwd: str | None = None) -> dict:
    """Run a shell command and return {success, output}."""
    logger.debug("[TypeScriptLint] Executing: %s (cwd=%s)", cmd, cwd or os.getcwd())
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd,
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
        }
    except Exception as exc:
        logger.debug("[TypeScriptLint] Command failed: %s", exc)
        return {"success": False, "output": "", "error": str(exc)}


def _exec(bin_: str, args: list[str], cwd: str | None = None) -> dict:
    """Wrapper for tool invocations."""
    cmd = " ".join([bin_, *args])
    return run_command(cmd, cwd=cwd)


def _check_tool_installed(tool: str, project_root: str) -> bool:
    """Check if tool is installed locally via npm."""
    local_bin = Path(project_root) / "node_modules" / ".bin" / tool
    return local_bin.exists()


def _run_typescript(resolved: Path, project_root: str) -> dict:
    """Run TypeScript type checking. Returns {success, output, error}."""
    if not _check_tool_installed("tsc-files", project_root):
        logger.debug(
            "[TypeScriptLint] tsc-files not installed, skipping type check for %s",
            resolved,
        )
        return {"success": True, "output": "", "error": "", "installed": False}

    tsc_files_bin = Path(project_root) / "node_modules" / ".bin" / "tsc-files"
    logger.debug(
        "[TypeScriptLint] Running: %s --noEmit %s (cwd=%s)",
        tsc_files_bin,
        resolved,
        project_root,
    )
    result = _exec(str(tsc_files_bin), ["--noEmit", str(resolved)], cwd=project_root)
    logger.debug("[TypeScriptLint] tsc-files result for %s: %s", resolved, result)
    if not result["success"]:
        logger.debug(
            "[TypeScriptLint] Type errors in %s:\n%s", resolved, result.get("error", "")
        )
    return {
        "success": result["success"],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def _run_eslint(resolved: Path, project_root: str) -> dict:
    """Run ESLint checks. Returns {success, output, error}."""
    if not _check_tool_installed("eslint", project_root):
        logger.debug(
            "[TypeScriptLint] ESLint not installed, skipping lint for %s", resolved
        )
        return {"success": True, "output": "", "error": "", "installed": False}

    eslint_bin = Path(project_root) / "node_modules" / ".bin" / "eslint"
    logger.debug(
        "[TypeScriptLint] Running: %s --quiet %s (cwd=%s)",
        eslint_bin,
        resolved,
        project_root,
    )
    result = _exec(str(eslint_bin), ["--quiet", str(resolved)], cwd=project_root)
    logger.debug("[TypeScriptLint] eslint result for %s: %s", resolved, result)
    if not result["success"]:
        logger.debug(
            "[TypeScriptLint] Lint issues in %s:\n%s",
            resolved,
            result.get("output", ""),
        )
    return {
        "success": result["success"],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def _run_jscpd(resolved: Path, project_root: str) -> dict:
    """Run jscpd duplication check via npx. Returns {success, output, error}."""
    cmd = f"npx jscpd --no-tips {str(resolved)}"
    logger.info("[TypeScriptLint] Executing: %s (cwd=%s)", cmd, project_root)
    result = run_command(cmd, cwd=project_root)
    logger.debug("[TypeScriptLint] jscpd result for %s: %s", resolved, result)
    if not result["success"]:
        logger.debug(
            "[TypeScriptLint] jscpd issues in %s:\n%s",
            resolved,
            result.get("output", ""),
        )
    return {
        "success": result["success"],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def maybe_run_typescript_lint(file_path: str | None) -> dict:
    """
    Run TypeScript, ESLint and jscpd checks for JS/TS files.

    Args:
        file_path: Path to the edited file.

    Returns:
        Dict with typescript, eslint and jscpd results.
    """
    result: dict[str, dict | None] = {"typescript": None, "eslint": None, "jscpd": None}

    if not file_path:
        logger.debug("[TypeScriptLint] No file_path provided, skipping.")
        return result

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        logger.debug("[TypeScriptLint] File %s does not exist, skipping.", resolved)
        return result

    ext = resolved.suffix.lower()
    if ext not in _TS_JS_EXTS:
        logger.debug(
            "[TypeScriptLint] File %s not JS/TS, skipping (%s).", resolved, ext
        )
        return result

    project_root = find_project_root(str(resolved.parent))
    logger.debug("[TypeScriptLint] Project root for %s: %s", resolved, project_root)

    result["typescript"] = _run_typescript(resolved, project_root)
    result["eslint"] = _run_eslint(resolved, project_root)
    result["jscpd"] = _run_jscpd(resolved, project_root)
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        pass

    output_data = stdin_data
    try:
        data = json.loads(stdin_data)
        tool_input = get_by_key(data, "tool_input")
        file_path = (
            get_by_key(tool_input, "file_path") if tool_input is not None else None
        )
        logger.debug("[TypeScriptLint] Received file_path: %s", file_path)
        lint_results = maybe_run_typescript_lint(file_path)

        # Add lint results to output data if present
        if (
            lint_results.get("typescript")
            or lint_results.get("eslint")
            or lint_results.get("jscpd")
        ):
            output_data = json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": json.dumps(lint_results),
                    }
                }
            )
    except (json.JSONDecodeError, AttributeError):
        # Ignore parse errors — pass through silently
        pass

    # Always pass (possibly augmented) data through to stdout (hook convention)
    sys.stdout.write(output_data)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("[TypeScriptLint] Error: %s", exc)
        sys.exit(0)
