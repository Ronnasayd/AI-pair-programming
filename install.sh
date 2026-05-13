#!/usr/bin/env bash

SCRIPT_FILE="${BASH_SOURCE[0]}"
echo "Running install script: $SCRIPT_FILE"

if [ -L "$SCRIPT_FILE" ]; then
  SCRIPT_FILE="$(readlink -f "$SCRIPT_FILE")"
else
  if [ ! -L "/usr/local/bin/init-ai" ]; then
    sudo ln -s "$(pwd)/$SCRIPT_FILE" "/usr/local/bin/init-ai"
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
  --help, -h     Display this help message

Examples:
  $0 --all                    # Install all backends
  $0 --copilot --claude       # Install only copilot and claude
  $0 --gemini                 # Install only gemini

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

# Parse arguments
BACKENDS=()

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

# Execute selected install scripts
for backend in "${BACKENDS[@]}"; do
  run_install "$backend"
done

# Copy configuration files
if [ ! -L "$LOCAL/.agentsignore" ] && [ ! -f "$LOCAL/.agentsignore" ]; then
  cp $SOURCE/.agentsignore $LOCAL/.agentsignore
fi

if [ ! -L "$LOCAL/.skillsignore" ] && [ ! -f "$LOCAL/.skillsignore" ]; then
  cp $SOURCE/.skillsignore $LOCAL/.skillsignore
fi

###########################################################################################




