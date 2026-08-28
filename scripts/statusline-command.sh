#!/bin/bash

# Claude Code Status Line Script
# Displays project info, context usage, and environment details
#
# Rate limit usage (5-hour session and 7-day weekly) is available
# via rate_limits.five_hour.used_percentage and rate_limits.seven_day.used_percentage
# Only populated for Pro/Max subscribers after the first API response.

# Nerd Font icons: set NERD_FONT=1 to enable glyphs, anything else disables them
NERD_FONT="${NERD_FONT:-1}"

if [ "$NERD_FONT" = "1" ]; then
    ICON_PYTHON=$'\U0000E73C'
    ICON_GO=$'\U0000E627'
    ICON_EFFORT=$'\U0000EE9C'
    ICON_JAIL=$'\U000F033E'
    ICON_CAVEMAN=$'\U0000EE9A'
    ICON_EMAIL=$'\U0000F42F'
    ICON_SERENA=$'\U000F1077'
    ICON_MEMORY=$'\U0000F0C7'
    ICON_RAGRAT=$'\U000F1636'
    ICON_COST=$'\U000F0CF4'
    ICON_WEEK=$'\U000F00ED'
    ICON_FOLDER=$'\U0000F07B'
    ICON_BRANCH=$'\U0000E702'
    ICON_MODEL=$'\U000F06A9'
    ICON_CTX=$'\U000F125F'
    ICON_CACHE=$'\U0000F49B'
    ICON_TOKEN=$'\U0000EB7E'
    ICON_5H=$'\u23F1'
else
    ICON_PYTHON="🐍" ICON_GO="🐹" ICON_EFFORT="🧠" ICON_JAIL="🔒" ICON_CAVEMAN="🦴"
    ICON_EMAIL="📧" ICON_SERENA="🧭" ICON_MEMORY="💾" ICON_RAGRAT="🐀" ICON_COST="💰"
    ICON_WEEK="📅" ICON_FOLDER="📁" ICON_BRANCH="🌿" ICON_MODEL="🤖" ICON_CTX="📚"
    ICON_CACHE="📦" ICON_TOKEN="🎟" ICON_5H="⏱"
fi

# Read JSON input from stdin
input=$(cat)

echo $input > $HOME/.claude/logs/claude_statusline.json

# Extract basic information
folder=$(basename "$(echo "$input" | jq -r '.workspace.current_dir')")
model=$(echo "$input" | jq -r '.model.display_name')

