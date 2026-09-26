#!/usr/bin/python3
"""UserPromptSubmit/PostToolUse hook that surfaces relevant context7 libraries."""

import json
from pathlib import Path
import sys
import urllib.parse
import urllib.request

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    encode_via_daemon,
    extract_query_text,
    get_by_key,
    get_hooks_logger,
    minify_json,
)

LOG = get_hooks_logger("Context7Search")

SEARCH_URL = "https://context7.com/api/search"
MIN_BENCHMARK_SCORE = 90
MIN_EMBEDDING_SIMILARITY = 0.6
MIN_STARS = 50
MIN_TRUST_SCORE = 8.0
TOP_N = 3
TIMEOUT_SECONDS = 5
DAEMON_SCRIPT = Path(__file__).parent / "embedding_daemon.py"
DAEMON_START_TIMEOUT = 90


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute the cosine similarity between two vectors.

    Args:
        a: First vector.
        b: Second vector.

    Returns:
        Cosine similarity in [-1, 1], or 0.0 if either vector is zero.
    """
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def fetch_results(query: str) -> list[dict]:
    """Query the context7 search API for libraries matching query.

    Args:
        query: Free-text search query.

    Returns:
        Raw result entries from the API, or [] if none.
    """
    url = f"{SEARCH_URL}?query={urllib.parse.quote(query)}"
    req = urllib.request.Request(  # noqa: S310
        url, headers={"User-Agent": "claude-code-hook"}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:  # noqa: S310
        payload = json.load(resp)
    return get_by_key(payload, "results") or []


def _passes_quality_floor(s: dict) -> bool:
    """Return True if a library entry clears benchmark and popularity floors.

    Args:
        s: A context7 search-result settings object.

    Returns:
        True when the entry's benchmark score exceeds ``MIN_BENCHMARK_SCORE`` and
        it clears either the star or the trust-score floor. Filters out toy repos
        that score 100 on the benchmark but have no real adoption.
    """
    if (get_by_key(s, "queryBenchmarkScore") or 0) <= MIN_BENCHMARK_SCORE:
        return False
    stars = get_by_key(s, "stars") or 0
    trust = get_by_key(s, "trustScore") or 0
    return stars >= MIN_STARS or trust >= MIN_TRUST_SCORE


def top_results(results: list[dict], query_vector: np.ndarray | None) -> list[dict]:
    """Filter and rank library results, keeping the top matches.

    Args:
        results: Raw context7 search results.
        query_vector: Embedding of the user's query, or None to skip
            similarity-based filtering and ranking.

    Returns:
        Up to ``TOP_N`` result settings objects, best match first.
    """
    settings = [get_by_key(r, "settings") or r for r in results]
    filtered = [s for s in settings if _passes_quality_floor(s)]

    if query_vector is not None:
        scored = []
        log_scores = []
        for s in filtered:
            description = get_by_key(s, "description") or ""
            desc_vector = (
                encode_via_daemon(description, DAEMON_SCRIPT, DAEMON_START_TIMEOUT)
                if description
                else None
            )
            similarity = (
                cosine_similarity(query_vector, desc_vector)
                if desc_vector is not None
                else 0.0
            )
            rank_score = (get_by_key(s, "queryBenchmarkScore") or 0) / 100 + similarity
            log_scores.append(
                (
                    rank_score,
                    similarity,
                    get_by_key(s, "queryBenchmarkScore") or 0,
                    get_by_key(s, "title"),
                )
            )
            if similarity >= MIN_EMBEDDING_SIMILARITY:
                s["_rankScore"] = rank_score
                scored.append(s)
        filtered = scored
        log_scores.sort(key=lambda x: x[0], reverse=True)
        LOG.debug("Scores: %s", log_scores)

    filtered.sort(
        key=lambda s: s.get(
            "_rankScore", (get_by_key(s, "queryBenchmarkScore") or 0) / 100
        ),
        reverse=True,
    )
    for s in filtered:
        s.pop("_rankScore", None)
    return filtered[:TOP_N]


def to_context(r: dict) -> dict:
    """Project a context7 result settings object into the hook's output shape.

    Args:
        r: A context7 search-result settings object.

    Returns:
        Dict with the fields surfaced to the model.
    """
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


def main() -> None:
    """Search context7 for libraries relevant to the prompt and emit matches."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse stdin JSON: %s", e)
        sys.exit(0)

    prompt = extract_query_text(payload)
    if not prompt:
        LOG.debug("No prompt/answer text in payload — skipping")
        sys.exit(0)

    try:
        results = fetch_results(prompt)
    except Exception as e:  # pylint: disable=broad-exception-caught
        LOG.warning("context7 search failed: %s", e)
        sys.exit(0)

    query_vector = encode_via_daemon(prompt, DAEMON_SCRIPT, DAEMON_START_TIMEOUT)
    if query_vector is None:
        LOG.warning("Failed to get prompt embedding — skipping similarity filter")

    matches = top_results(results, query_vector)
    if not matches:
        LOG.debug("No context7 matches above benchmark threshold")
        sys.exit(0)

    hook_event_name = (
        "PostToolUse" if get_by_key(payload, "tool_name") else "UserPromptSubmit"
    )
    output = {
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
            "additionalContext": minify_json(
                {
                    "instruction": (
                        "these context7 libraries match the user's query; if "
                        "relevant to the task, call the context7 MCP tools "
                        "(resolve-library-id then get-library-docs) using the "
                        "library's project id to fetch up-to-date docs before "
                        "answering"
                    ),
                    "context7_libraries": [to_context(r) for r in matches],
                }
            ),
        }
    }
    LOG.debug("[additionalContext]: %s", json.dumps(output, ensure_ascii=False))
    print(json.dumps(output, ensure_ascii=False))  # noqa: T201
    sys.exit(0)


if __name__ == "__main__":
    main()
