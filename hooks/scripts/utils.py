import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
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
    base = Path.cwd()
    return Path(base) / ".sessions"


def get_date_string() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_time_string() -> str:
    return datetime.now().strftime("%H:%M:%S")


def get_session_id_short(session_id: str) -> str:
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


def run_command_cwd(cmd: str, cwd: str | None = None, timeout: int = 30) -> dict:
    """Run a shell command with cwd/timeout support and return {success, output, error}."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
        }
    except Exception as exc:
        return {"success": False, "output": "", "error": str(exc)}


def parse_json_output(raw: str, tag: str, source: str, logger: logging.Logger) -> Any:
    """Parse a linter's stdout as JSON, falling back to the raw string on failure."""
    if not raw.strip():
        return raw
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("[%s] Failed to parse %s JSON output", tag, source)
        return raw


def parse_jsonlines_output(
    raw: str, tag: str, source: str, logger: logging.Logger
) -> Any:
    """Parse a linter's stdout as one JSON object per line (e.g. mypy --output json)."""
    lines = [line for line in raw.splitlines() if line.strip()]
    if not lines:
        return raw
    records = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            logger.warning("[%s] Failed to parse %s JSON line: %s", tag, source, line)
            return raw
    return records


def run_jscpd(
    resolved: Path, project_root: str, logger: logging.Logger, tag: str
) -> dict:
    """Run jscpd duplication check via npx. Returns {success, output, error, installed}.

    `output` is the parsed jscpd-report.json (structured duplicates list) when
    available, since agents parse structured data far more reliably than the
    console reporter's text table.
    """
    report_dir = tmp_project_dir(project_root, "jscpd-reports") / tag
    ensure_dir(report_dir)
    cmd = (
        f"npx jscpd --no-tips --exit-code 1 --reporters json "
        f"--output {report_dir} {str(resolved)}"
    )
    logger.debug("[%s] Executing: %s (cwd=%s)", tag, cmd, project_root)
    result = run_command_cwd(cmd, cwd=project_root)
    logger.debug("[%s] jscpd result: success=%s", tag, result["success"])

    report_path = report_dir / "jscpd-report.json"
    output: Any = result.get("output", "")
    report = read_file(report_path)
    if report:
        try:
            output = json.loads(report)
        except json.JSONDecodeError:
            logger.warning("[%s] Failed to parse jscpd report at %s", tag, report_path)

    if not result["success"]:
        logger.warning("[%s] jscpd found issues in %s:\n%s", tag, resolved, output)

    return {
        "success": result["success"],
        "output": output,
        "error": result.get("error", ""),
        "installed": True,
    }


def run_lint_hook_main(tag: str, logger: logging.Logger, maybe_run_lint) -> None:
    """Shared PostToolUse hook entrypoint: read stdin, run lint checks, emit output."""
    max_stdin = 1024 * 1024  # 1 MB
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(max_stdin)
    except OSError:
        pass

    output_data = stdin_data
    try:
        data = json.loads(stdin_data)
        tool_input = get_by_key(data, "tool_input")
        file_path = get_by_key(tool_input, "file_path") if tool_input else None
        logger.debug("[%s] Received file_path: %s", tag, file_path)
        lint_results = maybe_run_lint(file_path)
        output_data = emit_lint_output(stdin_data, lint_results, logger)
    except (json.JSONDecodeError, AttributeError):
        pass

    sys.stdout.write(output_data)
    sys.exit(0)


def emit_lint_output(
    stdin_data: str, lint_results: dict, logger: logging.Logger
) -> str:
    """Build the hook stdout payload, wrapping lint_results if any check ran."""
    if any(lint_results.values()):
        output = json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": json.dumps(lint_results),
                }
            }
        )
        logger.debug(f"[additionalContext]: {output}")
        return output
    return stdin_data


def escape_regexp(value: str) -> str:
    return re.escape(value)


# ---------------------------------------------------------------------------
# AST-based code info (tree-sitter)
# ---------------------------------------------------------------------------

_EXT_TO_TS_LANG = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".js": "javascript",
    ".jsx": "javascript",
    ".go": "go",
}

