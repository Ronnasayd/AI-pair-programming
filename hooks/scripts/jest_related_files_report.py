#!/usr/bin/python3
"""
Jest related-files hook.

After a JS/TS file is edited/created:
  - if it's a test file (*.test.*, *.spec.*), report which source files it
    imports (the files it tests).
  - if it's a plain source file, report which test files import it (the
    tests that cover it).

Uses rag-rat (find_callers / trace_callees via impact_surface) when
available for accurate, alias-aware resolution; falls back to a plain
ripgrep-based import scan otherwise.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    call_rag_rat_tool,
    find_project_root,
    get_by_key,
    get_hooks_logger,
    is_rag_rat_available,
)

logger = get_hooks_logger("JestRelatedFiles")

_JS_TS_EXTS = {".js", ".jsx", ".ts", ".tsx"}
_TEST_RE = re.compile(r"\.(test|spec)\.[jt]sx?$", re.IGNORECASE)
_IMPORT_RE = re.compile(
    r"""(?:from\s+|require\(\s*|import\(\s*)['"]((?:\.{1,2}|@[\w/-]*)/[^'"]+)['"]"""
)
# tsconfig.json "paths" aliases, longest prefix first so "@src/" doesn't get
# shadowed by a hypothetical "@/" match.
_ALIASES = [
    ("@src/", "src/"),
    ("@modules/", "src/modules/"),
    ("@/", ""),
]
MAX_RESULTS = 10
RAG_RAT_TIMEOUT = 15


def _is_test_file(path: Path) -> bool:
    return bool(_TEST_RE.search(path.name))


def _existing_with_ext(candidate: Path) -> Path | None:
    if candidate.suffix:
        return candidate if candidate.exists() else None
    for ext in (".ts", ".tsx", ".js", ".jsx"):
        f = candidate.with_suffix(ext)
        if f.exists():
            return f
    for ext in (".ts", ".tsx", ".js", ".jsx"):
        f = candidate / f"index{ext}"
        if f.exists():
            return f
    return None


def _resolve_import(
    source_file: Path, project_root: str, import_spec: str
) -> Path | None:
    if import_spec.startswith((".", "..")):
        return _existing_with_ext((source_file.parent / import_spec).resolve())
    for prefix, replacement in _ALIASES:
        if import_spec.startswith(prefix):
            rel = replacement + import_spec[len(prefix) :]
            return _existing_with_ext((Path(project_root) / rel).resolve())
    return None


def _grep_imports_in_file(path: Path, project_root: str) -> list[Path]:
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return []
    resolved = []
    for m in _IMPORT_RE.finditer(text):
        f = _resolve_import(path, project_root, m.group(1))
        if f and f not in resolved:
            resolved.append(f)
    return resolved


def _grep_tests_importing(target: Path, project_root: str) -> list[Path]:
    """Find test files under project_root whose relative import resolves to target."""
    try:
        result = subprocess.run(
            ["rg", "-l", "--glob", "*.test.*", "--glob", "*.spec.*", target.stem],
            capture_output=True,
            text=True,
            timeout=8,
            cwd=project_root,
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        logger.debug("rg search for tests failed: %s", exc)
        return []
    if result.returncode not in (0, 1):
        return []

    matches = []
    for rel in result.stdout.splitlines():
        test_path = Path(project_root) / rel
        if not _is_test_file(test_path):
            continue
        imports = _grep_imports_in_file(test_path, project_root)
        if any(f == target for f in imports):
            matches.append(test_path)
    return matches


def _fallback_for_test_file(resolved: Path, project_root: str) -> list[str]:
    imports = _grep_imports_in_file(resolved, project_root)
    return [str(f) for f in imports[:MAX_RESULTS]]


def _fallback_for_source_file(resolved: Path, project_root: str) -> list[str]:
    tests = _grep_tests_importing(resolved, project_root)
    return [str(f) for f in tests[:MAX_RESULTS]]


_PATH_LIKE_RE = re.compile(r'"([^"\n]+\.(?:ts|tsx|js|jsx))"|path:\s*"?([^"\n,]+)"?')


def _rag_rat_paths_from_impact(text: str, key: str) -> list[str]:
    """Pull file-path values out of an impact_surface/find_callers text blob.

    rag-rat's tool output shape varies (e.g. `imported_by`/`called_by`/`calls`
    arrays of quoted paths, or a `path: ...` field) — match both instead of
    assuming a fixed key.
    """
    paths = []
    for m in _PATH_LIKE_RE.finditer(text):
        p = (m.group(1) or m.group(2) or "").strip()
        if p and p not in paths and not p.startswith(".stryker/"):
            paths.append(p)
    return paths


def _rag_rat_for_source_file(resolved: Path, project_root: str) -> list[str] | None:
    text = call_rag_rat_tool(
        "impact_surface",
        {"query": resolved.stem, "include": ["tests"]},
        project_root,
        logger,
        timeout=RAG_RAT_TIMEOUT,
    )
    if not text:
        return None
    paths = _rag_rat_paths_from_impact(text, "tests")
    filtered = [p for p in paths if _is_test_file(Path(p))]
    return filtered[:MAX_RESULTS]


def build_related_files_context(file_path: str | None) -> str | None:
    if not file_path:
        return None

    resolved = Path(file_path).resolve()
    if not resolved.exists() or resolved.suffix.lower() not in _JS_TS_EXTS:
        return None

    project_root = find_project_root(str(resolved.parent))
    is_test = _is_test_file(resolved)
    logger.debug("file=%s is_test=%s project_root=%s", resolved, is_test, project_root)

    related: list[str] | None = None
    # Test -> source direction is unambiguous from the spec's own imports
    # (grep is exact); rag-rat's symbol-name query pulls in every consumer
    # of that name (controllers, DI containers, barrel files), not just what
    # this spec actually imports, so it's skipped here.
    if is_rag_rat_available(project_root) and not is_test:
        related = _rag_rat_for_source_file(resolved, project_root)
        if related:
            logger.debug("rag-rat related=%s", related)
        else:
            # Empty result can mean a genuinely uncovered file, or a
            # generic symbol name (e.g. "Role") that rag-rat's query
            # couldn't disambiguate. Fall back to grep to tell them apart.
            related = None

    if related is None:
        related = (
            _fallback_for_test_file(resolved, project_root)
            if is_test
            else _fallback_for_source_file(resolved, project_root)
        )
        logger.debug("fallback (rg) related=%s", related)

    if not related:
        return None

    rel_path = os.path.relpath(str(resolved), project_root)
    rel_related = [os.path.relpath(p, project_root) for p in related]
    if is_test:
        return f"Test file {rel_path} covers these source files: " + ", ".join(
            rel_related
        )
    return f"Source file {rel_path} is covered by these test files: " + ", ".join(
        rel_related
    )


def main() -> None:
    max_stdin = 1024 * 1024
    stdin_data = ""
    try:
        stdin_data = sys.stdin.read(max_stdin)
    except OSError:
        pass

    try:
        data = json.loads(stdin_data)
        tool_input = get_by_key(data, "tool_input")
        file_path = get_by_key(tool_input, "file_path") if tool_input else None
        context = build_related_files_context(file_path)
        if context:
            output = json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": context,
                    }
                }
            )
            logger.debug(f"[additionalContext]: {output}")
            print(output)
        else:
            logger.debug("No related-files context produced for %s", file_path)
    except (json.JSONDecodeError, AttributeError) as exc:
        logger.debug("Error parsing stdin: %s", exc)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("Error: %s", exc)
        sys.exit(0)
