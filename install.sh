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

$SOURCE/scripts/copilot.install.sh
# $SOURCE/scripts/claude.install.sh
# $SOURCE/scripts/codex.install.sh
$SOURCE/scripts/gemini.install.sh
$SOURCE/scripts/taskmaster.install.sh
$SOURCE/scripts/gitignore.install.sh



###########################################################################################




