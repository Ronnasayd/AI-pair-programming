#!/usr/bin/env bash
# Manage multiple Claude Code accounts by swapping oauthAccount/claudeAiOauth
# between saved profiles in ~/.claude/accounts and the live config files.
set -euo pipefail

CLAUDE_JSON="$HOME/.claude.json"
CREDENTIALS_JSON="$HOME/.claude/.credentials.json"
ACCOUNTS_DIR="$HOME/.claude/accounts"
BACKUPS_DIR="$HOME/.claude/backups"

log() { printf '%s\n' "$*" >&2; }
die() { log "error: $*"; exit 1; }

check_deps() {
    command -v jq >/dev/null 2>&1 || die "jq required, install it (e.g. apt install jq)"
    command -v fzf >/dev/null 2>&1 || die "fzf required, install it (e.g. apt install fzf)"
}

backup_file() {
    local f="$1"
    [ -f "$f" ] || return 0
    mkdir -p "$BACKUPS_DIR"
    local ts dest
    ts="$(date +%Y%m%d%H%M%S)"
    dest="$BACKUPS_DIR/$(basename "$f").bak.${ts}"
    cp -p "$f" "$dest"
    log "backup: $dest"
}

extract_mode() {
    check_deps
    mkdir -p "$ACCOUNTS_DIR"

    log "running: claude auth login"
    claude auth login

    [ -f "$CLAUDE_JSON" ] || die "$CLAUDE_JSON not found after login"
    [ -f "$CREDENTIALS_JSON" ] || die "$CREDENTIALS_JSON not found after login"

    local oauth_account claude_ai_oauth email
    oauth_account="$(jq -c '.oauthAccount' "$CLAUDE_JSON")"
    claude_ai_oauth="$(jq -c '.claudeAiOauth' "$CREDENTIALS_JSON")"

    [ "$oauth_account" = "null" ] && die "oauthAccount missing in $CLAUDE_JSON"
    [ "$claude_ai_oauth" = "null" ] && die "claudeAiOauth missing in $CREDENTIALS_JSON"

    email="$(jq -r '.emailAddress // .email // empty' <<<"$oauth_account")"
    [ -n "$email" ] || die "could not extract email from oauthAccount"

    local out="$ACCOUNTS_DIR/${email}.json"
    jq -n --argjson oauthAccount "$oauth_account" --argjson claudeAiOauth "$claude_ai_oauth" \
        '{oauthAccount: $oauthAccount, claudeAiOauth: $claudeAiOauth}' >"$out"
    chmod 600 "$out"

    log "saved: $out"
}

choose_mode() {
    check_deps
    [ -d "$ACCOUNTS_DIR" ] || die "no accounts saved yet, run extract mode first"

    local selected
    selected="$(find "$ACCOUNTS_DIR" -maxdepth 1 -name '*.json' -printf '%f\n' 2>/dev/null | sort | fzf --prompt="account> ")"
    [ -n "$selected" ] || die "no account selected"

    local account_file="$ACCOUNTS_DIR/$selected"
    local oauth_account claude_ai_oauth
    oauth_account="$(jq -c '.oauthAccount' "$account_file")"
    claude_ai_oauth="$(jq -c '.claudeAiOauth' "$account_file")"

    backup_file "$CLAUDE_JSON"
    backup_file "$CREDENTIALS_JSON"

    local tmp
    tmp="$(mktemp)"
    jq --argjson oauthAccount "$oauth_account" '.oauthAccount = $oauthAccount' "$CLAUDE_JSON" >"$tmp"
    mv "$tmp" "$CLAUDE_JSON"

    tmp="$(mktemp)"
    jq --argjson claudeAiOauth "$claude_ai_oauth" '.claudeAiOauth = $claudeAiOauth' "$CREDENTIALS_JSON" >"$tmp"
    mv "$tmp" "$CREDENTIALS_JSON"
    chmod 600 "$CREDENTIALS_JSON"

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
