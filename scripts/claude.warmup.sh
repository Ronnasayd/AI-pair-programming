#!/usr/bin/env bash
# Cron job: for each saved Claude account, check session usage.
# If usage is 0%, fire a trivial prompt to start the 5h session clock.
# Execute this script every 30 minutes to keep sessions alive.
# SCRIPT="$HOME/develop/personal/AI-pair-programming/scripts/claude.warmup.sh"
# CRON_LINE="*/30 * * * * $SCRIPT >> /tmp/warmup.log 2>&1"
# ( crontab -l 2>/dev/null | grep -vF "$SCRIPT" ; echo "$CRON_LINE" ) | crontab -
set -euo pipefail

# Cron uses a minimal PATH and won't see ~/.local/bin (where `claude` lives) or jq.
export PATH="$HOME/.local/bin:$PATH"

CLAUDE_JSON="$HOME/.claude.json"
ACCOUNTS_DIR="$HOME/.claude/accounts"
ACCOUNTS_SCRIPT="$(dirname "$0")/claude.accounts.sh"

log() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }

command -v jq >/dev/null 2>&1 || { log "error: jq required"; exit 1; }
command -v claude >/dev/null 2>&1 || { log "error: claude CLI required"; exit 1; }

[ -d "$ACCOUNTS_DIR" ] || { log "error: $ACCOUNTS_DIR not found"; exit 1; }

# Remember which account is currently live so we can restore it at the end.
original_email=""
if [ -f "$CLAUDE_JSON" ]; then
    original_email="$(jq -r '.oauthAccount.emailAddress // .oauthAccount.email // empty' "$CLAUDE_JSON")"
fi

for account_file in "$ACCOUNTS_DIR"/*.json; do
    email="$(basename "$account_file" .json)"
    "$ACCOUNTS_SCRIPT" choose "$email" >/dev/null

    usage="$(claude -p "/usage" | grep "Current session:" | grep -oP '\d+(?=% used)' || true)"

    if [ -z "$usage" ]; then
        log "$email: could not read usage, skipping"
        continue
    fi

    if [ "$usage" -eq 0 ]; then
        log "$email: usage 0%, warming up session"
        claude --model haiku -p "hello" >/dev/null
    else
        log "$email: usage ${usage}%, ok"
    fi
done

# Restore the account that was active before this script ran.
if [ -n "$original_email" ] && [ -f "$ACCOUNTS_DIR/${original_email}.json" ]; then
    "$ACCOUNTS_SCRIPT" choose "$original_email" >/dev/null
fi
