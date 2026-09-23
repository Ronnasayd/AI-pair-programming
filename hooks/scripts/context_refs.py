#!/usr/bin/python3
"""Context-Refs Hook.

PreToolUse hook for Edit|Write. Auto-injects reference file contents into Claude
context when a matched file is about to be edited.
"""

from contextlib import suppress
import fnmatch
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    get_by_key,
    get_hooks_logger,
    get_session_id_short,
    minify_json,
)

logger = get_hooks_logger("ContextRefs")

MAX_STDIN = 1024 * 1024
CONFIG_FILE = ".claude/context-refs.json"
DEFAULT_REPEAT_EVERY = 10
GIT_CACHE_ROOT = Path("/tmp/context_refs_git_cache")  # noqa: S108
CACHE_DIR = Path("/tmp/context_refs_cache")  # noqa: S108
REFS_DIR = Path("/tmp/context_refs")  # noqa: S108


def _cache_path(session_id: str) -> Path:
    """Build the per-session seen-set cache file path.

    Args:
        session_id: Short session identifier.

    Returns:
        Path to this session's context-refs cache file.
    """
    return CACHE_DIR / f"{session_id}.json"


def _load_cache(cache_path: Path) -> dict:
    """Load the skip-count cache from disk.

    Args:
        cache_path: Cache file to read.

    Returns:
        Parsed cache dict, or {} if missing or invalid.
    """
    if cache_path.exists():
        with suppress(json.JSONDecodeError, OSError):
            return json.loads(cache_path.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache_path: Path, cache: dict) -> None:
    """Persist the skip-count cache to disk, ignoring write failures.

    Args:
        cache_path: Cache file to write.
        cache: Cache dict to serialize.
    """
    with suppress(OSError):
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache), encoding="utf-8")


def _glob_match(file_path: str, glob: str) -> bool:
    """Match file_path against a comma-separated list of glob patterns.

    Args:
        file_path: Path to test.
        glob: Comma-separated glob patterns.

    Returns:
        True if file_path matches any of the patterns.
    """
    p = PurePosixPath(file_path.replace("\\", "/"))
    for g in glob.split(","):
        g = g.strip().replace("\\", "/")
        if fnmatch.fnmatch(str(p), g):
            return True
    return False


def _git_cache_dir(repo_url: str) -> Path:
    """Build the bare-mirror cache directory path for a repo URL.

    Args:
        repo_url: Git remote URL.

    Returns:
        Path to the cached bare mirror for repo_url.
    """
    name = PurePosixPath(repo_url.rstrip("/")).name or "repo"
    return GIT_CACHE_ROOT / name


def _ensure_git_cache(repo_url: str) -> Path | None:
    """Clone or fetch-update the cached bare mirror of a repo.

    Args:
        repo_url: Git remote URL to mirror.

    Returns:
        Path to the cache directory on success, None on failure.
    """
    cache_dir = _git_cache_dir(repo_url)
    try:
        if cache_dir.exists():
            result = subprocess.run(  # noqa: S603
                ["git", "--git-dir", str(cache_dir), "fetch", "--quiet", "origin"],  # noqa: S607
                capture_output=True,
                timeout=30,
                check=False,
            )
            return cache_dir if result.returncode == 0 else None
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(  # noqa: S603
            ["git", "clone", "--quiet", "--bare", repo_url, str(cache_dir)],  # noqa: S607
            capture_output=True,
            timeout=60,
            check=False,
        )
        return cache_dir if result.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _read_ref_from_git(ref: str, repo_url: str) -> str | None:
    """Fetch a ref's content from the cached repo clone.

    Used when the local file is missing on disk.

    Args:
        ref: Repo-relative path to read.
        repo_url: Git remote URL backing the cache.

    Returns:
        File contents at HEAD, or None if unavailable.
    """
    if not repo_url:
        return None
    rel_path = ref.replace("\\", "/")
    cache_dir = _ensure_git_cache(repo_url)
    if cache_dir is None:
        return None
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "--git-dir", str(cache_dir), "show", f"HEAD:{rel_path}"],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except (OSError, subprocess.SubprocessError):
        return None


