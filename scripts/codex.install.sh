#!/usr/bin/env bash

## CODEX
python3 "$SOURCE/md2toml.py" "$SOURCE/agents/" "$LOCAL/.agent/agents/"

########################################################################################
if [ -L "$LOCAL/.agent/skills/" ] || [ -d "$LOCAL/.agent/skills/" ]; then
    rm -rf "$LOCAL/.agent/skills/"
fi
mkdir -p "$LOCAL/.agent/skills/"
ln -s "$SOURCE/skills/"* "$LOCAL/.agent/skills/"

###########################################################################################
## GITIGNORE
if ! grep -q ".agent/skills/" .gitignore; then
    echo ".agent/skills/" >> .gitignore
fi
if ! grep -q ".agent/agents/" .gitignore; then
    echo ".agent/agents/" >> .gitignore
fi
if ! grep -q ".codex/" .gitignore; then
    echo ".codex/" >> .gitignore
fi

###########################################################################################
## CODEX CONFIG
CODEX_DIR="$LOCAL/.codex"
mkdir -p "$CODEX_DIR"

{
    echo "[features]"
    echo "multi_agent = true"
    echo ""
    echo "[agents]"
} > "$CODEX_DIR/config.toml"

for agent_toml in "$LOCAL/.agent/agents/"*.toml; do
    if [ -f "$agent_toml" ]; then
        agent_filename=$(basename "$agent_toml")
        agent_id="${agent_filename%.toml}"
        agent_id="${agent_id%.agent}"
        
        # Extract description safely using sed to remove prefix and suffix quotes
        description=$(grep '^description =' "$agent_toml" | head -n 1 | sed 's/^description = "//;s/"$//')
        
        {
            echo "[agents.\"$agent_id\"]"
            echo "description = \"$description\""
            echo "config_file = \".agent/agents/$agent_filename\""
            echo ""
        } >> "$CODEX_DIR/config.toml"
    fi
done

echo "Codex configuration generated at $CODEX_DIR/config.toml"
