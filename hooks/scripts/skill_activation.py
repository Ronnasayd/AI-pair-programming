#!/usr/bin/python3
"""UserPromptSubmit hook: suggest matching skills via embedding + BM25 fusion."""

from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    detect_skill,
    extract_query_text,
    get_by_key,
    get_hooks_logger,
    get_project_name,
    get_session_id_short,
    minify_json,
    read_file,
    resolve_command_text,
    write_file,
)

LOG = get_hooks_logger("SkillActivation")

DB_PATH = Path(os.environ["CLAUDE_PROJECT_DIR"]) / ".claude/skills/skills.db"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MIN_SIMILARITY = 0.55
MAX_SUGGESTIONS = 3
DEDUP_HOURS = 1
DAEMON_SCRIPT = Path(__file__).parent / "embedding_daemon.py"
DAEMON_START_TIMEOUT = 90


def get_daemon_socket_path() -> str:
    """Return the per-project unix socket path for the embedding daemon.

    Returns:
        str: Absolute path to the daemon's unix socket.
    """
    return f"/tmp/embedding-daemon-{get_project_name()}.sock"  # noqa: S108 hook temp socket path, per-project isolation


def is_daemon_running(sock_path: str) -> bool:
    """Return True if a socket connection to the daemon succeeds.

    Args:
        sock_path: Path to the daemon's unix socket.

    Returns:
        bool: True if the socket accepts a connection, False otherwise.
    """
    try:
        conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        conn.connect(sock_path)
        conn.close()
        return True
    except (ConnectionRefusedError, FileNotFoundError, OSError):
        return False


