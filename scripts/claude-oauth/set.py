#!/usr/bin/env python3

import json
import sys
from pathlib import Path

home_dir = Path.home()
CLAUDE_SETTINGS_PATH = home_dir / ".claude.json"


with open(
    home_dir / ".claude" / "oauthAccounts" / sys.argv[1],
) as f1:
    dataOauth = json.loads(f1.read())

with open(CLAUDE_SETTINGS_PATH) as f2:
    data = json.loads(f2.read())

data["oauthAccount"] = dataOauth

with open(CLAUDE_SETTINGS_PATH, "w") as f3:
    f3.write(json.dumps(data, indent=4))
