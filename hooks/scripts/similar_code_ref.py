#!/usr/bin/python3
"""
Similar-Code-Ref Hook (POC)

PreToolUse hook for Edit|Write. Extracts imports/symbols from the content
being written, greps the repo for existing usages via ripgrep (cheap,
no index), then — if the project's embedding daemon is already running —
ranks candidates by cosine similarity against the new content and keeps
only the ones that are actually close. Falls back to raw rg results if
the daemon isn't up; never starts it (would add latency to every edit).
"""

import json
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

import numpy as np

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger, get_project_name  # noqa: E402

logger = get_hooks_logger("SimilarCodeRef")

MAX_STDIN = 1024 * 1024
MAX_TERMS = 3
MAX_FILES_PER_TERM = 5
CONTEXT_LINES = 2
MAX_SNIPPET_CHARS = 800
MAX_EMBED_CHARS = 4000
MIN_SIMILARITY = 0.5
MAX_RESULTS = 3

# Trivial terms that would create noise (too common to be a useful signal)
DENYLIST = {
    "os",
    "sys",
    "json",
    "re",
    "path",
    "fs",
    "io",
    "time",
    "typing",
    "react",
    "utils",
    "types",
    "index",
    "config",
    "logging",
    "subprocess",
}

EXT_TO_RG_TYPE = {
    ".py": "py",
    ".ts": "ts",
    ".tsx": "ts",
    ".js": "js",
    ".jsx": "js",
    ".go": "go",
}

IMPORT_PATTERNS = [
    re.compile(r"^\s*import\s+.*?\s+from\s+['\"](.+?)['\"]", re.MULTILINE),  # JS/TS
    re.compile(r"^\s*import\s+['\"](.+?)['\"]", re.MULTILINE),  # JS side-effect import
    re.compile(r"^\s*from\s+([\w.]+)\s+import\s+", re.MULTILINE),  # Python
    re.compile(
        r"^\s*import\s+([\w.,\s]+)", re.MULTILINE
    ),  # Python (incl. multi-import)
    re.compile(r"require\(['\"](.+?)['\"]\)"),  # CJS
    re.compile(r'^\s*(?:\w+\s+)?"([\w./-]+)"\s*$', re.MULTILINE),  # Go import line
]

SYMBOL_PATTERNS = [
    re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)", re.MULTILINE),
    re.compile(r"^\s*(?:export\s+)?class\s+(\w+)", re.MULTILINE),
    re.compile(r"^\s*def\s+(\w+)", re.MULTILINE),
    re.compile(r"^\s*class\s+(\w+)", re.MULTILINE),
    re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?(\w+)", re.MULTILINE),  # Go
    re.compile(r"^\s*type\s+(\w+)\s+(?:struct|interface)\b", re.MULTILINE),  # Go
]


def extract_terms(content: str) -> list[str]:
    """Pull candidate library/symbol names out of new code, filtering noise."""
    terms: list[str] = []
    seen: set[str] = set()

    for pattern in IMPORT_PATTERNS + SYMBOL_PATTERNS:
        for match in pattern.finditer(content):
            raw = match.group(1)
            for part in raw.split(","):
                term = part.strip().split(".")[-1].split("/")[-1]
                term_norm = term.lower()
                if not term or term_norm in DENYLIST or len(term) < 3:
                    continue
                if term_norm in seen:
                    continue
                seen.add(term_norm)
                terms.append(term)
                if len(terms) >= MAX_TERMS:
                    return terms

    return terms


def rg_search(term: str, rg_type: str | None, exclude_file: str) -> list[str]:
    """Return up to MAX_FILES_PER_TERM file paths containing `term`."""
    # NOTE: "." must be passed explicitly. Without a path arg, ripgrep falls
    # back to reading stdin when stdin isn't a tty (always true in a hook,
    # since Claude Code feeds the event JSON via stdin) and blocks forever
    # waiting for EOF. stdin=DEVNULL is a second layer of defense.
    cmd = ["rg", "-l", "--fixed-strings", term]
    if rg_type:
        cmd += ["--type", rg_type]
    cmd += ["--glob", f"!{exclude_file}", "."]

    logger.debug("rg_search cmd=%s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=os.getcwd(),
            stdin=subprocess.DEVNULL,
        )
    except Exception as exc:
        logger.debug("rg -l failed for term=%s: %s", term, exc)
        return []

    if result.returncode not in (0, 1):
        logger.debug("rg -l nonzero for term=%s: %s", term, result.stderr)
        return []

    files = [f for f in result.stdout.splitlines() if f][:MAX_FILES_PER_TERM]
    logger.debug("rg_search term=%s found=%d files=%s", term, len(files), files)
    return files


def rg_snippet(term: str, file_path: str) -> str:
    """Return a truncated -C context snippet for `term` in `file_path`."""
    cmd = ["rg", "-n", "--fixed-strings", "-C", str(CONTEXT_LINES), term, file_path]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=os.getcwd(),
            stdin=subprocess.DEVNULL,
        )
    except Exception as exc:
        logger.debug("rg -C failed for %s in %s: %s", term, file_path, exc)
        return ""

    out = result.stdout.strip()
    truncated = len(out) > MAX_SNIPPET_CHARS
    if truncated:
        out = out[:MAX_SNIPPET_CHARS] + "\n... (truncated)"
    logger.debug(
        "rg_snippet term=%s file=%s len=%d truncated=%s",
        term,
        file_path,
        len(out),
        truncated,
    )
    return out


