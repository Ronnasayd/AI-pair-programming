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
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import detect_formatter, find_project_root, log, resolve_formatter_bin, run_command

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_STDIN = 1024 * 1024  # 1 MB

_JS_TS_EXTS = {".ts", ".tsx", ".js", ".jsx"}
_BIOME_EXTS = {".ts", ".tsx", ".js", ".jsx", ".json", ".md"}

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
        return

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        return

    ext    = resolved.suffix.lower()
    fix    = os.environ.get("ECC_QUALITY_GATE_FIX", "").lower() == "true"
    strict = os.environ.get("ECC_QUALITY_GATE_STRICT", "").lower() == "true"

    # ── JS / TS / JSON / MD ──────────────────────────────────────────────────
    if ext in _BIOME_EXTS:
        project_root = find_project_root(str(resolved.parent))
        formatter    = detect_formatter(project_root)

        if formatter == "biome":
            # JS/TS already handled by post-edit-format via `biome check --write`
            if ext in _JS_TS_EXTS:
                return

            # .json / .md — still need quality gate
            fmt_bin = resolve_formatter_bin(project_root, "biome")
            if not fmt_bin:
                return

            args = [*fmt_bin["prefix"], "check", str(resolved)]
            if fix:
                args.append("--write")

            result = _exec(fmt_bin["bin"], args, cwd=project_root)
            if not result["success"] and strict:
                log(f"[QualityGate] Biome check failed for {resolved}")
            return

        if formatter == "prettier":
            fmt_bin = resolve_formatter_bin(project_root, "prettier")
            if not fmt_bin:
                return

            args = [*fmt_bin["prefix"], "--write" if fix else "--check", str(resolved)]
            result = _exec(fmt_bin["bin"], args, cwd=project_root)
            if not result["success"] and strict:
                log(f"[QualityGate] Prettier check failed for {resolved}")
            return

        # No formatter configured — skip
        return

    # ── Go ───────────────────────────────────────────────────────────────────
    if ext == ".go":
        if fix:
            result = _exec("gofmt", ["-w", str(resolved)])
            if not result["success"] and strict:
                log(f"[QualityGate] gofmt failed for {resolved}")
        elif strict:
            result = _exec("gofmt", ["-l", str(resolved)])
            if not result["success"]:
                log(f"[QualityGate] gofmt failed for {resolved}")
            elif result.get("output", "").strip():
                log(f"[QualityGate] gofmt check failed for {resolved}")
        return

    # ── Python ───────────────────────────────────────────────────────────────
    if ext == ".py":
        args = ["format"]
        if not fix:
            args.append("--check")
        args.append(str(resolved))

        result = _exec("ruff", args)
        if not result["success"] and strict:
            log(f"[QualityGate] Ruff check failed for {resolved}")


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
        file_path = str((data.get("tool_input") or {}).get("file_path") or "")
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
        log(f"[QualityGate] Error: {exc}")
        sys.exit(0)