_DEF_NODE_TYPES = {
    "function_definition",  # python
    "class_definition",  # python
    "function_declaration",  # ts/js/go
    "class_declaration",  # ts/js
    "type_declaration",  # go (type X struct/interface)
    "method_declaration",  # go
}

_IMPORT_NODE_TYPES = {
    "import_statement",  # python, ts/js
    "import_from_statement",  # python
    "import_declaration",  # go
}

_STRING_NODE_TYPES = {"string", "interpreted_string_literal", "string_fragment"}

_ts_parser_cache: dict[str, Any] = {}


def _get_ts_parser(lang: str):
    if lang in _ts_parser_cache:
        return _ts_parser_cache[lang]
    try:
        from tree_sitter_language_pack import get_parser  # type: ignore[import-not-found]

        parser = get_parser(lang)
    except Exception:
        parser = None
    _ts_parser_cache[lang] = parser
    return parser


def _collect_defs(node, out: list[str]) -> None:
    if node.type in _DEF_NODE_TYPES:
        name_node = node.child_by_field_name("name")
        if name_node is not None:
            out.append(name_node.text.decode("utf-8", errors="ignore"))
    for child in node.children:
        _collect_defs(child, out)


def _collect_import_strings(node, out: list[str]) -> None:
    if node.type in _STRING_NODE_TYPES and node.type != "string_fragment":
        text = node.text.decode("utf-8", errors="ignore").strip("\"'")
        if text:
            out.append(text)
        return  # don't descend into string internals
    for child in node.children:
        _collect_import_strings(child, out)


def _collect_dotted_names(node, out: list[str]) -> None:
    if node.type == "dotted_name":
        out.append(node.text.decode("utf-8", errors="ignore"))
        return  # don't descend into a dotted_name's own identifier/./ children
    for child in node.children:
        _collect_dotted_names(child, out)


def _collect_imports(node, out: list[str]) -> None:
    if node.type == "import_from_statement":
        # python: from <dotted_name> import ... — first dotted_name is the module
        module = node.child_by_field_name("module_name")
        if module is not None:
            out.append(module.text.decode("utf-8", errors="ignore"))
        return
    if node.type == "import_statement":
        # python: import a, b.c as d — dotted_name may be wrapped in aliased_import
        _collect_dotted_names(node, out)
        _collect_import_strings(node, out)  # ts/js string-based imports
        return
    if node.type == "import_declaration":  # go
        _collect_import_strings(node, out)
        return
    for child in node.children:
        _collect_imports(child, out)


def extract_code_info(content: str, file_path: str) -> dict[str, list[str]]:
    """Extract top-level def/class names and imported module paths from source
    text via tree-sitter. Tolerates partial/invalid syntax (tree-sitter parses
    incrementally and still yields well-formed sibling nodes around an error);
    returns empty lists on unsupported extension or any parse failure.
    """
    empty: dict[str, list[str]] = {"defs": [], "imports": []}

    lang = _EXT_TO_TS_LANG.get(Path(file_path).suffix)
    if not lang or not content.strip():
        return empty

    parser = _get_ts_parser(lang)
    if parser is None:
        return empty

    try:
        tree = parser.parse(content.encode("utf-8", errors="ignore"))
    except Exception:
        return empty

    defs: list[str] = []
    imports: list[str] = []
    try:
        _collect_defs(tree.root_node, defs)
        _collect_imports(tree.root_node, imports)
    except Exception:
        return empty

    return {"defs": _dedupe(defs), "imports": _dedupe(imports)}


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def enclosing_def_name(content: str, file_path: str, offset: int) -> str | None:
    """Name of the innermost def/class node whose byte range contains `offset`."""
    lang = _EXT_TO_TS_LANG.get(Path(file_path).suffix)
    if not lang:
        return None
    parser = _get_ts_parser(lang)
    if parser is None:
        return None

    try:
        tree = parser.parse(content.encode("utf-8", errors="ignore"))
    except Exception:
        return None

    byte_offset = len(content[:offset].encode("utf-8", errors="ignore"))
    node = tree.root_node.descendant_for_byte_range(byte_offset, byte_offset)
    while node is not None:
        if node.type in _DEF_NODE_TYPES:
            name_node = node.child_by_field_name("name")
            if name_node is not None:
                return name_node.text.decode("utf-8", errors="ignore")
        node = node.parent
    return None


