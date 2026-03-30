if [ -L "$LOCAL/.skillsignore" ] || [ -f "$LOCAL/.skillsignore" ]; then
    while IFS= read -r pattern || [ -n "$pattern" ]; do
        [[ -z "$pattern" || "$pattern" == \#* ]] && continue
        for skill in "$LOCAL/$DEFAULT_FOLDER/skills/"$pattern; do
            if [ -L "$skill" ]; then
                rm "$skill"
                # echo "Removed skill: $(basename "$skill") (matched pattern: $pattern)"
            fi
        done
    done < "$LOCAL/.skillsignore"
fi


if [ -L "$LOCAL/.agentsignore" ] || [ -f "$LOCAL/.agentsignore" ]; then
    while IFS= read -r pattern || [ -n "$pattern" ]; do
        [[ -z "$pattern" || "$pattern" == \#* ]] && continue
        for agent in "$LOCAL/$DEFAULT_FOLDER/agents/"$pattern; do
            if [ -L "$agent" ]; then
                rm "$agent"
                # echo "Removed agent: $(basename "$agent") (matched pattern: $pattern)"
            fi
        done
    done < "$LOCAL/.agentsignore"
fi
