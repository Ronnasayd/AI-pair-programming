#!/usr/bin/env python3
"""Single owner of ~/.claude/aipp-settings.json reads/writes/migration/seeding.

Storage shape:
    {"projects": {"<abs-path>": {"skills": {}, "agents": {}, "instructions": {}}}}

CLI subcommands (see design.md):
    ensure-migrated <local_path> <source_path>
    register-if-absent <project_path> <category> <name> <default: true|false>
    get <project_path> <category>
    sync-catalog <source_path>
"""

import argparse
import json
import os
from pathlib import Path
import sys

import yaml

SETTINGS_PATH = Path.home() / ".claude" / "aipp-settings.json"

CATEGORIES = ("skills", "agents", "instructions")


def load(path: Path = SETTINGS_PATH) -> dict:
    """Read the JSON, creating {"projects": {}} if missing.

    Args:
        path: Settings file to read. Defaults to ~/.claude/aipp-settings.json.

    Returns:
        The parsed settings dict, or {"projects": {}} if the file is missing.

    Raises:
        json.JSONDecodeError: If the file exists but contains malformed JSON.
    """
    if not path.exists():
        return {"projects": {}}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(data: dict, path: Path = SETTINGS_PATH) -> None:
    """Write data to path atomically (temp file + os.replace).

    Args:
        data: Full settings dict to persist.
        path: Settings file to write. Defaults to ~/.claude/aipp-settings.json.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def get_project(path: str, settings_path: Path = SETTINGS_PATH) -> dict:
    """Return path's project entry, creating it in-memory if absent.

    Caller must call save() with the loaded data to persist any new entry;
    get_project() itself never writes to disk.

    Args:
        path: Absolute project path used as the JSON key.
        settings_path: Settings file to read from.

    Returns:
        The project's {"skills": {}, "agents": {}, "instructions": {}} entry.
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

# why: static catalog under $SOURCE, immune to migrate_legacy_files() deleting a
# project's own .ignore files -- previously seed_from_source_defaults() re-parsed
# $SOURCE's live .ignore files, which self-destructed when $SOURCE == $LOCAL
DEFAULT_SETTINGS_FILENAME = "claude/aipp-default-settings.json"


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

    No-op if a JSON entry for local_path already exists, or if none of the three
    legacy files exist. On success, deletes the legacy files.

    Args:
        local_path: Absolute project path to migrate.
        settings_path: Settings file to read from and write to.

    Returns:
        True if migration ran and legacy files were deleted, False if it was a no-op.
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
            entry[category] = _parse_ignore_lines(
                file_path.read_text(encoding="utf-8").splitlines()
            )

    projects[local_path] = entry
    save(data, settings_path)

    for file_path in legacy_paths.values():
        if file_path.exists():
            file_path.unlink()

    return True


def seed_from_source_defaults(
    local_path: str, source_path: str, settings_path: Path = SETTINGS_PATH
) -> None:
    """Add items from source_path's default-settings catalog to local_path's entry.

    Only items not already present in local_path's JSON entry are added, using the
    catalog's enabled state as the default. source_path's catalog file
    (DEFAULT_SETTINGS_FILENAME) is read-only here -- it is the toolkit-wide default
    catalog, static and independent of any project's own .ignore files.

    Args:
        local_path: Absolute project path whose entry is seeded.
        source_path: Toolkit root path holding the default-settings catalog.
        settings_path: Settings file to read from and write to.
    """
    data = load(settings_path)
    projects = data.setdefault("projects", {})
    if local_path not in projects:
        projects[local_path] = {c: {} for c in CATEGORIES}
    entry = projects[local_path]
    for c in CATEGORIES:
        entry.setdefault(c, {})

    defaults_file = Path(source_path) / DEFAULT_SETTINGS_FILENAME
    if not defaults_file.exists():
        save(data, settings_path)
        return

    defaults = json.loads(defaults_file.read_text(encoding="utf-8"))
    for category in CATEGORIES:
        for name, enabled in defaults.get(category, {}).items():
            entry[category].setdefault(name, enabled)

    save(data, settings_path)


