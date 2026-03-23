import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path
# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    print(msg, file=sys.stderr)



def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from a string."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def get_sessions_dir() -> Path:
    """Return the directory where session files are stored."""
    base =  Path.cwd()
    return Path(base) / ".sessions" 


def get_date_string() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_time_string() -> str:
    return datetime.now().strftime("%H:%M:%S")
    

def get_session_id_short() -> str:
    """Return a short session identifier from env var or a timestamp fallback."""
    return Path.cwd().name.lower() if Path.cwd().name else datetime.now().strftime("%H%M%S")


def get_project_name() -> str:
    """Return the current directory name as the project name."""
    return Path.cwd().name


def ensure_dir(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)


def read_file(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, IOError):
        return None


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def run_command(cmd: str) -> dict:
    """Run a shell command and return {success, output}."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
        }
    except Exception:
        return {"success": False, "output": ""}


def escape_regexp(value: str) -> str:
    return re.escape(value)

