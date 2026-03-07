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
#######################################################################################
if [ -L "$HOME/.gemini/skills/" ] || [ -d "$HOME/.gemini/skills/" ]; then
rm -rf $HOME/.gemini/skills/
fi
mkdir -p $HOME/.gemini/skills
ln -s "$SOURCE/skills/"* "$HOME/.gemini/skills/"
########################################################################################
# Installs for github
if [ -L "$LOCAL/.github/skills/" ] || [ -d "$LOCAL/.github/skills/" ]; then
rm -rf $LOCAL/.github/skills/
fi
mkdir -p $LOCAL/.github/skills/
ln -s "$SOURCE/skills/"* "$LOCAL/.github/skills/"
########################################################################################
if [ -L "$LOCAL/.github/prompts/" ] || [ -d "$LOCAL/.github/prompts/" ]; then
rm -rf $LOCAL/.github/prompts/
fi
mkdir -p $LOCAL/.github/prompts/
ln -s "$SOURCE/github/prompts/"* "$LOCAL/.github/prompts/"
########################################################################################3
if [ -L "$LOCAL/.github/instructions/copilot.instructions.md" ] || [ -f "$LOCAL/.github/instructions/copilot.instructions.md" ]; then
rm -rf $LOCAL/.github/instructions/copilot.instructions.md
fi
mkdir -p $LOCAL/.github/instructions/
ln -s "$SOURCE/instructions/copilot.instructions.md" "$LOCAL/.github/instructions/copilot.instructions.md"
##########################################################################################
if [ -L "$HOME/.config/Code/User/mcp.json" ] || [ -f "$HOME/.config/Code/User/mcp.json" ]; then
rm -rf "$HOME/.config/Code/User/mcp.json"
fi
ln -s "$SOURCE/mcps/vscode.mcp.json" "$HOME/.config/Code/User/mcp.json"
###########################################################################################
