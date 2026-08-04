#!/usr/bin/env python3
import json
from pathlib import Path

home_dir = Path.home()
CLAUDE_SETTINGS_PATH = home_dir / ".claude.json"

with open(CLAUDE_SETTINGS_PATH) as f:
    data = json.loads(f.read())

with open(
    home_dir
    / ".claude"
    / "oauthAccounts"
    / f"{data['oauthAccount']['emailAddress']}.json",
    "w",
) as f:
    f.write(json.dumps(data["oauthAccount"], indent=4))
