#!/usr/bin/env python3

import argparse
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
    "figma",
    "github-L",
    "github",
    "tokensave",
    "ai-memory",
    "omniroute",
    "iconify",
    "notebooklm",
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

cwd = os.getcwd()
if cwd not in config["projects"]:
    print(f"error: {cwd} not found in {config_path} projects", file=sys.stderr)
    sys.exit(1)

config["projects"][cwd]["disabledMcpServers"] = disabled_mcp_servers

with open(config_path, "w") as f:
    json.dump(config, f, indent=4)

print(f"disabled {len(disabled_mcp_servers)} mcp servers for {cwd}")
