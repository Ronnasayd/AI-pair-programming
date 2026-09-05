#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

disabled_mcp_servers = [
    "sqlite",
    "canva",
    "atlassian",
    "mongodb",
    "postgresql",
    "mysql",
    "keycloak",
    "claude.ai Canva",
    "claude.ai Google Drive",
    "claude.ai Google Calendar",
    "claude.ai Gmail",
    "caveman-shrink",
    "figma",
    "github-L",
    "github",
]

parser = argparse.ArgumentParser()
parser.add_argument(
    "config_path",
    nargs="?",
    default=str(Path.home() / ".claude.json"),
    help="path to claude config json (default: ~/.claude.json)",
)
args = parser.parse_args()
config_path = Path(args.config_path)

with open(config_path, "r") as f:
    config = json.load(f)

projects = config.get("projects", {})
for project_path in projects:
    projects[project_path]["disabledMcpServers"] = disabled_mcp_servers

with open(config_path, "w") as f:
    json.dump(config, f, indent=4)

print(f"disabled {len(disabled_mcp_servers)} mcp servers for {len(projects)} projects")
