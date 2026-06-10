## ANTIGRAVITY CLEAN
DEFAULT_FOLDER=".agents"

echo "Cleaning antigravity symlinks..."

########################################################################################
# if [ -L "$HOME/$DEFAULT_FOLDER/settings.json" ]; then
#   rm "$HOME/$DEFAULT_FOLDER/settings.json"
# fi
########################################################################################
if [ -L "$HOME/$DEFAULT_FOLDER/.geminignore" ]; then
  rm "$HOME/$DEFAULT_FOLDER/.geminignore"
fi
########################################################################################
# if [ -L "$LOCAL/$DEFAULT_FOLDER/commands/scripts" ]; then
#   rm -rf "$LOCAL/$DEFAULT_FOLDER/commands/scripts"
# fi
########################################################################################
# if [ -L "$HOME/$DEFAULT_FOLDER/policies" ]; then
#   rm "$HOME/$DEFAULT_FOLDER/policies"
# fi
########################################################################################
# if [ -L "$HOME/$DEFAULT_FOLDER/mcp-server-enablement.json" ]; then
#   rm "$HOME/$DEFAULT_FOLDER/mcp-server-enablement.json"
# fi
########################################################################################
find "$LOCAL/$DEFAULT_FOLDER/skills" -maxdepth 1 -type l 2>/dev/null | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/skills/"* ]]; then
        rm "$link"
    fi
done
########################################################################################
find "$LOCAL/$DEFAULT_FOLDER/rules" -maxdepth 1 -type l 2>/dev/null | while read -r link; do
    target=$(readlink "$link")
    if [[ "$target" == "$SOURCE/instructions/"* ]]; then
        rm "$link"
    fi
done
########################################################################################
echo "Gemini symlinks cleaned."
