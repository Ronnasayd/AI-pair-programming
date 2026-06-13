#!/usr/bin/env bash
# Claude Code status line: model name + context progress bar

input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

if [ -n "$used" ]; then
  used_int=$(printf "%.0f" "$used")
  filled=$(( used_int / 5 ))
  empty=$(( 20 - filled ))
  bar=""
  for i in $(seq 1 $filled); do bar="${bar}#"; done
  for i in $(seq 1 $empty); do bar="${bar}-"; done
  printf "%s  [%s] %d%% ctx" "$model" "$bar" "$used_int"
else
  printf "%s  [--------------------] --%% ctx" "$model"
fi
