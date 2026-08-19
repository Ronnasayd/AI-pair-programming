#!/usr/bin/env bash

if [[ -z "$GITHUB_PAT_TOKEN" ]]; then
  echo "Error: GITHUB_PAT_TOKEN not defined." >&2
  exit 1
fi

# ─── Utilitários ─────────────────────────────────────────────────────────────

# Calcula o git blob SHA1 de um arquivo local
# Formato: sha1("blob <tamanho>\0<conteudo>")
# Precisa GITHUB_PAT_TOKEN
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

    local curl_args=(-s -H "Accept: application/vnd.github+json")
    [[ -n "$AUTH_HEADER" ]] && curl_args+=(-H "$AUTH_HEADER")

    local http_code
    response=$(curl "${curl_args[@]}" -w $'\n%{http_code}' "${API_BASE}/${api_path}?ref=${BRANCH}")
    http_code="${response##*$'\n'}"
    response="${response%$'\n'*}"

    if [[ "$http_code" -ge 400 ]]; then
      echo "  ✗ Erro ao buscar: ${api_path} (HTTP $http_code)" >&2
      echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print('    →', d.get('message','') if isinstance(d, dict) else d)" 2>/dev/null >&2
      return 1
    fi

    mkdir -p "$local_path"

    # `sha` da API = git blob SHA1 — compara direto com o local, sem baixar
    echo "$response" | python3 -c "
import sys, json
d = json.load(sys.stdin)
entries = d if isinstance(d, list) else [d]
for e in entries:
    print(e.get('type','') + '|' + e.get('name','') + '|' + (e.get('download_url') or '') + '|' + (e.get('sha') or ''))
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

# ─── Função gghget_file (arquivo único) ─────────────────────────────────────

gghget_file() {
  local URL="${1:?Usage: gghget_file <github-url> [output-dir]}"
  local OUTPUT_DIR="${2:-.}"

  URL="${URL%/}"
  local stripped="${URL#https://github.com/}"

  local OWNER REPO BRANCH FILE_PATH tree
  OWNER="${stripped%%/*}";      stripped="${stripped#*/}"
  REPO="${stripped%%/*}";       stripped="${stripped#*/}"
  tree="${stripped%%/*}";       stripped="${stripped#*/}"
  BRANCH="${stripped%%/*}";     stripped="${stripped#*/}"
  FILE_PATH="$stripped"

  if [[ -z "$OWNER" || -z "$REPO" || "$tree" != "tree" || -z "$BRANCH" || -z "$FILE_PATH" ]]; then
    echo "Error: URL must be https://github.com/OWNER/REPO/tree/BRANCH/PATH/FILE" >&2
    return 1
  fi

  local name="$(basename "$FILE_PATH")"
  local local_file="${OUTPUT_DIR}/${name}"

  local AUTH_HEADER=""
  [[ -n "$GITHUB_PAT_TOKEN" ]] && AUTH_HEADER="Authorization: Bearer $GITHUB_PAT_TOKEN"

  local curl_args=(-s -H "Accept: application/vnd.github+json")
  [[ -n "$AUTH_HEADER" ]] && curl_args+=(-H "$AUTH_HEADER")

  local response http_code
  response=$(curl "${curl_args[@]}" -w $'\n%{http_code}' \
    "https://api.github.com/repos/${OWNER}/${REPO}/contents/${FILE_PATH}?ref=${BRANCH}")
  http_code="${response##*$'\n'}"
  response="${response%$'\n'*}"

  if [[ "$http_code" -ge 400 ]]; then
    echo "  ✗ Erro ao buscar: ${FILE_PATH} (HTTP $http_code)" >&2
    echo "$response" | python3 -c "import sys,json; d=json.loads(sys.stdin.read(), strict=False); print('    →', d.get('message',''))" 2>/dev/null >&2
    return 1
  fi

  local dl_url remote_sha
  read -r dl_url remote_sha <<< "$(echo "$response" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read(), strict=False)
print(d.get('download_url') or '', d.get('sha') or '')
")"

  mkdir -p "$OUTPUT_DIR"

  if _is_unchanged "$local_file" "$remote_sha"; then
    echo "  ✓ $local_file"
    return 0
  fi

  local label="✚ Novo"
  [[ -f "$local_file" ]] && label="↻ Atualizado"

  if curl -sf -L -o "$local_file" "$dl_url"; then
    echo "  $label: $local_file"
  else
    echo "  ✗ Erro: $local_file" >&2
    return 1
  fi
}

# ─── Lista de skills ──────────────────────────────────────────────────────────

