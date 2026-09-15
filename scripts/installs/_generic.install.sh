#!/bin/bash

# Generic installer helper: checks if a CLI is present, prompts to install if not.
# Usage: install_tool <bin_name> <version_cmd> <install_cmd> [post_install_cmd]
install_tool() {
    local bin_name="$1"
    local version_cmd="$2"
    local install_cmd="$3"
    local post_install_cmd="${4:-}"

    if command -v "$bin_name" &> /dev/null; then
        echo "$bin_name already installed. Version: $(eval "$version_cmd")"
        return 0
    fi

    echo "'$bin_name' not found."
    read -p "Install $bin_name now? [Y/n]: " answer
    answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]' | xargs)

    if [[ -z "$answer" || "$answer" == "y"* ]]; then
        echo "Installing by command $install_cmd"
        eval "$install_cmd"
        echo "$bin_name [ok]"
        [[ -n "$post_install_cmd" ]] && eval "$post_install_cmd"
    else
        echo "Installation cancelled by user."
        exit 1
    fi
}
