## CODEX
python3 $SOURCE/md2toml.py $SOURCE/agents/  $LOCAL/.agent/agents/
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
if ! grep -q ".agent/agents/" .gitignore; then
    echo ".agent/agents/" >> .gitignore
fi
###########################################################################################
