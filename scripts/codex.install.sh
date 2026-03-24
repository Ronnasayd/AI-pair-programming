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
if [ -L "$HOME/.codex/prompts/" ] || [ -d "$HOME/.codex/prompts/" ]; then
    rm -rf "$HOME/.codex/prompts/"
fi
mkdir -p "$HOME/.codex/prompts/"
ln -s "$SOURCE/commands/"* "$HOME/.codex/prompts/"
###########################################################################################
## GITIGNORE
if ! grep -q "AGENTS.md" .gitignore; then
    echo "AGENTS.md" >> .gitignore
fi
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
    echo "# Spawned agent nesting depth root session starts at 0 (Codex default: 1)"
    echo "max_depth = 1"
    echo ""

[mcp_servers.taskmaster.env]
TASK_MASTER_ALLOW_METADATA_UPDATES = "true"
    echo ""
} > "$CODEX_DIR/agents.toml"

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
            # Use relative path as per Codex documentation paths are resolved relative to agents.toml location
            echo "config_file = \"agents/$agent_filename\""
            echo ""
        } >> "$CODEX_DIR/agents.toml"
    fi
done

# Validate agents.toml syntax
if ! grep -q '\[agents\]' "$CODEX_DIR/agents.toml"; then
    echo "Error: Missing [agents] section in agents.toml" >&2
    exit 1
fi

if ! grep -q 'max_threads\|max_depth' "$CODEX_DIR/agents.toml"; then
    echo "Error: Missing required agent configuration fields" >&2
    exit 1
fi

echo "✓ Codex configuration generated at $CODEX_DIR/agents.toml"
echo "✓ All agent config_file paths use relative paths (as per Codex standard)"
echo "✓ Configuration ready for multi-agent workflows"

############################################################################################
if ! grep -q "## REFERENCES" $HOME/.codex/AGENTS.md; then
    echo -e "\n## REFERENCES" >> $HOME/.codex/AGENTS.md
fi
###########################################################################################
mkdir -p "$HOME/.codex/instructions/"
############################################################################################
if ! grep -q "$HOME/.codex/instructions/code.instructions.md" $HOME/.codex/AGENTS.md; then
    ln -s "$SOURCE/instructions/code.instructions.md" "$HOME/.codex/instructions/code.instructions.md"
    echo -e "\n- $HOME/.codex/instructions/code.instructions.md" >> $HOME/.codex/AGENTS.md
fi
############################################################################################
if ! grep -q "$HOME/.codex/instructions/agent.instructions.md" $HOME/.codex/AGENTS.md; then
    ln -s "$SOURCE/instructions/agent.instructions.md" "$HOME/.codex/instructions/agent.instructions.md"
    echo -e "\n- $HOME/.codex/instructions/agent.instructions.md" >> $HOME/.codex/AGENTS.md
fi