def _normalize_path(path: str) -> str:
    """Make a path relative to cwd for consistent cache keys.

    Args:
        path: Path to normalize.

    Returns:
        Path relative to cwd, or path unchanged if it isn't under cwd.
    """
    try:
        return str(Path(path).resolve().relative_to(Path.cwd()))
    except ValueError:
        return path


def _extract_description(contents: str) -> str:
    """Pull the `description:` field out of a file's YAML frontmatter.

    Args:
        contents: File contents to scan.

    Returns:
        The description value, or "" if absent.
    """
    lines = contents.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped.startswith("description:"):
            value = stripped[len("description:") :].strip()
            return value.strip('"').strip("'")
    return ""


def _read_stdin_payload() -> dict | None:
    """Read and parse the hook's JSON stdin payload.

    Returns:
        Parsed payload dict, or None if unreadable/invalid.
    """
    stdin_data = ""
    with suppress(OSError):
        stdin_data = sys.stdin.read(MAX_STDIN)
    try:
        return json.loads(stdin_data)
    except (json.JSONDecodeError, AttributeError):
        logger.debug("Failed to parse stdin JSON, exiting.")
        return None


def _rel_to_cwd(file_path: str) -> str:
    """Normalize file_path to a cwd-relative, forward-slash path.

    Args:
        file_path: Path to normalize.

    Returns:
        file_path relative to cwd when possible, otherwise unchanged.
    """
    try:
        rel_path = str(Path(file_path).resolve().relative_to(Path.cwd()))
    except ValueError:
        rel_path = file_path
    return rel_path.replace("\\", "/")


def _collect_matched_refs(rel_path: str, rules: list[dict]) -> list[tuple[str, str]]:
    """Build the ordered, deduplicated list of refs matching rel_path.

    Args:
        rel_path: Candidate file path to test against each rule's glob.
        rules: Config rules, each with a `glob` and a `refs` list.

    Returns:
        (ref, glob) pairs for every matching, deduplicated ref.
    """
    seen: set[str] = set()
    matched_refs: list[tuple[str, str]] = []
    for rule in rules:
        glob = rule.get("glob", "")
        if not glob or not _glob_match(rel_path, glob):
            continue
        for ref in rule.get("refs", []):
            if ref not in seen:
                seen.add(ref)
                matched_refs.append((ref, glob))
    return matched_refs


def _next_emit_kind(cache: dict, ref_key: str, repeat_every: int) -> str | None:
    """Decide what to emit for ref_key on this call, bumping its counter.

    First call embeds full content. Every `repeat_every`th call after that
    emits just a pointer. All other calls emit nothing.

    Args:
        cache: Mutable per-ref call-count cache, updated in place.
        ref_key: Cache key for the ref being considered.
        repeat_every: How often (in calls) to re-surface the pointer.

    Returns:
        "full", "pointer", or None (skip this ref entirely).
    """
    count = cache.get(ref_key, 0) + 1
    cache[ref_key] = count
    if count == 1:
        return "full"
    if repeat_every > 0 and count % repeat_every == 0:
        return "pointer"
    return None


def _resolve_ref(ref: str, git_repo_url: str) -> tuple[str | None, Path]:
    """Resolve a ref's contents from disk, falling back to the git cache.

    Args:
        ref: Repo-relative or absolute path to resolve.
        git_repo_url: Git remote URL to fall back to when the file is missing.

    Returns:
        A (contents, ref_path) pair; contents is None if unresolvable.
    """
    ref_path = Path(ref)
    if not ref_path.is_absolute():
        ref_path = REFS_DIR / ref_path

    if ref_path.exists():
        try:
            return ref_path.read_text(encoding="utf-8"), ref_path
        except OSError:
            logger.debug("Could not read ref: %s", ref)
            return None, ref_path

    logger.debug("ref not found locally, trying git cache: %s", ref)
    contents = _read_ref_from_git(ref, git_repo_url)
    if contents is not None:
        try:
            ref_path.parent.mkdir(parents=True, exist_ok=True)
            ref_path.write_text(contents, encoding="utf-8")
            logger.debug("Saved fetched ref locally: %s", ref_path)
        except OSError:
            logger.debug("Could not save ref locally: %s", ref_path)
    return contents, ref_path


