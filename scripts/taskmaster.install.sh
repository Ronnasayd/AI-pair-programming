###########################################################################################
## TASKMASTER
mkdir -p "$LOCAL/.taskmaster/tasks"
touch "$LOCAL/.taskmaster/tasks/tasks.json"

if [ ! -L "$LOCAL/.taskmaster/config.json" ] || [ ! -f "$LOCAL/.taskmaster/config.json" ]; then
cp -f "$SOURCE/taskmaster/config.json" "$LOCAL/.taskmaster/config.json"
fi

if [ ! -L "$LOCAL/.taskmaster/state.json" ] || [ ! -f "$LOCAL/.taskmaster/state.json" ]; then
cp -f "$SOURCE/taskmaster/state.json" "$LOCAL/.taskmaster/state.json"
fi

if [ ! -L "$LOCAL/.taskmaster/reports" ] || [ ! -d "$LOCAL/.taskmaster/reports" ]; then
cp -r "$SOURCE/taskmaster/reports" "$LOCAL/.taskmaster/reports"
fi
############################################################################################
## GITIGNORE
if ! grep -q ".taskmaster/" .gitignore; then
    echo ".taskmaster/" >> .gitignore
fi
###########################################################################################
