#!/usr/bin/python3
"""
Context-Refs Hook

PreToolUse hook for Edit|Write. Auto-injects reference file contents into Claude
context when a matched file is about to be edited.
"""

import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger, get_session_id_short  # noqa: E402

logger = get_hooks_logger("ContextRefs")

MAX_STDIN = 1024 * 1024
CONFIG_FILE = ".claude/context-refs.json"
DEFAULT_REFRESH_AFTER = 3
GIT_CACHE_ROOT = Path("/tmp/context_refs_git_cache")


def _cache_path(session_id: str) -> Path:
    return Path(f"/tmp/context_refs_{session_id}.json")


def _load_cache(cache_path: Path) -> dict:
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache_path: Path, cache: dict) -> None:
    try:
        cache_path.write_text(json.dumps(cache))
    except OSError:
        pass


def _glob_match(file_path: str, glob: str) -> bool:
    """Match file_path against glob pattern using fnmatch."""
    import fnmatch

    p = PurePosixPath(file_path.replace("\\", "/"))
    for g in glob.split(","):
        g = g.strip().replace("\\", "/")
        if fnmatch.fnmatch(str(p), g):
            return True
    return False


def _git_cache_dir(repo_url: str) -> Path:
    name = PurePosixPath(repo_url.rstrip("/")).name or "repo"
    return GIT_CACHE_ROOT / name


def _ensure_git_cache(repo_url: str) -> Path | None:
    """Clone or update the cached bare mirror of the repo. Returns the cache dir on success."""
    cache_dir = _git_cache_dir(repo_url)
    try:
        if cache_dir.exists():
            result = subprocess.run(
                ["git", "--git-dir", str(cache_dir), "fetch", "--quiet", "origin"],
                capture_output=True,
                timeout=30,
            )
            return cache_dir if result.returncode == 0 else None
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "clone", "--quiet", "--bare", repo_url, str(cache_dir)],
            capture_output=True,
            timeout=60,
        )
        return cache_dir if result.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _read_ref_from_git(ref: str, repo_url: str) -> str | None:
    """Fetch a ref's content from the cached repo clone when the local file is missing."""
    if not repo_url:
        return None
    rel_path = ref.replace("\\", "/")
    cache_dir = _ensure_git_cache(repo_url)
    if cache_dir is None:
        return None
    try:
        result = subprocess.run(
            ["git", "--git-dir", str(cache_dir), "show", f"HEAD:{rel_path}"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except (OSError, subprocess.SubprocessError):
        return None


def _normalize_path(path: str) -> str:
    """Make path relative to cwd for consistent cache keys."""
    try:
        return str(Path(path).resolve().relative_to(Path.cwd()))
    except ValueError:
        return path


def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        pass

    data: dict = {}
    try:
        data = json.loads(stdin_data)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
    except (json.JSONDecodeError, AttributeError):
        logger.debug("Failed to parse stdin JSON, exiting.")
        sys.exit(0)

    logger.debug("tool_name=%s", tool_name)

    if tool_name not in ("Edit", "Write"):
        logger.debug("Tool %s not in scope, skipping.", tool_name)
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        logger.debug("No file_path in tool_input, skipping.")
        sys.exit(0)

    logger.debug("file_path=%s", file_path)

    # Normalize to relative path for glob matching
    try:
        rel_path = str(Path(file_path).resolve().relative_to(Path.cwd()))
    except ValueError:
        rel_path = file_path
    rel_path = rel_path.replace("\\", "/")
    logger.debug("rel_path=%s", rel_path)

    config_path = Path(CONFIG_FILE)
    if not config_path.exists():
        logger.debug("Config %s not found, exiting silently.", CONFIG_FILE)
        sys.exit(0)

    try:
        config = json.loads(config_path.read_text())
    except (json.JSONDecodeError, OSError):
        logger.debug("Failed to parse config %s, exiting.", CONFIG_FILE)
        sys.exit(0)

    refresh_after = config.get("refresh_after", DEFAULT_REFRESH_AFTER)
    git_repo_url = config.get("git_repo_url", "")
    rules = config.get("rules", [])
    logger.debug("refresh_after=%d, rules_count=%d", refresh_after, len(rules))

    # Build ordered deduplicated union of matching refs
    seen: set[str] = set()
    matched_refs: list[str] = []
    for rule in rules:
        glob = rule.get("glob", "")
        if not glob:
            continue
        matched = _glob_match(rel_path, glob)
        logger.debug("glob=%s matched=%s", glob, matched)
        if not matched:
            continue
        for ref in rule.get("refs", []):
            if ref not in seen:
                seen.add(ref)
                matched_refs.append(ref)

    logger.debug("matched_refs=%s", matched_refs)

    if not matched_refs:
        logger.debug("No refs matched for %s, exiting.", rel_path)
        sys.exit(0)

    session_id = get_session_id_short(get_by_key(data, "session_id") or "")
    cache_path = _cache_path(session_id)
    logger.debug("session_id=%s cache_path=%s", session_id, cache_path)
    cache = _load_cache(cache_path)

    output_lines: list[str] = []
    for ref in matched_refs:
        ref_key = _normalize_path(ref)
        skip_count = cache.get(ref_key)
        logger.debug(
            "ref=%s skip_count=%s refresh_after=%d",
            ref,
            skip_count,
            refresh_after,
        )

        if skip_count is None:
            inject = True
            cache[ref_key] = 0
        elif skip_count < refresh_after:
            inject = False
            cache[ref_key] = skip_count + 1
        else:
            inject = True
            cache[ref_key] = 0

        logger.debug(
            "ref=%s inject=%s new_skip_count=%s",
            ref,
            inject,
            cache[ref_key],
        )

        if not inject:
            continue

        ref_path = Path(ref)
        if not ref_path.is_absolute():
            ref_path = Path.cwd() / ref_path
        contents: str | None = None
        if ref_path.exists():
            try:
                contents = ref_path.read_text()
            except OSError:
                logger.debug("Could not read ref: %s", ref)
        else:
            logger.debug("ref not found locally, trying git cache: %s", ref)
            contents = _read_ref_from_git(ref, git_repo_url)

        if contents is None:
            logger.debug("ref not found: %s", ref)
            output_lines.append(f"# WARNING: ref not found: {ref}")
            continue

        logger.debug("Injecting ref=%s (%d chars)", ref, len(contents))
        output_lines.append(f"=== {ref} ===")
        output_lines.append(contents)
        output_lines.append("")

    _save_cache(cache_path, cache)
    logger.debug("Cache saved. injected=%d lines.", len(output_lines))

    if output_lines:
        result = "\n".join(output_lines)
        output = json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": result,
                }
            }
        )
        logger.debug("Output: %s", output)
        sys.stdout.write(output)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
