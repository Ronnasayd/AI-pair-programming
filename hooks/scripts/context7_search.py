#!/usr/bin/python3
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import get_by_key, get_hooks_logger

LOG = get_hooks_logger("Context7Search")

SEARCH_URL = "https://context7.com/api/search"
MIN_BENCHMARK_SCORE = 70
TOP_N = 3
TIMEOUT_SECONDS = 5


def fetchResults(query: str) -> list[dict]:
    url = f"{SEARCH_URL}?query={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": "claude-code-hook"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        payload = json.load(resp)
    return get_by_key(payload, "results") or []


def topResults(results: list[dict]) -> list[dict]:
    settings = [get_by_key(r, "settings") or r for r in results]
    filtered = [
        s
        for s in settings
        if (get_by_key(s, "queryBenchmarkScore") or 0) > MIN_BENCHMARK_SCORE
    ]
    filtered.sort(key=lambda s: get_by_key(s, "queryBenchmarkScore") or 0, reverse=True)
    return filtered[:TOP_N]


def toContext(r: dict) -> dict:
    return {
        "title": get_by_key(r, "title"),
        "project": get_by_key(r, "project"),
        "type": get_by_key(r, "type"),
        "language": get_by_key(r, "language"),
        "description": get_by_key(r, "description"),
        "docsRepoUrl": get_by_key(r, "docsRepoUrl"),
        "stars": get_by_key(r, "stars"),
        "trustScore": get_by_key(r, "trustScore"),
        "popularityRank": get_by_key(r, "popularityRank"),
        "queryBenchmarkScore": get_by_key(r, "queryBenchmarkScore"),
        "lastFullRefreshDate": get_by_key(r, "lastFullRefreshDate"),
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse stdin JSON: {e}")
        sys.exit(0)

    prompt = get_by_key(payload, "prompt")
    if not prompt:
        LOG.debug("No prompt in payload — skipping")
        sys.exit(0)

    try:
        results = fetchResults(prompt)
    except Exception as e:
        LOG.warning(f"context7 search failed: {e}")
        sys.exit(0)

    matches = topResults(results)
    if not matches:
        LOG.debug("No context7 matches above benchmark threshold")
        sys.exit(0)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": json.dumps(
                {
                    "instruction": (
                        "these context7 libraries match the user's query; if relevant "
                        "to the task, call the context7 MCP tools "
                        "(resolve-library-id then get-library-docs) using the library's "
                        "project id to fetch up-to-date docs before answering"
                    ),
                    "context7_libraries": [toContext(r) for r in matches],
                },
                ensure_ascii=False,
            ),
        }
    }
    LOG.debug(f"Output: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
