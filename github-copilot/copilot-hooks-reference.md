# GitHub Copilot Hooks — Guia de Referência

> Fonte: [docs.github.com/en/copilot/reference/hooks-reference](https://docs.github.com/en/copilot/reference/hooks-reference)

---

## O que são Hooks?

Hooks são comandos externos executados em pontos específicos do ciclo de vida de uma sessão do Copilot. Permitem automação customizada, controles de segurança e integrações.

Suportados em duas superfícies:

- **Copilot CLI** — executa localmente na máquina do desenvolvedor
- **Copilot cloud agent** — executa dentro do sandbox Linux efêmero provisionado para cada job

---

## Onde ficam os arquivos de configuração

### Copilot CLI (ordem de carregamento)

| Fonte                  | Localização                                                                         |
| ---------------------- | ----------------------------------------------------------------------------------- |
| Repository-level       | `.github/hooks/*.json`                                                              |
| User-level             | `~/.copilot/hooks/*.json` (Linux/macOS) / `%USERPROFILE%\.copilot\hooks\` (Windows) |
| Settings inline (repo) | `.github/copilot/settings.json` ou `settings.local.json` → campo `hooks`            |
| Settings inline (user) | `~/.copilot/settings.json` → campo `hooks`                                          |
| Plugins                | `hooks.json` dentro do diretório do plugin                                          |

> Quando o mesmo evento aparece em múltiplas fontes, **todos** os hooks de todas as fontes são executados.

### Copilot cloud agent

Apenas `.github/hooks/*.json` no repositório clonado é carregado. Não há user-level hooks, settings.json ou plugins.

---

## Formatos de configuração

### Structure base

```json
{
  "version": 1,
  "disableAllHooks": false,
  "hooks": {
    "<eventName>": [
      /* array de hook entries */
    ]
  }
}
```

### Command hook (shell script)

```json
{
  "type": "command",
  "bash": "seu-comando-bash",
  "powershell": "seu-comando-powershell",
  "command": "fallback-cross-platform",
  "cwd": "diretório/de/trabalho",
  "env": { "VAR": "valor" },
  "timeoutSec": 30,
  "matcher": "regex-opcional"
}
```

> Cloud agent: apenas `bash` (ou `command` como fallback) é honrado. `powershell` é ignorado.

### HTTP hook (POST JSON)

```json
{
  "type": "http",
  "url": "https://hooks.exemplo.com/copilot",
  "headers": { "X-Source": "copilot-cli" },
  "allowedEnvVars": ["GITHUB_TOKEN"],
  "timeoutSec": 30,
  "matcher": "regex-opcional"
}
```

> Apenas `https://` por padrão. `http://localhost` é permitido com `COPILOT_HOOK_ALLOW_LOCALHOST=1`.
> Em cloud agent, a URL deve ser um host na allowlist do firewall.

### Prompt hook (apenas `sessionStart`, Copilot CLI somente)

```json
{
  "type": "prompt",
  "prompt": "Texto ou /slash-command"
}
```

---

## Tabela de Eventos (Hook Events)

| Evento                | O que faz                                      |            Pode bloquear?            |      Pode injetar `additionalContext`?      |             Cloud Agent?             |
| --------------------- | ---------------------------------------------- | :----------------------------------: | :-----------------------------------------: | :----------------------------------: |
| `sessionStart`        | Nova sessão ou sessão retomada                 |                 Não                  |                   ✅ Sim                    |   ✅ Sim (sempre como nova sessão)   |
| `sessionEnd`          | Sessão encerrada                               |                 Não                  |                     Não                     |                ✅ Sim                |
| `userPromptSubmitted` | Usuário submete um prompt                      |                 Não                  |                     Não                     |        ✅ Sim (no máximo 1×)         |
| `preToolUse`          | Antes de cada ferramenta executar              |      ✅ Sim (allow/deny/modify)      |                     Não                     |    ✅ Sim (`"ask"` vira `"deny"`)    |
| `postToolUse`         | Após ferramenta executar com sucesso           |                 Não                  |                   ✅ Sim                    |                ✅ Sim                |
| `postToolUseFailure`  | Após ferramenta falhar                         |                 Não                  |            ✅ Sim (exit code 2)             |                ✅ Sim                |
| `agentStop`           | Agente principal encerra um turno              | ✅ Sim (`"block"` força outro turno) |                     Não                     |                ✅ Sim                |
| `subagentStart`       | Subagente criado (antes de executar)           |                 Não                  | ✅ Sim (pré-anexado ao prompt do subagente) |                ✅ Sim                |
| `subagentStop`        | Subagente encerra                              | ✅ Sim (`"block"` força outro turno) |                     Não                     |                ✅ Sim                |
| `permissionRequest`   | Antes do serviço de permissões avaliar         |         ✅ Sim (allow/deny)          |                     Não                     | ❌ Não (pre-aprovado no cloud agent) |
| `notification`        | CLI emite notificação do sistema (async)       |        Não (fire-and-forget)         |                   ✅ Sim                    |                ❌ Não                |
| `preCompact`          | Compactação de contexto está prestes a começar |                 Não                  |                     Não                     |       ✅ Sim (apenas `"auto"`)       |
| `errorOccurred`       | Erro durante execução                          |                 Não                  |                     Não                     |                ✅ Sim                |

