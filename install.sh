#!/usr/bin/env bash
export ASDF_NODEJS_VERSION=23.11.1
SCRIPT_FILE="${BASH_SOURCE[0]}"


if [ -L "$SCRIPT_FILE" ]; then
  echo "Script already installed: $SCRIPT_FILE"
  echo "Building"
  SCRIPT_FILE="$(readlink -f "$SCRIPT_FILE")"
else
  if [ ! -L "/usr/local/bin/iai" ]; then
    echo "Running install script: $SCRIPT_FILE"
    SOURCE="$(pwd)"
    source "$SOURCE/scripts/installs/_generic.install.sh"
    install_tool "uv" "uv --version" "curl -LsSf https://astral.sh/uv/install.sh | sh"
    uv sync --project "$SOURCE" > /dev/null && echo "sync [ok]"
    uv run --project "$SOURCE" python3 -m spacy download pt_core_news_sm > /dev/null && echo "spacy pt model [ok]"
    uv run --project "$SOURCE" python3 -m spacy download en_core_web_sm > /dev/null && echo "spacy en model [ok]"
    # bash "$(pwd)/scripts/update-external-tools.sh"
    uv run --project "$SOURCE" python3 "$SOURCE/scripts/list_skills_agents.py" > /dev/null && echo "list skills [ok]"
    uv run --project "$SOURCE" python3 "$SOURCE/scripts/build-skill-index.py" > /dev/null && echo "build skills [ok]"
    sudo ln -s "$SOURCE/$SCRIPT_FILE" "/usr/local/bin/iai"
    sudo ln -s "$SOURCE/scripts/manage-ignore-files.py" "/usr/local/bin/mif"
    if [ -f ~/.bashrc ] && ! grep -q "source $SOURCE/.ai.alias.zshrc" ~/.bashrc; then
      echo "source $SOURCE/.ai.alias.zshrc" >> ~/.bashrc && echo ".ai.alias.zshrc add at .bashrc [ok]"
    fi
    if [ -f ~/.bashrc ] && ! grep -q "export AI_PROJECT_ROOT_DIR=\"$SOURCE\"" ~/.bashrc; then
      echo "export AI_PROJECT_ROOT_DIR=\"$SOURCE\"" >> ~/.bashrc && echo "AI_PROJECT_ROOT_DIR add at .bashrc [ok]"
    fi
    if [ -f ~/.zshrc ] && ! grep -q "source $SOURCE/.ai.alias.zshrc" ~/.zshrc; then
      echo "source $SOURCE/.ai.alias.zshrc" >> ~/.zshrc && echo ".ai.alias.zshrc add at .zshrc [ok]"
    fi
    if [ -f ~/.zshrc ] && ! grep -q "export AI_PROJECT_ROOT_DIR=\"$SOURCE\"" ~/.zshrc; then
      echo "export AI_PROJECT_ROOT_DIR=\"$SOURCE\"" >> ~/.zshrc && echo "AI_PROJECT_ROOT_DIR add at .zshrc [ok]"
    fi

    if [ -f ~/.bashrc ] && ! grep -q "export PATH=$HOME/.local/bin:$PATH" ~/.bashrc; then
      echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.bashrc
    fi
    if [ -f ~/.zshrc ] && ! grep -q "export PATH=$HOME/.local/bin:$PATH" ~/.zshrc; then
      echo "export PATH=$HOME/.local/bin:$PATH" >> ~/.zshrc
    fi

    

    install_tool "serena" "serena --version" "uv tool install serena-agent" "serena init"
    install_tool "rtk" "rtk --version" "curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh" "rtk init"
    install_tool "rag-rat" "rag-rat --version" "sudo apt install cargo && cargo install rag-rat"
    install_tool "bat" "bat --version" "sudo apt install bat"
    install_tool "jq" "jq --version" "sudo apt install jq"
    install_tool "ai-memory" "ai-memory --version" "mkdir -p ~/.local/bin && curl -fsSL https://raw.githubusercontent.com/akitaonrails/ai-memory/main/bin/ai-memory -o ~/.local/bin/ai-memory && chmod +x ~/.local/bin/ai-memory"

    echo "Use the command: iai --help"
    exit 0
  fi
fi

export SOURCE="$(dirname "$SCRIPT_FILE")"
export LOCAL="$(pwd)"
# echo $SOURCE
# echo $LOCAL

# Shared git_exclude / git_path helpers (resolve real .git dir, handle subdirs).
source "$SOURCE/scripts/_git-exclude.sh"
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
  BACKENDS=("copilot" "claude" "gemini" "codex" "antigravity" "taskmaster" "gitignore")
else
  while [[ $# -gt 0 ]]; do
    case $1 in
      --all)
        BACKENDS=("copilot" "claude" "gemini" "codex" "antigravity" "taskmaster" "gitignore")
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
      --antigravity)
        BACKENDS+=("antigravity")
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
  BACKENDS=("copilot" "claude" "gemini" "codex" "antigravity" "taskmaster" "gitignore")
fi

# Execute clean scripts if clean mode is active
if [ "$CLEAN_MODE" = true ]; then
  rm -rf $LOCAL/skills-lock.json
  for backend in "${BACKENDS[@]}"; do
    run_clean "$backend"
  done
  exit 0
fi

# Execute selected install scripts
for backend in "${BACKENDS[@]}"; do
  run_install "$backend"
done

ai-memory install-skills > /dev/null 2>&1 && echo "ia-memory install-skills [ok]"

git_exclude ".agents/skills/*" "skills-lock.json"

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

echo "Done!"


###########################################################################################




