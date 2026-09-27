#!/usr/bin/env python3
"""Single owner of ~/.claude/aipp-settings.json reads/writes/migration/seeding.

Storage shape:
    {"projects": {"<abs-path>": {"skills": {}, "agents": {}, "instructions": {}}}}

CLI subcommands (see design.md):
    ensure-migrated <local_path> <source_path>
    register-if-absent <project_path> <category> <name> <default: true|false>
    get <project_path> <category>
"""

import json
import os
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "aipp-settings.json"

CATEGORIES = ("skills", "agents", "instructions")


def load(path: Path = SETTINGS_PATH) -> dict:
    """Read the JSON, creating {"projects": {}} if missing.

    Raises json.JSONDecodeError on malformed content.
    """
    if not path.exists():
        return {"projects": {}}
    with open(path) as f:
        return json.load(f)


def save(data: dict, path: Path = SETTINGS_PATH) -> None:
    """Atomic write: temp file + os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def get_project(path: str, settings_path: Path = SETTINGS_PATH) -> dict:
    """Return path's project entry, creating it in-memory (loaded, not saved) if absent.

    Caller must call save() with the loaded data to persist any new entry.
    """
    data = load(settings_path)
    projects = data.setdefault("projects", {})
    if path not in projects:
        projects[path] = {c: {} for c in CATEGORIES}
    entry = projects[path]
    for c in CATEGORIES:
        entry.setdefault(c, {})
    return entry