# Tech Leads Club
BASE_URL="https://github.com/tech-leads-club/agent-skills/tree/main/packages/skills-catalog/skills"
SKILLS=(
  "(architecture)/coupling-analysis"
  "(architecture)/domain-analysis"
  "(architecture)/frontend-blueprint"
  "(architecture)/legacy-migration-planner"
  "(architecture)/modular-decomposition"
  "(architecture)/react-composition-patterns"
  "(creation)/create-adr"
  "(creation)/create-rfc"
  "(creation)/skill-architect"
  "(creation)/subagent-creator"
  "(decision-making)/the-fool"
  "(design)/figma-implement-design"
  "(development)/codenavi"
  "(development)/gh-address-comments"
  "(development)/jira-assistant"
  "(development)/tlc-spec-driven"
  "(gtm)/gtm-engineering"
  "(gtm)/gtm-metrics"
  "(performance)/perf-web-optimization"
  "(quality)/react-best-practices"
  "(quality)/seo"
  "(security)/security-best-practices"
  "(tooling)/gh-fix-ci"
  "(tooling)/mermaid-studio"
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
  "algorithmic-art"
  "docx"
  "frontend-design"
  "mcp-builder"
  "pdf"
  "skill-creator"
  "webapp-testing"
  "xlsx"
)
for skill in "${SKILLS[@]}"; do
  echo "━━━ ${skill} ━━━"
  gghget "${BASE_URL}/${skill}" "skills/anthropics/${skill}"
  grep -qF "${skill}" .skillsignore 2>/dev/null || echo "${skill}" >> .skillsignore
  echo ""
done

# Everything Claude Code
BASE_URL="https://github.com/affaan-m/ECC/tree/main/skills"
SKILLS=(
  "agent-architecture-audit"
  "agent-introspection-debugging"
  "agent-self-evaluation"
  "ai-regression-testing"
  "api-design"
  "architecture-decision-records"
  "autonomous-agent-harness"
  "autonomous-loops"
  "backend-patterns"
  "blueprint"
  "browser-qa"
  "codebase-onboarding"
  "coding-standards"
  "content-hash-cache-pattern"
  "cpp-coding-standards"
  "cpp-testing"
  "data-scraper-agent"
  "database-migrations"
  "deep-research"
  "deployment-patterns"
  "dmux-workflows"
  "docker-patterns"
  "e2e-testing"
  "error-handling"
  "exa-search"
  "frontend-a11y"
  "frontend-patterns"
  "gan-style-harness"
  "git-workflow"
  "github-ops"
  "golang-patterns"
  "golang-testing"
  "hexagonal-architecture"
  "jira-integration"
  "kubernetes-patterns"
  "mcp-server-patterns"
  "mysql-patterns"
  "parallel-execution-optimizer"
  "postgres-patterns"
  "prisma-patterns"
  "production-audit"
  "python-patterns"
  "python-testing"
  "react-native-patterns"
  "react-patterns"
  "react-performance"
  "react-testing"
  "redis-patterns"
  "regex-vs-llm-structured-text"
  "security-bounty-hunter"
  "security-review"
  "security-scan"
  "tdd-workflow"
  "team-builder"
  "vite-patterns"
  "vue-patterns"
)
for skill in "${SKILLS[@]}"; do
  echo "━━━ ${skill} ━━━"
  gghget "${BASE_URL}/${skill}" "skills/everything-claude-code/${skill}"
  grep -qF "${skill}" .skillsignore 2>/dev/null || echo "${skill}" >> .skillsignore
  echo ""
done


# Mattpocock
BASE_URL="https://github.com/mattpocock/skills/tree/main/skills"
SKILLS=(
  "productivity/grilling"
  "engineering/diagnosing-bugs"
  "engineering/domain-modeling"
  "engineering/grill-with-docs"
)
for skill in "${SKILLS[@]}"; do
  echo "━━━ ${skill} ━━━"
  gghget "${BASE_URL}/${skill}" "skills/mattpocock/${skill}"
  grep -qF "${skill}" .skillsignore 2>/dev/null || echo "${skill}" >> .skillsignore
  echo ""
done


# awesome-claude-code-toolkit
BASE_URL="https://github.com/rohitg00/awesome-claude-code-toolkit/tree/main/commands"
COMMANDS=(
  "security/dependency-audit.md"
  "architecture/plan.md"
  "architecture/migrate.md"
)
for command in "${COMMANDS[@]}"; do
  echo "━━━ ${command} ━━━"
  gghget_file "${BASE_URL}/${command}" "commands/awesome-claude-code-toolkit/${command%/*}"
  echo ""
done
