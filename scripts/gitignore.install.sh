## GITIGNORE
###############################################################################
if ! grep -q ".sessions/*" .git/info/exclude; then
    echo ".sessions/*" >> .git/info/exclude
fi
if ! grep -q ".agentsignore" .git/info/exclude; then
    echo ".agentsignore" >> .git/info/exclude
fi
if ! grep -q ".skillsignore" .git/info/exclude; then
    echo ".skillsignore" >> .git/info/exclude
fi
###############################################################################
