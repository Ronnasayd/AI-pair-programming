#!/usr/bin/env bash
# Cron job: for each saved Claude account, check session usage.
# If usage is 0%, fire a trivial prompt to start the 5h session clock.
# Run every 10min: */10 * * * * /path/to/claude.warmup.sh >> /tmp/warmup.log 2>&1
set -euo pipefail

# Cron uses a minimal PATH and won't see ~/.local/bin (where `claude` lives) or jq.
export PATH="$HOME/.local/bin:$PATH"

CLAUDE_JSON="$HOME/.claude.json"
CREDENTIALS_JSON="$HOME/.claude/.credentials.json"
ACCOUNTS_DIR="$HOME/.claude/accounts"

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

command -v jq >/dev/null 2>&1 || { log "error: jq required"; exit 1; }
command -v claude >/dev/null 2>&1 || { log "error: claude CLI required"; exit 1; }

[ -d "$ACCOUNTS_DIR" ] || { log "error: $ACCOUNTS_DIR not found"; exit 1; }

# Remember which account is currently live so we can restore it at the end.
original_email=""
if [ -f "$CLAUDE_JSON" ]; then
    original_email="$(jq -r '.oauthAccount.emailAddress // .oauthAccount.email // empty' "$CLAUDE_JSON")"
fi

load_account() {
    local account_file="$1"
    local oauth_account claude_ai_oauth tmp
    oauth_account="$(jq -c '.oauthAccount' "$account_file")"
    claude_ai_oauth="$(jq -c '.claudeAiOauth' "$account_file")"

    tmp="$(mktemp)"
    jq --argjson oauthAccount "$oauth_account" '.oauthAccount = $oauthAccount' "$CLAUDE_JSON" >"$tmp"
    mv "$tmp" "$CLAUDE_JSON"

    tmp="$(mktemp)"
    jq --argjson claudeAiOauth "$claude_ai_oauth" '.claudeAiOauth = $claudeAiOauth' "$CREDENTIALS_JSON" >"$tmp"
    mv "$tmp" "$CREDENTIALS_JSON"
    chmod 600 "$CREDENTIALS_JSON"
}

for account_file in "$ACCOUNTS_DIR"/*.json; do
    email="$(basename "$account_file" .json)"
    load_account "$account_file"

    usage="$(claude -p "/usage" | grep "Current session:" | grep -oP '\d+(?=% used)' || true)"

    if [ -z "$usage" ]; then
        log "$email: could not read usage, skipping"
        continue
    fi

    if [ "$usage" -eq 0 ]; then
        log "$email: usage 0%, warming up session"
        claude -p "hello" >/dev/null
    else
        log "$email: usage ${usage}%, ok"
    fi
done

# Restore the account that was active before this script ran.
if [ -n "$original_email" ] && [ -f "$ACCOUNTS_DIR/${original_email}.json" ]; then
    load_account "$ACCOUNTS_DIR/${original_email}.json"
fi
