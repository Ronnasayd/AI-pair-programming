#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
[ -f .env ] || { echo "❌ .env não encontrado — copie .env.example e edite"; exit 1; }
docker compose up -d
echo "export ANTHROPIC_BASE_URL=http://localhost:4000" >> /tmp/litellm_env.sh
echo "export ANTHROPIC_AUTH_TOKEN=$(grep LITELLM_MASTER_KEY $DIR/.env | cut -d '=' -f2)" >> /tmp/litellm_env.sh
echo "export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1" >> /tmp/litellm_env.sh
echo "✅ LiteLLM em http://$(hostname -I | awk '{print $1}'):4000"
echo "execute 'source /tmp/litellm_env.sh' to set ANTHROPIC_BASE_URL and ANTHROPIC_AUTH_TOKEN in your shell"
