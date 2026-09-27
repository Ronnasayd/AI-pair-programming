#!/usr/bin/env python3
"""Single owner of ~/.claude/aipp-settings.json reads/writes/migration/seeding.

Storage shape:
    {"projects": {"<abs-path>": {"skills": {}, "agents": {}, "instructions": {}}}}

CLI subcommands (see design.md):
    ensure-migrated <local_path> <source_path>
    register-if-absent <project_path> <category> <name> <default: true|false>
    get <project_path> <category>
"""

import argparse
import json
import os
from pathlib import Path
import sys

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


# why: maps legacy .ignore filenames to the JSON category key they migrate into
LEGACY_FILES = {
    ".skillsignore": "skills",
    ".agentsignore": "agents",
    ".rulesignore": "instructions",
}


def _parse_ignore_lines(lines: list) -> dict:
    """Parse one legacy .ignore file's lines into {name: enabled}.

    Ported from manage-ignore-files.py::parse_ignore_file semantics:
    - blank line: skipped
    - line starting with "##" (section header, e.g. "#### Section ####"): skipped
    - line starting with a single "#": enabled (name = text after stripping "#")
    - any other non-blank line: disabled (name = stripped text)
    """
    items = {}
    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("##"):
            continue
        if stripped.startswith("#"):
            name = stripped.lstrip("#").strip()
            if name:
                items[name] = True
        else:
            items[stripped] = False
    return items


def migrate_legacy_files(local_path: str, settings_path: Path = SETTINGS_PATH) -> bool:
    """Migrate local_path's legacy .ignore files into its JSON project entry.

    No-op (returns False) if a JSON entry for local_path already exists, or if none of
    the three legacy files exist. On success, deletes the legacy files and returns True.
    """
    data = load(settings_path)
    projects = data.setdefault("projects", {})
    if local_path in projects:
        return False

    local = Path(local_path)
    legacy_paths = {name: local / name for name in LEGACY_FILES}
    if not any(p.exists() for p in legacy_paths.values()):
        return False

    entry: dict = {c: {} for c in CATEGORIES}
    for filename, category in LEGACY_FILES.items():
        file_path = legacy_paths[filename]
        if file_path.exists():
            entry[category] = _parse_ignore_lines(file_path.read_text().splitlines())

    projects[local_path] = entry
    save(data, settings_path)

    for file_path in legacy_paths.values():
        if file_path.exists():
            file_path.unlink()

    return True


def seed_from_source_defaults(
    local_path: str, source_path: str, settings_path: Path = SETTINGS_PATH
) -> None:
    """Add items from source_path's legacy .ignore files to local_path's entry.

    Only items not already present in local_path's JSON entry are added, using the
    source file's enabled state as the default. source_path's legacy files are read-only
    here (never deleted) -- they remain the toolkit-wide default catalog.
    """
    data = load(settings_path)
    projects = data.setdefault("projects", {})
    if local_path not in projects:
        projects[local_path] = {c: {} for c in CATEGORIES}
    entry = projects[local_path]
    for c in CATEGORIES:
        entry.setdefault(c, {})

    source = Path(source_path)
    for filename, category in LEGACY_FILES.items():
        file_path = source / filename
        if not file_path.exists():
            continue
        defaults = _parse_ignore_lines(file_path.read_text().splitlines())
        for name, enabled in defaults.items():
            entry[category].setdefault(name, enabled)

    save(data, settings_path)


def ensure_migrated(
    local_path: str, source_path: str, settings_path: Path = SETTINGS_PATH
) -> None:
    """Migrate local_path's legacy files, if any, then seed from source_path's defaults.

    Single call install.sh makes: migration always runs first (idempotent, no-op
    if the entry already exists), then seeding fills in any items still missing.
    """
    migrate_legacy_files(local_path, settings_path)
    seed_from_source_defaults(local_path, source_path, settings_path)


def register_if_absent(
    project_path: str,
    category: str,
    name: str,
    default: bool,
    settings_path: Path = SETTINGS_PATH,
) -> None:
    """Add name under projects[project_path][category] only if not already a key."""
    data = load(settings_path)
    projects = data.setdefault("projects", {})
    if project_path not in projects:
        projects[project_path] = {c: {} for c in CATEGORIES}
    entry = projects[project_path]
    entry.setdefault(category, {})
    entry[category].setdefault(name, default)
    save(data, settings_path)


def set_item(
    project_path: str,
    category: str,
    name: str,
    enabled: bool,
    settings_path: Path = SETTINGS_PATH,
) -> None:
    """Set (create or overwrite) a single item's boolean value."""
    data = load(settings_path)
    projects = data.setdefault("projects", {})
    if project_path not in projects:
        projects[project_path] = {c: {} for c in CATEGORIES}
    entry = projects[project_path]
    entry.setdefault(category, {})
    entry[category][name] = enabled
    save(data, settings_path)


def _str2bool(value: str) -> bool:
    """Parse a CLI boolean argument (true/false/1/0/yes/no, case-insensitive)."""
    if value.lower() in ("true", "1", "yes"):
        return True
    if value.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(f"expected true/false, got: {value!r}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aipp_settings.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_ensure = sub.add_parser(
        "ensure-migrated", help="migrate legacy files, then seed from source"
    )
    p_ensure.add_argument("local_path")
    p_ensure.add_argument("source_path")

    p_register = sub.add_parser(
        "register-if-absent", help="add name under project/category only if absent"
    )
    p_register.add_argument("project_path")
    p_register.add_argument("category", choices=CATEGORIES)
    p_register.add_argument("name")
    p_register.add_argument("default", type=_str2bool)

    p_get = sub.add_parser("get", help="print a project's category as JSON")
    p_get.add_argument("project_path")
    p_get.add_argument("category", choices=CATEGORIES)

    return parser


def main(argv: list | None = None) -> int:
    """CLI entry point. Returns the process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "ensure-migrated":
            ensure_migrated(args.local_path, args.source_path)
        elif args.command == "register-if-absent":
            register_if_absent(
                args.project_path, args.category, args.name, args.default
            )
        elif args.command == "get":
            entry = get_project(args.project_path)
            print(json.dumps(entry[args.category]))  # noqa: T201 -- CLI stdout output
    except json.JSONDecodeError as exc:
        print(  # noqa: T201 -- CLI stderr output
            f"error: malformed JSON in {SETTINGS_PATH}: {exc}", file=sys.stderr
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
