#!/usr/bin/python3
import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from utils import (
    detect_skill,
    extract_query_text,
    get_by_key,
    get_hooks_logger,
    get_project_name,
    get_session_id_short,
    read_file,
    write_file,
)

LOG = get_hooks_logger("SkillActivation")

DB_PATH = Path(os.environ["AI_PROJECT_DIR"]) / ".claude/skills/skills.db"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MIN_SIMILARITY = 0.5
MAX_SUGGESTIONS = 3
DEDUP_HOURS = 1
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


def loadRecLog(rec_log_path: Path):
    try:
        if rec_log_path.exists():
            content = read_file(rec_log_path)
            if content:
                return json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        LOG.debug(f"Failed to load rec log: {e}")
    return {}


def saveRecLog(rec_log_path: Path, rec_log):
    try:
        write_file(rec_log_path, json.dumps(rec_log))
    except Exception as e:
        LOG.debug(f"Failed to save rec log: {e}")


def shouldSuggest(skill_name, rec_log):
    if skill_name not in rec_log:
        return True
    try:
        last_time = datetime.fromisoformat(rec_log[skill_name])
        if datetime.now() - last_time >= timedelta(hours=DEDUP_HOURS):
            return True
    except ValueError:
        return True
    return False


def loadDbSkills(db_path: Path):
    """Return list of (name, hint, embedding_array)."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name, hint, embedding FROM skills").fetchall()
    conn.close()
    return [
        (name, hint, np.frombuffer(emb, dtype=np.float32)) for name, hint, emb in rows
    ]


def cosineSimilarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


_FTS_TOKEN_RE = re.compile(r"[a-zA-Z0-9À-ÿ]+")
MIN_BM25_TERM_OVERLAP = 2
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
    "do",
    "da",
    "o",
    "a",
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


def bm25Search(db_path: Path, query: str, limit: int):
    """Return skills ranked by FTS5 BM25, best first: [(name, hint)].

    OR-joins query tokens (an AND-all match rarely fires on full prompts), then
    requires >=MIN_BM25_TERM_OVERLAP tokens actually present in name+description —
    a single incidental word overlap (e.g. "sandwich" in an unrelated hint) is
    lexical noise, not a real match.
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
            "SELECT skills.name, skills.hint, skills.description FROM skills_fts "
            "JOIN skills ON skills.id = skills_fts.rowid "
            "WHERE skills_fts MATCH ? ORDER BY bm25(skills_fts) LIMIT ?",
            (fts_query, limit * 3),
        ).fetchall()
    except sqlite3.OperationalError as e:
        LOG.debug(f"BM25 query failed (likely FTS5 syntax): {e}")
        return []
    finally:
        conn.close()

    results = []
    for name, hint, description in rows:
        doc_tokens = {t.lower() for t in _FTS_TOKEN_RE.findall(f"{name} {description}")}
        if len(token_set & doc_tokens) >= MIN_BM25_TERM_OVERLAP:
            results.append((name, hint))
    return results[:limit]


def reciprocalRankFuse(*ranked_lists: list[str], k: int = 60) -> dict[str, float]:
    """RRF-merge ranked name lists into a single {name: fused_score} map."""
    fused: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, name in enumerate(ranked, start=1):
            fused[name] = fused.get(name, 0.0) + 1.0 / (k + rank)
    return fused


def findSkills(
    db_path: Path, query: str, query_vector: np.ndarray, min_sim: float, limit: int
):
    """Fuse cosine-similarity and BM25 rankings via RRF, return sorted [(score, name, hint)]."""
    skills = loadDbSkills(db_path)
    hints = {name: hint for name, hint, _emb in skills}
    cosine_scored = sorted(
        ((cosineSimilarity(query_vector, emb), name) for name, _hint, emb in skills),
        key=lambda x: x[0],
        reverse=True,
    )
    cosine_names = [name for sim, name in cosine_scored if sim >= min_sim]
    bm25_names = [name for name, _hint in bm25Search(db_path, query, limit * 2)]

    fused = reciprocalRankFuse(cosine_names, bm25_names)
    ranked = sorted(fused.items(), key=lambda x: x[1], reverse=True)
    LOG.debug(
        f"Top fused skills: {[(name, f'{score:.4f}') for name, score in ranked[:5]]}"
    )
    return [(score, name, hints[name]) for name, score in ranked[:limit]]


def main():
    if not DB_PATH.exists():
        LOG.warning("skills.db not found — run scripts/build-skill-index.py")
        sys.exit(0)

    try:
        import importlib.util

        if importlib.util.find_spec("fastembed") is None:
            LOG.warning("fastembed not installed")
            sys.exit(0)
    except Exception:
        pass

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse stdin JSON: {e}")
        sys.exit(0)

    try:
        prompt = extract_query_text(payload)
        if not prompt:
            LOG.debug("No prompt/answer text in payload — skipping")
            sys.exit(0)

        LOG.debug(f"Processing prompt ({len(prompt)} chars): {prompt[:80]!r}...")

        session_id = get_session_id_short(get_by_key(payload, "session_id") or "")
        rec_log_path = Path(f"/tmp/skill-rec-log-{session_id}.json")
        LOG.debug(f"Session: {session_id} | rec_log: {rec_log_path}")
        rec_log = loadRecLog(rec_log_path)
        LOG.debug(f"Rec log has {len(rec_log)} entries: {list(rec_log.keys())}")

        query_vector = encodeViaDaemon(prompt)
        if query_vector is None:
            LOG.warning("Failed to get embedding — skipping")
            sys.exit(0)

        skills_raw = loadDbSkills(DB_PATH)
        LOG.debug(f"Loaded {len(skills_raw)} skills from DB")

        candidates = findSkills(
            DB_PATH, prompt, query_vector, MIN_SIMILARITY, MAX_SUGGESTIONS * 2
        )
        LOG.debug(
            f"Fused candidates: {[(name, f'{score:.4f}') for score, name, _ in candidates]}"
        )

        referenced_skill = detect_skill(prompt)
        referenced_skill_local = (
            referenced_skill is not None
            and Path(f".claude/skills/{referenced_skill}").exists()
        )
        matches = [
            (name, hint)
            for _, name, hint in candidates
            if shouldSuggest(name, rec_log)
            and not (referenced_skill_local and name == referenced_skill)
        ]
        skipped = [
            name
            for _, name, _ in candidates
            if not shouldSuggest(name, rec_log)
            or (referenced_skill_local and name == referenced_skill)
        ]
        if skipped:
            LOG.debug(f"Skipped (dedup {DEDUP_HOURS}h): {skipped}")
        matches = matches[:MAX_SUGGESTIONS]

        for name, _ in matches:
            rec_log[name] = datetime.now().isoformat()

        if matches:
            LOG.debug(f"Final matches ({len(matches)}): {[m[0] for m in matches]}")
            saveRecLog(rec_log_path, rec_log)
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
                    "additionalContext": json.dumps(
                        {
                            "instruction": (
                                "check if these skills match user request; if present_locally, "
                                "invoke via Skill tool; if not, call the skill-loader MCP tool "
                                "get_remote_skill(name) to fetch it and follow its instructions "
                                "inline — if the returned files list has entries SKILL.md "
                                "references, fetch them with get_remote_skill_file(name, relpath)"
                            ),
                            "suggestions": suggestions,
                        },
                        ensure_ascii=False,
                    ),
                }
            }
            LOG.debug(f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}")
            print(json.dumps(output, ensure_ascii=False))
        else:
            LOG.debug("No skill matches after dedup filter")

    except Exception as e:
        LOG.warning(f"Unexpected error: {type(e).__name__}: {e}", exc_info=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