def get_hooks_logger(
    name: str = "Hooks",
    log_file: str = str(Path.home() / ".claude" / "logs" / "hooks.log"),
) -> logging.Logger:
    LOG_FILE = log_file
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s]-[%(name)s]: %(message)s")
    )
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


def extract_query_text(payload: Mapping[str, Any]) -> Optional[str]:
    """
    Return text to embed/search for, from either a UserPromptSubmit
    payload ("prompt") or a PostToolUse payload for AskUserQuestion
    (question + selected answers from "tool_response").
    """
    prompt = get_by_key(payload, "prompt")
    if prompt:
        return prompt

    tool_name = get_by_key(payload, "tool_name")
    if tool_name != "AskUserQuestion":
        return None

    tool_response = get_by_key(payload, "tool_response") or {}
    answers = get_by_key(tool_response, "answers") or {}
    if not answers:
        return None

    return " ".join(f"{q} {a}" for q, a in answers.items())


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
    "npx": "npx.cmd",
    "pnpm": "pnpm.cmd",
    "yarn": "yarn.cmd",
    "bunx": "bunx.cmd",
}
_FORMATTER_PACKAGES = {
    "biome": {"bin_name": "biome", "pkg_name": "@biomejs/biome"},
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


def jest_installed(project_root: str) -> bool:
    """Check if jest binary exists in project's node_modules."""
    return (Path(project_root) / "node_modules" / ".bin" / "jest").exists()


def tmp_project_dir(project_root: str, namespace: str) -> Path:
    """Per-project scratch dir under the OS tmp dir, keyed by project path hash."""
    key = hashlib.sha1(project_root.encode()).hexdigest()[:12]
    tmp_dir = Path(tempfile.gettempdir()) / namespace / key
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


def _coverage_pct(covered: int, total: int) -> float:
    if total == 0:
        return 100
    return round((covered / total) * 10000) / 100


def _coverage_line_hits(file_coverage: dict) -> dict:
    """Collapse statement hits onto their starting line (istanbul's 'lines' metric)."""
    statement_map = file_coverage.get("statementMap", {})
    statement_hits = file_coverage.get("s", {})
    line_hits: dict[int, int] = {}
    for stmt_id, loc in statement_map.items():
        line = loc["start"]["line"]
        hits = statement_hits.get(stmt_id, 0)
        line_hits[line] = max(line_hits.get(line, 0), hits)
    return line_hits


def _coverage_file_summary(file_coverage: dict) -> dict:
    line_hits = _coverage_line_hits(file_coverage)
    lines_total = len(line_hits)
    lines_covered = sum(1 for hits in line_hits.values() if hits > 0)

    statement_hits = file_coverage.get("s", {})
    statements_total = len(statement_hits)
    statements_covered = sum(1 for hits in statement_hits.values() if hits > 0)

    fn_hits = file_coverage.get("f", {})
    functions_total = len(fn_hits)
    functions_covered = sum(1 for hits in fn_hits.values() if hits > 0)

    branch_hits = file_coverage.get("b", {})
    branches_total = sum(len(counts) for counts in branch_hits.values())
    branches_covered = sum(
        sum(1 for hit in counts if hit > 0) for counts in branch_hits.values()
    )

    return {
        "lines": {
            "total": lines_total,
            "covered": lines_covered,
            "skipped": 0,
            "pct": _coverage_pct(lines_covered, lines_total),
        },
        "statements": {
            "total": statements_total,
            "covered": statements_covered,
            "skipped": 0,
            "pct": _coverage_pct(statements_covered, statements_total),
        },
        "functions": {
            "total": functions_total,
            "covered": functions_covered,
            "skipped": 0,
            "pct": _coverage_pct(functions_covered, functions_total),
        },
        "branches": {
            "total": branches_total,
            "covered": branches_covered,
            "skipped": 0,
            "pct": _coverage_pct(branches_covered, branches_total),
        },
    }


def build_coverage_summary(merged_final: dict) -> dict:
    """Compute Istanbul coverage-summary.json shape from a coverage-final.json dict."""
    summary = {}
    totals = {
        "lines": [0, 0],
        "statements": [0, 0],
        "functions": [0, 0],
        "branches": [0, 0],
    }
    for file_path, file_coverage in merged_final.items():
        file_summary = _coverage_file_summary(file_coverage)
        summary[file_path] = file_summary
        for metric, (total, covered) in totals.items():
            totals[metric] = [
                total + file_summary[metric]["total"],
                covered + file_summary[metric]["covered"],
            ]

    summary["total"] = {
        metric: {
            "total": total,
            "covered": covered,
            "skipped": 0,
            "pct": _coverage_pct(covered, total),
        }
        for metric, (total, covered) in totals.items()
    }
    return summary


def find_last_coverage_dir(project_root: str) -> str:
    """Return existing coverage dir if present, else default 'coverage'."""
    default_dir = Path(project_root) / "coverage"
    if default_dir.exists():
        return str(default_dir)
    for candidate in Path(project_root).glob("**/coverage-final.json"):
        return str(candidate.parent)
    return str(default_dir)


def spawn_background(cmd: str, cwd: str, log_path: Path) -> None:
    """Detach a shell command so it survives after the calling process exits."""
    with open(log_path, "ab") as log_file:
        subprocess.Popen(
            ["nohup", "bash", "-c", cmd],
            cwd=cwd,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )


def lock_path_for(tmp_dir: Path, rel_path: str) -> Path:
    """Lockfile path for a given project-relative file, under tmp_dir/locks."""
    key = hashlib.sha1(rel_path.encode()).hexdigest()[:16]
    return tmp_dir / "locks" / f"{key}.lock"


def acquire_lock(lock_file: Path) -> bool:
    """Create lock_file if absent or its owning PID is dead. Returns True if acquired."""
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    if lock_file.exists():
        try:
            pid = int(lock_file.read_text().strip())
            os.kill(pid, 0)
            return False  # owner still alive
        except (ValueError, OSError):
            pass  # stale lock, PID dead or unreadable
    lock_file.write_text(str(os.getpid()))
    return True


def release_lock(lock_file: Path) -> None:
    try:
        lock_file.unlink()
    except OSError:
        pass


def detect_formatter(project_root: str, logger: logging.Logger) -> str | None:
    """
    Detect the formatter configured in the project.
    Biome takes priority over Prettier.
    Returns 'biome', 'prettier', or None.
    """
    if project_root in _formatter_cache:
        logger.debug(
            f"[detect_formatter] Cache hit for {project_root}: {_formatter_cache[project_root]}"
        )
        return _formatter_cache[project_root]

    root = Path(project_root)
    logger.debug(
        f"[detect_formatter] Detecting formatter for {project_root} with root {root}"
    )

    # Biome config files take top priority
    for cfg in _BIOME_CONFIGS:
        if (root / cfg).exists():
            _formatter_cache[project_root] = "biome"
            logger.debug(
                f"[detect_formatter] Detected Biome config for {project_root}: {cfg}"
            )
            return "biome"

    # package.json "prettier" key before standalone config files
    pkg_path = root / "package.json"
    logger.debug(f"[detect_formatter] Checking for package.json at {pkg_path}")
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            if "prettier" in pkg:
                _formatter_cache[project_root] = "prettier"
                logger.debug(
                    f"[detect_formatter] Detected Prettier config in package.json for {project_root}"
                )
                return "prettier"
        except (json.JSONDecodeError, OSError):
            pass  # Malformed package.json — continue to file-based detection

    for cfg in _PRETTIER_CONFIGS:
        if (root / cfg).exists():
            _formatter_cache[project_root] = "prettier"
            logger.debug(
                f"[detect_formatter] Detected Prettier config file for {project_root}: {cfg}"
            )
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
                    exec_cmd = {
                        "pnpm": "pnpm dlx",
                        "yarn": "yarn dlx",
                        "bun": "bunx",
                    }.get(pm_name, "npx")
            except (json.JSONDecodeError, OSError):
                pass

    if not exec_cmd:
        exec_cmd = "npx"

    parts = exec_cmd.split()
    raw_bin = parts[0] if parts else "npx"
    prefix = parts[1:] if len(parts) > 1 else []

    bin_ = _WIN_CMD_SHIMS.get(raw_bin, raw_bin) if is_win else raw_bin
    return {"bin": bin_, "prefix": prefix}


def resolve_formatter_bin(
    project_root: str, formatter: str, logger: logging.Logger
) -> dict | None:
    """
    Resolve the formatter binary, preferring the local node_modules/.bin
    installation over the package-manager exec command.

    Returns {"bin": str, "prefix": list[str]} or None.
    """
    cache_key = f"{project_root}:{formatter}"
    if cache_key in _bin_cache:
        logger.debug(
            f"[resolve_formatter_bin] Cache hit for {cache_key}: {_bin_cache[cache_key]}"
        )
        return _bin_cache[cache_key]

    pkg = _FORMATTER_PACKAGES.get(formatter)
    if not pkg:
        logger.debug(
            f"[resolve_formatter_bin] No package info for formatter '{formatter}'"
        )
        _bin_cache[cache_key] = None
        return None

    is_win = sys.platform == "win32"
    bin_name = pkg["bin_name"] + (".cmd" if is_win else "")
    local_bin = Path(project_root) / "node_modules" / ".bin" / bin_name

    if local_bin.exists():
        result = {"bin": str(local_bin), "prefix": []}
        _bin_cache[cache_key] = result
        logger.debug(
            f"[resolve_formatter_bin] Found local binary for {formatter} at {local_bin}"
        )
        return result

    runner = _get_runner_from_package_manager(project_root)
    result = {"bin": runner["bin"], "prefix": [*runner["prefix"], pkg["pkg_name"]]}
    _bin_cache[cache_key] = result
    logger.debug(
        f"[resolve_formatter_bin] Using package manager runner for {formatter}: {result}"
    )
    return result


# ---------------------------------------------------------------------------
# rag-rat MCP (raw JSON-RPC over stdio)
# ---------------------------------------------------------------------------


def is_rag_rat_available(cwd: str) -> bool:
    return shutil.which("rag-rat") is not None and (Path(cwd) / "rag-rat.toml").exists()


def call_rag_rat_tool(
    tool_name: str,
    arguments: dict,
    cwd: str,
    logger: logging.Logger,
    timeout: int = 15,
) -> str | None:
    """Call one rag-rat MCP tool via a throwaway `rag-rat mcp` subprocess.
    Returns the first content block's text, or None on any failure."""
    try:
        proc = subprocess.Popen(
            ["rag-rat", "mcp"],
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
    except OSError as e:
        logger.warning(f"Failed to spawn rag-rat mcp: {e}")
        return None

    try:
        _rag_rat_send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "hooks", "version": "0.0.1"},
                },
            },
        )
        _rag_rat_recv(proc, timeout)

        _rag_rat_send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})

        _rag_rat_send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            },
        )
        resp = _rag_rat_recv(proc, timeout)
    except (TimeoutError, EOFError, json.JSONDecodeError) as e:
        logger.warning(f"rag-rat {tool_name} call failed: {e}")
        return None
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

    if "error" in resp:
        logger.debug(f"rag-rat {tool_name} error: {resp['error']}")
        return None
    content = resp.get("result", {}).get("content", [])
    return content[0]["text"] if content else None


