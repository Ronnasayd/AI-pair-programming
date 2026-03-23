#!/usr/bin/env python3
# check_available_files.py

import os
import sys
import json
from pathlib import Path
from glob import glob


# ── Session-level file registry (in-process cache) ───────────────────────────
_SESSION_FILES: dict[str, str] = {}


def get_file(path: str) -> str:
    if path not in _SESSION_FILES:
        raise KeyError(
            f"'{path}' is not in the session registry. "
            "Was it available when check_available_files ran?"
        )
    return _SESSION_FILES[path]


def list_files() -> list[str]:
    return list(_SESSION_FILES.keys())


# ── File discovery ────────────────────────────────────────────────────────────
def check_documentation_files(workspace_root: str) -> dict:
    patterns = {
        "docs/agents/specs/":   "docs/agents/specs/**",
        "docs/agents/plans/":   "docs/agents/plans/**",
        "docs/agents/reviews/": "docs/agents/reviews/**",
        "docs/adr/":            "docs/adr/**",
        "docs/techs/":          "docs/techs/**",
        "docs/misc/":           "docs/misc/**",
        "docs/architecture.md": "docs/architecture.md",
        "docs/setup.md":        "docs/setup.md",
        "docs/usage.md":        "docs/usage.md",
        "docs/modules.md":      "docs/modules.md",
        "docs/contribution.md": "docs/contribution.md",
        "docs/faq.md":          "docs/faq.md",
        "docs/SUMMARY.md":      "docs/SUMMARY.md",
        ".taskmaster/tasks/":   ".taskmaster/tasks/tasks.json",
        ".taskmaster/prds/":    ".taskmaster/prds/*.md",
        ".taskmaster/tasksmd/":   ".taskmaster/tasks/*.md",
        "README.md":            "README.md",
        "GEMINI.md":            "GEMINI.md",
        "CLAUDE.md":            "CLAUDE.md",
    }

    available_files: dict = {}
    root_path = Path(workspace_root) if workspace_root else Path.cwd()

    for name, pattern in patterns.items():
        if "*" in pattern:
            matches = glob(str(root_path / pattern), recursive=True)
            available_files[name] = {
                "exists": len(matches) > 0,
                "count":  len(matches),
                "files":  matches[:10],
            }
        else:
            file_path = root_path / pattern
            available_files[name] = {
                "exists": file_path.exists(),
                "path":   str(file_path),
            }

    return available_files


# ── File loader ───────────────────────────────────────────────────────────────
def _load_into_registry(available_files: dict) -> None:
    global _SESSION_FILES

    for name, info in available_files.items():
        if not info.get("exists"):
            continue

        if "files" in info:
            for raw_path in info["files"]:
                path = Path(raw_path)
                if path.is_file():
                    _read_and_store(path)
        elif "path" in info:
            path = Path(info["path"])
            if path.is_file():
                _read_and_store(path)


def _read_and_store(path: Path) -> None:
    global _SESSION_FILES
    key = str(path)
    if key in _SESSION_FILES:
        return
    try:
        _SESSION_FILES[key] = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError, OSError):
        pass


# ── Markdown builder ──────────────────────────────────────────────────────────
def _build_markdown(available: dict) -> str:
    lines = ["---", 
             "description: List relevant doc files in repository. read the content of these files and make them available for agents to use if necessary.", 
             "applyTo: \"**/*\"", 
             "---", 
             "# Available Files\n"]

    for name, info in available.items():
        if "files" in info:
            for f in info["files"]:
                if os.path.isfile(f):
                    lines.append(f"- `{f}`")
        elif "path" in info:
            if os.path.isfile(name):
                lines.append(f"- `{name}`")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    try:
        payload        = json.load(sys.stdin)
        workspace_root = payload.get("workspace_root", ".")

        available_files = check_documentation_files(workspace_root)
        _load_into_registry(available_files)

        available = {
            name: info for name, info in available_files.items()
            if info.get("exists")
        }

        markdown = _build_markdown(available)

        # For github copilot, we can write the markdown to a file in the repository so it can be easily accessed by agents. 
        output_path = Path(".github/instructions/available_files.instructions.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        # For gemini, we can output the markdown directly in the hook output so it can be accessed by agents in the same session.
        print(json.dumps({"hookSpecificOutput":{"additionalContext": markdown}}))

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
