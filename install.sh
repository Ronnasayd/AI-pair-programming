#!/usr/bin/env bash
export SOURCE="/home/ronnas/develop/personal/AI-pair-programming"
export LOCAL="$(pwd)"

# echo $SOURCE
# echo $LOCAL
chmod -R +x $SOURCE/hooks/scripts
python3 $SOURCE/converter.py $SOURCE/gemini/commands/  $SOURCE/github/prompts/

$SOURCE/scripts/copilot.install.sh
$SOURCE/scripts/codex.install.sh
$SOURCE/scripts/gemini.install.sh
$SOURCE/scripts/taskmaster.install.sh






