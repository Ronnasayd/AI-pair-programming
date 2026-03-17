###########################################################################################
## TASKMASTER
mkdir -p "$LOCAL/.taskmaster/tasks"
touch "$LOCAL/.taskmaster/tasks/tasks.json"
if [ -L "$LOCAL/.taskmaster/config.json" ] || [ -f "$LOCAL/.taskmaster/config.json" ]; then
rm -rf "$LOCAL/.taskmaster/config.json"
fi
cp -f "$SOURCE/taskmaster/config.json" "$LOCAL/.taskmaster/config.json"

if [ -L "$LOCAL/.taskmaster/state.json" ] || [ -f "$LOCAL/.taskmaster/state.json" ]; then
rm -rf "$LOCAL/.taskmaster/state.json"
fi
cp -f "$SOURCE/taskmaster/state.json" "$LOCAL/.taskmaster/state.json"

if [ -L "$LOCAL/.taskmaster/reports" ] || [ -d "$LOCAL/.taskmaster/reports" ]; then
rm -rf "$LOCAL/.taskmaster/reports"
fi
cp -r "$SOURCE/taskmaster/reports" "$LOCAL/.taskmaster/reports"
############################################################################################
## GITIGNORE
if ! grep -q ".taskmaster/" .gitignore; then
    echo ".taskmaster/" >> .gitignore
fi
###########################################################################################
