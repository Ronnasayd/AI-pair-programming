if [ -L "$LOCAL/.skillsignore" ] || [ -f "$LOCAL/.skillsignore" ]; then
    while IFS= read -r pattern || [ -n "$pattern" ]; do
        [[ -z "$pattern" || "$pattern" == \#* ]] && continue
        for skill in "$LOCAL/$DEFAULT_FOLDER/skills/"$pattern; do
            if [ -L "$skill" ]; then
                rm "$skill"
                # echo "Removed skill($DEFAULT_FOLDER): $(basename "$skill") (matched pattern: $pattern)"
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
                # echo "Removed agent($DEFAULT_FOLDER): $(basename "$agent") (matched pattern: $pattern)"
            fi
        done
    done < "$LOCAL/.agentsignore"
fi


if [ -L "$LOCAL/.rulesignore" ] || [ -f "$LOCAL/.rulesignore" ]; then
    while IFS= read -r pattern || [ -n "$pattern" ]; do
        [[ -z "$pattern" || "$pattern" == \#* ]] && continue
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
    done < "$LOCAL/.rulesignore"
fi


if ! grep -q ".rulesignore" .gitignore; then
      echo ".rulesignore" >> .gitignore
fi
if ! grep -q ".skillsignore" .gitignore; then
      echo ".skillsignore" >> .gitignore
fi
if ! grep -q ".agentsignore" .gitignore; then
      echo ".agentsignore" >> .gitignore
fi
