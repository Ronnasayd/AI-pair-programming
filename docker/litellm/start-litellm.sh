#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

[ -f .env ] || { echo "❌ .env não encontrado — copie .env.example e edite"; exit 1; }

docker compose down --remove-orphans
docker compose up -d

: "${AI_PROJECT_DIR:?AI_PROJECT_DIR não definida}"


ANTHROPIC_MODEL="$(yq -r '.model_list[].model_name' "$AI_PROJECT_DIR/docker/litellm/config.yaml" | fzf)"
ANTHROPIC_AUTH_TOKEN="$(grep LITELLM_MASTER_KEY "$DIR/.env" | cut -d '=' -f2 | tr -d '"')"
ANTHROPIC_BASE_URL=http://localhost:4000

sudo rm -f /tmp/litellm_env.sh
echo "export ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL" >> /tmp/litellm_env.sh
echo "export ANTHROPIC_AUTH_TOKEN=$ANTHROPIC_AUTH_TOKEN" >> /tmp/litellm_env.sh
echo "export ANTHROPIC_MODEL=$ANTHROPIC_MODEL" >> /tmp/litellm_env.sh
echo "export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1" >> /tmp/litellm_env.sh
echo "claude" >> /tmp/litellm_env.sh
echo "✅ LiteLLM em http://$(hostname -I | awk '{print $1}'):4000"
echo "Execute 'source /tmp/litellm_env.sh' to set environment variables for LiteLLM."
