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
# Função auxiliar para criar symlinks de instruções
setup_instruction_file() {
    local file_name="$1"
    local source_file="$SOURCE/instructions/$file_name"
    local local_file="$LOCAL/.github/instructions/$file_name"

    if [ -L "$local_file" ] || [ -f "$local_file" ]; then
        rm -rf "$local_file"
    fi

    mkdir -p "$LOCAL/.github/instructions/"
    ln -s "$source_file" "$local_file"
}

# Configurar arquivos de instruções
setup_instruction_file "copilot.instructions.md"
setup_instruction_file "orchestration.instructions.md"
setup_instruction_file "lessons.instructions.md"
##########################################################################################
if [ -L "$HOME/.config/Code/User/mcp.json" ] || [ -f "$HOME/.config/Code/User/mcp.json" ]; then
rm $HOME/.config/Code/User/mcp.json
fi
ln -s "$SOURCE/mcps/vscode.mcp.json" "$HOME/.config/Code/User/mcp.json"
###########################################################################################
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
if ! grep -q ".github/hooks/" .gitignore; then
    echo ".github/hooks/" >> .gitignore
fi
###########################################################################################
