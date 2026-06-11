## CLAUDE
DEFAULT_FOLDER=".claude"

############################################################################################
replace_between() {
    local inicio="$1"
    local fim="$2"
    local conteudo="$3"
    local arquivo="$4"

    if grep -Fq "$inicio" "$arquivo"; then
        awk -v ini="$inicio" \
            -v end="$fim" \
            -v content="$conteudo" '
        $0 == ini {
            print
            print content
            inside = 1
            next
        }

        inside && $0 == end {
            inside = 0
            print
            next
        }

        !inside {
            print
        }
        ' "$arquivo" > "${arquivo}.tmp" &&
        mv "${arquivo}.tmp" "$arquivo"
    else
        {
            cat "$arquivo"
            printf "\n%s\n%s\n%s\n" "$inicio" "$conteudo" "$fim"
        } > "${arquivo}.tmp" &&
        mv "${arquivo}.tmp" "$arquivo"
    fi
}

instructions=""
while read -r rule; do
    if [[ $rule == \#* ]]; then
        rule="${rule#\#}"
        rule="${rule#"${rule%%[![:space:]]*}"}"
        rule="${rule%"${rule##*[![:space:]]}"}"

        instructions+=$'\n'"$(<"$SOURCE/instructions/$rule")"
    fi
done < "$LOCAL/.rulesignore"

replace_between \
  "<!-- INIT AUTO-CONTEXT -->" \
  "<!-- END AUTO-CONTEXT -->" \
  "$instructions" \
  "$LOCAL/CLAUDE.md"

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
mkdir -p $LOCAL/$DEFAULT_FOLDER/commands/
find "$LOCAL/$DEFAULT_FOLDER/commands" -maxdepth 1 -type l | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/commands/"* ]]; then
        rm "$link"
    fi
done
ln -s "$SOURCE/commands/"* "$LOCAL/$DEFAULT_FOLDER/commands/"
########################################################################################
mkdir -p $LOCAL/$DEFAULT_FOLDER/hooks/
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
if ! grep -q "$DEFAULT_FOLDER/skills/*" .gitignore; then
    echo "$DEFAULT_FOLDER/skills/*" >> .gitignore
fi
if ! grep -q "$DEFAULT_FOLDER/commands/*" .gitignore; then
    echo "$DEFAULT_FOLDER/commands/*" >> .gitignore
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
rtk init -g
##########################################################################################
source $SOURCE/scripts/ignores.sh

###########################################################################################
if  [ ! -f "$LOCAL/skills-lock.json" ]; then
  curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash -s -- --only claude
  if ! grep -q ".agents/skills/*" .gitignore; then
      echo ".agents/skills/*" >> .gitignore
  fi
  if ! grep -q "skills-lock.json" .gitignore; then
      echo "skills-lock.json" >> .gitignore
  fi
fi
########################################################################################
## GITIGNORE
if ! grep -q "CLAUDE.md" .gitignore; then
    echo "CLAUDE.md" >> .gitignore
fi
if ! grep -q ".mcp.json" .gitignore; then
    echo ".mcp.json" >> .gitignore
fi
###########################################################################################
