#!/usr/bin/env python3
import json
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
    get_by_key,
    get_hooks_logger,
    get_project_name,
    get_session_id_short,
    read_file,
    write_file,
)

LOG = get_hooks_logger("SkillActivation")

DB_PATH = Path(".claude/skills/skills.db")
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MIN_SIMILARITY = 0.48
MAX_SUGGESTIONS = 5
DEDUP_HOURS = 24
DAEMON_SCRIPT = Path(__file__).parent / "embedding_daemon.py"
DAEMON_START_TIMEOUT = 10


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


def findSkills(db_path: Path, query_vector: np.ndarray, min_sim: float, limit: int):
    """Score all skills, return sorted [(sim, name, hint)]."""
    skills = loadDbSkills(db_path)
    scored = [
        (cosineSimilarity(query_vector, emb), name, hint) for name, hint, emb in skills
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    LOG.debug(f"Top scored skills: {[(name, f'{sim:.3f}') for sim, name, _ in scored[:5]]}")
    return [(sim, name, hint) for sim, name, hint in scored if sim >= min_sim][:limit]


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
        LOG.debug(f"Payload keys: {list(payload.keys())}")
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse stdin JSON: {e}")
        sys.exit(0)

    try:
        prompt = get_by_key(payload, "prompt")
        if not prompt:
            LOG.debug("No prompt in payload — skipping")
            sys.exit(0)

        LOG.debug(f"Processing prompt ({len(prompt)} chars): {prompt[:80]!r}...")

        session_id = get_session_id_short(get_by_key(payload, "session_id") or "")
        rec_log_path = Path(f"/tmp/skill-rec-log-{session_id}.json")
        LOG.debug(f"Session: {session_id} | rec_log: {rec_log_path}")
        rec_log = loadRecLog(rec_log_path)
        LOG.debug(f"Rec log has {len(rec_log)} entries: {list(rec_log.keys())}")

        LOG.debug("Requesting embedding from daemon")
        query_vector = encodeViaDaemon(prompt)
        if query_vector is None:
            LOG.warning("Failed to get embedding — skipping")
            sys.exit(0)
        LOG.debug(f"Query vector shape: {query_vector.shape}")

        skills_raw = loadDbSkills(DB_PATH)
        LOG.debug(f"Loaded {len(skills_raw)} skills from DB")

        candidates = findSkills(
            DB_PATH, query_vector, MIN_SIMILARITY, MAX_SUGGESTIONS * 2
        )
        LOG.debug(
            f"Candidates above sim={MIN_SIMILARITY}: {[(name, f'{sim:.3f}') for sim, name, _ in candidates]}"
        )

        matches = [
            (name, hint) for _, name, hint in candidates if shouldSuggest(name, rec_log)
        ]
        skipped = [
            name for _, name, _ in candidates if not shouldSuggest(name, rec_log)
        ]
        if skipped:
            LOG.debug(f"Skipped (dedup {DEDUP_HOURS}h): {skipped}")
        matches = matches[:MAX_SUGGESTIONS]

        for name, _ in matches:
            rec_log[name] = datetime.now().isoformat()

        if matches:
            LOG.debug(f"Final matches ({len(matches)}): {[m[0] for m in matches]}")
            saveRecLog(rec_log_path, rec_log)
            suggestions = "; ".join(f"`/{m[0]}` — {m[1]}" for m in matches)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": f"**Skill suggestions:** {suggestions}",
                }
            }
            LOG.debug(f"Output JSON: {json.dumps(output)}")
            print(json.dumps(output))
        else:
            LOG.debug("No skill matches after dedup filter")

    except Exception as e:
        LOG.warning(f"Unexpected error: {type(e).__name__}: {e}", exc_info=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
