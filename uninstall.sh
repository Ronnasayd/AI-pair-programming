#!/usr/bin/env bash
set -euo pipefail

SCRIPT_FILE="${BASH_SOURCE[0]}"
if [ -L "$SCRIPT_FILE" ]; then
  SCRIPT_FILE="$(readlink -f "$SCRIPT_FILE")"
fi
SOURCE="$(cd "$(dirname "$SCRIPT_FILE")" && pwd)"

echo "Uninstalling from: $SOURCE"

# Remove all backend symlinks/configs via existing clean scripts.
"$SOURCE/install.sh" --clean --all

# Remove global command symlinks.
for bin in /usr/local/bin/iai /usr/local/bin/mif; do
  if [ -L "$bin" ]; then
    sudo rm "$bin" && echo "Removed $bin"
  fi
done

# Strip lines this project's install.sh injected into shell rc files.
strip_lines() {
  local rc="$1"
  [ -f "$rc" ] || return 0
  if grep -qF "$SOURCE/.ai.alias.zshrc" "$rc" || grep -qF "AI_PROJECT_ROOT_DIR=\"$SOURCE\"" "$rc"; then
    sed -i.bak \
      -e "\#source $SOURCE/.ai.alias.zshrc#d" \
      -e "\#export AI_PROJECT_ROOT_DIR=\"$SOURCE\"#d" \
      "$rc"
    echo "Cleaned $rc (backup: $rc.bak)"
  fi
}

strip_lines ~/.bashrc
strip_lines ~/.zshrc

echo "Uninstall complete."
