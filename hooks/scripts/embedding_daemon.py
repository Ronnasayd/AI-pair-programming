#!/usr/bin/python3
"""Persistent embedding daemon — loads SentenceTransformer once, serves via Unix socket."""

import json
import logging
import os
import signal
import socket
import sys
import time
from pathlib import Path

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
INACTIVITY_TIMEOUT = 30 * 60  # 30 min


def get_socket_path(project_name: str) -> str:
    return f"/tmp/embedding-daemon-{project_name}.sock"


def get_pid_path(project_name: str) -> str:
    return f"/tmp/embedding-daemon-{project_name}.pid"


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("EmbeddingDaemon")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler("/tmp/hooks.log")
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s]-[%(name)s]: %(message)s")
    )
    logger.addHandler(handler)
    return logger


def main():
    project_name = Path.cwd().name
    sock_path = get_socket_path(project_name)
    pid_path = get_pid_path(project_name)

    LOG = setup_logger()
    LOG.debug(f"Daemon starting — project={project_name} socket={sock_path}")

    try:
        from fastembed import TextEmbedding
    except ImportError:
        LOG.error("fastembed not installed")
        sys.exit(1)

    model = TextEmbedding(MODEL_NAME)
    LOG.debug(f"Model '{MODEL_NAME}' loaded")

    # Write PID
    Path(pid_path).write_text(str(os.getpid()))

    # Clean stale socket
    if Path(sock_path).exists():
        Path(sock_path).unlink()

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(sock_path)
    server.listen(5)
    server.settimeout(60)  # wake up every 60s to check inactivity

    last_activity = time.monotonic()

    def shutdown(signum, frame):
        LOG.debug("Daemon shutting down")
        server.close()
        for p in (sock_path, pid_path):
            try:
                Path(p).unlink()
            except FileNotFoundError:
                pass
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    LOG.debug("Daemon ready — listening")

    while True:
        if time.monotonic() - last_activity > INACTIVITY_TIMEOUT:
            LOG.debug("Inactivity timeout — exiting")
            shutdown(None, None)

        try:
            conn, _ = server.accept()
        except socket.timeout:
            continue

        last_activity = time.monotonic()
        try:
            data = b""
            while not data.endswith(b"\n"):
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk

            request = json.loads(data.decode())
            text = request.get("text", "")
            vector = list(model.embed([text]))[0].tolist()
            response = json.dumps({"vector": vector}) + "\n"
            conn.sendall(response.encode())
        except Exception as e:
            LOG.warning(f"Request error: {e}")
            try:
                conn.sendall((json.dumps({"error": str(e)}) + "\n").encode())
            except Exception:
                pass
        finally:
            conn.close()


if __name__ == "__main__":
    main()
