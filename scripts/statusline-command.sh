#!/bin/bash

# Claude Code Status Line Script
# Displays project info, context usage, and environment details
#
# Rate limit usage (5-hour session and 7-day weekly) is available
# via rate_limits.five_hour.used_percentage and rate_limits.seven_day.used_percentage
# Only populated for Pro/Max subscribers after the first API response.

# Read JSON input from stdin
input=$(cat)

echo $input > /tmp/claude_status_debug.json

# Extract basic information
folder=$(basename "$(echo "$input" | jq -r '.workspace.current_dir')")
model=$(echo "$input" | jq -r '.model.display_name')

# Context window usage percentage (📚 = library/context)
ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
ctx_pct_int=${ctx_pct%.*}
if [ "$ctx_pct_int" -ge 80 ] 2>/dev/null; then
    ctx_color="\033[31m"
elif [ "$ctx_pct_int" -ge 50 ] 2>/dev/null; then
    ctx_color="\033[33m"
else
    ctx_color="\033[32m"
fi
RESET="\033[0m"

# Detect project type and language info
lang_info=""

# Check for Python project (venv exists or Python files present)
if [ -n "$VIRTUAL_ENV" ]; then
    venv_raw=$(echo "${VIRTUAL_ENV##*/}" | sed 's/-[0-9].*//')
    if [ "$venv_raw" = ".venv" ] || [ "$venv_raw" = "venv" ]; then
        venv="($folder)"
    else
        venv="($venv_raw)"
    fi
    pyver=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo 'N/A')
    lang_info=" | 💼 $venv | 🐍 $pyver"
elif [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ] || [ -f "Pipfile" ]; then
    pyver=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo 'N/A')
    lang_info=" | 🐍 $pyver"
elif [ -f "go.mod" ] || [ -f "go.sum" ] || ls *.go >/dev/null 2>&1; then
    gover=$(go version 2>/dev/null | grep -oE 'go[0-9]+\.[0-9]+(\.[0-9]+)?' | sed 's/go//' || echo 'N/A')
    if [ "$gover" != "N/A" ]; then
        lang_info=" | 🦫 $gover"
    fi
fi

# Git branch
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'N/A')

# Thinking effort level (🧠 = thinking). Absent if model doesn't support it.
effort_level=$(echo "$input" | jq -r '.effort.level // empty')
effort_info=""
if [ -n "$effort_level" ]; then
    case "$effort_level" in
        low)    effort_color="\033[32m" ;;
        medium) effort_color="\033[33m" ;;
        high|xhigh|max) effort_color="\033[31m" ;;
        *)      effort_color="" ;;
    esac
    effort_info=" | 🧠 ${effort_color}${effort_level}${RESET}"
fi

# Caveman mode status
caveman_info=""
CAVEMAN_FLAG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.caveman-active"
if [ -f "$CAVEMAN_FLAG" ] && [ ! -L "$CAVEMAN_FLAG" ]; then
    CAVEMAN_MODE=$(head -c 64 "$CAVEMAN_FLAG" 2>/dev/null | tr -d '\n\r' | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-')
    if [ -n "$CAVEMAN_MODE" ] && [ "$CAVEMAN_MODE" != "off" ]; then
        if [ "$CAVEMAN_MODE" = "full" ]; then
            caveman_info=" | 🦴 caveman"
        else
            caveman_info=" | 🦴 caveman($CAVEMAN_MODE)"
        fi
    fi
fi

# AI Memory server status
memory_status=""
if docker ps --filter "name=ai-memory" --format "{{.Names}}" 2>/dev/null | grep -q "ai-memory"; then
    memory_status=" | 💾 ai-memory(on)"
else
    memory_status=" | 💾 ai-memory(off)"
fi

# Session cost
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
cost_info=""
if [ -n "$cost" ]; then
    cost=$(printf "%.3f" "$cost")
    cost_info=" | 💰 \$$cost"
fi

# Rate limit usage (session = 5-hour window, week = 7-day window)
five_h=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
seven_d=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')

rate_info=""
if [ -n "$five_h" ] || [ -n "$seven_d" ]; then
    five_int=${five_h%.*}
    seven_int=${seven_d%.*}
    [ -z "$five_int" ] && five_int=0
    [ -z "$seven_int" ] && seven_int=0

    if [ "$five_int" -ge 80 ] 2>/dev/null; then
        five_color="\033[31m"
    elif [ "$five_int" -ge 50 ] 2>/dev/null; then
        five_color="\033[33m"
    else
        five_color="\033[32m"
    fi

    if [ "$seven_int" -ge 80 ] 2>/dev/null; then
        seven_color="\033[31m"
    elif [ "$seven_int" -ge 50 ] 2>/dev/null; then
        seven_color="\033[33m"
    else
        seven_color="\033[32m"
    fi

    # Calculate time remaining in 5-hour session from resets_at timestamp
    five_resets_at=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
    if [ -n "$five_resets_at" ]; then
        now_epoch=$(date +%s)
        remaining_seconds=$(( five_resets_at - now_epoch ))
        if [ "$remaining_seconds" -lt 0 ]; then
            remaining_seconds=0
        fi
        remaining_h=$((remaining_seconds / 3600))
        remaining_m=$(( (remaining_seconds % 3600) / 60 ))
        time_left=$(printf "%d:%02d" "$remaining_h" "$remaining_m")
    else
        time_left="--:--"
    fi

    # Calculate next weekly reset day from resets_at timestamp
    seven_resets_at=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')
    if [ -n "$seven_resets_at" ]; then
        reset_date=$(date -r "$seven_resets_at" "+%b %-d")
        reset_day=$(date -r "$seven_resets_at" "+%-d")
    else
        # Fallback: next Sunday
        dow=$(date +%u)
        days_until_sun=$(( (7 - dow) % 7 ))
        [ "$days_until_sun" -eq 0 ] && days_until_sun=7
        reset_date=$(date -v+"${days_until_sun}d" "+%b %-d")
        reset_day=$(date -v+"${days_until_sun}d" "+%-d")
    fi
    case "$reset_day" in
        1|21|31) reset_suffix="st" ;;
        2|22)    reset_suffix="nd" ;;
        3|23)    reset_suffix="rd" ;;
        *)       reset_suffix="th" ;;
    esac
    reset_label="${reset_date}${reset_suffix}"

    rate_info=" | ⏱ 5h ${five_color}${five_int}%${RESET} (${time_left} left) | 📅 7d ${seven_color}${seven_int}%${RESET} (${reset_label})"
fi

# Output the complete status line
echo -e "📁 $folder${lang_info} | 🌿 $branch | 🤖 $model${effort_info} | 📚 ctx ${ctx_color}${ctx_pct_int}%${RESET}${memory_status}${caveman_info}${cost_info}${rate_info}"
