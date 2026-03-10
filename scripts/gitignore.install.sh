############################################################################################
## GITIGNORE
if ! grep -q ".github/skills/" .gitignore; then
    echo ".github/skills/" >> .gitignore
fi
if ! grep -q ".github/prompts/" .gitignore; then
    echo ".github/prompts/" >> .gitignore
fi
if ! grep -q ".github/instructions/" .gitignore; then
    echo ".github/instructions/" >> .gitignore
fi
if ! grep -q ".github/agents/" .gitignore; then
    echo ".github/agents/" >> .gitignore
fi
if ! grep -q ".github/hooks/" .gitignore; then
    echo ".github/hooks/" >> .gitignore
fi
if ! grep -q ".taskmaster/" .gitignore; then
    echo ".taskmaster/" >> .gitignore
fi
if ! grep -q "GEMINI.md" .gitignore; then
    echo "GEMINI.md" >> .gitignore
fi
############################################################################################
