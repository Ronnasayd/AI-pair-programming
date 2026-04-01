## GITIGNORE
###############################################################################
if ! grep -q ".sessions/" .gitignore; then
    echo ".sessions/" >> .gitignore
fi
if ! grep -q ".mcp.json" .gitignore; then
    echo ".mcp.json" >> .gitignore
fi
###############################################################################
