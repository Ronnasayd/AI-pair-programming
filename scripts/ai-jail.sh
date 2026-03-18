#!/bin/bash

# ai-jail — bubblewrap sandbox for AI coding agents
# Mounts the project dir read-write, auto-discovers home dotfiles with a
# deny-list for sensitive dirs, and isolates namespaces.
#
# Usage: ai-jail [--map PATH]... COMMAND [ARGS...]
#        ai-jail claude
#        ai-jail bash

PROJECT_DIR=$(pwd)
TEMP_HOSTS=$(mktemp /tmp/bwrap-hosts.XXXXXX)

trap 'rm -f "$TEMP_HOSTS"' EXIT

# ── Mise discovery ─────────────────────────────────────────────
REAL_MISE_BIN=$(type -p mise 2>/dev/null || echo "")

# ── Localhost fix (Go resolver needs /etc/hosts) ───────────────
printf '127.0.0.1 localhost ai-sandbox\n::1       localhost ai-sandbox\n' > "$TEMP_HOSTS"

# ── Parse --map / --rw-map arguments ─────────────────────────
EXTRA_MOUNTS=()
while [[ "${1:-}" == --map || "${1:-}" == --rw-map ]]; do
    FLAG="$1"
    MAP_PATH="$2"
    if [ -e "$MAP_PATH" ]; then
        if [[ "$FLAG" == "--rw-map" ]]; then
            EXTRA_MOUNTS+=("--bind" "$MAP_PATH" "$MAP_PATH")
        else
            EXTRA_MOUNTS+=("--ro-bind" "$MAP_PATH" "$MAP_PATH")
        fi
    else
        echo "Warning: Path $MAP_PATH not found, skipping." >&2
    fi
    shift 2
done

# ── Mise init command ──────────────────────────────────────────
if [ -n "$REAL_MISE_BIN" ]; then
    MISE_INIT="$REAL_MISE_BIN trust && eval \"\$($REAL_MISE_BIN activate bash)\" && eval \"\$($REAL_MISE_BIN env)\""
else
    MISE_INIT="true"
fi

# ── Dotfile deny-list (never mounted — sensitive data) ─────────
DOTDIR_DENY=(.gnupg .aws .mozilla .basilisk-dev .sparrow .ssh)

# Subdirs of ~/.config to hide (tmpfs over rw config mount)
CONFIG_DENY=(BraveSoftware Bitwarden)

# Subdirs of ~/.cache to hide (sensitive browser/app caches)
CACHE_DENY=(BraveSoftware basilisk-dev chromium spotify nvidia mesa_shader_cache)

# Dotdirs requiring read-write access
DOTDIR_RW=(.claude .crush .codex .aider .config .cargo .cache .docker .github)

# ── Helper functions ───────────────────────────────────────────
is_denied() {
    local name="$1"
    for d in "${DOTDIR_DENY[@]}"; do [[ "$name" == "$d" ]] && return 0; done
    return 1
}

is_rw() {
    local name="$1"
    for d in "${DOTDIR_RW[@]}"; do [[ "$name" == "$d" ]] && return 0; done
    return 1
}

# ── Auto-discover dot-directories in $HOME ─────────────────────
# Only directories — regular dotfiles (e.g. .claude.json) are NOT mounted.
# The tmpfs $HOME is writable so tools can create dotfiles as needed.
DOTFILE_MOUNTS=()
for entry in "$HOME"/.*; do
    [ -d "$entry" ] || continue
    name=$(basename "$entry")
    [[ "$name" == "." || "$name" == ".." ]] && continue
    is_denied "$name" && continue

    if is_rw "$name"; then
        DOTFILE_MOUNTS+=("--bind" "$entry" "$HOME/$name")
    else
        DOTFILE_MOUNTS+=("--ro-bind" "$entry" "$HOME/$name")
    fi
done

# ── Explicit dotfile mounts (regular files) ────────────────────
[ -f "$HOME/.gitconfig" ] && DOTFILE_MOUNTS+=("--ro-bind" "$HOME/.gitconfig" "$HOME/.gitconfig")
[ -f "$HOME/.claude.json" ] && DOTFILE_MOUNTS+=("--bind" "$HOME/.claude.json" "$HOME/.claude.json")

# ── Hide sensitive subdirs inside ~/.config (after rw mount) ───
CONFIG_HIDE_MOUNTS=()
for denied in "${CONFIG_DENY[@]}"; do
    [ -d "$HOME/.config/$denied" ] && CONFIG_HIDE_MOUNTS+=("--tmpfs" "$HOME/.config/$denied")
done

