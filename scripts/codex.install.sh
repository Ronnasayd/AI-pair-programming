#!/usr/bin/env bash

## CODEX
python3 "$SOURCE/md2toml.py" "$SOURCE/agents/" "$HOME/.codex/agents/"

###########################################################################################
## Rename 'prompt' to 'developer_instructions' in all agent TOML files
for agent_toml in "$HOME/.codex/agents/"*.toml; do
    if [ -f "$agent_toml" ]; then
        sed -i 's/^prompt = /developer_instructions = /' "$agent_toml"
    fi
done

########################################################################################
if [ -L "$HOME/.codex/skills/" ] || [ -d "$HOME/.codex/skills/" ]; then
    rm -rf "$HOME/.codex/skills/"
fi
mkdir -p "$HOME/.codex/skills/"
ln -s "$SOURCE/skills/"* "$HOME/.codex/skills/"

###########################################################################################
# ## GITIGNORE
# if ! grep -q ".agent/agents/" .gitignore; then
#     echo ".agent/agents/" >> .gitignore
# fi
# if ! grep -q ".codex/" .gitignore; then
#     echo ".codex/" >> .gitignore
# fi

###########################################################################################
## CODEX CONFIG
CODEX_DIR="$HOME/.codex"
mkdir -p "$CODEX_DIR"

{
    echo "[features]"
    echo "multi_agent = true"
    echo ""
    echo "[agents]"
    echo "# Concurrent open agent thread cap (Codex default: 6)"
    echo "max_threads = 6"
    echo "# Spawned agent nesting depth - root session starts at 0 (Codex default: 1)"
    echo "max_depth = 1"
    echo ""
} > "$CODEX_DIR/config.toml"

for agent_toml in "$HOME/.codex/agents/"*.toml; do
    if [ -f "$agent_toml" ]; then
        agent_filename=$(basename "$agent_toml")
        agent_id="${agent_filename%.toml}"
        agent_id="${agent_id%.agent}"

        # Extract description safely using sed to remove prefix and suffix quotes
        description=$(grep '^description =' "$agent_toml" | head -n 1 | sed 's/^description = "//;s/"$//')

        {
            echo "[agents.$agent_id]"
            echo "description = \"$description\""
            # Use relative path as per Codex documentation - paths are resolved relative to config.toml location
            echo "config_file = \"agents/$agent_filename\""
            echo ""
        } >> "$CODEX_DIR/config.toml"
    fi
done

# Validate config.toml syntax
if ! grep -q '\[agents\]' "$CODEX_DIR/config.toml"; then
    echo "Error: Missing [agents] section in config.toml" >&2
    exit 1
fi

if ! grep -q 'max_threads\|max_depth' "$CODEX_DIR/config.toml"; then
    echo "Error: Missing required agent configuration fields" >&2
    exit 1
fi

echo "✓ Codex configuration generated at $CODEX_DIR/config.toml"
echo "✓ All agent config_file paths use relative paths (as per Codex standard)"
echo "✓ Configuration ready for multi-agent workflows"
