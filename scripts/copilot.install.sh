## GITHUB COPILOT
DEFAULT_FOLDER=".github"
########################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/skills/" ] || [ -d "$LOCAL/$DEFAULT_FOLDER/skills/" ]; then
rm -rf $LOCAL/$DEFAULT_FOLDER/skills/
fi
mkdir -p $LOCAL/$DEFAULT_FOLDER/skills/
ln -s "$SOURCE/skills/"* "$LOCAL/$DEFAULT_FOLDER/skills/"
########################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/prompts" ] || [ -d "$LOCAL/$DEFAULT_FOLDER/prompts" ]; then
rm -rf $LOCAL/$DEFAULT_FOLDER/prompts
fi
mkdir -p $LOCAL/$DEFAULT_FOLDER/prompts
ln -s "$SOURCE/commands/"* "$LOCAL/$DEFAULT_FOLDER/prompts/"
########################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/hooks/scripts" ] || [ -d "$LOCAL/$DEFAULT_FOLDER/hooks/scripts" ]; then
rm -rf $LOCAL/$DEFAULT_FOLDER/hooks/scripts
fi
mkdir -p $LOCAL/$DEFAULT_FOLDER/hooks/scripts
ln -s "$SOURCE/hooks/scripts/"* "$LOCAL/$DEFAULT_FOLDER/hooks/scripts"
python3 "$SOURCE/hooks/generator.py" --config "$SOURCE/hooks/config.json" --agent copilot --output "$LOCAL/.github"
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
setup_instruction_file "orchestration.instructions.md"
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
if ! grep -q "$DEFAULT_FOLDER/prompts/" .gitignore; then
    echo "$DEFAULT_FOLDER/prompts/" >> .gitignore
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