---

## Hooks que podem passar `additionalContext` ao agente

> `additionalContext` é texto injetado no contexto do modelo. Múltiplos hooks que retornam `additionalContext` são joinados com `\n\n` e limitados a **10 KB**.

| Hook                 | Como é injetado                                                                                |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| `postToolUse`        | Anexado ao `textResultForLlm` da ferramenta no mesmo turno                                     |
| `postToolUseFailure` | Contexto de recuperação mostrado ao agente após falha                                          |
| `sessionStart`       | Injetado no início da sessão                                                                   |
| `subagentStart`      | Pré-anexado ao prompt do subagente antes de ele rodar                                          |
| `notification`       | Injetado como mensagem de usuário pré-pendente (pode disparar processamento do agente se idle) |

---

## Payloads de Entrada por Evento

> Dois formatos suportados:
>
> - **camelCase** → campos em camelCase (ex: `sessionId`, `toolName`)
> - **PascalCase** (VS Code compatible) → campos em snake_case (ex: `session_id`, `tool_name`)
>   Use o nome do evento em camelCase ou PascalCase no config para selecionar o formato.

### `sessionStart` / `SessionStart`

```ts
// camelCase
{
  sessionId: string;
  timestamp: number;       // Unix ms
  cwd: string;
  source: "startup" | "resume" | "new";
  initialPrompt?: string;
}

// VS Code (PascalCase event name)
{
  hook_event_name: "SessionStart";
  session_id: string;
  timestamp: string;       // ISO 8601
  cwd: string;
  source: "startup" | "resume" | "new";
  initial_prompt?: string;
}
```

### `sessionEnd` / `SessionEnd`

```ts
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  reason: "complete" | "error" | "abort" | "timeout" | "user_exit";
}
```

### `userPromptSubmitted` / `UserPromptSubmit`

```ts
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  prompt: string;
}
```

### `preToolUse` / `PreToolUse`

```ts
// camelCase
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  toolName: string;
  toolArgs: unknown;
}

// VS Code
{
  hook_event_name: "PreToolUse";
  session_id: string;
  timestamp: string;
  cwd: string;
  tool_name: string;
  tool_input: unknown;
}
```

### `postToolUse` / `PostToolUse`

```ts
// camelCase
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  toolName: string;
  toolArgs: unknown;
  toolResult: {
    resultType: "success";
    textResultForLlm: string;
  }
}

// VS Code
{
  hook_event_name: "PostToolUse";
  session_id: string;
  timestamp: string;
  cwd: string;
  tool_name: string;
  tool_input: unknown;
  tool_result: {
    result_type: "success";
    text_result_for_llm: string;
  }
}
```

### `postToolUseFailure` / `PostToolUseFailure`

```ts
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  toolName: string;
  toolArgs: unknown;
  error: string;
}
```

### `agentStop` / `Stop`

```ts
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  transcriptPath: string;
  stopReason: "end_turn";
}
```

### `subagentStart`

> O agente `general-purpose` built-in **não** emite `subagentStart` ou `subagentStop`.

```ts
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  transcriptPath: string;
  agentName: string;
  agentDisplayName?: string;
  agentDescription?: string;
}
```

### `subagentStop` / `SubagentStop`

```ts
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  transcriptPath: string;
  agentName: string;
  agentDisplayName?: string;
  stopReason: "end_turn";
}
```

### `errorOccurred` / `ErrorOccurred`

```ts
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  error: {
    message: string;
    name: string;
    stack?: string;
  };
  errorContext: "model_call" | "tool_execution" | "system" | "user_input";
  recoverable: boolean;
}
```

### `preCompact` / `PreCompact`