def _rag_rat_send(proc: subprocess.Popen, msg: dict) -> None:
    assert proc.stdin is not None
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()


def _rag_rat_recv(proc: subprocess.Popen, timeout: int) -> dict:
    import select

    assert proc.stdout is not None
    ready, _, _ = select.select([proc.stdout], [], [], timeout)
    if not ready:
        raise TimeoutError("no response from rag-rat mcp")
    line = proc.stdout.readline()
    if not line:
        stderr = proc.stderr.read()[:500] if proc.stderr else ""
        raise EOFError("rag-rat mcp closed: " + stderr)
    return json.loads(line)


def rgb_to_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def colorize_json(payload, indent: int = 0) -> str:
    """Dump JSON with ANSI-colored keys and values (recursive, no regex)."""
    _KEY_COLOR = "\033[36m"  # cyan
    _VALUE_COLOR = "\033[32m"  # green
    _RESET = "\033[0m"
    pad = "  " * indent
    child_pad = "  " * (indent + 1)

    if isinstance(payload, dict):
        if not payload:
            return "{}"
        items = []
        for key, value in payload.items():
            key_str = f"{_KEY_COLOR}{json.dumps(key)}{_RESET}"
            value_str = colorize_json(value, indent + 1)
            items.append(f"{child_pad}{key_str}: {value_str}")
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"

    if isinstance(payload, list):
        if not payload:
            return "[]"
        items = [f"{child_pad}{colorize_json(v, indent + 1)}" for v in payload]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"

    return f"{_VALUE_COLOR}{json.dumps(payload)}{_RESET}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def detect_skill(text: str) -> str | None:
    """Return skill name referenced in text via /skill-name, if any."""
    match = re.search(r"(?<!\S)/([a-zA-Z0-9_-]+)(?!\S)", text)
    return match.group(1) if match else None