# Context window usage percentage (📚 = library/context)
ctx_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
ctx_pct_int=${ctx_pct%.*}
ctx_size=$(echo "$input" | jq -r '.context_window.context_window_size // 0')
ctx_usage=$(( (ctx_pct_int * ctx_size) / 100 ))
input_tokens=$(echo "$input" | jq -r '.context_window.current_usage.input_tokens // 0')
cache_read=$(echo "$input" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')
cache_creation=$(echo "$input" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
total_input=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
total_output=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
# Catppuccin Frappe palette (24-bit true color)
C_RED="\033[38;2;231;130;132m"
C_YELLOW="\033[38;2;229;200;144m"
C_GREEN="\033[38;2;166;209;137m"
C_TEAL="\033[38;2;129;200;190m"
C_BLUE="\033[38;2;140;170;238m"
C_MAUVE="\033[38;2;202;158;230m"
C_LAVENDER="\033[38;2;186;187;241m"
C_PEACH="\033[38;2;239;159;118m"
C_SUBTEXT="\033[38;2;165;173;206m"
RESET="\033[0m"

if [ "$ctx_pct_int" -ge 80 ] 2>/dev/null; then
    ctx_color="$C_RED"
elif [ "$ctx_pct_int" -ge 50 ] 2>/dev/null; then
    ctx_color="$C_YELLOW"
else
    ctx_color="$C_GREEN"
fi

# Context bar (10 segments) + k-formatted tokens
ctx_filled=$(( ctx_pct_int / 10 ))
[ "$ctx_filled" -gt 10 ] && ctx_filled=10
[ "$ctx_filled" -lt 0 ] && ctx_filled=0
ctx_bar=""
for i in $(seq 1 10); do
    if [ "$i" -le "$ctx_filled" ]; then
        ctx_bar="${ctx_bar}▓"
    else
        ctx_bar="${ctx_bar}░"
    fi
done
ctx_usage_k=$(( ctx_usage / 1000 ))
ctx_size_k=$(( ctx_size / 1000 ))

# Format a token count: k-suffixed when > 1000, raw otherwise
fmt_k() {
    if [ "$1" -gt 1000 ] 2>/dev/null; then
        echo "$(( $1 / 1000 ))k"
    else
        echo "$1"
    fi
}
cache_read_f=$(fmt_k "$cache_read")
cache_creation_f=$(fmt_k "$cache_creation")
input_tokens_f=$(fmt_k "$input_tokens")
total_input_f=$(fmt_k "$total_input")
total_output_f=$(fmt_k "$total_output")

# Detect project type and language info
lang_info=""

# Check for Python project (venv exists or Python files present)
if [ -n "$VIRTUAL_ENV" ]; then
    # venv_raw=$(echo "${VIRTUAL_ENV##*/}" | sed 's/-[0-9].*//')
    # if [ "$venv_raw" = ".venv" ] || [ "$venv_raw" = "venv" ]; then
    #     venv="($folder)"
    # else
    #     venv="($venv_raw)"
    # fi
    pyver=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo 'N/A')
    lang_info=" | ${ICON_PYTHON} $pyver(venv)"
elif [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ] || [ -f "Pipfile" ]; then
    pyver=$(python3 --version 2>/dev/null | cut -d' ' -f2 || echo 'N/A')
    lang_info=" | ${ICON_PYTHON} $pyver"
elif [ -f "go.mod" ] || [ -f "go.sum" ] || ls *.go >/dev/null 2>&1; then
    gover=$(go version 2>/dev/null | grep -oE 'go[0-9]+\.[0-9]+(\.[0-9]+)?' | sed 's/go//' || echo 'N/A')
    if [ "$gover" != "N/A" ]; then
        lang_info=" | ${ICON_GO} $gover"
    fi
fi

# Git branch
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'N/A')
if [ "${#branch}" -gt 20 ]; then
    branch="${branch:0:19}…"
fi

# Claude Code version
cc_version=$(claude --version 2>/dev/null | awk '{print $1}')

# Thinking effort level (🧠 = thinking). Absent if model doesn't support it.
effort_level=$(echo "$input" | jq -r '.effort.level // empty')
effort_info=""
if [ -n "$effort_level" ]; then
    case "$effort_level" in
        low)    effort_color="$C_GREEN" ;;
        medium) effort_color="$C_YELLOW" ;;
        high|xhigh|max) effort_color="$C_RED" ;;
        *)      effort_color="" ;;
    esac
    effort_info=" | ${ICON_EFFORT} ${effort_color}${effort_level}${RESET}"
fi

# ai-jail sandbox status
jail_info=""
if [ -n "$AI_JAIL" ]; then
    jail_info=" | ${ICON_JAIL} lock"
fi

