#!/bin/bash

# Claude Code Subagent Status Line Script
# Renders one custom row per visible subagent in the agent panel.
#
# Configured via the `subagentStatusLine` setting. Receives a single JSON
# object on stdin with the base hook fields, a `columns` field (usable row
# width) and a `tasks` array. Each task has: id, name, type, status,
# description, label, startTime, model, effort, contextWindowSize,
# tokenCount, tokenSamples, cwd.
#
# Output: one JSON line per row to override, {"id": "...", "content": "..."}.
# Omit a task's id to keep its default rendering; empty content hides it.
#
# Mirrors scripts/statusline-command.sh: same Catppuccin Frappe palette,
# fmt_k helper, 20-segment context bar and effort colour scheme.

NERD_FONT="${NERD_FONT:-1}"

if [ "$NERD_FONT" = "1" ]; then
    ICON_EFFORT=$'\U0000EE9C'
    ICON_MODEL=$'\U000F06A9'
    ICON_CTX=$'\U000F125F'
    ICON_TOKEN=$'\U0000EB7E'
    ICON_CLOCK=$'⏱'
    ICON_RUN=$'\U000F0450'
    ICON_OK=$'\U0000F00C'
    ICON_ERR=$'\U0000EA87'
    ICON_WAIT=$'\U000F04E6'
else
    ICON_EFFORT="🧠" ICON_MODEL="🤖" ICON_CTX="📚" ICON_TOKEN="🎟" ICON_CLOCK="⏱"
    ICON_RUN="▶" ICON_OK="✓" ICON_ERR="✗" ICON_WAIT="⏸"
fi

# Catppuccin Frappe (24-bit true color)
C_RED="\033[38;2;231;130;132m"
C_YELLOW="\033[38;2;229;200;144m"
C_GREEN="\033[38;2;166;209;137m"
C_BLUE="\033[38;2;140;170;238m"
C_MAUVE="\033[38;2;202;158;230m"
C_LAVENDER="\033[38;2;186;187;241m"
C_SUBTEXT="\033[38;2;165;173;206m"
RESET="\033[0m"

SEP=" • "

input=$(cat)

# Format a token count: k-suffixed when > 1000, raw otherwise
fmt_k() {
    if [ "$1" -gt 1000 ] 2>/dev/null; then
        echo "$(( $1 / 1000 ))k"
    else
        echo "$1"
    fi
}

now_epoch=$(date +%s)
task_count=$(echo "$input" | jq -r '.tasks | length')
[ -z "$task_count" ] && task_count=0

i=0
while [ "$i" -lt "$task_count" ]; do
    task=$(echo "$input" | jq -c ".tasks[$i]")
    i=$(( i + 1 ))

    id=$(echo "$task" | jq -r '.id // empty')
    [ -z "$id" ] && continue

    name=$(echo "$task"   | jq -r '.name // "agent"')
    type=$(echo "$task"   | jq -r '.type // empty')
    status=$(echo "$task" | jq -r '.status // empty')
    model=$(echo "$task"  | jq -r '.model // empty')
    effort=$(echo "$task" | jq -r '.effort // empty')
    ctx_size=$(echo "$task"  | jq -r '.contextWindowSize // 0')
    tok=$(echo "$task"       | jq -r '.tokenCount // 0')
    start=$(echo "$task"     | jq -r '.startTime // empty')

    # --- status icon ---
    case "$status" in
        running|in_progress|active) status_seg="${C_BLUE}${ICON_RUN}${RESET}" ;;
        completed|done|success)     status_seg="${C_GREEN}${ICON_OK}${RESET}" ;;
        error|failed)               status_seg="${C_RED}${ICON_ERR}${RESET}" ;;
        *)                          status_seg="${C_SUBTEXT}${ICON_WAIT}${RESET}" ;;
    esac

    # --- name + type (type dim, skipped when identical to name) ---
    name_seg="${C_MAUVE}${name}${RESET}"
    if [ -n "$type" ] && [ "$type" != "$name" ]; then
        name_seg="${name_seg} ${C_SUBTEXT}${type}${RESET}"
    fi

    # --- model short: strip claude- prefix, -YYYYMMDD date, [..] suffix ---
    model_seg=""
    if [ -n "$model" ]; then
        m=$(echo "$model" | sed -E 's/^claude-//; s/-[0-9]{8}//; s/\[[^]]*\]//')
        model_seg="${SEP}${ICON_MODEL} ${C_LAVENDER}${m}${RESET}"
    fi

    # --- effort (colour matches main status line) ---
    effort_seg=""
    if [ -n "$effort" ]; then
        case "$effort" in
            low)            ec="$C_GREEN" ;;
            medium)         ec="$C_YELLOW" ;;
            high|xhigh|max) ec="$C_RED" ;;
            *)              ec="$C_SUBTEXT" ;;  # numeric token budget
        esac
        effort_seg="${SEP}${ICON_EFFORT} ${ec}${effort}${RESET}"
    fi

    # --- context bar (20 segments, 5% each) ---
    ctx_seg=""
    if [ "$ctx_size" -gt 0 ] 2>/dev/null; then
        ctx_pct=$(( tok * 100 / ctx_size ))
        [ "$ctx_pct" -gt 100 ] && ctx_pct=100
        if [ "$ctx_pct" -ge 80 ]; then cc="$C_RED"
        elif [ "$ctx_pct" -ge 50 ]; then cc="$C_YELLOW"
        else cc="$C_MAUVE"; fi
        filled=$(( ctx_pct / 5 ))
        [ "$filled" -gt 20 ] && filled=20
        [ "$filled" -lt 0 ] && filled=0
        bar=""
        for s in $(seq 1 20); do
            if [ "$s" -le "$filled" ]; then bar="${bar}█"; else bar="${bar}░"; fi
        done
        ctx_seg="${SEP}${ICON_CTX} ${cc}${bar}${RESET} ${cc}${ctx_pct}%${RESET}"
    fi

    # --- tokens ---
    tok_seg="${SEP}${ICON_TOKEN} $(fmt_k "$tok")"

    # --- elapsed since startTime (epoch seconds or ISO-8601) ---
    elapsed_seg=""
    if [ -n "$start" ]; then
        if echo "$start" | grep -qE '^[0-9]+$'; then
            start_epoch=$(( start > 9999999999 ? start / 1000 : start ))
        else
            start_epoch=$(date -d "$start" +%s 2>/dev/null || echo "")
        fi
        if [ -n "$start_epoch" ]; then
            e=$(( now_epoch - start_epoch ))
            [ "$e" -lt 0 ] && e=0
            if [ "$e" -ge 3600 ]; then
                elapsed_seg="${SEP}${ICON_CLOCK} $(( e / 3600 ))h$(( (e % 3600) / 60 ))m"
            elif [ "$e" -ge 60 ]; then
                elapsed_seg="${SEP}${ICON_CLOCK} $(( e / 60 ))m$(( e % 60 ))s"
            else
                elapsed_seg="${SEP}${ICON_CLOCK} ${e}s"
            fi
        fi
    fi

    content="${status_seg} ${name_seg}${model_seg}${effort_seg}${ctx_seg}${tok_seg}${elapsed_seg}"

    # Render escapes, then emit as a JSON string.
    printf '%b' "$content" | jq -Rs --arg id "$id" '{id: $id, content: .}' -c
done
