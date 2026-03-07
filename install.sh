#!/usr/bin/env bash
SOURCE="/home/ronnas/develop/personal/AI-pair-programming"
LOCAL="$(pwd)"

# echo $SOURCE
# echo $LOCAL

python3 $SOURCE/converter.py $SOURCE/gemini/commands/  $SOURCE/github/prompts/

## GEMINI
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
########################################################################################

## GITHUB COPILOT
########################################################################################
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
########################################################################################
if [ -L "$LOCAL/.github/agents/" ] || [ -d "$LOCAL/.github/agents/" ]; then
rm -rf $LOCAL/.github/agents/
fi
mkdir -p $LOCAL/.github/agents/
ln -s "$SOURCE/agents/"* "$LOCAL/.github/agents/"
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
###########################################################################################
## TASKMASTER
mkdir -p "$LOCAL/.taskmaster/tasks"
touch "$LOCAL/.taskmaster/tasks/tasks.json"
if [ -L "$LOCAL/.taskmaster/config.json" ] || [ -f "$LOCAL/.taskmaster/config.json" ]; then
rm -rf "$LOCAL/.taskmaster/config.json"
fi
cp -f "$SOURCE/taskmaster/config.json" "$LOCAL/.taskmaster/config.json"

if [ -L "$LOCAL/.taskmaster/state.json" ] || [ -f "$LOCAL/.taskmaster/state.json" ]; then
rm -rf "$LOCAL/.taskmaster/state.json"
fi
cp -f "$SOURCE/taskmaster/state.json" "$LOCAL/.taskmaster/state.json"
############################################################################################
############################################################################################
## GITIGNORE
if ! grep -q ".github/skills/" .gitignore; then
    echo ".github/skills/" >> .gitignore
fi
if ! grep -q ".github/prompts/" .gitignore; then
    echo ".github/prompts/" >> .gitignore
fi
if ! grep -q ".github/instructions/" .gitignore; then
    echo ".github/instructions/" >> .gitignore
fi
if ! grep -q ".github/agents/" .gitignore; then
    echo ".github/agents/" >> .gitignore
fi
if ! grep -q ".taskmaster/" .gitignore; then
    echo ".taskmaster/" >> .gitignore
fi
############################################################################################
############################################################################################
