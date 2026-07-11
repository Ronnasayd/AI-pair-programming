#!/home/ronnas/develop/personal/AI-pair-programming/src/venv/bin/python3
"""
skill_loader_mcp.py

Fetches skill content from the AI-pair-programming GitHub repo so agents in
other projects can use a suggested skill even when it isn't present in the
current project's .claude/skills/ directory.
"""

import json
import urllib.request
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP

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

    try:
        content = _fetch_text(f"{_RAW_BASE}/{entry['skill_md']}")
    except Exception as e:
        return {"error": f"Failed to fetch skill content: {e}"}

    return {"name": name, "content": content, "files": entry.get("files", [])}


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

    if relpath not in entry.get("files", []):
        return {"error": f"'{relpath}' is not a listed file of skill '{name}'"}

    skill_dir = entry["skill_md"].rsplit("/", 1)[0]
    try:
        content = _fetch_text(f"{_RAW_BASE}/{skill_dir}/{relpath}")
    except Exception as e:
        return {"error": f"Failed to fetch file content: {e}"}

    return {"name": name, "relpath": relpath, "content": content}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
