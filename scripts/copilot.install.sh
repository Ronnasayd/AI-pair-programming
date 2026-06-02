## GITHUB COPILOT
DEFAULT_FOLDER=".github"

########################################################################################
if [ -L "$HOME/.copilot/mcp-config.json" ] || [ -d "$HOME/.copilot/mcp-config.json" ]; then
rm  $HOME/.copilot/mcp-config.json
fi
ln -s "$SOURCE/github-copilot/mcp-config.json" "$HOME/.copilot/mcp-config.json"
########################################################################################
if [ -L "$HOME/.copilot/config.json" ] || [ -d "$HOME/.copilot/config.json" ]; then
rm  $HOME/.copilot/config.json
fi
ln -s "$SOURCE/github-copilot/config.json" "$HOME/.copilot/config.json"
########################################################################################
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
mkdir -p "$LOCAL/$DEFAULT_FOLDER/prompts"
find "$LOCAL/$DEFAULT_FOLDER/prompts" -maxdepth 1 -type l | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/commands/"* ]]; then
        rm "$link"
    fi
done
ln -s "$SOURCE/commands/"* "$LOCAL/$DEFAULT_FOLDER/prompts/"
########################################################################################
mkdir -p $LOCAL/$DEFAULT_FOLDER/hooks
find "$LOCAL/$DEFAULT_FOLDER/hooks" -maxdepth 1 -type l | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/hooks/"* ]]; then
        rm "$link"
    fi
done
ln -s "$SOURCE/hooks/"* "$LOCAL/$DEFAULT_FOLDER/hooks"
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
mkdir -p $LOCAL/$DEFAULT_FOLDER/instructions/
find "$LOCAL/$DEFAULT_FOLDER/instructions" -maxdepth 1 -type l | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/instructions/"* ]]; then
        rm "$link"
    fi
done
ln -s "$SOURCE/instructions/"* "$LOCAL/$DEFAULT_FOLDER/instructions/"
##########################################################################################
if [ -L "$HOME/.config/Code/User/mcp.json" ] || [ -f "$HOME/.config/Code/User/mcp.json" ]; then
rm $HOME/.config/Code/User/mcp.json
fi
ln -s "$SOURCE/mcps/vscode.mcp.json" "$HOME/.config/Code/User/mcp.json"
###########################################################################################
## GITIGNORE
if ! grep -q "$DEFAULT_FOLDER/skills/*" .gitignore; then
    echo "$DEFAULT_FOLDER/skills/*" >> .gitignore
fi
if ! grep -q "$DEFAULT_FOLDER/prompts/*" .gitignore; then
    echo "$DEFAULT_FOLDER/prompts/*" >> .gitignore
fi
if ! grep -q "$DEFAULT_FOLDER/instructions/*" .gitignore; then
    echo "$DEFAULT_FOLDER/instructions/*" >> .gitignore
fi
if ! grep -q "$DEFAULT_FOLDER/agents/*" .gitignore; then
    echo "$DEFAULT_FOLDER/agents/*" >> .gitignore
fi
if ! grep -q "$DEFAULT_FOLDER/hooks/*" .gitignore; then
    echo "$DEFAULT_FOLDER/hooks/*" >> .gitignore
fi
###########################################################################################
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash -s -- --only copilot
if ! grep -q "*caveman*" .gitignore; then
    echo "*caveman*" >> .gitignore
fi
if ! grep -q "*cavecrew*" .gitignore; then
    echo "*cavecrew*" >> .gitignore
fi
if ! grep -q "skills-lock.json" .gitignore; then
    echo "skills-lock.json" >> .gitignore
fi
###########################################################################################
rtk init -g --copilot
rm .github/instructions/rtk.instructions.md
touch .github/instructions/rtk.instructions.md
BODY=`cat .github/copilot-instructions.md`
rm .github/copilot-instructions.md
echo "---" >> .github/instructions/rtk.instructions.md
echo "description: rtk usage rules." >> .github/instructions/rtk.instructions.md
echo "applyTo: \"**/*\"" >> .github/instructions/rtk.instructions.md
echo "---" >> .github/instructions/rtk.instructions.md
echo  "$BODY" >> .github/instructions/rtk.instructions.md
##########################################################################################
source $SOURCE/scripts/ignores.sh
