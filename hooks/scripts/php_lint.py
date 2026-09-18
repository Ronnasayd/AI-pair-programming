#!/usr/bin/python3
"""Runs Laravel Pint (https://laravel.com/docs/pint) on PHP files after edit.

- Skips if pint not installed locally (vendor/bin/pint)
- Reports style violations (dry-run via --test -v)
- Falls back to no-op when tool unavailable

Cross-platform (Windows, macOS, Linux)
"""

import os
from pathlib import Path
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    find_project_root,
    get_hooks_logger,
    run_command_cwd,
    run_jscpd,
    run_lint_hook_main,
    truncate_large_output,
)

logger = get_hooks_logger("PhpLint")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PHP_EXTS = {".php"}


def _exec(bin_: str, args: list[str], cwd: str | None = None) -> dict:
    """Wrapper for tool invocations."""
    cmd = " ".join([bin_, *args])
    return run_command_cwd(cmd, cwd=cwd)


def _check_tool_installed(project_root: str) -> bool:
    """Check if pint is installed locally via composer."""
    local_bin = Path(project_root) / "vendor" / "bin" / "pint"
    return local_bin.exists()


def _run_pint(resolved: Path, project_root: str) -> dict:
    """Run Pint in dry-run mode.

    Returns {success, output, error}. Pint has no structured JSON output
    format, so `--test -v` (dry-run, verbose) text output is reported as-is;
    violations make it exit non-zero.
    """
    if not _check_tool_installed(project_root):
        logger.debug("pint not installed, skipping lint for %s", resolved)
        return {"success": True, "output": "", "error": "", "installed": False}

    pint_bin = Path(project_root) / "vendor" / "bin" / "pint"
    cmd = f"{pint_bin} --test -v {resolved!s}"
    logger.debug("Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec(str(pint_bin), ["--test", "-v", str(resolved)], cwd=project_root)
    logger.debug("pint result: success=%s", result["success"])
    output = result.get("output", "")
    if result["success"]:
        logger.debug("pint passed for %s", resolved)
    else:
        logger.warning("pint found style issues in %s:\n%s", resolved, output)
    if result.get("error"):
        logger.warning("pint stderr: %s", result.get("error", ""))
    output = truncate_large_output(output, "pint")
    return {
        "success": result["success"],
        "output": output,
        "error": result.get("error", ""),
        "installed": True,
    }


def maybe_run_php_lint(file_path: str | None) -> dict:
    """Run Pint and jscpd checks for PHP files.

    Args:
        file_path: Path to the edited file.

    Returns:
        Dict with pint and jscpd results.
    """
    result: dict[str, dict | None] = {"pint": None, "jscpd": None}

    if not file_path:
        logger.debug("No file_path provided, skipping.")
        return result

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        logger.debug("File %s does not exist, skipping.", resolved)
        return result

    ext = resolved.suffix.lower()
    if ext not in _PHP_EXTS:
        logger.debug("File %s not PHP, skipping (%s).", resolved, ext)
        return result

    project_root = find_project_root(str(resolved.parent))
    logger.debug("Project root for %s: %s", resolved, project_root)

    result["pint"] = _run_pint(resolved, project_root)
    result["jscpd"] = run_jscpd(resolved, project_root, logger, "PhpLint")
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point: run PHP lint checks via the shared PostToolUse pipeline."""
    run_lint_hook_main("PhpLint", logger, maybe_run_php_lint)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("Error: %s", exc)
        sys.exit(0)
