#!/usr/bin/env python3
"""
Quality Gate Hook

Runs lightweight quality checks after file edits.
- Targets one file when file_path is provided
- Falls back to no-op when language/tooling is unavailable

For JS/TS files with Biome, this hook is skipped because
post-edit-format already runs `biome check --write`.
This hook still handles .json/.md files for Biome, and all
Prettier / Go / Python checks.

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

from utils import (
    detect_formatter,
    find_project_root,
    get_by_key,
    resolve_formatter_bin,
    get_hooks_logger,
)

logger = get_hooks_logger("QualityGate")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_STDIN = 1024 * 1024  # 1 MB

_JS_TS_EXTS = {".ts", ".tsx", ".js", ".jsx"}
_BIOME_EXTS = {".ts", ".tsx", ".js", ".jsx", ".json", ".md"}


def run_command(cmd: str, cwd: str | None = None) -> dict:
    """Run a shell command and return {success, output}."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=cwd,
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
        }
    except Exception:
        return {"success": False, "output": ""}


def _exec(bin_: str, args: list[str], cwd: str | None = None) -> dict:
    """
    Thin wrapper around run_command for formatter/linter invocations.
    Returns the run_command result dict: {"success": bool, "output": str, ...}
    """
    cmd = " ".join([bin_, *args])
    return run_command(cmd, cwd=cwd)


# ---------------------------------------------------------------------------
# Per-language helpers
# ---------------------------------------------------------------------------


def _run_biome(
    resolved: Path,
    ext: str,
    project_root: str,
    fix: bool,
    strict: bool,
) -> None:
    """Run Biome checks for .json/.md files (JS/TS handled by post-edit-format)."""
    if ext in _JS_TS_EXTS:
        logger.debug(
            "[QualityGate] Skipping Biome check for %s (handled by post-edit-format)",
            resolved,
        )
        return

    fmt_bin = resolve_formatter_bin(project_root, "biome", logger)
    if not fmt_bin:
        logger.debug(
            "[QualityGate] Biome configured but binary not found, skipping %s",
            resolved,
        )
        return

    args = [*fmt_bin["prefix"], "check", str(resolved)]
    if fix:
        args.append("--write")

    result = _exec(fmt_bin["bin"], args, cwd=project_root)
    logger.debug("[QualityGate] Biome result for %s: %s", resolved, result)
    if not result["success"] and strict:
        logger.debug("[QualityGate] Biome check failed for %s", resolved)


def _run_prettier(
    resolved: Path,
    project_root: str,
    fix: bool,
    strict: bool,
) -> None:
    """Run Prettier checks for supported file types."""
    fmt_bin = resolve_formatter_bin(project_root, "prettier", logger)
    if not fmt_bin:
        logger.debug(
            "[QualityGate] Prettier configured but binary not found, skipping %s",
            resolved,
        )
        return

    flag = "--write" if fix else "--check"
    args = [*fmt_bin["prefix"], flag, str(resolved)]
    result = _exec(fmt_bin["bin"], args, cwd=project_root)
    logger.debug("[QualityGate] Prettier result for %s: %s", resolved, result)
    if not result["success"] and strict:
        logger.debug("[QualityGate] Prettier check failed for %s", resolved)


def _run_js_ts_json_md(
    resolved: Path,
    ext: str,
    fix: bool,
    strict: bool,
) -> None:
    """Dispatch JS/TS/JSON/MD files to the configured formatter."""
    project_root = find_project_root(str(resolved.parent))
    formatter = detect_formatter(project_root, logger)
    logger.debug("[QualityGate] Detected formatter for %s: %s", resolved, formatter)
    logger.debug(
        "[QualityGate] Detected project root for %s: %s", resolved, project_root
    )

    if formatter == "biome":
        _run_biome(resolved, ext, project_root, fix, strict)
    elif formatter == "prettier":
        _run_prettier(resolved, project_root, fix, strict)
    else:
        logger.debug(
            "[QualityGate] No formatter configured for %s, skipping.", resolved
        )


def _run_go(resolved: Path, fix: bool, strict: bool) -> None:
    """Run gofmt on a Go file."""
    if fix:
        result = _exec("gofmt", ["-w", str(resolved)])
        if not result["success"] and strict:
            logger.debug("[QualityGate] gofmt failed for %s", resolved)
        return

    if strict:
        result = _exec("gofmt", ["-l", str(resolved)])
        logger.debug("[QualityGate] gofmt result for %s: %s", resolved, result)
        if not result["success"]:
            logger.debug("[QualityGate] gofmt failed for %s", resolved)
        elif result.get("output", "").strip():
            logger.debug(
                "[QualityGate] gofmt check found unformatted code in %s", resolved
            )


def _run_python(resolved: Path, fix: bool, strict: bool) -> None:
    """Run Ruff on a Python file."""
    args = ["format"]
    if not fix:
        logger.debug("[QualityGate] Running Ruff in check mode for %s", resolved)
        args.append("--check")
    args.append(str(resolved))

    result = _exec("ruff", args)
    logger.debug("[QualityGate] Ruff result for %s: %s", resolved, result)
    if not result["success"] and strict:
        logger.debug("[QualityGate] Ruff check failed for %s", resolved)


# ---------------------------------------------------------------------------
# Quality gate logic
# ---------------------------------------------------------------------------


def maybe_run_quality_gate(file_path: str) -> None:
    """
    Run quality-gate checks for a single file based on its extension.
    Skips JS/TS files when Biome is configured (handled by post-edit-format).

    Args:
        file_path: Path to the edited file.
    """
    if not file_path:
        logger.debug("[QualityGate] No file_path provided, skipping quality gate.")
        return

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        logger.debug(
            "[QualityGate] File %s does not exist, skipping quality gate.", resolved
        )
        return

    ext = resolved.suffix.lower()
    fix = True
    strict = False

    if ext in _BIOME_EXTS:
        _run_js_ts_json_md(resolved, ext, fix, strict)
    elif ext == ".go":
        _run_go(resolved, fix, strict)
    elif ext == ".py":
        _run_python(resolved, fix, strict)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        pass

    try:
        data = json.loads(stdin_data)
        file_path = get_by_key(get_by_key(data, "tool_input"), "file_path")
        logger.debug("[QualityGate] Received file_path: %s", file_path)
        maybe_run_quality_gate(file_path)
    except (json.JSONDecodeError, AttributeError):
        # Ignore parse errors — pass through silently
        pass

    # Always pass stdin through to stdout (hook convention)
    sys.stdout.write(stdin_data)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("[QualityGate] Error: %s", exc)
        sys.exit(0)
