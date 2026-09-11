## GITIGNORE
###############################################################################
source "$(dirname "${BASH_SOURCE[0]}")/_git-exclude.sh"
git_exclude ".sessions/*" ".agentsignore" ".skillsignore"
###############################################################################