def ensure_migrated(
    local_path: str, source_path: str, settings_path: Path = SETTINGS_PATH
) -> None:
    """Migrate local_path's legacy files, if any, then seed from source_path's defaults.

    Single call install.sh makes: migration always runs first (idempotent, no-op
    if the entry already exists), then seeding fills in any items still missing.

    Args:
        local_path: Absolute project path to migrate and seed.
        source_path: Toolkit root path holding the default .ignore catalogs.
        settings_path: Settings file to read from and write to.
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
    """Add name under projects[project_path][category] only if not already a key.

    Args:
        project_path: Absolute project path used as the JSON key.
        category: One of "skills", "agents", "instructions".
        name: Item key to add.
        default: Value to set if name is absent; ignored if name already exists.
        settings_path: Settings file to read from and write to.
    """
    data = load(settings_path)
    projects = data.setdefault("projects", {})
    if project_path not in projects:
        projects[project_path] = {c: {} for c in CATEGORIES}
    entry = projects[project_path]
    entry.setdefault(category, {})
    entry[category].setdefault(name, default)
    save(data, settings_path)


def list_project_paths(settings_path: Path = SETTINGS_PATH) -> list:
    """Return every project path with an existing JSON entry.

    Args:
        settings_path: Settings file to read from.

    Returns:
        Absolute project paths currently keyed under "projects".
    """
    return list(load(settings_path).get("projects", {}).keys())


# where each category's index.yaml lives under $SOURCE, and what filename it
# writes under claude/ as the static default-settings catalog
_INDEX_YAML_PATHS = {
    "skills": "skills/index.yaml",
    "agents": "agents/index.yaml",
    "instructions": "instructions/index.yaml",
}


def _read_index_yaml_names(source_path: str, category: str) -> set:
    """Return the set of item names an index.yaml lists for one category."""
    index_file = Path(source_path) / _INDEX_YAML_PATHS[category]
    if not index_file.exists():
        return set()
    data = yaml.safe_load(index_file.read_text(encoding="utf-8")) or {}
    names = set()
    for entry in data.get(category, []) or []:
        entry_names = entry.get("name") or []
        for name in entry_names:
            if name:
                names.add(name)
    return names


def sync_catalog(source_path: str, settings_path: Path = SETTINGS_PATH) -> dict:
    """Add items only present in index.yaml to the catalog and every migrated project.

    Diffs each category's index.yaml (regenerated by list_skills_agents.py)
    against source_path's DEFAULT_SETTINGS_FILENAME catalog to find items new
    to the catalog (added there as False). Independently, every name on disk
    is also registered (via register_if_absent, a per-project no-op when the
    key already exists) on every project that already has a JSON entry in
    settings_path -- so a project migrated before an item entered the catalog
    still receives it, not just items new in this run. Never removes or
    re-enables anything.

    Args:
        source_path: Toolkit root path holding index.yaml files and the
            default-settings catalog.
        settings_path: Settings file whose existing projects get the new item.

    Returns:
        {"skills": [new catalog names], "agents": [...], "instructions": [...]}
    """
    defaults_file = Path(source_path) / DEFAULT_SETTINGS_FILENAME
    catalog = {}
    if defaults_file.exists():
        catalog = json.loads(defaults_file.read_text(encoding="utf-8"))
    for c in CATEGORIES:
        catalog.setdefault(c, {})

    new_items: dict = {c: [] for c in CATEGORIES}

    data = load(settings_path)
    projects = data.setdefault("projects", {})

    for category in CATEGORIES:
        on_disk = _read_index_yaml_names(source_path, category)
        new_names = sorted(on_disk - catalog[category].keys())
        for name in new_names:
            catalog[category][name] = False
            new_items[category].append(name)
        for name in on_disk:
            for entry in projects.values():
                entry.setdefault(category, {}).setdefault(name, False)

    save(data, settings_path)

    if any(new_items.values()):
        defaults_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = defaults_file.with_suffix(defaults_file.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, sort_keys=True)
        os.replace(tmp, defaults_file)

    return new_items


def set_item(
    project_path: str,
    category: str,
    name: str,
    enabled: bool,
    settings_path: Path = SETTINGS_PATH,
) -> None:
    """Set (create or overwrite) a single item's boolean value.

    Args:
        project_path: Absolute project path used as the JSON key.
        category: One of "skills", "agents", "instructions".
        name: Item key to set.
        enabled: Value to store.
        settings_path: Settings file to read from and write to.
    """
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

    p_sync = sub.add_parser(
        "sync-catalog",
        help="add index.yaml items missing from the catalog to it and to every project",
    )
    p_sync.add_argument("source_path")

    return parser


def main(argv: list | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Argument list to parse; defaults to sys.argv[1:] via argparse.

    Returns:
        Process exit code: 0 on success, 1 on malformed settings JSON.
    """
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
        elif args.command == "sync-catalog":
            new_items = sync_catalog(args.source_path)
            print(json.dumps(new_items))  # noqa: T201 -- CLI stdout output
    except json.JSONDecodeError as exc:
        print(  # noqa: T201 -- CLI stderr output
            f"error: malformed JSON in {SETTINGS_PATH}: {exc}", file=sys.stderr
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