def _build_files(
    matched_refs: list[tuple[str, str]],
    cache: dict,
    git_repo_url: str,
    repeat_every: int,
) -> list[dict]:
    """Resolve each matched ref and build the additionalContext file entries.

    First time a ref is seen this session, its full content is embedded.
    Every `repeat_every`th call after that re-sends just a pointer
    (description + location). All other calls emit nothing for that ref.

    Args:
        matched_refs: (ref, glob) pairs to process.
        cache: Mutable per-ref call-count cache, updated in place.
        git_repo_url: Git remote URL to fall back to for missing refs.
        repeat_every: How often (in calls) to re-surface the pointer.

    Returns:
        File entries ready to embed in additionalContext.
    """
    files: list[dict] = []
    for ref, glob in matched_refs:
        ref_key = _normalize_path(ref)
        emit_kind = _next_emit_kind(cache, ref_key, repeat_every)
        if emit_kind is None:
            continue

        contents, ref_path = _resolve_ref(ref, git_repo_url)
        if contents is None:
            logger.debug("ref not found: %s", ref)
            files.append(
                {
                    "matcher": glob,
                    "description": f"WARNING: ref not found: {ref}",
                    "location": str(ref_path),
                }
            )
            continue

        description = _extract_description(contents) or ref
        entry = {"matcher": glob, "description": description, "location": str(ref_path)}
        if emit_kind == "full":
            entry["content"] = contents
        files.append(entry)
    return files


_INSTRUCTIONS = (
    "MANDATORY: before this edit/write proceeds, you MUST read each rule file "
    "at `location` below (matched by file type) and apply its rules to the "
    "content you are about to write."
)


def _emit_files(files: list[dict]) -> None:
    """Write the additionalContext payload for the matched files to stdout.

    Args:
        files: File entries built by _build_files.
    """
    if not files:
        return
    output = json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": minify_json(
                    {"instructions": _INSTRUCTIONS, "files": files}
                ),
            }
        }
    )
    logger.debug("[additionalContext]: %s", output)
    sys.stdout.write(output)


def main() -> None:
    """Match the edited file against configured refs and re-surface their content."""
    data = _read_stdin_payload()
    if data is None:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        logger.debug("Tool %s not in scope, skipping.", tool_name)
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    if not file_path:
        logger.debug("No file_path in tool_input, skipping.")
        sys.exit(0)

    rel_path = _rel_to_cwd(file_path)
    logger.debug("file_path=%s rel_path=%s", file_path, rel_path)

    config_path = Path(CONFIG_FILE)
    if not config_path.exists():
        logger.debug("Config %s not found, exiting silently.", CONFIG_FILE)
        sys.exit(0)

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        logger.debug("Failed to parse config %s, exiting.", CONFIG_FILE)
        sys.exit(0)

    matched_refs = _collect_matched_refs(rel_path, config.get("rules", []))
    logger.debug("matched_refs=%s", matched_refs)
    if not matched_refs:
        logger.debug("No refs matched for %s, exiting.", rel_path)
        sys.exit(0)

    session_id = get_session_id_short(get_by_key(data, "session_id") or "")
    cache_path = _cache_path(session_id)
    cache = _load_cache(cache_path)

    repeat_every = config.get("repeat_every", DEFAULT_REPEAT_EVERY)
    git_repo_url = config.get("git_repo_url", "")
    files = _build_files(matched_refs, cache, git_repo_url, repeat_every)

    _save_cache(cache_path, cache)
    logger.debug("Cache saved. files=%d.", len(files))
    _emit_files(files)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # pylint: disable=broad-exception-caught
        sys.exit(0)
