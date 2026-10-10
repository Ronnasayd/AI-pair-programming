#!$AI_PROJECT_ROOT_DIR/src/venv/bin/python3
"""Fetch skill content from the aipp GitHub repo.

So agents in other projects can use a suggested skill even when it isn't
present in the current project's .claude/skills/ directory.
"""

import json
import os
from typing import Any
import urllib.request

# pylint: disable=import-error
from fastmcp import FastMCP  # type: ignore[import-not-found]

# pylint: enable=import-error

mcp = FastMCP(name="skill_loader")

_RAW_BASE = "https://raw.githubusercontent.com/Ronnasayd/aipp/master/skills"


def _fetch_text(url: str) -> str:
    """Fetch `url` over HTTPS and return its body decoded as UTF-8.

    Args:
        url: HTTPS URL to fetch.

    Returns:
        The response body as text.
    """
    with urllib.request.urlopen(url, timeout=10) as response:  # noqa: S310
        return response.read().decode("utf-8")


def _fetch_manifest() -> dict[str, dict[str, Any]]:
    """Fetch and parse the skills manifest.json from the GitHub repo.

    Returns:
        The manifest mapping skill name to its metadata.
    """
    return json.loads(_fetch_text(f"{_RAW_BASE}/manifest.json"))


def _resolve_skill(
    manifest: dict[str, dict[str, Any]], name: str
) -> tuple[str, list[str]] | None:
    """Look up `name` in `manifest` and return its (skill_md path, files).

    Args:
        manifest: the parsed skills manifest.
        name: skill name to look up.

    Returns:
        A `(skill_md, files)` tuple, or None if `name` isn't in the manifest.
    """
    entry = manifest.get(name)
    if not entry:
        return None
    skill_md = entry["skill_md"] if isinstance(entry, dict) else entry
    files = entry.get("files", []) if isinstance(entry, dict) else []
    return skill_md, files


@mcp.tool()
def list_remote_skills() -> dict[str, Any]:
    """List all skill names available in the aipp GitHub repo.

    Returns:
        `{"skills": manifest}` or `{"error": message}` on failure.
    """
    try:
        return {"skills": _fetch_manifest()}
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"error": f"Failed to fetch manifest: {e}"}


@mcp.tool()
def get_remote_skill(name: str) -> dict[str, Any]:
    """Fetch a skill's SKILL.md content by name from the GitHub repo.

    For use when the skill isn't present in the current project. The
    response also lists `files`: relative paths of scripts/references
    adjacent to SKILL.md in the skill's directory. Fetch any of them with
    get_remote_skill_file(name, relpath) if SKILL.md references them.

    Args:
        name: skill name, as listed by list_remote_skills().

    Returns:
        `{"name", "content", "files"}` or `{"error": message}` on failure.
    """
    try:
        manifest = _fetch_manifest()
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"error": f"Failed to fetch manifest: {e}"}

    resolved = _resolve_skill(manifest, name)
    if resolved is None:
        return {"error": f"Skill '{name}' not found in manifest"}
    skill_md, files = resolved

    try:
        content = _fetch_text(f"{_RAW_BASE}/{skill_md}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"error": f"Failed to fetch skill content: {e}"}

    return {"name": name, "content": content, "files": files}


@mcp.tool()
def get_remote_skill_file(name: str, relpath: str) -> dict[str, Any]:
    """Fetch one adjacent file (script or reference) for a remote skill.

    Args:
        name: skill name, as listed by list_remote_skills().
        relpath: file's relative path, as listed in `files` from
            get_remote_skill(name).

    Returns:
        `{"name", "relpath", "content"}` or `{"error": message}` on failure.
    """
    try:
        manifest = _fetch_manifest()
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"error": f"Failed to fetch manifest: {e}"}

    resolved = _resolve_skill(manifest, name)
    if resolved is None:
        return {"error": f"Skill '{name}' not found in manifest"}
    skill_md, files = resolved
    if relpath not in files:
        return {"error": f"'{relpath}' is not a listed file of skill '{name}'"}

    skill_dir = skill_md.rsplit("/", 1)[0]
    try:
        content = _fetch_text(f"{_RAW_BASE}/{skill_dir}/{relpath}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"error": f"Failed to fetch file content: {e}"}

    return {"name": name, "relpath": relpath, "content": content}


def _save_skill_md(skill_md: str, target_dir: str) -> str:
    """Fetch and save a skill's SKILL.md into `target_dir`; return its path."""
    content = _fetch_text(f"{_RAW_BASE}/{skill_md}")
    skill_md_path = os.path.join(target_dir, "SKILL.md")
    with open(skill_md_path, "w", encoding="utf-8") as f:
        f.write(content)
    return skill_md_path


def _save_skill_files(
    skill_dir: str, files: list[str], target_dir: str
) -> tuple[list[str], list[str]]:
    """Fetch and save each adjacent file; return (saved paths, error messages)."""
    saved = []
    errors = []
    for relpath in files:
        try:
            content = _fetch_text(f"{_RAW_BASE}/{skill_dir}/{relpath}")
            file_path = os.path.join(target_dir, relpath)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            saved.append(file_path)
        except Exception as e:  # pylint: disable=broad-exception-caught
            errors.append(f"{relpath}: {e}")
    return saved, errors


@mcp.tool()
def download_remote_skill(
    name: str, dest_dir: str = ".claude/skills"
) -> dict[str, Any]:
    """Download a skill (SKILL.md + all adjacent files) to disk.

    Saves under `<dest_dir>/<name>/`. Use this instead of get_remote_skill +
    get_remote_skill_file when the skill has many auxiliary files — one
    call writes everything locally, no per-file MCP round trips.

    Args:
        name: skill name, as listed by list_remote_skills().
        dest_dir: local directory to save the skill under.

    Returns:
        `{"name", "dir", "saved", "errors"?}` or `{"error": message}`.
    """
    try:
        manifest = _fetch_manifest()
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"error": f"Failed to fetch manifest: {e}"}

    resolved = _resolve_skill(manifest, name)
    if resolved is None:
        return {"error": f"Skill '{name}' not found in manifest"}
    skill_md, files = resolved
    skill_dir = skill_md.rsplit("/", 1)[0]

    target_dir = os.path.join(dest_dir, name)
    os.makedirs(target_dir, exist_ok=True)

    try:
        skill_md_path = _save_skill_md(skill_md, target_dir)
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"error": f"Failed to fetch/save SKILL.md: {e}"}

    saved, errors = _save_skill_files(skill_dir, files, target_dir)
    saved.insert(0, skill_md_path)

    result: dict[str, Any] = {"name": name, "dir": target_dir, "saved": saved}
    if errors:
        result["errors"] = errors
    return result


def main() -> None:
    """Run the skill_loader MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
