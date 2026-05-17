#!/usr/bin/env bash

ghget() {
  local URL="${1:?Usage: ghget <github-url> [output-dir]}"
  local OUTPUT_DIR="${2:-}"

  URL="${URL%/}"
  local stripped="${URL#https://github.com/}"

  local OWNER REPO BRANCH DIR_PATH tree
  OWNER="${stripped%%/*}";      stripped="${stripped#*/}"
  REPO="${stripped%%/*}";       stripped="${stripped#*/}"
  tree="${stripped%%/*}";       stripped="${stripped#*/}"
  BRANCH="${stripped%%/*}";     stripped="${stripped#*/}"
  DIR_PATH="$stripped"

  if [[ -z "$OWNER" || -z "$REPO" || "$tree" != "tree" || -z "$BRANCH" || -z "$DIR_PATH" ]]; then
    echo "Error: URL must be https://github.com/OWNER/REPO/tree/BRANCH/PATH" >&2
    return 1
  fi

  [[ -z "$OUTPUT_DIR" ]] && OUTPUT_DIR="$(basename "$DIR_PATH")"

  echo "Owner:  $OWNER"
  echo "Repo:   $REPO"
  echo "Branch: $BRANCH"
  echo "Path:   $DIR_PATH"
  echo "Output: $OUTPUT_DIR"
  echo ""

  # Method 1: svn (preferred)
  if command -v svn &>/dev/null; then
    local SVN_URL
    if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
      SVN_URL="https://github.com/${OWNER}/${REPO}/trunk/${DIR_PATH}"
    else
      SVN_URL="https://github.com/${OWNER}/${REPO}/branches/${BRANCH}/${DIR_PATH}"
    fi
    echo "Using svn export..."
    svn export --force "$SVN_URL" "$OUTPUT_DIR" && echo "Done → $OUTPUT_DIR" && return 0
    echo "svn failed, falling back to curl..." >&2
  fi

  # Method 2: GitHub API + curl
  if ! command -v curl &>/dev/null; then
    echo "Error: neither 'svn' nor 'curl' is available." >&2
    return 1
  fi

  local API_BASE="https://api.github.com/repos/${OWNER}/${REPO}/contents"
  # Uncomment to avoid rate limits or access private repos:
  # local AUTH_HEADER="Authorization: Bearer $GITHUB_TOKEN"

  _ghget_recurse() {
    local api_path="$1" local_path="$2"
    local response

    response=$(curl -sf \
      -H "Accept: application/vnd.github+json" \
      ${AUTH_HEADER:+-H "$AUTH_HEADER"} \
      "${API_BASE}/${api_path}?ref=${BRANCH}") || {
      echo "Error: could not fetch ${api_path}" >&2
      return 1
    }

    mkdir -p "$local_path"

    # Parse JSON entries using python (available on virtually every system)
    echo "$response" | python3 -c "
import sys, json
for entry in json.load(sys.stdin):
    print(entry['type'] + '|' + entry['name'] + '|' + (entry.get('download_url') or ''))
" | while IFS='|' read -r type name dl_url; do
      if [[ "$type" == "file" ]]; then
        echo "  ↓ ${local_path}/${name}"
        curl -sf -L -o "${local_path}/${name}" "$dl_url"
      elif [[ "$type" == "dir" ]]; then
        _ghget_recurse "${api_path}/${name}" "${local_path}/${name}"
      fi
    done
  }

  echo "Using GitHub API + curl..."
  _ghget_recurse "$DIR_PATH" "$OUTPUT_DIR" && echo "Done → $OUTPUT_DIR"
}
# Tech leads club
BASE_URL="https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills/(creation)"
SKILLS=(
  "skill-architect"
)
for skill in "${SKILLS[@]}"; do
  ghget "${BASE_URL}/${skill}" "skills/tech-leads-club/${skill}"
  if ! grep -q "${skill}" .skillsignore; then
    echo "${skill}" >> .skillsignore
  fi
done

# Anthropics
BASE_URL="https://github.com/anthropics/skills/tree/main/skills"
SKILLS=(
  "skill-creator"
)
for skill in "${SKILLS[@]}"; do
  ghget "${BASE_URL}/${skill}" "skills/anthropics/${skill}"
  if ! grep -q "${skill}" .skillsignore; then
    echo "${skill}" >> .skillsignore
  fi
done
