#!/usr/bin/env bash
# Manage multiple Claude Code accounts by swapping oauthAccount/claudeAiOauth
# between saved profiles in ~/.claude/accounts and the live config files.
set -euo pipefail

CLAUDE_JSON="$HOME/.claude.json"
CREDENTIALS_JSON="$HOME/.claude/.credentials.json"
ACCOUNTS_DIR="$HOME/.claude/accounts"
BACKUPS_DIR="$HOME/.claude/backups"
KEYCHAIN_SERVICE="Claude Code-credentials"

log() { printf '%s\n' "$*" >&2; }
die() { log "error: $*"; exit 1; }

check_deps() {
    command -v jq >/dev/null 2>&1 || die "jq required, install it (e.g. apt install jq)"
    command -v fzf >/dev/null 2>&1 || die "fzf required, install it (e.g. apt install fzf)"
    if [ "$(uname -s)" = "Darwin" ]; then
        command -v security >/dev/null 2>&1 || die "security (macOS Keychain CLI) required"
    fi
}

# On macOS, claudeAiOauth lives in the Keychain (service "Claude Code-credentials"),
# not in $CREDENTIALS_JSON. These wrappers abstract the storage backend.
read_claude_ai_oauth() {
    if [ "$(uname -s)" = "Darwin" ]; then
        security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null || echo "null"
    else
        [ -f "$CREDENTIALS_JSON" ] || { echo "null"; return; }
        jq -c '.claudeAiOauth' "$CREDENTIALS_JSON"
    fi
}

write_claude_ai_oauth() {
    local claude_ai_oauth="$1"
    if [ "$(uname -s)" = "Darwin" ]; then
        security delete-generic-password -s "$KEYCHAIN_SERVICE" >/dev/null 2>&1 || true
        security add-generic-password -s "$KEYCHAIN_SERVICE" -a "$USER" -w "$claude_ai_oauth" -U
    else
        backup_file "$CREDENTIALS_JSON"
        local tmp
        tmp="$(mktemp)"
        jq --argjson claudeAiOauth "$claude_ai_oauth" '.claudeAiOauth = $claudeAiOauth' "$CREDENTIALS_JSON" >"$tmp"
        mv "$tmp" "$CREDENTIALS_JSON"
        chmod 600 "$CREDENTIALS_JSON"
    fi
}

backup_file() {
    local f="$1"
    [ -f "$f" ] || return 0
    mkdir -p "$BACKUPS_DIR"
    local dest
    dest="$BACKUPS_DIR/$(basename "$f").bak"
    cp -p "$f" "$dest"
    log "backup: $dest"
}


save_current_account() {
    [ -f "$CLAUDE_JSON" ] || return 0

    local oauth_account claude_ai_oauth email
    oauth_account="$(jq -c '.oauthAccount' "$CLAUDE_JSON")"
    claude_ai_oauth="$(read_claude_ai_oauth)"

    [ "$oauth_account" = "null" ] && return 0
    [ "$claude_ai_oauth" = "null" ] && return 0

    email="$(jq -r '.emailAddress // .email // empty' <<<"$oauth_account")"
    [ -n "$email" ] || return 0

    local out="$ACCOUNTS_DIR/${email}.json"
    jq -n --argjson oauthAccount "$oauth_account" --argjson claudeAiOauth "$claude_ai_oauth" \
        '{oauthAccount: $oauthAccount, claudeAiOauth: $claudeAiOauth}' >"$out"
    chmod 600 "$out"

    log "saved current account state (latest refresh token): $out"
}

extract_mode() {
    check_deps
    mkdir -p "$ACCOUNTS_DIR"

    log "running: claude auth login"
    claude auth login

    save_current_account
}

choose_mode() {
    check_deps
    [ -d "$ACCOUNTS_DIR" ] || die "no accounts saved yet, run extract mode first"

    save_current_account

    local selected
    selected="$(find "$ACCOUNTS_DIR" -maxdepth 1 -name '*.json' -exec basename {} \; 2>/dev/null | sort | fzf --prompt="account> ")"
    [ -n "$selected" ] || die "no account selected"

    local account_file="$ACCOUNTS_DIR/$selected"
    local oauth_account claude_ai_oauth
    oauth_account="$(jq -c '.oauthAccount' "$account_file")"
    claude_ai_oauth="$(jq -c '.claudeAiOauth' "$account_file")"

    backup_file "$CLAUDE_JSON"

    local tmp
    tmp="$(mktemp)"
    jq --argjson oauthAccount "$oauth_account" '.oauthAccount = $oauthAccount' "$CLAUDE_JSON" >"$tmp"
    mv "$tmp" "$CLAUDE_JSON"

    write_claude_ai_oauth "$claude_ai_oauth"

    log "switched to account: $selected"
}

usage() {
    cat <<EOF
Usage: $(basename "$0") <extract|choose>

  extract   Run 'claude auth login', then save oauthAccount/claudeAiOauth
            into $ACCOUNTS_DIR/<email>.json
  choose    Pick a saved account and load it into
            $CLAUDE_JSON and $CREDENTIALS_JSON
EOF
}

main() {
    case "${1:-}" in
        extract) extract_mode ;;
        choose) choose_mode ;;
        *) usage; exit 1 ;;
    esac
}

main "$@"
