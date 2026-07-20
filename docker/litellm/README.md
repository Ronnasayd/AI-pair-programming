# Claude Code + LiteLLM + OpenRouter (Docker)

Sobe um proxy LiteLLM localmente que traduz chamadas do Claude Code para o formato do OpenRouter.

## 1. Configurar as chaves

```bash
cp .env.example .env
# edite o .env e coloque sua OPENROUTER_API_KEY e uma LITELLM_MASTER_KEY à sua escolha
```

## 2. Subir o proxy

```bash
docker compose up -d
```

Verifique se subiu certo:

```bash
docker compose logs -f litellm
curl http://localhost:4000/health/liveliness
```

## 3. Apontar o Claude Code para o proxy

Exporte as variáveis no seu shell (adicione no `~/.bashrc` ou `~/.zshrc` para persistir):

```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=<mesma LITELLM_MASTER_KEY do seu .env>
export ANTHROPIC_MODEL=openrouter-claude-sonnet
```

Ou, alternativa mais permanente, em `~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:4000/",
    "ANTHROPIC_AUTH_TOKEN": "<mesma LITELLM_MASTER_KEY do seu .env>",
    "ANTHROPIC_MODEL": "openrouter-claude-sonnet"
  }
}
```

## 4. Rodar o Claude Code

```bash
claude
```

Todas as chamadas agora passam pelo LiteLLM e são roteadas para o OpenRouter.

## 5. (Opcional) Ver todos os modelos no seletor `/model`

```bash
export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1
```

Assim, ao rodar `/model` dentro do Claude Code, aparecem todos os `model_name` definidos no `config.yaml`, marcados como "From gateway".

## 6. Trocar de modelo

Edite `config.yaml` para adicionar/remover modelos (qualquer um do catálogo do OpenRouter, prefixado com `openrouter/<provedor>/<modelo>`), depois:

```bash
docker compose restart litellm
```

## Testar o proxy manualmente

```bash
curl http://localhost:4000/v1/messages \
  -H "x-api-key: <sua LITELLM_MASTER_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model": "openrouter-claude-sonnet", "max_tokens": 100, "messages": [{"role": "user", "content": "oi"}]}'
```

## Parar tudo

```bash
docker compose down
```

## ⚠️ Nota de segurança

As versões **1.82.7** e **1.82.8** do LiteLLM no PyPI foram comprometidas com malware que rouba credenciais (BerriAI/litellm#24518). Este compose usa a tag `main-stable` da imagem oficial do GHCR, mas se você instalar o LiteLLM via `pip` separadamente, evite essas duas versões e rotacione qualquer credencial exposta em máquinas onde elas foram instaladas.
