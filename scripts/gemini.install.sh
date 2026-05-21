## GEMINI
DEFAULT_FOLDER=".gemini"
yes | rtk init -g --gemini
python3 $SOURCE/scripts/md2toml.py $SOURCE/commands/  $LOCAL/$DEFAULT_FOLDER/commands/

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
if [ -L "$HOME/$DEFAULT_FOLDER/.geminignore" ] || [ -f "$HOME/$DEFAULT_FOLDER/.geminignore" ]; then
rm $HOME/$DEFAULT_FOLDER/.geminignore
fi
ln -s "$SOURCE/gemini/.geminignore" "$HOME/$DEFAULT_FOLDER/.geminignore"
#######################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/commands/scripts" ] || [ -d "$LOCAL/$DEFAULT_FOLDER/commands/scripts" ]; then
rm -rf $LOCAL/$DEFAULT_FOLDER/commands/scripts
fi
ln -s "$SOURCE/commands/scripts"* "$LOCAL/$DEFAULT_FOLDER/commands/scripts"
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
mkdir -p $LOCAL/$DEFAULT_FOLDER/skills/
find "$LOCAL/$DEFAULT_FOLDER/skills" -maxdepth 1 -type l | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/skills/"* ]]; then
        rm "$link"
    fi
done
ln -s "$SOURCE/skills/index.yaml" "$LOCAL/$DEFAULT_FOLDER/skills/index.yaml"
# Procurar por todos os SKILL.md e criar symlinks para seus diretórios pai
find "$SOURCE/skills" -name "SKILL.md" -type f | while read skill_file; do
    # Obter o diretório pai de SKILL.md (diretório da skill)
    skill_dir=$(dirname "$skill_file")
    # Obter apenas o nome da skill
    skill_name=$(basename "$skill_dir")

    # Criar symlink
    ln -s "$skill_dir" "$LOCAL/$DEFAULT_FOLDER/skills/$skill_name"
done
########################################################################################
mkdir -p $LOCAL/$DEFAULT_FOLDER/agents/
find "$LOCAL/$DEFAULT_FOLDER/agents" -maxdepth 1 -type l | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/agents/"* ]]; then
        rm "$link"
    fi
done
ln -s "$SOURCE/agents/"* "$LOCAL/$DEFAULT_FOLDER/agents/"
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
if ! grep -q "$DEFAULT_FOLDER/" .gitignore; then
    echo "$DEFAULT_FOLDER/" >> .gitignore
fi
###########################################################################################

source $SOURCE/scripts/ignores.sh