# find's -exec ... ; terminator uses a bare/escaped semicolon that is NOT a
# shell command separator — splitting there truncates the -exec argument list
# (and any protected target inside it), silently defeating a targets scan.
EXEC_TERMINATOR_RE = re.compile(r"(-exec\b(?:(?!\\;|;).)*?)(\\;|;)", re.DOTALL)


def strip_heredocs(command: str) -> str:
    """Strip heredoc bodies, leaving just the <<DELIM marker.

    Prevents heredoc content lines (which may legitimately mention protected
    filenames as text, e.g. a doc example) from being treated as sub-commands
    once split_on_operators() cuts on newlines.
    """
    lines = command.split("\n")
    result = []
    heredoc_delim = None
    i = 0

    while i < len(lines):
        if heredoc_delim is not None:
            if lines[i].strip() == heredoc_delim:
                heredoc_delim = None
            i += 1
            continue

        m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", lines[i])
        if m:
            heredoc_delim = m.group(1)

        result.append(lines[i])
        i += 1

    return "\n".join(result)


def split_on_operators(command: str, protect_exec: bool = False) -> list[str]:
    """Split a shell command string on &&, ||, ;, |, and newlines.

    Quote- and $()-depth-aware (a `;` inside a quoted string or a subshell is
    not a split point), unlike a plain regex split. Heredoc bodies are stripped
    and backslash-newline continuations collapsed before parsing.

    protect_exec=True additionally shields `find -exec ... ;` terminators from
    being treated as command separators.
    """
    if protect_exec:
        command = EXEC_TERMINATOR_RE.sub(lambda m: m.group(1) + "\x00", command)
    command = strip_heredocs(command)
    command = command.replace("\\\n", " ")

    segments = []
    current = []
    i = 0
    in_single_quote = False
    in_double_quote = False
    paren_depth = 0

    while i < len(command):
        ch = command[i]

        # Backslash escaping (not inside single quotes, where \ is literal)
        if ch == "\\" and not in_single_quote and i + 1 < len(command):
            current.append(ch)
            current.append(command[i + 1])
            i += 2
            continue

        if ch == "'" and not in_double_quote and paren_depth == 0:
            in_single_quote = not in_single_quote
            current.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single_quote and paren_depth == 0:
            in_double_quote = not in_double_quote
            current.append(ch)
            i += 1
            continue

        if in_single_quote or in_double_quote:
            current.append(ch)
            i += 1
            continue

        # $() subshell depth — consume $( as a single token
        if ch == "$" and i + 1 < len(command) and command[i + 1] == "(":
            paren_depth += 1
            current.append("$")
            current.append("(")
            i += 2
            continue
        if ch == "(" and paren_depth > 0:
            paren_depth += 1
            current.append(ch)
            i += 1
            continue
        if ch == ")" and paren_depth > 0:
            paren_depth -= 1
            current.append(ch)
            i += 1
            continue

        if paren_depth > 0:
            current.append(ch)
            i += 1
            continue

        # Split on operators at top level
        if ch == "&" and i + 1 < len(command) and command[i + 1] == "&":
            segments.append("".join(current))
            current = []
            i += 2
            continue
        if ch == "|" and i + 1 < len(command) and command[i + 1] == "|":
            segments.append("".join(current))
            current = []
            i += 2
            continue
        if ch in (";", "|", "\n"):
            segments.append("".join(current))
            current = []
            i += 1
            continue

        current.append(ch)
        i += 1

    segments.append("".join(current))
    return [s.replace("\x00", ";").strip() for s in segments if s.strip()]