def daemon_socket_path() -> str:
    return f"/tmp/embedding-daemon-{get_project_name()}.sock"


def is_daemon_running(sock_path: str) -> bool:
    try:
        conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        conn.settimeout(1)
        conn.connect(sock_path)
        conn.close()
        logger.debug("daemon running at %s", sock_path)
        return True
    except (ConnectionRefusedError, FileNotFoundError, OSError) as exc:
        logger.debug("daemon not running at %s: %s", sock_path, exc)
        return False


def encode_via_daemon(text: str, sock_path: str) -> np.ndarray | None:
    """Best-effort embed via the already-running daemon. Never starts it —
    a cold start (~seconds to load the model) would stall every Edit/Write."""
    try:
        conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        conn.settimeout(3)
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
            logger.debug("daemon error: %s", response["error"])
            return None
        vec = np.array(response["vector"], dtype=np.float32)
        logger.debug("encode_via_daemon ok, vec shape=%s", vec.shape)
        return vec
    except Exception as exc:
        logger.debug("daemon communication failed: %s", exc)
        return None


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def rank_by_similarity(
    content: str, candidates: list[tuple[str, str, str]]
) -> list[tuple[str, str, str]]:
    """Filter+sort (term, file, snippet) candidates by cosine similarity to
    `content`. Returns candidates unranked if the embedding daemon isn't up."""
    sock_path = daemon_socket_path()
    if not is_daemon_running(sock_path):
        logger.debug("embedding daemon not running, skipping similarity rank")
        return candidates[:MAX_RESULTS]

    new_vec = encode_via_daemon(content[:MAX_EMBED_CHARS], sock_path)
    if new_vec is None:
        logger.debug("could not encode new content, skipping similarity rank")
        return candidates[:MAX_RESULTS]

    scored: list[tuple[float, tuple[str, str, str]]] = []
    for candidate in candidates:
        _, _, snippet = candidate
        vec = encode_via_daemon(snippet, sock_path)
        if vec is None:
            logger.debug("could not encode candidate=%s, skipping", candidate[1])
            continue
        sim = cosine_similarity(new_vec, vec)
        logger.debug("similarity=%.3f candidate=%s", sim, candidate[1])
        if sim >= MIN_SIMILARITY:
            scored.append((sim, candidate))
        else:
            logger.debug(
                "similarity=%.3f below threshold=%.3f, dropping candidate=%s",
                sim,
                MIN_SIMILARITY,
                candidate[1],
            )

    scored.sort(key=lambda x: -x[0])
    logger.debug(
        "rank_by_similarity kept=%d of %d candidates", len(scored), len(candidates)
    )
    return [c for _, c in scored[:MAX_RESULTS]]


def build_context(content: str, target_file: str) -> str:
    ext = Path(target_file).suffix.lower()
    rg_type = EXT_TO_RG_TYPE.get(ext)

    terms = extract_terms(content)
    logger.debug("target=%s ext=%s terms=%s", target_file, ext, terms)
    if not terms:
        logger.debug("no terms extracted, skipping build_context")
        return ""

    candidates: list[tuple[str, str, str]] = []
    for term in terms:
        files = rg_search(term, rg_type, target_file)
        for f in files:
            snippet = rg_snippet(term, f)
            if not snippet:
                logger.debug("empty snippet for term=%s file=%s, skipping", term, f)
                continue
            candidates.append((term, f, snippet))

    logger.debug("collected %d candidates before ranking", len(candidates))
    if not candidates:
        return ""

    ranked = rank_by_similarity(content, candidates)
    logger.debug("build_context returning %d ranked blocks", len(ranked))
    blocks = [
        f"=== existing usage of '{term}' in {f} ===\n{snippet}"
        for term, f, snippet in ranked
    ]
    return "\n\n".join(blocks)


def main() -> None:
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(MAX_STDIN)
    except OSError:
        pass

    try:
        data = json.loads(stdin_data)
        tool_name = get_by_key(data, "tool_name")
        tool_input = get_by_key(data, "tool_input")
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.debug("failed to parse stdin json: %s", exc)
        sys.exit(0)

    logger.debug("tool_name=%s", tool_name)

    if tool_name not in ("Edit", "Write") or not tool_input:
        logger.debug("skipping: tool_name not in (Edit, Write) or no tool_input")
        sys.exit(0)

    file_path = get_by_key(tool_input, "file_path") or ""
    content = (
        get_by_key(tool_input, "content") or get_by_key(tool_input, "new_string") or ""
    )

    logger.debug("file_path=%s content_len=%d", file_path, len(content))

    if not file_path or not content:
        logger.debug("skipping: missing file_path or content")
        sys.exit(0)

    context = build_context(content, file_path)
    if context:
        logger.debug("emitting additionalContext: %s", context)
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "additionalContext": context,
                    }
                }
            )
        )
    else:
        logger.debug("no context found, emitting nothing")

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.debug("Error: %s", exc, exc_info=True)
        sys.exit(0)
