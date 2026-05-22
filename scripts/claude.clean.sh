## CLAUDE CLEAN
DEFAULT_FOLDER=".claude"

echo "Cleaning claude symlinks..."

########################################################################################
if [ -L "$LOCAL/.mcp.json" ]; then
  rm "$LOCAL/.mcp.json"
fi
########################################################################################
if [ -L "$LOCAL/$DEFAULT_FOLDER/settings.local.json" ]; then
  rm "$LOCAL/$DEFAULT_FOLDER/settings.local.json"
fi
########################################################################################
find "$LOCAL/$DEFAULT_FOLDER/skills" -maxdepth 1 -type l 2>/dev/null | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/skills/"* ]]; then
        rm "$link"
    fi
done
########################################################################################
find "$LOCAL/$DEFAULT_FOLDER/commands" -maxdepth 1 -type l 2>/dev/null | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/commands/"* ]]; then
        rm "$link"
    fi
done
########################################################################################
find "$LOCAL/$DEFAULT_FOLDER/hooks" -maxdepth 1 -type l 2>/dev/null | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/hooks/"* ]]; then
        rm "$link"
    fi
done
########################################################################################
find "$LOCAL/$DEFAULT_FOLDER/agents" -maxdepth 1 -type l 2>/dev/null | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/agents/"* ]]; then
        rm "$link"
    fi
done
########################################################################################
find "$LOCAL/$DEFAULT_FOLDER/instructions" -maxdepth 1 -type l 2>/dev/null | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/instructions/"* ]]; then
        rm "$link"
    fi
done
########################################################################################
if [ -L "$HOME/.config/Code/User/mcp.json" ]; then
  rm "$HOME/.config/Code/User/mcp.json"
fi
########################################################################################
echo "Claude symlinks cleaned."