def start_daemon(sock_path: str) -> None:
    """Spawn the embedding daemon as a detached background process.

    Args:
        sock_path: Path to the daemon's unix socket, used only for logging.
    """
    subprocess.Popen(  # noqa: S603 controlled daemon script path via DAEMON_SCRIPT constant
        [sys.executable, str(DAEMON_SCRIPT)],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    LOG.debug("Daemon started — socket=%s", sock_path)


def wait_for_daemon(sock_path: str, timeout: int = DAEMON_START_TIMEOUT) -> bool:
    """Poll until the daemon socket accepts connections or timeout elapses.

    Args:
        sock_path: Path to the daemon's unix socket.
        timeout: Max seconds to poll before giving up.

    Returns:
        bool: True if the daemon became reachable, False on timeout.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if is_daemon_running(sock_path):
            return True
        time.sleep(0.2)
    return False


def encode_via_daemon(text: str) -> np.ndarray | None:
    """Request an embedding vector for text from the daemon, starting it if needed.

    Args:
        text: Text to embed.

    Returns:
        np.ndarray | None: The embedding vector, or None on failure.
    """
    sock_path = get_daemon_socket_path()
    if not is_daemon_running(sock_path):
        LOG.debug("Daemon not running — starting")
        start_daemon(sock_path)
        if not wait_for_daemon(sock_path):
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
            LOG.warning("Daemon error: %s", response["error"])
            return None
        return np.array(response["vector"], dtype=np.float32)
    except Exception as e:
        LOG.warning("Daemon communication failed: %s", e)
        return None


def load_rec_log(rec_log_path: Path) -> dict:
    """Load the per-session skill recommendation log, or {} if absent/invalid.

    Args:
        rec_log_path: Path to the recommendation log JSON file.

    Returns:
        dict: The parsed recommendation log, or {} if absent/invalid.
    """
    try:
        if rec_log_path.exists():
            content = read_file(rec_log_path)
            if content:
                return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        LOG.debug("Failed to load rec log: %s", e)
    return {}


def save_rec_log(rec_log_path: Path, rec_log: dict) -> None:
    """Persist the per-session skill recommendation log.

    Args:
        rec_log_path: Path to write the recommendation log JSON file to.
        rec_log: The recommendation log to persist.
    """
    try:
        write_file(rec_log_path, json.dumps(rec_log))
    except Exception as e:
        LOG.debug("Failed to save rec log: %s", e)


def should_suggest(skill_name: str, rec_log: dict) -> bool:
    """Return True if skill_name hasn't been suggested within DEDUP_HOURS.

    Args:
        skill_name: Name of the skill to check.
        rec_log: The recommendation log mapping skill name to last-suggested timestamp.

    Returns:
        bool: True if the skill should be suggested again, False otherwise.
    """
    if skill_name not in rec_log:
        return True
    try:
        last_time = datetime.fromisoformat(rec_log[skill_name])
        if datetime.now() - last_time >= timedelta(hours=DEDUP_HOURS):
            return True
    except ValueError:
        return True
    return False


def load_db_skills(db_path: Path) -> list[tuple[str, str, np.ndarray]]:
    """Return list of (name, hint, embedding_array).

    Args:
        db_path: Path to the skills sqlite database.

    Returns:
        list[tuple[str, str, np.ndarray]]: Rows of (name, hint, embedding_array).
    """
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name, hint, embedding FROM skills").fetchall()
    conn.close()
    return [
        (name, hint, np.frombuffer(emb, dtype=np.float32)) for name, hint, emb in rows
    ]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Return the cosine similarity between two vectors, 0.0 if either is zero.

    Args:
        a: First vector.
        b: Second vector.

    Returns:
        float: Cosine similarity in [-1.0, 1.0], or 0.0 if either vector is zero.
    """
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


_FTS_TOKEN_RE = re.compile(r"[a-zA-Z0-9À-ÿ]+")
MIN_BM25_TERM_OVERLAP = 3
MAX_BM25_SCORE = -0.5
BM25_RRF_WEIGHT = 0.5
# Generic function words in en/pt that shouldn't count as a lexical match on
# their own — without this filter, "how do I..." matches almost any skill.
_BM25_STOPWORDS = {
    "a",
    "an",
    "the",
    "i",
    "do",
    "does",
    "did",
    "how",
    "what",
    "when",
    "where",
    "why",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "and",
    "or",
    "my",
    "me",
    "it",
    "this",
    "that",
    "can",
    "you",
    "eu",
    "de",
    "da",
    "o",
    "os",
    "as",
    "que",
    "para",
    "com",
    "como",
    "um",
    "uma",
    "e",
    "ou",
    "meu",
    "minha",
    "isso",
    "esse",
    "essa",
}


def bm25_search(db_path: Path, query: str, limit: int) -> list[tuple[str, str]]:
    """Return skills ranked by FTS5 BM25, best first: [(name, hint)].

    OR-joins query tokens (an AND-all match rarely fires on full prompts), then
    requires >=MIN_BM25_TERM_OVERLAP tokens actually present in name+description —
    a single incidental word overlap (e.g. "sandwich" in an unrelated hint) is
    lexical noise, not a real match.

    Args:
        db_path: Path to the skills database file.
        query: Search query text to tokenize and match.
        limit: Maximum number of results to return.

    Returns:
        List of (name, hint) tuples ranked by BM25 score.
    """
    tokens = [
        t for t in _FTS_TOKEN_RE.findall(query) if t.lower() not in _BM25_STOPWORDS
    ]
    if len(tokens) < MIN_BM25_TERM_OVERLAP:
        return []
    fts_query = " OR ".join(f'"{t}"' for t in tokens)
    token_set = {t.lower() for t in tokens}

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT skills.name, skills.hint, skills.description, bm25(skills_fts) "
            "FROM skills_fts JOIN skills ON skills.id = skills_fts.rowid "
            "WHERE skills_fts MATCH ? ORDER BY bm25(skills_fts) LIMIT ?",
            (fts_query, limit * 3),
        ).fetchall()
    except sqlite3.OperationalError as e:
        LOG.debug("BM25 query failed (likely FTS5 syntax): %s", e)
        return []
    finally:
        conn.close()

    results = []
    for name, hint, description, bm25_score in rows:
        if bm25_score > MAX_BM25_SCORE:
            continue
        doc_tokens = {t.lower() for t in _FTS_TOKEN_RE.findall(f"{name} {description}")}
        if len(token_set & doc_tokens) >= MIN_BM25_TERM_OVERLAP:
            results.append((name, hint))
    return results[:limit]


