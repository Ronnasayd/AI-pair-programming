#!/usr/bin/python3
"""
Format on Session End Hook

Reads the list of files edited during the session (written incrementally by
track_edited_files.py) and formats each one in place:
- .py         -> ruff format
- .go         -> gofmt -w
- .json/.md   -> Biome/Prettier --write
- .ts/.tsx/.js/.jsx -> Biome/Prettier --write

Runs once at SessionEnd instead of after every single edit, so Claude's
in-context view of a file's content never goes stale mid-session.

Cross-platform (Windows, macOS, Linux)
"""

import json
import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    detect_formatter,
    find_project_root,
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
    resolve_formatter_bin,
    run_command_cwd,
)

logger = get_hooks_logger("FormatOnSessionEnd")

MAX_STDIN = 1024 * 1024  # 1 MB
_JS_TS_JSON_MD_EXTS = {".ts", ".tsx", ".js", ".jsx", ".json", ".md"}


def tracked_files_path(session_id: str) -> Path:
    return Path(f"/tmp/edited-files-{get_session_id_short(session_id)}.json")


def _exec(bin_: str, args: list[str], cwd: str | None = None) -> dict:
    cmd = " ".join([bin_, *args])
    return run_command_cwd(cmd, cwd=cwd)


def _format_js_ts_json_md(resolved: Path) -> None:
    project_root = find_project_root(str(resolved.parent))
    formatter = detect_formatter(project_root, logger)
    if not formatter:
        logger.debug("No formatter configured for %s, skipping.", resolved)
        return

    fmt_bin = resolve_formatter_bin(project_root, formatter, logger)
    if not fmt_bin:
        logger.debug("%s configured but binary not found, skipping %s", formatter, resolved)
        return

    if formatter == "biome":
        args = [*fmt_bin["prefix"], "check", "--write", str(resolved)]
    else:
        args = [*fmt_bin["prefix"], "--write", str(resolved)]

    result = _exec(fmt_bin["bin"], args, cwd=project_root)
    logger.debug("%s --write result for %s: %s", formatter, resolved, result)


def _format_go(resolved: Path) -> None:
    result = _exec("gofmt", ["-w", str(resolved)])
    logger.debug("gofmt -w result for %s: %s", resolved, result)


def _format_python(resolved: Path) -> None:
    result = _exec("ruff", ["format", str(resolved)])
    logger.debug("ruff format result for %s: %s", resolved, result)


def format_file(file_path: str) -> None:
    resolved = Path(file_path).resolve()
    if not resolved.exists():
        logger.debug("File %s no longer exists, skipping.", resolved)
        return

    ext = resolved.suffix.lower()
    if ext in _JS_TS_JSON_MD_EXTS:
        _format_js_ts_json_md(resolved)
    elif ext == ".go":
        _format_go(resolved)
    elif ext == ".py":
        _format_python(resolved)
    else:
        logger.debug("No formatter for extension %s, skipping %s.", ext, resolved)


def format_session_files(session_id: str) -> None:
    path = tracked_files_path(session_id)
    if not path.exists():
        logger.debug("No tracked files for session %s.", session_id)
        return

    try:
        files = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.debug("Could not read tracked files at %s.", path)
        files = []

    for file_path in files:
        format_file(file_path)

    try:
        path.unlink()
    except OSError:
        pass


def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        pass

    try:
        data = json.loads(stdin_data)
        session_id = get_by_key(data, "session_id") or ""
        logger.debug("SessionEnd for session_id=%s", session_id)
        format_session_files(session_id)
    except (json.JSONDecodeError, AttributeError):
        pass

    sys.stdout.write(stdin_data)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("Error: %s", exc)
        sys.exit(0)
