#!/usr/bin/env bash
export ASDF_NODEJS_VERSION=23.11.1
SCRIPT_FILE="${BASH_SOURCE[0]}"
echo "Running install script: $SCRIPT_FILE"

if [ -L "$SCRIPT_FILE" ]; then
  SCRIPT_FILE="$(readlink -f "$SCRIPT_FILE")"
else
  if [ ! -L "/usr/local/bin/init-ai" ]; then
    bash "$(pwd)/scripts/update-external-tools.sh"
    python "$(pwd)/scripts/list_skills_agents.py"
    sudo ln -s "$(pwd)/$SCRIPT_FILE" "/usr/local/bin/init-ai"
    sudo ln -s "$(pwd)/scripts/manage-ignore-files.py" "/usr/local/bin/manage-ignore-files"
  fi
fi

export SOURCE="$(dirname "$SCRIPT_FILE")"
export LOCAL="$(pwd)"
# echo $SOURCE
# echo $LOCAL
chmod -R +x $SOURCE/hooks/scripts

# Function to display help
show_help() {
  cat << EOF
Usage: $0 [OPTIONS]

Options:
  --all          Execute all install scripts
  --copilot      Execute copilot install script
  --claude       Execute claude install script
  --gemini       Execute gemini install script
  --codex        Execute codex install script
  --taskmaster   Execute taskmaster install script
  --gitignore    Execute gitignore install script
  --clean        Remove all symlinks created by the install scripts
  --help, -h     Display this help message

Examples:
  $0 --all                    # Install all backends
  $0 --copilot --claude       # Install only copilot and claude
  $0 --gemini                 # Install only gemini
  $0 --clean                  # Clean all symlinks
  $0 --clean --copilot        # Clean and reinstall copilot only

If no options are specified, --all is used by default.
EOF
}

# Function to execute install script
run_install() {
  local script=$1
  if [ -f "$SOURCE/scripts/${script}.install.sh" ]; then
    echo "Running ${script} install..."
    $SOURCE/scripts/${script}.install.sh
  else
    echo "Warning: Script not found: $SOURCE/scripts/${script}.install.sh"
  fi
}

# Function to execute clean script
run_clean() {
  local script=$1
  if [ -f "$SOURCE/scripts/${script}.clean.sh" ]; then
    echo "Running ${script} clean..."
    $SOURCE/scripts/${script}.clean.sh
  else
    echo "Warning: Clean script not found: $SOURCE/scripts/${script}.clean.sh"
  fi
}

# Parse arguments
BACKENDS=()
CLEAN_MODE=false

if [ $# -eq 0 ]; then
  # No arguments provided, run all by default
  BACKENDS=("copilot" "claude" "gemini" "codex" "taskmaster" "gitignore")
else
  while [[ $# -gt 0 ]]; do
    case $1 in
      --all)
        BACKENDS=("copilot" "claude" "gemini" "codex" "taskmaster" "gitignore")
        shift
        ;;
      --copilot)
        BACKENDS+=("copilot")
        shift
        ;;
      --claude)
        BACKENDS+=("claude")
        shift
        ;;
      --gemini)
        BACKENDS+=("gemini")
        shift
        ;;
      --codex)
        BACKENDS+=("codex")
        shift
        ;;
      --taskmaster)
        BACKENDS+=("taskmaster")
        shift
        ;;
      --gitignore)
        BACKENDS+=("gitignore")
        shift
        ;;
      --clean)
        CLEAN_MODE=true
        shift
        ;;
      --help|-h)
        show_help
        exit 0
        ;;
      *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
    esac
  done
fi

# If clean mode and no backends specified, clean all
if [ "$CLEAN_MODE" = true ] && [ ${#BACKENDS[@]} -eq 0 ]; then
  BACKENDS=("copilot" "claude" "gemini" "codex")
fi

# Execute clean scripts if clean mode is active
if [ "$CLEAN_MODE" = true ]; then
  for backend in "${BACKENDS[@]}"; do
    run_clean "$backend"
  done
  exit 0
fi

# Execute selected install scripts
for backend in "${BACKENDS[@]}"; do
  run_install "$backend"
done

# Copy configuration files
cat $SOURCE/.agentsignore | while read agent; do
    if ! grep -q "$agent" $LOCAL/.agentsignore; then
      echo "$agent" >> $LOCAL/.agentsignore
    fi
done

cat $SOURCE/.skillsignore | while read skill; do
    if ! grep -q "$skill" $LOCAL/.skillsignore; then
      echo "$skill" >> $LOCAL/.skillsignore
    fi
done

cat $SOURCE/.rulesignore | while read rule; do
    if ! grep -q "$rule" $LOCAL/.rulesignore; then
      echo "$rule" >> $LOCAL/.rulesignore
    fi
done



###########################################################################################




