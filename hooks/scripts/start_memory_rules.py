#!/usr/bin/env python3
"""SessionStart hook: inject durable ai-memory pages at session start."""

import json
import os
import subprocess
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("StartMemoryRules")

# Durable page path prefixes worth surfacing at session start.
DURABLE_PREFIXES = ("rules/", "_rules/", "gotchas/", "procedures/", "feedback")

# Query the FTS index (which covers the `path` field) with both singular and
# plural forms of every durable prefix, so a page is matched by its path alone
# even when its title/body contains none of these words.
FTS_QUERY = "rules OR rule OR feedback OR gotcha OR gotchas OR procedure OR procedures"
LIMIT = "60"


def fetch_pages() -> list[tuple[str, str]]:
    """Fetch durable memory pages from ai-memory CLI.

    Returns:
        List of (path, title) tuples for durable pages matching prefixes.
    """
    env = {**os.environ, "AI_MEMORY_PROJECT_STRATEGY": "repo-root"}
    try:
        proc = subprocess.run(  # noqa: S603
            ["ai-memory", "search", FTS_QUERY, "--json", "-n", LIMIT],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        LOG.debug("[fetch_pages] ai-memory unavailable: %r", exc)
        return []
    if proc.returncode != 0:
        LOG.debug(
            "[fetch_pages] ai-memory exit %d: %s",
            proc.returncode,
            proc.stderr.strip(),
        )
    # CLI prints an INFO log line to stderr; JSON is on stdout.
    try:
        hits = json.loads(proc.stdout)
    except json.JSONDecodeError:
        LOG.debug("[fetch_pages] non-JSON stdout: %r", proc.stdout[:200])
        return []
    seen = {}
    for h in hits:
        path = h.get("path", "")
        if path.startswith(DURABLE_PREFIXES) and path not in seen:
            seen[path] = h.get("title", path)
    return sorted(seen.items())


def main() -> None:
    """Process stdin and output hook-specific context with durable pages."""
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    pages = fetch_pages()
    LOG.debug("[main] %d durable pages matched", len(pages))
    if not pages:
        sys.exit(0)

    lines = [
        "## ai-memory: durable pages in this project",
        "",
        "Permanent memory (rules, feedback, gotchas, procedures). "
        "Read a page with `ai-memory read-page --path <path>` or "
        "`memory_read_page` when relevant.",
        "",
    ]
    lines.extend(f"- `{path}` — {title}" for path, title in pages)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }
    LOG.debug("[additionalContext]: %s", json.dumps(output, ensure_ascii=False))
    print(json.dumps(output, ensure_ascii=False))  # noqa: T201
    sys.exit(0)


if __name__ == "__main__":
    main()
