## CLAUDE
DEFAULT_FOLDER=".claude"

############################################################################################
if ! grep -q "@.claude/instructions/code.instructions.md" $LOCAL/CLAUDE.md; then
    echo -e "\n@.claude/instructions/code.instructions.md" >> $LOCAL/CLAUDE.md
fi
############################################################################################
if ! grep -q "@.claude/instructions/agent.instructions.md" $LOCAL/CLAUDE.md; then
    echo -e "\n@.claude/instructions/agent.instructions.md" >> $LOCAL/CLAUDE.md
fi
########################################################################################
if [ -L "$LOCAL/.mcp.json" ] || [ -d "$LOCAL/.mcp.json" ]; then
rm -rf $LOCAL/.mcp.json
fi
ln -s "$SOURCE/claude/.mcp.json" "$LOCAL/.mcp.json"
########################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/settings.local.json" ] || [ -d "$LOCAL/$DEFAULT_FOLDER/settings.local.json" ]; then
rm -rf $LOCAL/$DEFAULT_FOLDER/settings.local.json
fi
ln -s "$SOURCE/claude/settings.local.json" "$LOCAL/$DEFAULT_FOLDER/settings.local.json"
########################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/skills/" ] || [ -d "$LOCAL/$DEFAULT_FOLDER/skills/" ]; then
rm -rf $LOCAL/$DEFAULT_FOLDER/skills/
fi
mkdir -p $LOCAL/$DEFAULT_FOLDER/skills/
ln -s "$SOURCE/skills/"* "$LOCAL/$DEFAULT_FOLDER/skills/"
########################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/commands" ] || [ -d "$LOCAL/$DEFAULT_FOLDER/commands" ]; then
rm -rf $LOCAL/$DEFAULT_FOLDER/commands
fi
mkdir -p $LOCAL/$DEFAULT_FOLDER/commands
ln -s "$SOURCE/commands/"* "$LOCAL/$DEFAULT_FOLDER/commands/"
########################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/hooks" ] || [ -d "$LOCAL/$DEFAULT_FOLDER/hooks" ]; then
rm -rf $LOCAL/$DEFAULT_FOLDER/hooks
fi
mkdir -p $LOCAL/$DEFAULT_FOLDER/hooks
ln -s "$SOURCE/hooks/"* "$LOCAL/$DEFAULT_FOLDER/hooks"
########################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/agents/" ] || [ -d "$LOCAL/$DEFAULT_FOLDER/agents/" ]; then
rm -rf $LOCAL/$DEFAULT_FOLDER/agents/
fi
mkdir -p $LOCAL/$DEFAULT_FOLDER/agents/
ln -s "$SOURCE/agents/"* "$LOCAL/$DEFAULT_FOLDER/agents/"
########################################################################################3
# Função auxiliar para criar symlinks de instruções
setup_instruction_file() {
    local file_name="$1"
    local source_file="$SOURCE/instructions/$file_name"
    local local_file="$LOCAL/$DEFAULT_FOLDER/instructions/$file_name"

    if [ -L "$local_file" ] || [ -f "$local_file" ]; then
        rm -rf "$local_file"
    fi

    mkdir -p "$LOCAL/$DEFAULT_FOLDER/instructions/"
    ln -s "$source_file" "$local_file"
}

# Configurar arquivos de instruções
setup_instruction_file "code.instructions.md"
setup_instruction_file "agent.instructions.md"
##########################################################################################
if [ -L "$HOME/.config/Code/User/mcp.json" ] || [ -f "$HOME/.config/Code/User/mcp.json" ]; then
rm $HOME/.config/Code/User/mcp.json
fi
ln -s "$SOURCE/mcps/vscode.mcp.json" "$HOME/.config/Code/User/mcp.json"
###########################################################################################
## GITIGNORE
if ! grep -q "$DEFAULT_FOLDER/skills/" .gitignore; then
    echo "$DEFAULT_FOLDER/skills/" >> .gitignore
fi
if ! grep -q "$DEFAULT_FOLDER/commands/" .gitignore; then
    echo "$DEFAULT_FOLDER/commands/" >> .gitignore
fi
if ! grep -q "$DEFAULT_FOLDER/instructions/" .gitignore; then
    echo "$DEFAULT_FOLDER/instructions/" >> .gitignore
fi
if ! grep -q "$DEFAULT_FOLDER/agents/" .gitignore; then
    echo "$DEFAULT_FOLDER/agents/" >> .gitignore
fi
if ! grep -q "$DEFAULT_FOLDER/hooks/" .gitignore; then
    echo "$DEFAULT_FOLDER/hooks/" >> .gitignore
fi
###########################################################################################
rtk init -g
# rm .github/instructions/rtk.instructions.md
# touch .github/instructions/rtk.instructions.md
# BODY=`cat .github/copilot-instructions.md`
# rm .github/copilot-instructions.md
# echo "---" >> .github/instructions/rtk.instructions.md
# echo "description: rtk usage rules." >> .github/instructions/rtk.instructions.md
# echo "applyTo: \"**/*\"" >> .github/instructions/rtk.instructions.md
# echo "---" >> .github/instructions/rtk.instructions.md
# echo  "$BODY" >> .github/instructions/rtk.instructions.md
##########################################################################################
source $SOURCE/scripts/ignores.sh


########################################################################################
## GITIGNORE
if ! grep -q "CLAUDE.md" .gitignore; then
    echo "CLAUDE.md" >> .gitignore
fi
if ! grep -q ".mcp.json" .gitignore; then
    echo ".mcp.json" >> .gitignore
fi
###########################################################################################