# ── Hide sensitive subdirs inside ~/.cache (after rw mount) ──
CACHE_HIDE_MOUNTS=()
for denied in "${CACHE_DENY[@]}"; do
    [ -d "$HOME/.cache/$denied" ] && CACHE_HIDE_MOUNTS+=("--tmpfs" "$HOME/.cache/$denied")
done

# ── Override ~/.local subdirs as rw (parent .local is ro) ──────
LOCAL_OVERRIDES=()
[ -d "$HOME/.local/state" ] && LOCAL_OVERRIDES+=("--bind" "$HOME/.local/state" "$HOME/.local/state")
for rw_share in zoxide crush opencode atuin mise yarn flutter kotlin NuGet pipx ruby-advisory-db uv; do
    [ -d "$HOME/.local/share/$rw_share" ] && LOCAL_OVERRIDES+=("--bind" "$HOME/.local/share/$rw_share" "$HOME/.local/share/$rw_share")
done

# ── GPU device mounts (NVIDIA + DRM) ─────────────────────────
GPU_MOUNTS=()
for dev in /dev/nvidia* /dev/dri; do
    [ -e "$dev" ] && GPU_MOUNTS+=("--dev-bind" "$dev" "$dev")
done

# ── Docker socket ────────────────────────────────────────────
DOCKER_MOUNT=()
[ -S /var/run/docker.sock ] && DOCKER_MOUNT+=("--bind" "/var/run/docker.sock" "/var/run/docker.sock")

# ── Shared memory (Chromium needs large /dev/shm) ───────────
SHM_MOUNT=()
[ -d /dev/shm ] && SHM_MOUNT+=("--dev-bind" "/dev/shm" "/dev/shm")

# ── Display passthrough (X11 + Wayland) ─────────────────────
DISPLAY_MOUNTS=()
DISPLAY_ENV=()

# X11 / XWayland socket
[ -d /tmp/.X11-unix ] && DISPLAY_MOUNTS+=("--bind" "/tmp/.X11-unix" "/tmp/.X11-unix")
[ -n "${DISPLAY:-}" ] && DISPLAY_ENV+=("--setenv" "DISPLAY" "$DISPLAY")
[ -n "${XAUTHORITY:-}" ] && {
    DISPLAY_MOUNTS+=("--ro-bind" "$XAUTHORITY" "$XAUTHORITY")
    DISPLAY_ENV+=("--setenv" "XAUTHORITY" "$XAUTHORITY")
}

# Wayland socket (lives in XDG_RUNTIME_DIR, typically /run/user/UID)
if [ -n "${XDG_RUNTIME_DIR:-}" ] && [ -d "$XDG_RUNTIME_DIR" ]; then
    DISPLAY_MOUNTS+=("--bind" "$XDG_RUNTIME_DIR" "$XDG_RUNTIME_DIR")
    DISPLAY_ENV+=("--setenv" "XDG_RUNTIME_DIR" "$XDG_RUNTIME_DIR")
    [ -n "${WAYLAND_DISPLAY:-}" ] && DISPLAY_ENV+=("--setenv" "WAYLAND_DISPLAY" "$WAYLAND_DISPLAY")
fi

# ── Assemble and launch ───────────────────────────────────────
echo "Jail Active: $PROJECT_DIR"

bwrap \
  --ro-bind /usr /usr \
  --symlink usr/bin /bin \
  --ro-bind /lib /lib \
  --ro-bind /lib64 /lib64 \
  --ro-bind /etc /etc \
  --ro-bind "$TEMP_HOSTS" /etc/hosts \
  --ro-bind /opt /opt \
  --ro-bind /sys /sys \
  --dev /dev \
  "${GPU_MOUNTS[@]}" \
  "${SHM_MOUNT[@]}" \
  --proc /proc \
  --tmpfs /tmp \
  --tmpfs /run \
  "${DOCKER_MOUNT[@]}" \
  "${DISPLAY_MOUNTS[@]}" \
  --tmpfs "$HOME" \
  "${DOTFILE_MOUNTS[@]}" \
  "${CONFIG_HIDE_MOUNTS[@]}" \
  "${CACHE_HIDE_MOUNTS[@]}" \
  "${LOCAL_OVERRIDES[@]}" \
  "${EXTRA_MOUNTS[@]}" \
  --bind "$PROJECT_DIR" "$PROJECT_DIR" \
  --chdir "$PROJECT_DIR" \
  --die-with-parent \
  --unshare-pid \
  --unshare-uts \
  --unshare-ipc \
  --hostname "ai-sandbox" \
  "${DISPLAY_ENV[@]}" \
  --setenv PS1 "(jail) \w \$ " \
  --setenv _ZO_DOCTOR 0 \
  bash -c "$MISE_INIT && ${*:-bash}"
