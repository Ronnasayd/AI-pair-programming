#!/bin/bash

# Cross-platform package install: picks the available package manager.
# Usage: pkg_install <package_name>
pkg_install() {
    local pkg="$1"
    if command -v pkg &> /dev/null; then
        pkg install -y "$pkg"
    elif command -v apt &> /dev/null; then
        sudo apt install -y "$pkg"
    elif command -v brew &> /dev/null; then
        brew install "$pkg"
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm "$pkg"
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y "$pkg"
    else
        echo "No supported package manager found for '$pkg'." >&2
        return 1
    fi
}

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
        echo "Installing by command \"$install_cmd\""
        eval "$install_cmd"
        echo "$bin_name [ok]"
        [[ -n "$post_install_cmd" ]] && eval "$post_install_cmd"
    else
        echo "Installation cancelled by user."
        exit 1
    fi
}
