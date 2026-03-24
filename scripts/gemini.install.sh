## GEMINI
DEFAULT_FOLDER=".gemini"
python3 $SOURCE/md2toml.py $SOURCE/commands/  $HOME/$DEFAULT_FOLDER/commands/

############################################################################################
if ! grep -q "@.github/instructions/code.instructions.md" $LOCAL/GEMINI.md; then
    echo -e "\n@.github/instructions/code.instructions.md" >> $LOCAL/GEMINI.md
fi
############################################################################################
if ! grep -q "@.github/instructions/agent.instructions.md" $LOCAL/GEMINI.md; then
    echo -e "\n@.github/instructions/agent.instructions.md" >> $LOCAL/GEMINI.md
fi
#######################################################################################
if [ -L "$HOME/$DEFAULT_FOLDER/settings.json" ] || [ -f "$HOME/$DEFAULT_FOLDER/settings.json" ]; then
rm $HOME/$DEFAULT_FOLDER/settings.json
fi
ln -s "$SOURCE/gemini/settings.json" "$HOME/$DEFAULT_FOLDER/settings.json"
#######################################################################################
if [ -L "$HOME/$DEFAULT_FOLDER/commands/scripts" ] || [ -d "$HOME/$DEFAULT_FOLDER/commands/scripts" ]; then
rm -rf $HOME/$DEFAULT_FOLDER/commands/scripts
fi
ln -s "$SOURCE/commands/scripts"* "$HOME/$DEFAULT_FOLDER/commands/scripts"
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
if [ -L "$HOME/$DEFAULT_FOLDER/hooks/scripts" ] || [ -d "$HOME/$DEFAULT_FOLDER/hooks/scripts" ]; then
rm -rf $HOME/$DEFAULT_FOLDER/hooks/scripts
fi
mkdir -p $HOME/$DEFAULT_FOLDER/hooks/scripts
cp -r "$SOURCE/hooks/scripts"* "$HOME/$DEFAULT_FOLDER/hooks"
########################################################################################
## GITIGNORE
if ! grep -q "GEMINI.md" .gitignore; then
    echo "GEMINI.md" >> .gitignore
fi
###########################################################################################