def reciprocal_rank_fuse(
    *ranked_lists: list[str], k: int = 60, weights: list[float] | None = None
) -> dict[str, float]:
    """RRF-merge ranked name lists into a single {name: fused_score} map.

    weights scales each list's contribution (default 1.0 each) — used to make
    BM25 a tie-breaker/booster rather than cosine's equal, since lexical
    overlap alone is a weaker relevance signal than semantic similarity.

    Args:
        *ranked_lists: Variable number of ranked name lists to merge.
        k: RRF parameter for rank-based score calculation (default 60).
        weights: Per-list weights (default 1.0 for each list).

    Returns:
        Dictionary mapping skill names to their fused RRF scores.
    """
    if weights is None:
        weights = [1.0] * len(ranked_lists)
    fused: dict[str, float] = {}
    for ranked, weight in zip(ranked_lists, weights, strict=False):
        for rank, name in enumerate(ranked, start=1):
            fused[name] = fused.get(name, 0.0) + weight / (k + rank)
    return fused


def find_skills(
    db_path: Path, query: str, query_vector: np.ndarray, min_sim: float, limit: int
) -> list[tuple[float, str, str]]:
    """Fuse cosine-similarity and BM25 rankings via RRF.

    Returns sorted [(score, name, hint)].

    Args:
        db_path: Path to the skills database file.
        query: Search query text for BM25 matching.
        query_vector: Embedding vector for cosine similarity search.
        min_sim: Minimum cosine similarity threshold to include a skill.
        limit: Maximum number of results to return.

    Returns:
        List of (score, name, hint) tuples sorted by fused score descending.
    """
    skills = load_db_skills(db_path)
    hints = {name: hint for name, hint, _emb in skills}
    cosine_scored = sorted(
        ((cosine_similarity(query_vector, emb), name) for name, _hint, emb in skills),
        key=lambda x: x[0],
        reverse=True,
    )
    cosine_names = [name for sim, name in cosine_scored if sim >= min_sim]
    cosine_name_set = set(cosine_names)
    bm25_names = [
        name
        for name, _hint in bm25_search(db_path, query, limit * 2)
        if name in cosine_name_set
    ]
    LOG.debug(
        "cosine_names (%d): %s",
        len(cosine_names),
        [(name, sim) for sim, name in cosine_scored if sim >= min_sim],
    )
    LOG.debug("bm25_names (%d, cosine-gated): %s", len(bm25_names), bm25_names)

    fused = reciprocal_rank_fuse(
        cosine_names, bm25_names, weights=[1.0, BM25_RRF_WEIGHT]
    )
    ranked = sorted(fused.items(), key=lambda x: x[1], reverse=True)
    LOG.debug(
        "Top fused skills: %s",
        [(name, f"{score:.4f}") for name, score in ranked[:5]],
    )
    return [(score, name, hints[name]) for name, score in ranked[:limit]]


