#!/usr/bin/env bash
# Cron job: for each saved Claude account, check session usage.
# If usage is 0%, fire a trivial prompt to start the 5h session clock.
# Execute this script every 30 minutes to keep sessions alive.
# SCRIPT="$AI_PROJECT_ROOT_DIR/scripts/claude.warmup.sh"
# CRON_LINE="*/30 * * * * $SCRIPT >> /tmp/warmup.log 2>&1"
# ( crontab -l 2>/dev/null | grep -vF "$SCRIPT" ; echo "$CRON_LINE" ) | crontab -
set -euo pipefail

# Project root derived from this script's own location (scripts/.. ), not from
# AI_PROJECT_ROOT_DIR — cron runs a non-login shell where that env var isn't set yet.
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Cron runs a non-interactive, non-login shell, so ~/.bashrc's "not interactive -> return"
# guard skips every export in it (CLAUDE_CONFIG_DIR, PATH additions, etc). Re-exec this
# script through an interactive login shell once, but only when those exports are
# actually missing, so a manual `bash claude.warmup.sh` run doesn't pay for it twice.
if [ -z "${WARMUP_REEXECED:-}" ] && [ -z "${CLAUDE_CONFIG_DIR:-}" ]; then
    export WARMUP_REEXECED=1
    exec bash -lic "$(printf '%q ' "$0" "$@")"
fi

CLAUDE_CONFIG_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
ACCOUNTS_DIR="$CLAUDE_CONFIG_DIR/accounts"
LOCK_FILE="${TMPDIR:-/tmp}/claude.warmup.lock"
WARMUP_TMP_ROOT="${TMPDIR:-/tmp}/claude-warmup-configs"

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

command -v jq >/dev/null 2>&1 || { log "error: jq required"; exit 1; }
command -v claude >/dev/null 2>&1 || { log "error: claude CLI required"; exit 1; }
command -v flock >/dev/null 2>&1 || { log "error: flock required"; exit 1; }

[ -d "$ACCOUNTS_DIR" ] || { log "error: $ACCOUNTS_DIR not found"; exit 1; }

exec 9>"$LOCK_FILE"
flock -n 9 || { log "error: another warmup run is already in progress, skipping"; exit 0; }

# Each account warms up inside its own throwaway copy of CLAUDE_CONFIG_DIR, under
# /tmp — never touching $CLAUDE_CONFIG_DIR itself. That dir may be the one the
# user has open in an interactive session right now; mutating it in place (the
# old approach, via claude.accounts.sh choose) would swap credentials out from
# under that live session.
rm -rf "$WARMUP_TMP_ROOT"
trap 'rm -rf "$WARMUP_TMP_ROOT"' EXIT

for account_file in "$ACCOUNTS_DIR"/*.json; do
    email="$(basename "$account_file" .json)"
    account_tmp_dir="$WARMUP_TMP_ROOT/$email"

    mkdir -p "$account_tmp_dir"
    cp -R "$CLAUDE_CONFIG_DIR/." "$account_tmp_dir/" 2>/dev/null || true

    oauth_account="$(jq -c '.oauthAccount' "$account_file")"
    claude_ai_oauth="$(jq -c '.claudeAiOauth' "$account_file")"

    tmp_claude_json="$account_tmp_dir/.claude.json"
    tmp_credentials_json="$account_tmp_dir/.credentials.json"

    [ -f "$tmp_claude_json" ] || echo '{}' >"$tmp_claude_json"
    jq --argjson oauthAccount "$oauth_account" '.oauthAccount = $oauthAccount' \
        "$tmp_claude_json" >"$tmp_claude_json.new"
    mv "$tmp_claude_json.new" "$tmp_claude_json"

    [ -f "$tmp_credentials_json" ] || echo '{}' >"$tmp_credentials_json"
    jq --argjson claudeAiOauth "$claude_ai_oauth" '.claudeAiOauth = $claudeAiOauth' \
        "$tmp_credentials_json" >"$tmp_credentials_json.new"
    mv "$tmp_credentials_json.new" "$tmp_credentials_json"
    chmod 600 "$tmp_credentials_json"

    usage="$(CLAUDE_CONFIG_DIR="$account_tmp_dir" claude -p "/usage" | grep "Current session:" | grep -oP '\d+(?=% used)' || true)"

    if [ -z "$usage" ]; then
        log "$email: could not read usage, skipping"
        rm -rf "$account_tmp_dir"
        continue
    fi

    if [ "$usage" -eq 0 ]; then
        log "$email: usage 0%, warming up session"
        CLAUDE_CONFIG_DIR="$account_tmp_dir" claude --model haiku -p "hello" >/dev/null
    else
        log "$email: usage ${usage}%, ok"
    fi

    rm -rf "$account_tmp_dir"
done
