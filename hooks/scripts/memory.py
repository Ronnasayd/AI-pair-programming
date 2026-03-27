#!/usr/bin/env python3
# check_available_files.py

import os
import sys
import json
import subprocess
from pathlib import Path
from glob import glob

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_hooks_logger

logger = get_hooks_logger("Memory")


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
        "docs/agents/specs/": "docs/agents/specs/**",
        "docs/agents/plans/": "docs/agents/plans/**",
        "docs/agents/reviews/": "docs/agents/reviews/**",
        "docs/adr/": "docs/adr/**",
        "docs/techs/": "docs/techs/**",
        "docs/misc/": "docs/misc/**",
        "docs/features/": "docs/features/**",
        "docs/architecture.md": "docs/architecture.md",
        "docs/setup.md": "docs/setup.md",
        "docs/usage.md": "docs/usage.md",
        "docs/modules.md": "docs/modules.md",
        "docs/contribution.md": "docs/contribution.md",
        "docs/faq.md": "docs/faq.md",
        "docs/SUMMARY.md": "docs/SUMMARY.md",
        ".taskmaster/tasks/": ".taskmaster/tasks/*.json",
        ".taskmaster/prds/": ".taskmaster/prds/*.md",
        ".taskmaster/tasksmd/": ".taskmaster/tasks/*.md",
        "README.md": "README.md",
        "GEMINI.md": "GEMINI.md",
        "CLAUDE.md": "CLAUDE.md",
    }

    available_files: dict = {}
    root_path = Path(workspace_root) if workspace_root else Path.cwd()

    for name, pattern in patterns.items():
        if "*" in pattern:
            matches = glob(str(root_path / pattern), recursive=True)
            available_files[name] = {
                "exists": len(matches) > 0,
                "count": len(matches),
                "files": matches[:10],
            }
        else:
            file_path = root_path / pattern
            available_files[name] = {
                "exists": file_path.exists(),
                "path": str(file_path),
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
    lines = []

    for name, info in available.items():
        if "files" in info:
            for f in info["files"]:
                if os.path.isfile(f):
                    lines.append(f"- `{f}`")
        elif "path" in info:
            if os.path.isfile(name):
                lines.append(f"- `{name}`")

    return "\n".join(lines)


# ── Git diff files ────────────────────────────────────────────────────────────
def get_diff_files(workspace_root: str = ".") -> str:
    """Get list of modified files using git diff.

    Tries main..HEAD first, falls back to master..HEAD if main doesn't exist.
    Returns markdown formatted list or empty string if no changes or git fails.
    """
    try:
        os.chdir(workspace_root)

        # Try main..HEAD first
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "main..HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                files = result.stdout.strip().split("\n")
                return "\n".join(f"- `{f}`" for f in files if f)
        except Exception:
            pass

        # Fall back to master..HEAD
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "master..HEAD"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                files = result.stdout.strip().split("\n")
                return "\n".join(f"- `{f}`" for f in files if f)
        except Exception:
            pass

        return ""
    except Exception:
        return ""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        workspace_root = payload.get("cwd", ".")

        markdown_doc_files = make_doc_files(workspace_root)
        diff_files = get_diff_files(workspace_root)
        list_of_files = [f for f in glob(f".sessions/*.*") if os.path.isfile(f)]
        latest_created_file = max(list_of_files, key=os.path.getctime)
        latest_session = open(latest_created_file).read()

        diff_section = ""
        if diff_files:
            diff_section = f"\n\n# [SessionStart] Diff files:\n{diff_files}"

        result = f"""---
description: \"Provide useful memory for agents, such as relevant documentation files in the repository and the latest session information.\"
applyTo: \"**/*\"
---
# [SessionStart] Reference Documentation Files:
{markdown_doc_files}{diff_section}

# [SessionStart] Found:
{len(list_of_files)} session files found at .sessions/.

# [SessionStart] Latest:
```markdown
{latest_session}
```
"""

        # For github copilot, we can write the markdown to a file in the repository so it can be easily accessed by agents.
        output_path = Path(".github/instructions/memory.instructions.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding="utf-8")
        # For gemini, we can output the markdown directly in the hook output so it can be accessed by agents in the same session.
        print(json.dumps({"hookSpecificOutput": {"additionalContext": result}}))
        logger.debug(json.dumps({"hookSpecificOutput": {"additionalContext": result}}))
        logger.debug("Memory hook executed successfully.")

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)

    sys.exit(0)


def make_doc_files(workspace_root):
    available_files = check_documentation_files(workspace_root)
    _load_into_registry(available_files)

    available = {
        name: info for name, info in available_files.items() if info.get("exists")
    }

    markdown = _build_markdown(available)
    return markdown


if __name__ == "__main__":
    main()
