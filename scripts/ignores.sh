SETTINGS_FILE="$HOME/.claude/aipp-settings.json"

if [ -f "$SETTINGS_FILE" ]; then
    while IFS= read -r pattern; do
        for skill in "$LOCAL/$DEFAULT_FOLDER/skills/"$pattern; do
            if [ -L "$skill" ]; then
                rm "$skill"
                # echo "Removed skill($DEFAULT_FOLDER): $(basename "$skill") (matched pattern: $pattern)"
            fi
        done
    done < <(jq -r --arg local "$LOCAL" '.projects[$local].skills // {} | to_entries[] | select(.value == false) | .key' "$SETTINGS_FILE")

    while IFS= read -r pattern; do
        for agent in "$LOCAL/$DEFAULT_FOLDER/agents/"$pattern; do
            if [ -L "$agent" ]; then
                rm "$agent"
                # echo "Removed agent($DEFAULT_FOLDER): $(basename "$agent") (matched pattern: $pattern)"
            fi
        done
    done < <(jq -r --arg local "$LOCAL" '.projects[$local].agents // {} | to_entries[] | select(.value == false) | .key' "$SETTINGS_FILE")

    while IFS= read -r pattern; do
        for rule in "$LOCAL/$DEFAULT_FOLDER/instructions/"$pattern; do
            if [ -L "$rule" ]; then
                rm "$rule"
                # echo "Removed rule($DEFAULT_FOLDER): $(basename "$rule") (matched pattern: $pattern)"
            fi
        done
        for rule in "$LOCAL/$DEFAULT_FOLDER/rules/"$pattern; do
            if [ -L "$rule" ]; then
                rm "$rule"
                # echo "Removed rule($DEFAULT_FOLDER): $(basename "$rule") (matched pattern: $pattern)"
            fi
        done
    done < <(jq -r --arg local "$LOCAL" '.projects[$local].instructions // {} | to_entries[] | select(.value == false) | .key' "$SETTINGS_FILE")
fi