def main() -> None:
    """UserPromptSubmit/PostToolUse hook entrypoint: suggest matching skills."""
    if not DB_PATH.exists():
        LOG.warning("skills.db not found — run scripts/build-skill-index.py")
        sys.exit(0)

    try:
        import importlib.util

        if importlib.util.find_spec("fastembed") is None:
            LOG.warning("fastembed not installed")
            sys.exit(0)
    except Exception as e:
        LOG.debug("Failed to check fastembed availability: %s", e)

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug("Failed to parse stdin JSON: %s", e)
        sys.exit(0)

    try:
        prompt = extract_query_text(payload)
        if not prompt:
            LOG.debug("No prompt/answer text in payload — skipping")
            sys.exit(0)

        LOG.debug("Processing prompt (%d chars): %r...", len(prompt), prompt[:80])

        command_text = resolve_command_text(
            prompt, Path(os.environ["CLAUDE_PROJECT_DIR"])
        )
        query_text = command_text if command_text is not None else prompt
        if command_text is not None:
            LOG.debug(
                "Resolved /command to body (%d chars): %r...",
                len(command_text),
                command_text[:80],
            )

        session_id = get_session_id_short(get_by_key(payload, "session_id") or "")
        rec_log_path = Path(f"/tmp/skill-rec-log-{session_id}.json")  # noqa: S108 hook temp session log, isolated per-session
        LOG.debug("Session: %s | rec_log: %s", session_id, rec_log_path)
        rec_log = load_rec_log(rec_log_path)
        LOG.debug("Rec log has %d entries: %s", len(rec_log), list(rec_log.keys()))

        query_vector = encode_via_daemon(query_text)
        if query_vector is None:
            LOG.warning("Failed to get embedding — skipping")
            sys.exit(0)

        skills_raw = load_db_skills(DB_PATH)
        LOG.debug("Loaded %d skills from DB", len(skills_raw))

        candidates = find_skills(
            DB_PATH, query_text, query_vector, MIN_SIMILARITY, MAX_SUGGESTIONS * 2
        )
        LOG.debug(
            "Fused candidates: %s",
            [(name, f"{score:.4f}") for score, name, _ in candidates],
        )

        referenced_skill = detect_skill(prompt)
        referenced_skill_local = (
            referenced_skill is not None
            and Path(f".claude/skills/{referenced_skill}").exists()
        )
        LOG.debug(
            "Referenced skill in prompt: %r (local=%s)",
            referenced_skill,
            referenced_skill_local,
        )
        matches = [
            (name, hint)
            for _, name, hint in candidates
            if should_suggest(name, rec_log)
            and not (referenced_skill_local and name == referenced_skill)
        ]
        skipped_dedup = [
            name for _, name, _ in candidates if not should_suggest(name, rec_log)
        ]
        skipped_referenced = [
            name
            for _, name, _ in candidates
            if referenced_skill_local and name == referenced_skill
        ]
        if skipped_dedup:
            LOG.debug(
                "Skipped (already suggested within %dh): %s",
                DEDUP_HOURS,
                skipped_dedup,
            )
        if skipped_referenced:
            LOG.debug(
                "Skipped (explicitly referenced + present locally): %s",
                skipped_referenced,
            )
        matches = matches[:MAX_SUGGESTIONS]

        for name, _ in matches:
            rec_log[name] = datetime.now().isoformat()

        if matches:
            LOG.debug("Final matches (%d): %s", len(matches), [m[0] for m in matches])
            save_rec_log(rec_log_path, rec_log)
            suggestions = [
                {
                    "skill": name,
                    "hint": hint,
                    "present_locally": Path(f".claude/skills/{name}").exists(),
                }
                for name, hint in matches
            ]
            hook_event_name = (
                "PostToolUse"
                if get_by_key(payload, "tool_name")
                else "UserPromptSubmit"
            )
            output = {
                "hookSpecificOutput": {
                    "hookEventName": hook_event_name,
                    "additionalContext": minify_json(
                        {
                            "instruction": (
                                "check if these skills match user request; "
                                "if present_locally, invoke via Skill tool; "
                                "if not, call the skill-loader MCP tool "
                                "get_remote_skill(name) to fetch it and "
                                "follow its instructions inline — if the "
                                "returned files list has entries SKILL.md "
                                "references, fetch them with "
                                "get_remote_skill_file(name, relpath)"
                            ),
                            "suggestions": suggestions,
                        }
                    ),
                }
            }
            LOG.debug("[additionalContext]: %s", json.dumps(output, ensure_ascii=False))
            print(json.dumps(output, ensure_ascii=False))  # noqa: T201 hook stdout protocol
        else:
            LOG.debug("No skill matches after dedup filter")

    except Exception as e:
        LOG.warning("Unexpected error: %s: %s", type(e).__name__, e, exc_info=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
