#!/usr/bin/python3
"""
Markdown/JSON Lint Hook

Runs Biome or Prettier in check-only mode on .json/.md files after edit.
Never writes to disk — only reports formatting issues.
Falls back to no-op when no formatter is configured or binary is missing.

Cross-platform (Windows, macOS, Linux)
"""

import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    detect_formatter,
    find_project_root,
    get_hooks_logger,
    resolve_formatter_bin,
    run_command_cwd,
    run_lint_hook_main,
)

logger = get_hooks_logger("MdJsonLint")

_MD_JSON_EXTS = {".json", ".md"}


def _exec(bin_: str, args: list[str], cwd: str | None = None) -> dict:
    cmd = " ".join([bin_, *args])
    return run_command_cwd(cmd, cwd=cwd)


def _run_biome_check(resolved: Path, project_root: str) -> dict:
    fmt_bin = resolve_formatter_bin(project_root, "biome", logger)
    if not fmt_bin:
        logger.debug("Biome configured but binary not found, skipping %s", resolved)
        return {"success": True, "output": "", "error": "", "installed": False}

    args = [*fmt_bin["prefix"], "check", str(resolved)]
    result = _exec(fmt_bin["bin"], args, cwd=project_root)
    logger.debug("Biome check result for %s: success=%s", resolved, result["success"])
    if not result["success"]:
        logger.warning(
            "Biome found issues in %s:\n%s", resolved, result.get("output", "")
        )
    return {
        "success": result["success"],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def _run_prettier_check(resolved: Path, project_root: str) -> dict:
    fmt_bin = resolve_formatter_bin(project_root, "prettier", logger)
    if not fmt_bin:
        logger.debug(
            "Prettier configured but binary not found, skipping %s", resolved
        )
        return {"success": True, "output": "", "error": "", "installed": False}

    args = [*fmt_bin["prefix"], "--check", str(resolved)]
    result = _exec(fmt_bin["bin"], args, cwd=project_root)
    logger.debug(
        "Prettier check result for %s: success=%s", resolved, result["success"]
    )
    if not result["success"]:
        logger.warning(
            "Prettier found issues in %s:\n%s", resolved, result.get("output", "")
        )
    return {
        "success": result["success"],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def maybe_run_md_json_lint(file_path: str | None) -> dict:
    result: dict = {"biome": None, "prettier": None}

    if not file_path:
        logger.debug("No file_path provided, skipping.")
        return result

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        logger.debug("File %s does not exist, skipping.", resolved)
        return result

    ext = resolved.suffix.lower()
    if ext not in _MD_JSON_EXTS:
        logger.debug("File %s not .json/.md, skipping (%s).", resolved, ext)
        return result

    project_root = find_project_root(str(resolved.parent))
    formatter = detect_formatter(project_root, logger)
    logger.debug("Detected formatter for %s: %s", resolved, formatter)

    if formatter == "biome":
        result["biome"] = _run_biome_check(resolved, project_root)
    elif formatter == "prettier":
        result["prettier"] = _run_prettier_check(resolved, project_root)
    else:
        logger.debug("No formatter configured for %s, skipping.", resolved)

    return result


def main() -> None:
    run_lint_hook_main("MdJsonLint", logger, maybe_run_md_json_lint)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("Error: %s", exc)
        sys.exit(0)
