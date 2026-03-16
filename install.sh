#!/usr/bin/env bash

SCRIPT_FILE="${BASH_SOURCE[0]}"
if [ -L "$SCRIPT_FILE" ]; then
  SCRIPT_FILE="$(readlink -f "$SCRIPT_FILE")"
fi
export SOURCE="$(dirname "$SCRIPT_FILE")"
export LOCAL="$(pwd)"
# echo $SOURCE
# echo $LOCAL
chmod -R +x $SOURCE/hooks/scripts
python3 $SOURCE/toml2md.py $SOURCE/gemini/commands/  $SOURCE/github/prompts/


$SOURCE/scripts/copilot.install.sh
# $SOURCE/scripts/codex.install.sh
$SOURCE/scripts/gemini.install.sh
$SOURCE/scripts/taskmaster.install.sh

## GITIGNORE
if ! grep -q "docs/agents/" .gitignore; then
    echo "docs/agents/" >> .gitignore
fi
###########################################################################################




