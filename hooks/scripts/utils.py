import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path
import json
import os
import sys
import logging
import re
from typing import Any, Mapping, Optional
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
    

def get_session_id_short(session_id:str) -> str:
    """Return a short session identifier from env var or a timestamp fallback."""
    return session_id[:8] if session_id else datetime.now().strftime("%H%M%S")


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
    except Exception as err:
        return {"success": False, "output": str(err)}


def escape_regexp(value: str) -> str:
    return re.escape(value)

def get_hooks_logger(name:str="Hooks") -> logging.Logger:
    LOG_FILE = "/tmp/hooks.log"
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]-[%(name)s]: %(message)s"))
    logger.addHandler(file_handler)
    return logger




def normalize_key(key: str) -> str:
    """
    Normaliza:
    - camelCase / PascalCase → snake_case
    - remove separadores inconsistentes
    - lower case
    """
    # camelCase → snake_case
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", key)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)

    # normaliza separadores e case
    return s2.replace("-", "_").lower()


def get_by_key(data: Mapping[str, Any], target_key: str) -> Optional[Any]:
    """
    Busca valor independente do formato da chave.
    Ex:
        tool_input, toolInput, ToolInput, TOOL_INPUT → todos equivalentes
    """
    target_norm = normalize_key(target_key)

    for k, v in data.items():
        if normalize_key(k) == target_norm:
            return v

    return None

# ---------------------------------------------------------------------------
# Inlined resolver helpers (ported from resolve_formatter.js)
# ---------------------------------------------------------------------------
# Module-level caches (mirrors the JS per-process Maps)
_project_root_cache: dict[str, str] = {}
_formatter_cache: dict[str, str | None] = {}
_bin_cache: dict[str, dict | None] = {}
_BIOME_CONFIGS = ["biome.json", "biome.jsonc"]

_PRETTIER_CONFIGS = [
    ".prettierrc",
    ".prettierrc.json",
    ".prettierrc.js",
    ".prettierrc.cjs",
    ".prettierrc.mjs",
    ".prettierrc.yml",
    ".prettierrc.yaml",
    ".prettierrc.toml",
    "prettier.config.js",
    "prettier.config.cjs",
    "prettier.config.mjs",
]
_PROJECT_ROOT_MARKERS = ["package.json", *_BIOME_CONFIGS, *_PRETTIER_CONFIGS]
_WIN_CMD_SHIMS = {
    "npx":  "npx.cmd",
    "pnpm": "pnpm.cmd",
    "yarn": "yarn.cmd",
    "bunx": "bunx.cmd",
}
_FORMATTER_PACKAGES = {
    "biome":    {"bin_name": "biome",    "pkg_name": "@biomejs/biome"},
    "prettier": {"bin_name": "prettier", "pkg_name": "prettier"},
}

def find_project_root(start_dir: str) -> str:
    """
    Walk up from start_dir until a directory containing a known project-root
    marker (package.json or formatter config) is found.
    Returns start_dir as a fallback when no marker exists above it.
    """
    if start_dir in _project_root_cache:
        return _project_root_cache[start_dir]

    directory = Path(start_dir).resolve()
    while True:
        for marker in _PROJECT_ROOT_MARKERS:
            if (directory / marker).exists():
                _project_root_cache[start_dir] = str(directory)
                return str(directory)
        parent = directory.parent
        if parent == directory:
            break
        directory = parent

    _project_root_cache[start_dir] = start_dir
    return start_dir


