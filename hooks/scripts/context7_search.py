#!/usr/bin/python3
import json
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from utils import extract_query_text, get_by_key, get_hooks_logger, get_project_name

LOG = get_hooks_logger("Context7Search")

SEARCH_URL = "https://context7.com/api/search"
MIN_BENCHMARK_SCORE = 80
MIN_EMBEDDING_SIMILARITY = 0.5
TOP_N = 3
TIMEOUT_SECONDS = 5
DAEMON_SCRIPT = Path(__file__).parent / "embedding_daemon.py"
DAEMON_START_TIMEOUT = 90


def getDaemonSocketPath() -> str:
    return f"/tmp/embedding-daemon-{get_project_name()}.sock"


def isDaemonRunning(sock_path: str) -> bool:
    try:
        conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        conn.connect(sock_path)
        conn.close()
        return True
    except (ConnectionRefusedError, FileNotFoundError, OSError):
        return False


def startDaemon(sock_path: str) -> None:
    subprocess.Popen(
        [sys.executable, str(DAEMON_SCRIPT)],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    LOG.debug(f"Daemon started — socket={sock_path}")


def waitForDaemon(sock_path: str, timeout: int = DAEMON_START_TIMEOUT) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if isDaemonRunning(sock_path):
            return True
        time.sleep(0.2)
    return False


def encodeViaDaemon(text: str) -> np.ndarray | None:
    sock_path = getDaemonSocketPath()
    if not isDaemonRunning(sock_path):
        LOG.debug("Daemon not running — starting")
        startDaemon(sock_path)
        if not waitForDaemon(sock_path):
            LOG.warning("Daemon failed to start within timeout")
            return None
    try:
        conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        conn.connect(sock_path)
        conn.sendall((json.dumps({"text": text}) + "\n").encode())
        data = b""
        while not data.endswith(b"\n"):
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
        conn.close()
        response = json.loads(data.decode())
        if "error" in response:
            LOG.warning(f"Daemon error: {response['error']}")
            return None
        return np.array(response["vector"], dtype=np.float32)
    except Exception as e:
        LOG.warning(f"Daemon communication failed: {e}")
        return None


def cosineSimilarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def fetchResults(query: str) -> list[dict]:
    url = f"{SEARCH_URL}?query={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": "claude-code-hook"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        payload = json.load(resp)
    return get_by_key(payload, "results") or []


def topResults(results: list[dict], query_vector: np.ndarray | None) -> list[dict]:
    settings = [get_by_key(r, "settings") or r for r in results]
    filtered = [
        s
        for s in settings
        if (get_by_key(s, "queryBenchmarkScore") or 0) > MIN_BENCHMARK_SCORE
    ]

    if query_vector is not None:
        scored = []
        log_scores = []
        for s in filtered:
            description = get_by_key(s, "description") or ""
            desc_vector = encodeViaDaemon(description) if description else None
            similarity = (
                cosineSimilarity(query_vector, desc_vector)
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
        LOG.debug(f"Scores: {log_scores}")

    filtered.sort(
        key=lambda s: s.get(
            "_rankScore", (get_by_key(s, "queryBenchmarkScore") or 0) / 100
        ),
        reverse=True,
    )
    for s in filtered:
        s.pop("_rankScore", None)
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

    prompt = extract_query_text(payload)
    if not prompt:
        LOG.debug("No prompt/answer text in payload — skipping")
        sys.exit(0)

    try:
        results = fetchResults(prompt)
    except Exception as e:
        LOG.warning(f"context7 search failed: {e}")
        sys.exit(0)

    query_vector = encodeViaDaemon(prompt)
    if query_vector is None:
        LOG.warning("Failed to get prompt embedding — skipping similarity filter")

    matches = topResults(results, query_vector)
    if not matches:
        LOG.debug("No context7 matches above benchmark threshold")
        sys.exit(0)

    hook_event_name = (
        "PostToolUse" if get_by_key(payload, "tool_name") else "UserPromptSubmit"
    )
    output = {
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
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
    LOG.debug(f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
