#!/usr/bin/env python3
"""Set the default disabledMcpServers list for every project in $CLAUDE_CONFIG_DIR/.claude.json."""

import argparse
import json
import os
from pathlib import Path
import sys

disabled_mcp_servers = [
    "aipp:sqlite",
    "aipp:canva",
    "aipp:atlassian",
    "aipp:mongodb",
    "aipp:postgresql",
    "aipp:mysql",
    "aipp:keycloak",
    "claude.ai Canva",
    "claude.ai Google Drive",
    "claude.ai Google Calendar",
    "claude.ai Claude Docs",
    "claude.ai Gmail",
    "caveman-shrink",
    "aipp:figma",
    "aipp:github",
    "aipp:omniroute",
    "aipp:ssh-mcp",
    "aipp:notion",
    "aipp:vrep",
    "aipp:laya",
    "aipp:krita",
]

parser = argparse.ArgumentParser()
CONFIG_DIR = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))

parser.add_argument(
    "config_path",
    nargs="?",
    default=str(CONFIG_DIR / ".claude.json"),
    help="path to claude config json (default: $CLAUDE_CONFIG_DIR/.claude.json)",
)
args = parser.parse_args()
config_path = Path(args.config_path)

with open(config_path, encoding="utf-8") as f:
    config = json.load(f)

projects = config.get("projects", {})
for project_path in projects:
    projects[project_path]["disabledMcpServers"] = disabled_mcp_servers

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4)

sys.stdout.write(
    f"disabled {len(disabled_mcp_servers)} mcp servers for {len(projects)} projects\n"
)