def detect_formatter(project_root: str, logger: logging.Logger) -> str | None:
    """
    Detect the formatter configured in the project.
    Biome takes priority over Prettier.
    Returns 'biome', 'prettier', or None.
    """
    if project_root in _formatter_cache:
        logger.debug(f"[detect_formatter] Cache hit for {project_root}: {_formatter_cache[project_root]}")
        return _formatter_cache[project_root]

    root = Path(project_root)
    logger.debug(f"[detect_formatter] Detecting formatter for {project_root} with root {root}")

    # Biome config files take top priority
    for cfg in _BIOME_CONFIGS:
        if (root / cfg).exists():
            _formatter_cache[project_root] = "biome"
            logger.debug(f"[detect_formatter] Detected Biome config for {project_root}: {cfg}")
            return "biome"

    # package.json "prettier" key before standalone config files
    pkg_path = root / "package.json"
    logger.debug(f"[detect_formatter] Checking for package.json at {pkg_path}")
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            if "prettier" in pkg:
                _formatter_cache[project_root] = "prettier"
                logger.debug(f"[detect_formatter] Detected Prettier config in package.json for {project_root}")
                return "prettier"
        except (json.JSONDecodeError, OSError):
            pass  # Malformed package.json — continue to file-based detection

    for cfg in _PRETTIER_CONFIGS:
        if (root / cfg).exists():
            _formatter_cache[project_root] = "prettier"
            logger.debug(f"[detect_formatter] Detected Prettier config file for {project_root}: {cfg}")
            return "prettier"

    _formatter_cache[project_root] = None
    logger.debug(f"[detect_formatter] No formatter detected for {project_root}")
    return None


def _get_runner_from_package_manager(project_root: str) -> dict:
    """
    Resolve the runner binary and prefix args for the configured package
    manager. Respects the CLAUDE_PACKAGE_MANAGER env var; falls back to npx.
    """
    is_win = sys.platform == "win32"

    # Honour explicit override first, then inspect package.json packageManager
    exec_cmd = os.environ.get("CLAUDE_PACKAGE_MANAGER", "").strip()
    if not exec_cmd:
        pkg_path = Path(project_root) / "package.json"
        if pkg_path.exists():
            try:
                pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
                pm_field = pkg.get("packageManager", "")  # e.g. "pnpm@9.0.0"
                if pm_field:
                    pm_name = pm_field.split("@")[0].strip()
                    exec_cmd = {"pnpm": "pnpm dlx", "yarn": "yarn dlx", "bun": "bunx"}.get(pm_name, "npx")
            except (json.JSONDecodeError, OSError):
                pass

    if not exec_cmd:
        exec_cmd = "npx"

    parts = exec_cmd.split()
    raw_bin = parts[0] if parts else "npx"
    prefix = parts[1:] if len(parts) > 1 else []

    bin_ = _WIN_CMD_SHIMS.get(raw_bin, raw_bin) if is_win else raw_bin
    return {"bin": bin_, "prefix": prefix}


def resolve_formatter_bin(project_root: str, formatter: str, logger: logging.Logger) -> dict | None:
    """
    Resolve the formatter binary, preferring the local node_modules/.bin
    installation over the package-manager exec command.

    Returns {"bin": str, "prefix": list[str]} or None.
    """
    cache_key = f"{project_root}:{formatter}"
    if cache_key in _bin_cache:
        logger.debug(f"[resolve_formatter_bin] Cache hit for {cache_key}: {_bin_cache[cache_key]}")
        return _bin_cache[cache_key]

    pkg = _FORMATTER_PACKAGES.get(formatter)
    if not pkg:
        logger.debug(f"[resolve_formatter_bin] No package info for formatter '{formatter}'")
        _bin_cache[cache_key] = None
        return None

    is_win = sys.platform == "win32"
    bin_name = pkg["bin_name"] + (".cmd" if is_win else "")
    local_bin = Path(project_root) / "node_modules" / ".bin" / bin_name

    if local_bin.exists():
        result = {"bin": str(local_bin), "prefix": []}
        _bin_cache[cache_key] = result
        logger.debug(f"[resolve_formatter_bin] Found local binary for {formatter} at {local_bin}")
        return result

    runner = _get_runner_from_package_manager(project_root)
    result = {"bin": runner["bin"], "prefix": [*runner["prefix"], pkg["pkg_name"]]}
    _bin_cache[cache_key] = result
    logger.debug(f"[resolve_formatter_bin] Using package manager runner for {formatter}: {result}")
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