# Caveman mode status
caveman_info=""
CAVEMAN_FLAG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.caveman-active"
if [ -f "$CAVEMAN_FLAG" ] && [ ! -L "$CAVEMAN_FLAG" ]; then
    CAVEMAN_MODE=$(head -c 64 "$CAVEMAN_FLAG" 2>/dev/null | tr -d '\n\r' | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-')
    if [ -n "$CAVEMAN_MODE" ] && [ "$CAVEMAN_MODE" != "off" ]; then
        if [ "$CAVEMAN_MODE" = "full" ]; then
            caveman_info=" | ${ICON_CAVEMAN} cav"
        else
            caveman_info=" | ${ICON_CAVEMAN} cav($CAVEMAN_MODE)"
        fi
    fi
fi

# email proxy status
email_info=""
email_color="$C_MAUVE"
if [ "$CLAUDE_CONFIG_DIR" == "$HOME/.claude-L" ] ; then
    email_info="${ICON_EMAIL} $(cat $HOME/.claude-L/.claude.json | jq -r '.oauthAccount.emailAddress')"
else
    email_info="${ICON_EMAIL} $(cat $HOME/.claude.json | jq -r '.oauthAccount.emailAddress')"
fi

# Serena status (sr(<dot>) is an OSC 8 hyperlink to the dashboard)
serena_dash="http://localhost:24282/dashboard/"
serena_info=""
if  pgrep -f "serena" > /dev/null; then
    serena_info=" | ${ICON_SERENA} \e]8;;${serena_dash}\e\\\\sr(🟢)\e]8;;\e\\\\"
else
    serena_info=" | ${ICON_SERENA} \e]8;;${serena_dash}\e\\\\sr(🔴)\e]8;;\e\\\\"
fi



# AI Memory server status (ai-mem(<dot>) is an OSC 8 hyperlink to the web UI)
memory_web="http://localhost:49374/web"
memory_status=""
if docker ps --filter "name=ai-memory" --format "{{.Names}}" 2>/dev/null | grep -q "ai-memory"; then
    memory_status=" | ${ICON_MEMORY} \e]8;;${memory_web}\e\\\\ai-mem(🟢)\e]8;;\e\\\\"
else
    memory_status=" | ${ICON_MEMORY} \e]8;;${memory_web}\e\\\\ai-mem(🔴)\e]8;;\e\\\\"
fi

if [ -f "rag-rat.toml" ] && [ ! -L "rag-rat.toml" ]; then
    ragrat_status=" | ${ICON_RAGRAT} rr(🟢)"
else
    ragrat_status=" | ${ICON_RAGRAT} rr(🔴)"
fi

# Session cost
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // empty')
cost_info=""
if [ -n "$cost" ]; then
    cost=$(LC_NUMERIC=C printf "%.3f" "$cost")
    cost_color="$C_GREEN"
    cost_info=" | ${ICON_COST} ${cost_color}\$$cost${RESET}"

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
        five_color="$C_RED"
    elif [ "$five_int" -ge 50 ] 2>/dev/null; then
        five_color="$C_YELLOW"
    else
        five_color="$C_GREEN"
    fi

    if [ "$seven_int" -ge 80 ] 2>/dev/null; then
        seven_color="$C_RED"
    elif [ "$seven_int" -ge 50 ] 2>/dev/null; then
        seven_color="$C_YELLOW"
    else
        seven_color="$C_GREEN"
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
        reset_date=$(date -d "@$seven_resets_at" "+%b %-d")
        reset_day=$(date -d "@$seven_resets_at" "+%-d")
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

    rate_info=" | ${ICON_5H} 5h ${five_color}${five_int}%${RESET} (-${time_left}) | ${ICON_WEEK} 7d ${seven_color}${seven_int}%${RESET} (${reset_label})"
fi

# Output the complete status line
cc_ver_info=""
# OSC 8 hyperlink: v<version> -> release notes (degrades to plain text on terminals without support)
[ -n "$cc_version" ] && cc_ver_info=" | \e]8;;https://github.com/anthropics/claude-code/releases\e\\\\${C_SUBTEXT}v${cc_version}${RESET}\e]8;;\e\\\\"
echo -e "${email_color}${email_info}${RESET}"
echo -e "${ICON_FOLDER} ${C_TEAL}$folder${RESET}${lang_info} | ${ICON_BRANCH} ${C_MAUVE}$branch${RESET} | ${ICON_MODEL} ${C_LAVENDER}$model${RESET}${effort_info}${memory_status}${serena_info}${ragrat_status}${caveman_info}${jail_info}${cc_ver_info}"
echo -e "${ICON_CTX} ctx ${C_BLUE}${ctx_bar}${RESET} ${C_BLUE}${ctx_pct_int}%${RESET} (${ctx_usage_k}k/${ctx_size_k}k) | ${ICON_CACHE} cache(r:${cache_read_f} c:${cache_creation_f} i:${input_tokens_f}) | ${ICON_TOKEN} tok(in:${total_input_f} out:${total_output_f}) | ${cost_info# | }${rate_info}"

