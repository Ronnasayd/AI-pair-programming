#!/usr/bin/env bash
SOURCE="/home/ronnas/develop/personal/AI-pair-programming"
LOCAL="$(pwd)"

# echo $SOURCE
# echo $LOCAL

# Installs for gemini
if [ -L "$HOME/.gemini/commands/" ] || [ -d "$HOME/.gemini/commands/" ]; then
rm -rf $HOME/.gemini/commands/
fi
mkdir -p $HOME/.gemini/commands
ln -s "$SOURCE/gemini/commands/"* "$HOME/.gemini/commands/"

# Installs for github
if [ -L "$LOCAL/.github/skills/" ] || [ -d "$LOCAL/.github/skills/" ]; then
rm -rf $LOCAL/.github/skills/
fi
mkdir -p $LOCAL/.github/skills/
ln -s "$SOURCE/skills/"* "$LOCAL/.github/skills/"



if [ -L "$LOCAL/.github/instructions/copilot.instructions.md" ] || [ -f "$LOCAL/.github/instructions/copilot.instructions.md" ]; then
rm -rf $LOCAL/.github/instructions/copilot.instructions.md
fi
mkdir -p $LOCAL/.github/instructions/
ln -s "$SOURCE/instructions/copilot.instructions.md" "$LOCAL/.github/instructions/copilot.instructions.md"
