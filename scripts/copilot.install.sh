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
if [ -L "$LOCAL/.github/hooks/" ] || [ -d "$LOCAL/.github/hooks/" ]; then
rm -rf $LOCAL/.github/hooks/
fi
mkdir -p $LOCAL/.github/hooks/
ln -s "$SOURCE/hooks/"* "$LOCAL/.github/hooks/"
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
if [ ! -f "$HOME/.config/Code/User/mcp.json" ]; then
cp "$SOURCE/mcps/vscode.mcp.json" "$HOME/.config/Code/User/mcp.json"
fi
###########################################################################################
