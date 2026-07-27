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
LITELLM_BASE_URL=http://localhost:4000
HEADROOM_PORT=8787

sudo rm -f /tmp/litellm_env.sh
echo "export ANTHROPIC_BASE_URL=http://localhost:$HEADROOM_PORT" >> /tmp/litellm_env.sh
echo "export ANTHROPIC_AUTH_TOKEN=$ANTHROPIC_AUTH_TOKEN" >> /tmp/litellm_env.sh
echo "export ANTHROPIC_TARGET_API_URL=$LITELLM_BASE_URL" >> /tmp/litellm_env.sh
echo "export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1" >> /tmp/litellm_env.sh
echo "export ANTHROPIC_DEFAULT_OPUS_MODEL=9router-high" >> /tmp/litellm_env.sh
echo "export ANTHROPIC_DEFAULT_SONNET_MODEL=9router-medium" >> /tmp/litellm_env.sh
echo "export ANTHROPIC_DEFAULT_HAIKU_MODEL=9router-low" >> /tmp/litellm_env.sh
echo "export ANTHROPIC_MODEL=$ANTHROPIC_MODEL" >> /tmp/litellm_env.sh
echo "headroom proxy --port 8787 --anthropic-api-url \$ANTHROPIC_TARGET_API_URL > /dev/null 2>&1 &" >> /tmp/litellm_env.sh
echo "sleep 1" >> /tmp/litellm_env.sh
echo "claude" >> /tmp/litellm_env.sh
echo "docker compose -f $DIR/docker-compose.yml down --remove-orphans" >> /tmp/litellm_env.sh
echo "killall headroom" >> /tmp/litellm_env.sh
echo "unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN ANTHROPIC_TARGET_API_URL CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY ANTHROPIC_DEFAULT_SONNET_MODEL ANTHROPIC_DEFAULT_HAIKU_MODEL ANTHROPIC_MODEL" >> /tmp/litellm_env.sh
echo "✅ LiteLLM em http://$(hostname -I | awk '{print $1}'):4000"
echo "✅ Headroom vai escutar em http://localhost:$HEADROOM_PORT (target: $LITELLM_BASE_URL)"
echo "Execute 'source /tmp/litellm_env.sh' to set environment variables for LiteLLM + Headroom."
