## GEMINI
DEFAULT_FOLDER=".gemini"
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
if [ -L "$HOME/$DEFAULT_FOLDER/commands/" ] || [ -d "$HOME/$DEFAULT_FOLDER/commands/" ]; then
rm -rf $HOME/$DEFAULT_FOLDER/commands/
fi
mkdir -p $HOME/$DEFAULT_FOLDER/commands
ln -s "$SOURCE/commands/"* "$HOME/$DEFAULT_FOLDER/commands/"
#######################################################################################
if [ -L "$HOME/$DEFAULT_FOLDER/settings.json" ] || [ -f "$HOME/$DEFAULT_FOLDER/settings.json" ]; then
rm $HOME/$DEFAULT_FOLDER/settings.json
fi
ln -s "$SOURCE/gemini/settings.json" "$HOME/$DEFAULT_FOLDER/settings.json"
#######################################################################################
if [ -L "$HOME/$DEFAULT_FOLDER/policies" ] || [ -f "$HOME/$DEFAULT_FOLDER/policies" ]; then
rm $HOME/$DEFAULT_FOLDER/policies
fi
ln -s "$SOURCE/gemini/policies"* "$HOME/$DEFAULT_FOLDER/policies"
#######################################################################################
if [ -L "$HOME/$DEFAULT_FOLDER/mcp-server-enablement.json" ] || [ -f "$HOME/$DEFAULT_FOLDER/mcp-server-enablement.json" ]; then
rm $HOME/$DEFAULT_FOLDER/mcp-server-enablement.json
fi
ln -s "$SOURCE/gemini/mcp-server-enablement.json" "$HOME/$DEFAULT_FOLDER/mcp-server-enablement.json"
#######################################################################################
if [ -L "$HOME/$DEFAULT_FOLDER/skills/" ] || [ -d "$HOME/$DEFAULT_FOLDER/skills/" ]; then
rm -rf $HOME/$DEFAULT_FOLDER/skills/
fi
mkdir -p $HOME/$DEFAULT_FOLDER/skills
ln -s "$SOURCE/skills/"* "$HOME/$DEFAULT_FOLDER/skills/"
########################################################################################
if [ -L "$HOME/$DEFAULT_FOLDER/agents/" ] || [ -d "$HOME/$DEFAULT_FOLDER/agents/" ]; then
rm -rf $HOME/$DEFAULT_FOLDER/agents/
fi
mkdir -p $HOME/$DEFAULT_FOLDER/agents
cp -r "$SOURCE/agents/"* "$HOME/$DEFAULT_FOLDER/agents/"
########################################################################################
## GITIGNORE
if ! grep -q "GEMINI.md" .gitignore; then
    echo "GEMINI.md" >> .gitignore
fi
###########################################################################################
