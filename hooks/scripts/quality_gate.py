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

from utils import log, run_command

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_STDIN = 1024 * 1024  # 1 MB

_JS_TS_EXTS = {".ts", ".tsx", ".js", ".jsx"}
_BIOME_EXTS = {".ts", ".tsx", ".js", ".jsx", ".json", ".md"}

_BIOME_CONFIGS = ["biome.json", "biome.jsonc"]

_PRETTIER_CONFIGS = [
    ".prettierrc",
    ".prettierrc.json",
    ".prettierrc.js",
    ".prettierrc.cjs",
    ".prettierrc.mjs",
    ".prettierrc.yml",
    ".prettierrc.yaml",
    ".prettierrc.toml",
    "prettier.config.js",
    "prettier.config.cjs",
    "prettier.config.mjs",
]

_PROJECT_ROOT_MARKERS = ["package.json", *_BIOME_CONFIGS, *_PRETTIER_CONFIGS]

_FORMATTER_PACKAGES = {
    "biome":    {"bin_name": "biome",    "pkg_name": "@biomejs/biome"},
    "prettier": {"bin_name": "prettier", "pkg_name": "prettier"},
}

_WIN_CMD_SHIMS = {
    "npx":  "npx.cmd",
    "pnpm": "pnpm.cmd",
    "yarn": "yarn.cmd",
    "bunx": "bunx.cmd",
}

# Module-level caches (mirrors the JS per-process Maps)
_project_root_cache: dict[str, str] = {}
_formatter_cache: dict[str, str | None] = {}
_bin_cache: dict[str, dict | None] = {}


# ---------------------------------------------------------------------------
# Inlined resolver helpers (ported from resolve_formatter.js)
# ---------------------------------------------------------------------------

def find_project_root(start_dir: str) -> str:
    """
    Walk up from start_dir until a directory containing a known project-root
    marker (package.json or formatter config) is found.
    Returns start_dir as a fallback when no marker exists above it.
    """
    if start_dir in _project_root_cache:
        return _project_root_cache[start_dir]

    directory = Path(start_dir).resolve()
    while True:
        for marker in _PROJECT_ROOT_MARKERS:
            if (directory / marker).exists():
                _project_root_cache[start_dir] = str(directory)
                return str(directory)
        parent = directory.parent
        if parent == directory:
            break
        directory = parent

    _project_root_cache[start_dir] = start_dir
    return start_dir


def detect_formatter(project_root: str) -> str | None:
    """
    Detect the formatter configured in the project.
    Biome takes priority over Prettier.
    Returns 'biome', 'prettier', or None.
    """
    if project_root in _formatter_cache:
        return _formatter_cache[project_root]

    root = Path(project_root)

    # Biome config files take top priority
    for cfg in _BIOME_CONFIGS:
        if (root / cfg).exists():
            _formatter_cache[project_root] = "biome"
            return "biome"

    # package.json "prettier" key before standalone config files
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            if "prettier" in pkg:
                _formatter_cache[project_root] = "prettier"
                return "prettier"
        except (json.JSONDecodeError, OSError):
            pass  # Malformed package.json — continue to file-based detection

    for cfg in _PRETTIER_CONFIGS:
        if (root / cfg).exists():
            _formatter_cache[project_root] = "prettier"
            return "prettier"

    _formatter_cache[project_root] = None
    return None


def _get_runner_from_package_manager(project_root: str) -> dict:
    """
    Resolve the runner binary and prefix args for the configured package
    manager. Respects the CLAUDE_PACKAGE_MANAGER env var; falls back to npx.
    """
    is_win = sys.platform == "win32"

    # Honour explicit override first, then inspect package.json packageManager
    exec_cmd = os.environ.get("CLAUDE_PACKAGE_MANAGER", "").strip()
    if not exec_cmd:
        pkg_path = Path(project_root) / "package.json"
        if pkg_path.exists():
            try:
                pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
                pm_field = pkg.get("packageManager", "")  # e.g. "pnpm@9.0.0"
                if pm_field:
                    pm_name = pm_field.split("@")[0].strip()
                    exec_cmd = {"pnpm": "pnpm dlx", "yarn": "yarn dlx", "bun": "bunx"}.get(pm_name, "npx")
            except (json.JSONDecodeError, OSError):
                pass

    if not exec_cmd:
        exec_cmd = "npx"

    parts = exec_cmd.split()
    raw_bin = parts[0] if parts else "npx"
    prefix = parts[1:] if len(parts) > 1 else []

    bin_ = _WIN_CMD_SHIMS.get(raw_bin, raw_bin) if is_win else raw_bin
    return {"bin": bin_, "prefix": prefix}


def resolve_formatter_bin(project_root: str, formatter: str) -> dict | None:
    """
    Resolve the formatter binary, preferring the local node_modules/.bin
    installation over the package-manager exec command.

    Returns {"bin": str, "prefix": list[str]} or None.
    """
    cache_key = f"{project_root}:{formatter}"
    if cache_key in _bin_cache:
        return _bin_cache[cache_key]

    pkg = _FORMATTER_PACKAGES.get(formatter)
    if not pkg:
        _bin_cache[cache_key] = None
        return None

    is_win = sys.platform == "win32"
    bin_name = pkg["bin_name"] + (".cmd" if is_win else "")
    local_bin = Path(project_root) / "node_modules" / ".bin" / bin_name

    if local_bin.exists():
        result = {"bin": str(local_bin), "prefix": []}
        _bin_cache[cache_key] = result
        return result

    runner = _get_runner_from_package_manager(project_root)
    result = {"bin": runner["bin"], "prefix": [*runner["prefix"], pkg["pkg_name"]]}
    _bin_cache[cache_key] = result
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
