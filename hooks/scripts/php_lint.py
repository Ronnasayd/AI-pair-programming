#!/usr/bin/python3
"""Runs PHPStan (https://phpstan.org) on PHP files after edit.

- Skips if phpstan not installed locally (vendor/bin/phpstan)
- Reports static analysis errors (--error-format=json)
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
    parse_json_output,
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
    """Check if phpstan is installed locally via composer."""
    local_bin = Path(project_root) / "vendor" / "bin" / "phpstan"
    return local_bin.exists()


def _run_phpstan(resolved: Path, project_root: str) -> dict:
    """Run PHPStan analyse. Returns {success, output, error, installed}.

    `output` is parsed from phpstan's `--error-format=json` since agents
    parse structured data far more reliably than the default text output.
    """
    if not _check_tool_installed(project_root):
        logger.debug("phpstan not installed, skipping lint for %s", resolved)
        return {"success": True, "output": "", "error": "", "installed": False}

    phpstan_bin = Path(project_root) / "vendor" / "bin" / "phpstan"
    cmd = f"{phpstan_bin} analyse --error-format=json --no-progress {resolved!s}"
    logger.debug("Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec(
        str(phpstan_bin),
        ["analyse", "--error-format=json", "--no-progress", str(resolved)],
        cwd=project_root,
    )
    logger.debug("phpstan result: success=%s", result["success"])
    output = parse_json_output(result.get("output", ""), "PhpLint", "phpstan", logger)
    if result["success"]:
        logger.debug("phpstan passed for %s", resolved)
    else:
        logger.warning("phpstan found issues in %s:\n%s", resolved, output)
    if result.get("error"):
        logger.warning("phpstan stderr: %s", result.get("error", ""))
    output = truncate_large_output(output, "phpstan")
    return {
        "success": result["success"],
        "output": output,
        "error": result.get("error", ""),
        "installed": True,
    }


def maybe_run_php_lint(file_path: str | None) -> dict:
    """Run PHPStan and jscpd checks for PHP files.

    Args:
        file_path: Path to the edited file.

    Returns:
        Dict with phpstan and jscpd results.
    """
    result: dict[str, dict | None] = {"phpstan": None, "jscpd": None}

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

    result["phpstan"] = _run_phpstan(resolved, project_root)
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
