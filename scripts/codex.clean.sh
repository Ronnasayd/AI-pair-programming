## CODEX CLEAN

echo "Cleaning codex symlinks..."

########################################################################################
find "$HOME/.codex/skills" -maxdepth 1 -type l 2>/dev/null | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/skills/"* ]]; then
        rm "$link"
    fi
done
########################################################################################
find "$HOME/.codex/prompts" -maxdepth 1 -type l 2>/dev/null | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/commands/"* ]]; then
        rm "$link"
    fi
done
########################################################################################
echo "Codex symlinks cleaned."
