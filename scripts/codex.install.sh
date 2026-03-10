## AGENT COPILOT
########################################################################################
if [ -L "$LOCAL/.agent/skills/" ] || [ -d "$LOCAL/.agent/skills/" ]; then
rm -rf $LOCAL/.agent/skills/
fi
mkdir -p $LOCAL/.agent/skills/
ln -s "$SOURCE/skills/"* "$LOCAL/.agent/skills/"
###########################################################################################
## GITIGNORE
if ! grep -q ".agent/skills/" .gitignore; then
    echo ".agent/skills/" >> .gitignore
fi
###########################################################################################
