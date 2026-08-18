#!/usr/bin/python3
# log-tool-calls.py

import json
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("StartContext")

with open(os.path.join(script_dir, "..", "markdown/START.md")) as f:
    RULES = f.read()


def package_json(payload):
    cwd = get_by_key(payload, "cwd")
    package_json_path = os.path.join(cwd, "package.json")
    if not os.path.exists(package_json_path):
        return ""
    with open(package_json_path) as f:
        package_data = json.loads(f.read())
    scripts = package_data.get("scripts", {})
    if not scripts:
        return ""
    return "## package.json scripts\n\n" + "\n".join(
        f"- `{name}`: {cmd}" for name, cmd in scripts.items()
    )


KNOWN_CONFIG_FILES = [
    # TypeScript / JavaScript
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "tsconfig.json",
    ".eslintrc",
    ".eslintrc.json",
    ".eslintrc.js",
    ".eslintrc.yml",
    "eslint.config.js",
    "eslint.config.mjs",
    ".prettierrc",
    "prettier.config.js",
    "next.config.js",
    "next.config.ts",
    "vite.config.ts",
    "vite.config.js",
    "webpack.config.js",
    "rollup.config.js",
    "babel.config.js",
    ".babelrc",
    "jest.config.js",
    "vitest.config.ts",
    ".env",
    ".env.local",
    ".nvmrc",
    # Python
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "requirements-dev.txt",
    "Pipfile",
    "poetry.lock",
    "uv.lock",
    ".flake8",
    "tox.ini",
    "pytest.ini",
    ".python-version",
    # Go
    "go.mod",
    "go.sum",
    ".golangci.yml",
    # Common
    ".gitignore",
    ".editorconfig",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
]


def find_config_files(payload):
    cwd = get_by_key(payload, "cwd")
    if not cwd:
        return ""

    ignored_dirs = {".git", "node_modules", ".venv", "__pycache__"}
    glob_hits = []
    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for name in files:
            if "config" in name.lower():
                glob_hits.append(os.path.relpath(os.path.join(root, name), cwd))
    glob_hits.sort()

    known_hits = sorted(
        name for name in KNOWN_CONFIG_FILES
        if os.path.exists(os.path.join(cwd, name))
    )

    if not glob_hits and not known_hits:
        return ""

    lines = ["## Configuration files found"]
    if glob_hits:
        lines.append("\n### Matching `*config*`\n")
        lines.extend(f"- `{p}`" for p in glob_hits)
    if known_hits:
        lines.append("\n### Known config files\n")
        lines.extend(f"- `{p}`" for p in known_hits)
    return "\n".join(lines)


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # erro no parse não bloqueia nada
    additional_context = f"{RULES}"
    package_text = package_json(payload)
    if package_text:
        additional_context += f"\n\n{package_text}"
    config_text = find_config_files(payload)
    if config_text:
        additional_context += f"\n\n{config_text}"
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context,
        }
    }
    LOG.debug(f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}")
    print(json.dumps(output, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
