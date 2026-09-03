#!/usr/bin/env python3
# start_memory_rules.py
# SessionStart hook: inject a list of durable ai-memory pages (rules, feedback,
# gotchas, procedures) so the agent knows what permanent memory exists without
# having to query for it.

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

FTS_QUERY = "rules OR feedback OR gotcha OR procedure OR rule"
LIMIT = "60"


def fetch_pages():
    env = {**os.environ, "AI_MEMORY_PROJECT_STRATEGY": "repo-root"}
    try:
        proc = subprocess.run(
            ["ai-memory", "search", FTS_QUERY, "--json", "-n", LIMIT],
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        LOG.debug(f"[fetch_pages] ai-memory unavailable: {exc!r}")
        return []
    if proc.returncode != 0:
        LOG.debug(
            f"[fetch_pages] ai-memory exit {proc.returncode}: {proc.stderr.strip()}"
        )
    # CLI prints an INFO log line to stderr; JSON is on stdout.
    try:
        hits = json.loads(proc.stdout)
    except json.JSONDecodeError:
        LOG.debug(f"[fetch_pages] non-JSON stdout: {proc.stdout[:200]!r}")
        return []
    seen = {}
    for h in hits:
        path = h.get("path", "")
        if path.startswith(DURABLE_PREFIXES) and path not in seen:
            seen[path] = h.get("title", path)
    return sorted(seen.items())


def main():
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    pages = fetch_pages()
    LOG.debug(f"[main] {len(pages)} durable pages matched")
    if not pages:
        sys.exit(0)

    lines = [
        "## ai-memory: durable pages in this project",
        "",
        "Permanent memory (rules, feedback, gotchas, procedures). "
        "Read a page with `ai-memory read-page --path <path>` or `memory_read_page` when relevant.",
        "",
    ]
    lines.extend(f"- `{path}` — {title}" for path, title in pages)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }
    LOG.debug(f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
