#!/usr/bin/python3
"""Persistent embedding daemon.

Loads SentenceTransformer once, serves via Unix socket.
"""

import contextlib
import json
import logging
import os
from pathlib import Path
import signal
import socket
import sys
import time
import traceback

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
SPACY_MODELS = {"pt": "pt_core_news_sm", "en": "en_core_web_sm"}
INACTIVITY_TIMEOUT = 30 * 60  # 30 min
# why: /tmp survives login-session teardown; XDG_RUNTIME_DIR killed early
RUNTIME_DIR = Path("/tmp")  # noqa: S108


def load_nlp(logger: logging.Logger) -> dict:
    """Load spaCy models for stopword removal, one per supported language.

    Args:
        logger: Logger to report a load failure to.

    Returns:
        Mapping of language code to loaded spaCy model, empty if unavailable.
    """
    try:
        # why: spacy is an optional dependency, only needed for stopword removal
        import spacy  # pylint: disable=import-outside-toplevel

        return {lang: spacy.load(name) for lang, name in SPACY_MODELS.items()}
    # why: any load failure (missing model, bad install) must not crash the daemon
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("spacy unavailable, skipping stopword removal: %s", e)
        return {}


def clean_query(nlp: dict, text: str) -> str:
    """Detect language, then lemmatize and strip stopwords/punctuation.

    Args:
        nlp: Mapping of language code to spaCy model, as returned by load_nlp.
        text: Raw query text to clean.

    Returns:
        Cleaned text, or the original text if language detection/model is unavailable.
    """
    if not nlp or not text.strip():
        return text

    try:
        # why: langdetect is an optional dependency, only needed for language detection
        from langdetect import detect  # pylint: disable=import-outside-toplevel

        language = detect(text)
    # why: detection failure on malformed/short text must fall back to raw text
    except Exception:  # pylint: disable=broad-exception-caught
        return text

    model = nlp.get(language)
    if model is None:
        return text

    doc = model(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space
    ]
    return " ".join(tokens) or text


def get_socket_path(project_name: str) -> str:
    """Return the Unix socket path for a project's embedding daemon.

    Args:
        project_name: Name of the project the daemon serves.

    Returns:
        Absolute path to the daemon's Unix socket.
    """
    return str(RUNTIME_DIR / f"embedding-daemon-{project_name}.sock")


def get_pid_path(project_name: str) -> str:
    """Return the PID file path for a project's embedding daemon.

    Args:
        project_name: Name of the project the daemon serves.

    Returns:
        Absolute path to the daemon's PID file.
    """
    return str(RUNTIME_DIR / f"embedding-daemon-{project_name}.pid")


def setup_logger() -> logging.Logger:
    """Configure and return the daemon's file logger.

    Returns:
        Logger writing to ~/.claude/logs/hooks.log.
    """
    logger = logging.getLogger("EmbeddingDaemon")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(str(Path.home() / ".claude" / "logs" / "hooks.log"))
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s]-[%(name)s]: %(message)s")
    )
    logger.addHandler(handler)
    return logger


# why: daemon entrypoint — setup + serve loop naturally exceeds statement/local limits
def main() -> None:  # pylint: disable=too-many-locals,too-many-statements
    """Run the embedding daemon.

    Loads the model, listens on a Unix socket, and serves requests until
    the inactivity timeout elapses.
    """
    project_name = Path.cwd().name
    sock_path = get_socket_path(project_name)
    pid_path = get_pid_path(project_name)

    log = setup_logger()
    log.debug("Daemon starting — project=%s socket=%s", project_name, sock_path)

    try:
        # why: fastembed is an optional dependency, checked here to give a clear error
        from fastembed import TextEmbedding  # pylint: disable=import-outside-toplevel
    except ImportError:
        log.error("fastembed not installed")
        sys.exit(1)

    nlp = load_nlp(log)

    hf_cache = str(Path.home() / ".cache" / "huggingface" / "hub")
    model = TextEmbedding(MODEL_NAME, cache_dir=hf_cache)
    log.debug("Model '%s' loaded", MODEL_NAME)

    # Write PID
    Path(pid_path).write_text(str(os.getpid()), encoding="utf-8")

    # Clean stale socket
    if Path(sock_path).exists():
        Path(sock_path).unlink()

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(sock_path)
    server.listen(5)
    server.settimeout(60)  # wake up every 60s to check inactivity

    last_activity = time.monotonic()

    def shutdown(signum: int | None, frame: object | None) -> None:  # noqa: ARG001
        log.debug("Daemon shutting down")
        server.close()
        for p in (sock_path, pid_path):
            with contextlib.suppress(FileNotFoundError):
                Path(p).unlink()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    log.debug("Daemon ready — listening")

    while True:  # pylint: disable=too-many-nested-blocks
        idle_for = time.monotonic() - last_activity
        if idle_for > INACTIVITY_TIMEOUT:
            log.debug("Inactivity timeout — %s > %s", idle_for, INACTIVITY_TIMEOUT)
            shutdown(None, None)

        try:
            conn, _ = server.accept()
        except TimeoutError:
            continue

        last_activity = time.monotonic()
        try:
            data = b""
            while not data.endswith(b"\n"):
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk

            if not data:
                continue

            request = json.loads(data.decode())
            text = clean_query(nlp, request.get("text", ""))
            log.debug("text: %s", text)
            vector = next(iter(model.embed([text]))).tolist()
            response = json.dumps({"vector": vector}) + "\n"
            conn.sendall(response.encode())
        # why: any per-request failure must be reported without killing the daemon
        except Exception as e:  # pylint: disable=broad-exception-caught
            log.warning("Request error: %s — raw data: %r", e, data)
            log.warning(traceback.format_exc())
            try:
                conn.sendall((json.dumps({"error": str(e)}) + "\n").encode())
            except OSError as send_exc:
                log.debug("Failed to send error response: %s", send_exc)
        finally:
            conn.close()


if __name__ == "__main__":
    main()
