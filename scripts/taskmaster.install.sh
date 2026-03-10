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
############################################################################################
