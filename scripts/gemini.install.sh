## GEMINI
############################################################################################
if ! grep -q "@.github/instructions/code.instructions.md" $LOCAL/GEMINI.md; then
    echo -e "\n@.github/instructions/code.instructions.md" >> $LOCAL/GEMINI.md
fi
############################################################################################
if ! grep -q "@.github/instructions/orchestration.instructions.md" $LOCAL/GEMINI.md; then
    echo -e "\n@.github/instructions/orchestration.instructions.md" >> $LOCAL/GEMINI.md
fi
############################################################################################
if ! grep -q "@.github/instructions/agent.instructions.md" $LOCAL/GEMINI.md; then
    echo -e "\n@.github/instructions/agent.instructions.md" >> $LOCAL/GEMINI.md
fi
#######################################################################################
if [ -L "$HOME/.gemini/commands/" ] || [ -d "$HOME/.gemini/commands/" ]; then
rm -rf $HOME/.gemini/commands/
fi
mkdir -p $HOME/.gemini/commands
ln -s "$SOURCE/commands/"* "$HOME/.gemini/commands/"
#######################################################################################
if [ -L "$HOME/.gemini/settings.json" ] || [ -f "$HOME/.gemini/settings.json" ]; then
rm $HOME/.gemini/settings.json
fi
ln -s "$SOURCE/gemini/settings.json" "$HOME/.gemini/settings.json"
#######################################################################################
if [ -L "$HOME/.gemini/mcp-server-enablement.json" ] || [ -f "$HOME/.gemini/mcp-server-enablement.json" ]; then
rm $HOME/.gemini/mcp-server-enablement.json
fi
ln -s "$SOURCE/gemini/mcp-server-enablement.json" "$HOME/.gemini/mcp-server-enablement.json"
#######################################################################################
if [ -L "$HOME/.gemini/skills/" ] || [ -d "$HOME/.gemini/skills/" ]; then
rm -rf $HOME/.gemini/skills/
fi
mkdir -p $HOME/.gemini/skills
ln -s "$SOURCE/skills/"* "$HOME/.gemini/skills/"
########################################################################################
if [ -L "$HOME/.gemini/agents/" ] || [ -d "$HOME/.gemini/agents/" ]; then
rm -rf $HOME/.gemini/agents/
fi
mkdir -p $HOME/.gemini/agents
cp -r "$SOURCE/agents/"* "$HOME/.gemini/agents/"
########################################################################################
## GITIGNORE
if ! grep -q "GEMINI.md" .gitignore; then
    echo "GEMINI.md" >> .gitignore
fi
###########################################################################################