```ts
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  transcriptPath: string;
  trigger: "manual" | "auto";
  customInstructions: string;
}
```

### `notification` (CLI only)

```ts
{
  sessionId: string;
  timestamp: number;
  cwd: string;
  hook_event_name: "Notification";
  message: string;
  title?: string;
  notification_type: string;
}
```

Tipos de `notification_type`:
| Tipo | Quando dispara |
|------|----------------|
| `shell_completed` | Comando shell assíncrono termina |
| `shell_detached_completed` | Sessão shell detachada completa |
| `agent_completed` | Subagente em background termina |
| `agent_idle` | Agente em background entra em estado idle (aguardando `write_agent`) |
| `permission_prompt` | Agente solicita permissão para executar ferramenta |
| `elicitation_dialog` | Agente solicita informações adicionais do usuário |

---

## Outputs e Controle de Decisão

### `preToolUse` → stdout JSON

```json
{
  "permissionDecision": "allow" | "deny" | "ask",
  "permissionDecisionReason": "string (obrigatório quando deny)",
  "modifiedArgs": { /* argumentos substitutos */ }
}
```

> Cloud agent: `"ask"` é tratado como `"deny"`.

### `agentStop` / `subagentStop` → stdout JSON

```json
{
  "decision": "block" | "allow",
  "reason": "prompt para o próximo turno (quando block)"
}
```

### `postToolUse` → stdout JSON

```json
{
  "modifiedResult": {
    "resultType": "success",
    "textResultForLlm": "resultado substituto"
  },
  "additionalContext": "contexto extra injetado após o resultado"
}
```

> Retorne `{}` ou vazio para manter o resultado original.

### `permissionRequest` → stdout JSON (CLI only)

```json
{
  "behavior": "allow" | "deny",
  "message": "razão enviada ao LLM quando deny",
  "interrupt": true
}
```

> Exit code `2` = deny implícito. Vazio = fluxo normal de permissão.

### `sessionStart` / `subagentStart` / `notification` → stdout JSON

```json
{
  "additionalContext": "texto injetado no contexto do agente"
}
```

---

## Matcher Filtering

Eventos que suportam `matcher` (regex ancorado como `^(?:pattern)$`):

| Evento              | Campo filtrado                     |
| ------------------- | ---------------------------------- |
| `notification`      | `notification_type`                |
| `permissionRequest` | `toolName`                         |
| `preCompact`        | `trigger` (`"manual"` ou `"auto"`) |
| `preToolUse`        | `toolName`                         |
| `subagentStart`     | `agentName`                        |

---

## Tool Names para Matching

| Nome         | Descrição                                           |
| ------------ | --------------------------------------------------- |
| `ask_user`   | Faz pergunta ao usuário                             |
| `bash`       | Executa shell (Unix)                                |
| `create`     | Cria novos arquivos                                 |
| `edit`       | Modifica conteúdo de arquivos                       |
| `glob`       | Encontra arquivos por padrão                        |
| `grep`       | Busca conteúdo em arquivos                          |
| `powershell` | Executa shell (Windows, não aparece no cloud agent) |
| `task`       | Executa subagentes                                  |
| `view`       | Lê conteúdo de arquivos                             |
| `web_fetch`  | Busca páginas web                                   |

---

## Exit Codes para Command Hooks

| Exit code       | Comportamento                                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `0`             | Sucesso. stdout é parseado como JSON de output                                                                                        |
| `2`             | Aviso. Para `permissionRequest`: tratado como `{"behavior":"deny"}`. Para `postToolUseFailure`: stdout é anexado ao contexto de falha |
| Outros não-zero | Falha logada, execução continua (fail-open)                                                                                           |

---

## Variáveis de Ambiente no Cloud Agent

| Variável                   | Conteúdo                          |
| -------------------------- | --------------------------------- |
| `GITHUB_COPILOT_API_TOKEN` | Token de API do Copilot           |
| `GITHUB_COPILOT_GIT_TOKEN` | Token Git do Copilot              |
| `COPILOT_AGENT_PROMPT`     | Prompt com que o job foi invocado |
| `HOME`                     | `/root` (sandbox efêmero)         |

---

## Desabilitar todos os hooks

```json
{
  "version": 1,
  "disableAllHooks": true,
  "hooks": {}
}
```

- Dentro de um único arquivo `.github/hooks/*.json` → apenas aquele arquivo é ignorado (CLI + cloud agent)
- Em `settings.json` do repositório → todos os hooks de todas as fontes são ignorados (CLI only)
