#!/usr/bin/env bash

# ─── Utilitários ─────────────────────────────────────────────────────────────

# Calcula o git blob SHA1 de um arquivo local
# Formato: sha1("blob <tamanho>\0<conteudo>")
_git_blob_sha1() {
  local file="$1"
  [[ -f "$file" ]] || return 1
  local size
  size=$(wc -c < "$file")
  (printf "blob %s\0" "$size"; cat "$file") | sha1sum | cut -d' ' -f1
}

# Compara SHA1 local (git blob) com o sha retornado pela API do GitHub
_is_unchanged() {
  local local_file="$1"
  local remote_sha="$2"

  [[ -f "$local_file" ]] || return 1
  [[ -n "$remote_sha" ]] || return 1

  local local_sha
  local_sha=$(_git_blob_sha1 "$local_file")
  [[ "$local_sha" == "$remote_sha" ]]
}

# ─── Função principal gghget ─────────────────────────────────────────────────

gghget() {
  local URL="${1:?Usage: gghget <github-url> [output-dir]}"
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

  if ! command -v curl &>/dev/null; then
    echo "Error: 'curl' não está disponível." >&2
    return 1
  fi

  local API_BASE="https://api.github.com/repos/${OWNER}/${REPO}/contents"
  local AUTH_HEADER=""
  [[ -n "$GITHUB_PAT_TOKEN" ]] && AUTH_HEADER="Authorization: Bearer $GITHUB_PAT_TOKEN"

  _gghget_recurse() {
    local api_path="$1" local_path="$2"
    local response

    local curl_args=(-sf -H "Accept: application/vnd.github+json")
    [[ -n "$AUTH_HEADER" ]] && curl_args+=(-H "$AUTH_HEADER")

    response=$(curl "${curl_args[@]}" "${API_BASE}/${api_path}?ref=${BRANCH}") || {
      echo "  ✗ Erro ao buscar: ${api_path}" >&2
      return 1
    }

    mkdir -p "$local_path"

    # `sha` da API = git blob SHA1 — compara direto com o local, sem baixar
    echo "$response" | python3 -c "
import sys, json
for e in json.load(sys.stdin):
    print(e['type'] + '|' + e['name'] + '|' + (e.get('download_url') or '') + '|' + (e.get('sha') or ''))
" | while IFS='|' read -r type name dl_url remote_sha; do
      if [[ "$type" == "file" ]]; then
        local local_file="${local_path}/${name}"

        if _is_unchanged "$local_file" "$remote_sha"; then
          echo "  ✓ $local_file"
          continue
        fi

        local label="✚ Novo"
        [[ -f "$local_file" ]] && label="↻ Atualizado"

        if curl -sf -L -o "$local_file" "$dl_url"; then
          echo "  $label: $local_file"
        else
          echo "  ✗ Erro: $local_file" >&2
        fi

      elif [[ "$type" == "dir" ]]; then
        _gghget_recurse "${api_path}/${name}" "${local_path}/${name}"
      fi
    done
  }

  _gghget_recurse "$DIR_PATH" "$OUTPUT_DIR"
  echo "Concluído → $OUTPUT_DIR"
}

# ─── Lista de skills ──────────────────────────────────────────────────────────

# Tech Leads Club
BASE_URL="https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills"
SKILLS=(
  "(creation)/skill-architect"
  "(development)/tlc-spec-driven"
  "(architecture)/legacy-migration-planner"
)
for skill in "${SKILLS[@]}"; do
  skill_name=$(echo "$skill" | cut -d'/' -f2)
  echo "━━━ ${skill_name} ━━━"
  gghget "${BASE_URL}/${skill}" "skills/tech-leads-club/${skill_name}"
  grep -qF "${skill_name}" .skillsignore 2>/dev/null || echo "${skill_name}" >> .skillsignore
  echo ""
done

# Anthropic
BASE_URL="https://github.com/anthropics/skills/tree/main/skills"
SKILLS=(
  "skill-creator"
  "frontend-design"
  "mcp-builder"
)
for skill in "${SKILLS[@]}"; do
  echo "━━━ ${skill} ━━━"
  gghget "${BASE_URL}/${skill}" "skills/anthropics/${skill}"
  grep -qF "${skill}" .skillsignore 2>/dev/null || echo "${skill}" >> .skillsignore
  echo ""
done

# Everything Claude Code
BASE_URL="https://github.com/affaan-m/everything-claude-code/tree/main/skills"
SKILLS=(
  "ai-regression-testing"
  "api-design"
  "backend-patterns"
  "blueprint"
  "coding-standards"
  "content-hash-cache-pattern"
  "cpp-coding-standards"
  "data-scraper-agent"
  "database-migrations"
  "deep-research"
  "deployment-patterns"
  "docker-patterns"
  "regex-vs-llm-structured-text"
)
for skill in "${SKILLS[@]}"; do
  echo "━━━ ${skill} ━━━"
  gghget "${BASE_URL}/${skill}" "skills/everything-claude-code/${skill}"
  grep -qF "${skill}" .skillsignore 2>/dev/null || echo "${skill}" >> .skillsignore
  echo ""
done