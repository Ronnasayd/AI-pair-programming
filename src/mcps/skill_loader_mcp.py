#!/home/ronnas/develop/personal/AI-pair-programming/src/venv/bin/python3
"""
skill_loader_mcp.py

Fetches skill content from the AI-pair-programming GitHub repo so agents in
other projects can use a suggested skill even when it isn't present in the
current project's .claude/skills/ directory.
"""

import json
import os
import urllib.request
from typing import Any, Dict

from fastmcp import FastMCP

mcp = FastMCP(name="skill_loader")

_RAW_BASE = (
    "https://raw.githubusercontent.com/Ronnasayd/AI-pair-programming/master/skills"
)


def _fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8")


def _fetch_manifest() -> Dict[str, Dict[str, Any]]:
    return json.loads(_fetch_text(f"{_RAW_BASE}/manifest.json"))


@mcp.tool()
def list_remote_skills() -> Dict[str, Any]:
    """
    List all skill names available in the AI-pair-programming GitHub repo,
    mapped to their relative path under skills/.
    """
    try:
        return {"skills": _fetch_manifest()}
    except Exception as e:
        return {"error": f"Failed to fetch manifest: {e}"}


@mcp.tool()
def get_remote_skill(name: str) -> Dict[str, Any]:
    """
    Fetch a skill's SKILL.md content by name from the AI-pair-programming
    GitHub repo, for use when the skill isn't present in the current project.

    The response also lists `files`: relative paths of scripts/references
    adjacent to SKILL.md in the skill's directory. Fetch any of them with
    get_remote_skill_file(name, relpath) if SKILL.md references them.
    """
    try:
        manifest = _fetch_manifest()
    except Exception as e:
        return {"error": f"Failed to fetch manifest: {e}"}

    entry = manifest.get(name)
    if not entry:
        return {"error": f"Skill '{name}' not found in manifest"}

    skill_md = entry["skill_md"] if isinstance(entry, dict) else entry
    files = entry.get("files", []) if isinstance(entry, dict) else []

    try:
        content = _fetch_text(f"{_RAW_BASE}/{skill_md}")
    except Exception as e:
        return {"error": f"Failed to fetch skill content: {e}"}

    return {"name": name, "content": content, "files": files}


@mcp.tool()
def get_remote_skill_file(name: str, relpath: str) -> Dict[str, Any]:
    """
    Fetch one adjacent file (script or reference) for a remote skill by its
    relative path, as listed in `files` from get_remote_skill(name).
    """
    try:
        manifest = _fetch_manifest()
    except Exception as e:
        return {"error": f"Failed to fetch manifest: {e}"}

    entry = manifest.get(name)
    if not entry:
        return {"error": f"Skill '{name}' not found in manifest"}

    files = entry.get("files", []) if isinstance(entry, dict) else []
    if relpath not in files:
        return {"error": f"'{relpath}' is not a listed file of skill '{name}'"}

    skill_md = entry["skill_md"] if isinstance(entry, dict) else entry
    skill_dir = skill_md.rsplit("/", 1)[0]
    try:
        content = _fetch_text(f"{_RAW_BASE}/{skill_dir}/{relpath}")
    except Exception as e:
        return {"error": f"Failed to fetch file content: {e}"}

    return {"name": name, "relpath": relpath, "content": content}


@mcp.tool()
def download_remote_skill(
    name: str, dest_dir: str = ".claude/skills"
) -> Dict[str, Any]:
    """
    Download a skill (SKILL.md + all adjacent files) from the
    AI-pair-programming GitHub repo and save to disk under
    `<dest_dir>/<name>/`. Use this instead of get_remote_skill +
    get_remote_skill_file when the skill has many auxiliary files — one
    call writes everything locally, no per-file MCP round trips.
    """
    try:
        manifest = _fetch_manifest()
    except Exception as e:
        return {"error": f"Failed to fetch manifest: {e}"}

    entry = manifest.get(name)
    if not entry:
        return {"error": f"Skill '{name}' not found in manifest"}

    skill_md = entry["skill_md"] if isinstance(entry, dict) else entry
    files = entry.get("files", []) if isinstance(entry, dict) else []
    skill_dir = skill_md.rsplit("/", 1)[0]

    target_dir = os.path.join(dest_dir, name)
    os.makedirs(target_dir, exist_ok=True)

    saved = []
    errors = []

    try:
        content = _fetch_text(f"{_RAW_BASE}/{skill_md}")
        skill_md_path = os.path.join(target_dir, "SKILL.md")
        with open(skill_md_path, "w", encoding="utf-8") as f:
            f.write(content)
        saved.append(skill_md_path)
    except Exception as e:
        return {"error": f"Failed to fetch/save SKILL.md: {e}"}

    for relpath in files:
        try:
            content = _fetch_text(f"{_RAW_BASE}/{skill_dir}/{relpath}")
            file_path = os.path.join(target_dir, relpath)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            saved.append(file_path)
        except Exception as e:
            errors.append(f"{relpath}: {e}")

    result = {"name": name, "dir": target_dir, "saved": saved}
    if errors:
        result["errors"] = errors
    return result


def main():
    mcp.run()


if __name__ == "__main__":
    main()
