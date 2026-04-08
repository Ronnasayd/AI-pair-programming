## GITIGNORE
###############################################################################
if ! grep -q ".sessions/" .gitignore; then
    echo ".sessions/" >> .gitignore
fi
if ! grep -q ".agentsignore" .gitignore; then
    echo ".agentsignore" >> .gitignore
fi
if ! grep -q ".skillsignore" .gitignore; then
    echo ".skillsignore" >> .gitignore
fi
###############################################################################
