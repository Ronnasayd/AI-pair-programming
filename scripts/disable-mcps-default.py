#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path

disabled_mcp_servers = [
    "sqlite",
    "canva",
    "atlassian",
    "mongodb",
    "postgresql",
    "mysql",
    "keycloak",
    "gcloud",
    "claude.ai Canva",
    "claude.ai Google Drive",
    "claude.ai Google Calendar",
    "claude.ai Gmail",
    "expo",
    "caveman-shrink",
    "mobile-mcp",
    "context7",
    "figma",
    "github-L",
    "tokensave",
    "ai-memory",
]

config_path = Path.home() / ".claude.json"

with open(config_path, "r") as f:
    config = json.load(f)

cwd = os.getcwd()
if cwd not in config["projects"]:
    print(f"error: {cwd} not found in {config_path} projects", file=sys.stderr)
    sys.exit(1)

config["projects"][cwd]["disabledMcpServers"] = disabled_mcp_servers

with open(config_path, "w") as f:
    json.dump(config, f, indent=4)

print(f"disabled {len(disabled_mcp_servers)} mcp servers for {cwd}")
