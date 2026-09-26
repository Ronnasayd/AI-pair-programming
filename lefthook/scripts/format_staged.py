#!/usr/bin/env python3
"""Format staged files (pre-commit).

Formats every file staged for commit in place, then re-stages it so the commit
is atomic and already formatted:
- .py                 -> ruff format
- .go                 -> gofmt -w
- .json/.md           -> Biome / Prettier --write
- .ts/.tsx/.js/.jsx   -> Biome / Prettier --write

Replaces the old SessionEnd formatter (format_on_session_end.py +
track_edited_files.py). Runs at git pre-commit time instead, so Claude's
in-context view of a file never goes stale mid-session.

Self-contained: no dependency on hooks/scripts/utils.py, so it works from a
bare `.git/hooks/pre-commit` symlink with a plain `python3` shebang.

ponytail: js/ts formatter detection duplicated from utils.py (~40 lines).
Upgrade path: extract a shared formatting module if a third caller appears.
"""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path
import shutil
import subprocess
import sys

_JS_TS_JSON_MD_EXTS = {".ts", ".tsx", ".js", ".jsx", ".json", ".md"}
_IGNORE_PATTERNS = (
    "node_modules",
    "dist",
    "build",
    "vendor",
    ".venv",
    "venv",
    "skills/anthropics",
    "skills/tech-leads-club",
    "skills/everything-claude-code",
    "skills/mattpocock",
    "skills/agent-toolkit",
    "commands/awesome-claude-code-toolkit",
)
_BIOME_CONFIGS = ("biome.json", "biome.jsonc")
_PRETTIER_CONFIGS = (
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
)
_PROJECT_ROOT_MARKERS = ("package.json", *_BIOME_CONFIGS, *_PRETTIER_CONFIGS)
_FORMATTER_BIN_NAME = {"biome": "biome", "prettier": "prettier"}
_FORMATTER_PKG = {"biome": "@biomejs/biome", "prettier": "prettier"}


def _resolve(binary: str) -> str:
    """Resolve `binary` to its absolute path, or return it unchanged."""
    return shutil.which(binary) or binary


def _run(cmd: list[str], cwd: str | None = None) -> bool:
    """Run cmd, return True on exit 0. Missing binary / any failure -> False."""
    resolved = [_resolve(cmd[0]), *cmd[1:]]
    try:
        proc = subprocess.run(  # noqa: S603
            resolved, cwd=cwd, capture_output=True, text=True, timeout=120, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    if proc.returncode != 0:
        sys.stderr.write(f"[format_staged] {' '.join(cmd)} failed:\n{proc.stderr}")
    return proc.returncode == 0


def _git_root() -> str:
    return subprocess.run(  # noqa: S603
        [_resolve("git"), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def is_ignored(rel_path: str) -> bool:
    """Check `rel_path` against `_IGNORE_PATTERNS` (gitignore-style globs).

    A bare name (`"node_modules"`) matches that dir at any depth, same as a
    gitignore pattern with no slash. A pattern with `/` anchors to the repo
    root, e.g. `"skills/anthropics"` or `"skills/anthropics/**"`.

    Args:
        rel_path: File path relative to the repo root, forward-slash separated.

    Returns:
        True if `rel_path` falls under any ignored pattern.
    """
    parts = rel_path.split("/")
    for raw_pattern in _IGNORE_PATTERNS:
        pattern = raw_pattern.rstrip("/")
        if "/" not in pattern:
            if any(fnmatch.fnmatch(part, pattern) for part in parts):
                return True
        elif fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(
            rel_path, f"{pattern}/**"
        ):
            return True
    return False


def staged_files(root: str) -> list[Path]:
    """List staged files, excluding paths matching `_IGNORE_PATTERNS`.

    Args:
        root: Absolute path to the git repository root.

    Returns:
        Absolute paths of staged files, skipping ignored paths.
    """
    out = subprocess.run(  # noqa: S603
        [_resolve("git"), "diff", "--cached", "--name-only", "--diff-filter=ACM", "-z"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [Path(root) / p for p in out.split("\0") if p and not is_ignored(p)]


def find_project_root(start: Path) -> Path:
    """Walk up from `start` to the nearest dir with a project root marker.

    Args:
        start: Directory to start the upward search from.

    Returns:
        The nearest ancestor directory containing a root marker, or `start`
        resolved if none is found.
    """
    directory = start.resolve()
    while True:
        if any((directory / m).exists() for m in _PROJECT_ROOT_MARKERS):
            return directory
        if directory.parent == directory:
            return start.resolve()
        directory = directory.parent


def detect_js_formatter(project_root: Path) -> str | None:
    """Biome over Prettier.

    Args:
        project_root: Directory to look for formatter config/package.json in.

    Returns:
        `"biome"`, `"prettier"`, or `None` if neither is configured.
    """
    if any((project_root / c).exists() for c in _BIOME_CONFIGS):
        return "biome"
    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        try:
            if "prettier" in json.loads(pkg_path.read_text(encoding="utf-8")):
                return "prettier"
        except (json.JSONDecodeError, OSError):
            pass
    if any((project_root / c).exists() for c in _PRETTIER_CONFIGS):
        return "prettier"
    return None


def resolve_js_bin(project_root: Path, formatter: str) -> list[str] | None:
    """Prefer node_modules/.bin, else `npx <pkg>`.

    Args:
        project_root: Directory to look for a local install in.
        formatter: Either `"biome"` or `"prettier"`.

    Returns:
        The argv prefix to invoke the formatter, or `None` if unavailable.
    """
    local = project_root / "node_modules" / ".bin" / _FORMATTER_BIN_NAME[formatter]
    if local.exists():
        return [str(local)]
    if shutil.which("npx"):
        return ["npx", _FORMATTER_PKG[formatter]]
    return None


def _format_js_ts_json_md(resolved: Path) -> None:
    project_root = find_project_root(resolved.parent)
    formatter = detect_js_formatter(project_root)
    if not formatter:
        return
    argv = resolve_js_bin(project_root, formatter)
    if not argv:
        return
    if formatter == "biome":
        _run([*argv, "check", "--write", str(resolved)], cwd=str(project_root))
    else:
        _run([*argv, "--write", str(resolved)], cwd=str(project_root))


def format_file(path: Path) -> None:
    """Format `path` in place based on its extension.

    Args:
        path: Absolute path of the staged file to format.
    """
    if not path.exists():
        return
    ext = path.suffix.lower()
    if ext in _JS_TS_JSON_MD_EXTS:
        _format_js_ts_json_md(path)
    elif ext == ".go":
        _run(["gofmt", "-w", str(path)])
    elif ext == ".py":
        _run(["ruff", "format", str(path)])


def main() -> int:
    """Format all staged files and re-stage them.

    Returns:
        Exit code, always `0` so a formatter bug never blocks a commit.
    """
    try:
        root = _git_root()
        files = staged_files(root)
    except (subprocess.CalledProcessError, OSError):
        return 0  # not a git repo / git unavailable: don't block the commit

    if not files:
        return 0

    for f in files:
        format_file(f)

    # Re-stage so the commit is atomic and already formatted.
    # ponytail: `git add -p` partial hunks get promoted to the whole file.
    rel = [str(f) for f in files if f.exists()]
    if rel:
        subprocess.run([_resolve("git"), "add", "--", *rel], cwd=root, check=False)  # noqa: S603
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    # why: never let a formatter bug block a commit
    except Exception as exc:  # pylint: disable=broad-exception-caught
        sys.stderr.write(f"[format_staged] error: {exc}\n")
        sys.exit(0)
