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

from utils import detect_formatter, find_project_root, get_by_key, resolve_formatter_bin, run_command,get_hooks_logger
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
        logger.debug(f"[QualityGate] File {resolved} does not exist, skipping quality gate.")
        return

    ext    = resolved.suffix.lower()
    fix    = os.environ.get("ECC_QUALITY_GATE_FIX", "").lower() == "true"
    strict = os.environ.get("ECC_QUALITY_GATE_STRICT", "").lower() == "true"

    # ── JS / TS / JSON / MD ──────────────────────────────────────────────────
    if ext in _BIOME_EXTS:
        project_root = find_project_root(str(resolved.parent))
        formatter    = detect_formatter(project_root,logger)
        logger.debug(f"[QualityGate] Detected formatter for {resolved}: {formatter}")
        logger.debug(f"[QualityGate] Detected project root for {resolved}: {project_root}")

        if formatter == "biome":
            # JS/TS already handled by post-edit-format via `biome check --write`
            if ext in _JS_TS_EXTS:
                logger.debug(f"[QualityGate] Skipping Biome check for {resolved} (handled by post-edit-format)")
                return

            # .json / .md — still need quality gate
            fmt_bin = resolve_formatter_bin(project_root, "biome")
            if not fmt_bin:
                logger.debug(f"[QualityGate] Biome configured but binary not found, skipping check for {resolved}")
                return

            args = [*fmt_bin["prefix"], "check", str(resolved)]
            if fix:
                args.append("--write")

            result = _exec(fmt_bin["bin"], args, cwd=project_root)
            logger.debug(f"[QualityGate] Biome result for {resolved}: {result}")
            if not result["success"] and strict:
                logger.debug(f"[QualityGate] Biome check failed for {resolved}")
            return

        if formatter == "prettier":
            fmt_bin = resolve_formatter_bin(project_root, "prettier")
            if not fmt_bin:
                logger.debug(f"[QualityGate] Prettier configured but binary not found, skipping check for {resolved}")
                return

            args = [*fmt_bin["prefix"], "--write" if fix else "--check", str(resolved)]
            result = _exec(fmt_bin["bin"], args, cwd=project_root)
            logger.debug(f"[QualityGate] Prettier result for {resolved}: {result}")
            if not result["success"] and strict:
                logger.debug(f"[QualityGate] Prettier check failed for {resolved}")
            return

        # No formatter configured — skip
        return

    # ── Go ───────────────────────────────────────────────────────────────────
    if ext == ".go":
        if fix:
            result = _exec("gofmt", ["-w", str(resolved)])
            if not result["success"] and strict:
                logger.debug(f"[QualityGate] gofmt failed for {resolved}")
        elif strict:
            result = _exec("gofmt", ["-l", str(resolved)])
            logger.debug(f"[QualityGate] gofmt result for {resolved}: {result}")
            if not result["success"]:
                logger.debug(f"[QualityGate] gofmt failed for {resolved}")
            elif result.get("output", "").strip():
                logger.debug(f"[QualityGate] gofmt check failed for {resolved}")
        return

    # ── Python ───────────────────────────────────────────────────────────────
    if ext == ".py":
        args = ["format"]
        if not fix:
            logger.debug(f"[QualityGate] Running Ruff in check mode for {resolved}")
            args.append("--check")
        args.append(str(resolved))

        result = _exec("ruff", args)
        logger.debug(f"[QualityGate] Ruff result for {resolved}: {result}")
        if not result["success"] and strict:
            logger.debug(f"[QualityGate] Ruff check failed for {resolved}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except Exception:
        pass

    try:
        data = json.loads(stdin_data)
        file_path = get_by_key(get_by_key(data,"tool_input"),"file_path")
        logger.debug(f"[QualityGate] Received file_path: {file_path}")
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
    except Exception as exc:
        logger.debug(f"[QualityGate] Error: {exc}")
        sys.exit(0)
