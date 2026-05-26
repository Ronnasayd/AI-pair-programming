# Claude Code Hooks — Guia de Referência

> Fonte: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)

---

## O que são Hooks?

Hooks são comandos de shell, endpoints HTTP, ferramentas MCP, prompts LLM ou agentes definidos pelo usuário que executam automaticamente em pontos específicos do ciclo de vida do Claude Code. Permitem automação customizada, controles de segurança e integrações.

---

## Onde ficam os arquivos de configuração

| Escopo                | Localização                                   | Git?             |
| --------------------- | --------------------------------------------- | ---------------- |
| Todos os projetos     | `~/.claude/settings.json` → campo `hooks`     | Não (local)      |
| Projeto único         | `.claude/settings.json` → campo `hooks`       | Sim              |
| Projeto único (local) | `.claude/settings.local.json` → campo `hooks` | Não (gitignored) |
| Organização           | Managed policy settings                       | Sim (admin)      |
| Plugin                | `hooks/hooks.json` dentro do plugin           | Sim              |
| Skill/Agent           | YAML frontmatter do componente                | Sim              |

---

## Estrutura de configuração

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/script.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

> Três níveis: **evento** → **matcher group** → **hook handler**

---

## Tipos de Hook Handlers

| Tipo       | Descrição                                                |
| ---------- | -------------------------------------------------------- |
| `command`  | Executa script shell. Recebe JSON via stdin              |
| `http`     | Envia JSON como POST. Recebe resposta JSON               |
| `mcp_tool` | Chama ferramenta em servidor MCP conectado               |
| `prompt`   | Envia prompt a um modelo Claude para decisão sim/não     |
| `agent`    | Spawna subagente com acesso a ferramentas (experimental) |

---

## Tabela de Eventos (Hook Events)

| Evento                | O que faz                                                   |        Pode bloquear?         | `additionalContext`?  | Matcher em                              |
| --------------------- | ----------------------------------------------------------- | :---------------------------: | :-------------------: | --------------------------------------- |
| `SessionStart`        | Nova sessão ou retomada                                     |              Não              |        ✅ Sim         | `source` (startup/resume/clear/compact) |
| `Setup`               | Apenas com `--init-only`, `--init -p`, `--maintenance -p`   |              Não              |        ✅ Sim         | `trigger` (init/maintenance)            |
| `InstructionsLoaded`  | CLAUDE.md ou `.claude/rules/*.md` carregado                 |              Não              |          Não          | `load_reason`                           |
| `UserPromptSubmit`    | Usuário submete prompt (antes de Claude processar)          |        ✅ Sim (exit 2)        |        ✅ Sim         | Sem matcher                             |
| `UserPromptExpansion` | Comando `/slash` expande para prompt                        |        ✅ Sim (exit 2)        |        ✅ Sim         | `command_name`                          |
| `PreToolUse`          | Antes de cada ferramenta executar                           | ✅ Sim (allow/deny/ask/defer) |        ✅ Sim         | `tool_name`                             |
| `PermissionRequest`   | Diálogo de permissão prestes a aparecer                     |      ✅ Sim (allow/deny)      |          Não          | `tool_name`                             |
| `PermissionDenied`    | Classificador (auto mode) negou chamada                     |          Não (retry)          |          Não          | `tool_name`                             |
| `PostToolUse`         | Após ferramenta executar com sucesso                        |        ✅ Sim (block)         |        ✅ Sim         | `tool_name`                             |
| `PostToolUseFailure`  | Após ferramenta falhar                                      |              Não              |        ✅ Sim         | `tool_name`                             |
| `PostToolBatch`       | Após batch completo de ferramentas, antes do próximo modelo |        ✅ Sim (block)         |        ✅ Sim         | Sem matcher                             |
| `Notification`        | Claude Code emite notificação do sistema                    |              Não              |          Não          | `notification_type`                     |
| `SubagentStart`       | Subagente spawned via Agent tool                            |              Não              | ✅ Sim (no subagente) | `agent_type`                            |
| `SubagentStop`        | Subagente encerrou                                          |        ✅ Sim (block)         |          Não          | `agent_type`                            |
| `TaskCreated`         | Tarefa criada via `TaskCreate`                              |        ✅ Sim (exit 2)        |          Não          | Sem matcher                             |
| `TaskCompleted`       | Tarefa marcada como concluída                               |        ✅ Sim (exit 2)        |          Não          | Sem matcher                             |
| `Stop`                | Agente principal encerrou um turno                          |        ✅ Sim (block)         |          Não          | Sem matcher                             |
| `StopFailure`         | Turno encerrou por erro de API                              |              Não              |          Não          | `error` type                            |
| `TeammateIdle`        | Teammate de equipe prestes a ficar idle                     |        ✅ Sim (exit 2)        |          Não          | Sem matcher                             |
| `ConfigChange`        | Arquivo de configuração alterado durante sessão             |        ✅ Sim (block)         |          Não          | `source`                                |
| `CwdChanged`          | Diretório de trabalho mudou (ex: `cd`)                      |              Não              |          Não          | Sem matcher                             |
| `FileChanged`         | Arquivo observado mudou no disco                            |              Não              |          Não          | `matcher` = nome do arquivo             |
| `WorktreeCreate`      | Worktree sendo criada (`--worktree` ou isolation)           |          Sim (falha)          |          Não          | Sem matcher                             |
| `WorktreeRemove`      | Worktree sendo removida                                     |              Não              |          Não          | Sem matcher                             |
| `PreCompact`          | Compactação de contexto prestes a começar                   |   ✅ Sim (exit 2 ou block)    |          Não          | `trigger` (manual/auto)                 |
| `PostCompact`         | Compactação concluída                                       |              Não              |          Não          | `trigger` (manual/auto)                 |
| `Elicitation`         | Servidor MCP solicita input do usuário durante task         |        ✅ Sim (exit 2)        |          Não          | `mcp_server_name`                       |
| `ElicitationResult`   | Usuário respondeu a elicitação MCP                          |        ✅ Sim (exit 2)        |          Não          | `mcp_server_name`                       |
| `SessionEnd`          | Sessão encerrada                                            |              Não              |          Não          | `reason`                                |

---

## Hooks que podem injetar `additionalContext` ao agente

> Claude Code envolve o texto em um **system reminder** e insere no contexto. Não aparece como mensagem de chat. Limite: 10.000 caracteres (acima disso, salva em arquivo e passa o caminho).

| Hook                  | Onde é inserido                               |
| --------------------- | --------------------------------------------- |
| `SessionStart`        | Antes do primeiro prompt (início da conversa) |
| `Setup`               | No contexto de Claude                         |
| `SubagentStart`       | Antes do primeiro prompt do subagente         |
| `UserPromptSubmit`    | Junto ao prompt submetido                     |
| `UserPromptExpansion` | Junto ao prompt expandido                     |
| `PreToolUse`          | Junto ao resultado da ferramenta              |
| `PostToolUse`         | Junto ao resultado da ferramenta              |
| `PostToolUseFailure`  | Junto ao erro da ferramenta                   |
| `PostToolBatch`       | Uma vez antes do próximo model call           |

> **Boas práticas**: Escreva como fato ("O branch atual é feat/auth"), não como instrução imperativa. Texto imperativo pode disparar defesas contra prompt injection.

---

## Campos comuns de entrada (todos os eventos)

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "effort": { "level": "medium" }
}
```

> Dentro de subagentes, incluem também `agent_id` e `agent_type`.

---

## Payloads de Entrada por Evento

### `SessionStart`

```json
{
  "hook_event_name": "SessionStart",
  "source": "startup | resume | clear | compact",
  "model": "claude-sonnet-4-6",
  "agent_type": "optional-agent-name"
}
```

### `Setup`

```json
{
  "hook_event_name": "Setup",
  "trigger": "init | maintenance"
}
```

### `InstructionsLoaded`

```json
{
  "hook_event_name": "InstructionsLoaded",
  "file_path": "/path/to/CLAUDE.md",
  "memory_type": "User | Project | Local | Managed",
  "load_reason": "session_start | nested_traversal | path_glob_match | include | compact",
  "globs": ["*.ts"],
  "trigger_file_path": "/path/to/trigger",
  "parent_file_path": "/path/to/parent"
}
```

### `UserPromptSubmit`

```json
{
  "hook_event_name": "UserPromptSubmit",
  "prompt": "Write a function to..."
}
```

### `UserPromptExpansion`

```json
{
  "hook_event_name": "UserPromptExpansion",
  "expansion_type": "slash_command | mcp_prompt",
  "command_name": "example-skill",
  "command_args": "arg1 arg2",
  "command_source": "plugin",
  "prompt": "/example-skill arg1 arg2"
}
```

### `PreToolUse`

```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash | Write | Edit | Read | Glob | Grep | ...",
  "tool_input": {
    /* depende da ferramenta */
  },
  "tool_use_id": "toolu_01ABC..."
}
```

Tool inputs por ferramenta:

| Ferramenta        | Campos de `tool_input`                                           |
| ----------------- | ---------------------------------------------------------------- |
| `Bash`            | `command`, `description?`, `timeout?`, `run_in_background?`      |
| `Write`           | `file_path`, `content`                                           |
| `Edit`            | `file_path`, `old_string`, `new_string`, `replace_all?`          |
| `Read`            | `file_path`, `offset?`, `limit?`                                 |
| `Glob`            | `pattern`, `path?`                                               |
| `Grep`            | `pattern`, `path?`, `glob?`, `output_mode?`, `-i?`, `multiline?` |
| `WebFetch`        | `url`, `prompt`                                                  |
| `WebSearch`       | `query`, `allowed_domains?`, `blocked_domains?`                  |
| `Agent`           | `prompt`, `description`, `subagent_type?`, `model?`              |
| `AskUserQuestion` | `questions[]`, `answers?`                                        |
| `ExitPlanMode`    | `plan`, `planFilePath`, `allowedPrompts?`                        |

### `PermissionRequest`

```json
{
  "hook_event_name": "PermissionRequest",
  "tool_name": "Bash",
  "tool_input": { "command": "rm -rf node_modules" },
  "permission_suggestions": [
    {
      "type": "addRules",
      "rules": [{ "toolName": "Bash", "ruleContent": "rm -rf node_modules" }],
      "behavior": "allow",
      "destination": "localSettings"
    }
  ]
}
```

### `PermissionDenied`

```json
{
  "hook_event_name": "PermissionDenied",
  "tool_name": "Bash",
  "tool_input": { "command": "rm -rf /tmp/build" },
  "tool_use_id": "toolu_01ABC...",
  "reason": "Auto mode denied: command targets a path outside the project"
}
```

### `PostToolUse`

```json
{
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": { "file_path": "/path/to/file.txt", "content": "..." },
  "tool_response": { "filePath": "/path/to/file.txt", "success": true },
  "tool_use_id": "toolu_01ABC...",
  "duration_ms": 12
}
```

### `PostToolUseFailure`

```json
{
  "hook_event_name": "PostToolUseFailure",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test" },
  "tool_use_id": "toolu_01ABC...",
  "error": "Command exited with non-zero status code 1",
  "is_interrupt": false,
  "duration_ms": 4187
}
```

### `PostToolBatch`

```json
{
  "hook_event_name": "PostToolBatch",
  "tool_calls": [
    {
      "tool_name": "Read",
      "tool_input": { "file_path": "/path/to/file.py" },
      "tool_use_id": "toolu_01...",
      "tool_response": "1\tconteúdo..."
    }
  ]
}
```

### `Notification`

```json
{
  "hook_event_name": "Notification",
  "message": "Claude needs your permission",
  "title": "Permission needed",
  "notification_type": "permission_prompt | idle_prompt | auth_success | elicitation_dialog | elicitation_complete | elicitation_response"
}
```

### `SubagentStart`

```json
{
  "hook_event_name": "SubagentStart",
  "agent_id": "agent-abc123",
  "agent_type": "Explore | Plan | general-purpose | custom-name"
}
```

### `SubagentStop`

```json
{
  "hook_event_name": "SubagentStop",
  "stop_hook_active": false,
  "agent_id": "def456",
  "agent_type": "Explore",
  "agent_transcript_path": "~/.claude/projects/.../subagents/agent-def456.jsonl",
  "last_assistant_message": "Analysis complete...",
  "background_tasks": [],
  "session_crons": []
}
```

### `Stop`

```json
{
  "hook_event_name": "Stop",
  "stop_hook_active": true,
  "last_assistant_message": "I've completed the refactoring...",
  "background_tasks": [
    {
      "id": "task-001",
      "type": "shell | subagent | monitor | workflow | teammate | cloud session | MCP task",
      "status": "running",
      "description": "tail logs",
      "command": "tail -f /var/log/syslog"
    }
  ],
  "session_crons": [
    {
      "id": "cron-001",
      "schedule": "0 9 * * 1-5",
      "recurring": true,
      "prompt": "check the build"
    }
  ]
}
```

> `stop_hook_active: true` = já está continuando por um Stop hook. Claude Code interrompe depois de 8 bloqueios consecutivos.

### `StopFailure`

```json
{
  "hook_event_name": "StopFailure",
  "error": "rate_limit | authentication_failed | oauth_org_not_allowed | billing_error | invalid_request | model_not_found | server_error | max_output_tokens | unknown",
  "error_details": "429 Too Many Requests",
  "last_assistant_message": "API Error: Rate limit reached"
}
```

### `TaskCreated` / `TaskCompleted`

```json
{
  "hook_event_name": "TaskCreated",
  "task_id": "task-001",
  "task_subject": "Implement user authentication",
  "task_description": "Add login and signup endpoints",
  "teammate_name": "implementer",
  "team_name": "my-project"
}
```

### `TeammateIdle`

```json
{
  "hook_event_name": "TeammateIdle",
  "teammate_name": "researcher",
  "team_name": "my-project"
}
```

### `ConfigChange`

```json
{
  "hook_event_name": "ConfigChange",
  "source": "user_settings | project_settings | local_settings | policy_settings | skills",
  "file_path": "/path/to/.claude/settings.json"
}
```

### `CwdChanged`

```json
{
  "hook_event_name": "CwdChanged",
  "old_cwd": "/Users/my-project",
  "new_cwd": "/Users/my-project/src"
}
```

### `FileChanged`

```json
{
  "hook_event_name": "FileChanged",
  "file_path": "/Users/my-project/.envrc",
  "event": "change | add | unlink"
}
```

### `WorktreeCreate`

```json
{
  "hook_event_name": "WorktreeCreate",
  "name": "feature-auth"
}
```

### `WorktreeRemove`

```json
{
  "hook_event_name": "WorktreeRemove",
  "worktree_path": "/path/to/worktree"
}
```

### `PreCompact`

```json
{
  "hook_event_name": "PreCompact",
  "trigger": "manual | auto",
  "custom_instructions": ""
}
```

### `PostCompact`

```json
{
  "hook_event_name": "PostCompact",
  "trigger": "manual | auto",
  "compact_summary": "Summary of the compacted conversation..."
}
```

### `Elicitation`

```json
{
  "hook_event_name": "Elicitation",
  "mcp_server_name": "my-mcp-server",
  "message": "Please provide your credentials",
  "mode": "form | url",
  "requested_schema": {
    "type": "object",
    "properties": { "username": { "type": "string" } }
  },
  "url": "https://auth.example.com/login",
  "elicitation_id": "elicit-123"
}
```

### `ElicitationResult`

```json
{
  "hook_event_name": "ElicitationResult",
  "mcp_server_name": "my-mcp-server",
  "action": "accept | decline | cancel",
  "content": { "username": "alice" },
  "mode": "form",
  "elicitation_id": "elicit-123"
}
```

### `SessionEnd`

```json
{
  "hook_event_name": "SessionEnd",
  "reason": "clear | resume | logout | prompt_input_exit | bypass_permissions_disabled | other"
}
```

---

## Outputs e Controle de Decisão

### Campos JSON universais (todos os eventos)

| Campo              | Padrão  | Descrição                                                          |
| ------------------ | ------- | ------------------------------------------------------------------ |
| `continue`         | `true`  | Se `false`, Claude para completamente após o hook                  |
| `stopReason`       | —       | Mensagem ao usuário quando `continue: false`                       |
| `suppressOutput`   | `false` | Se `true`, oculta stdout do transcript (ainda vai para debug log)  |
| `systemMessage`    | —       | Mensagem de aviso mostrada ao usuário (não ao Claude)              |
| `terminalSequence` | —       | Escape sequence para Claude Code emitir (OSC 0/1/2/9/99/777 e BEL) |

### `SessionStart` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Branch atual: feat/auth-refactor\nMudanças: src/auth.ts",
    "initialUserMessage": "Primeiro prompt em modo não-interativo (-p)",
    "watchPaths": ["/absolute/path/to/watch"]
  }
}
```

> `SessionStart` também aceita stdout diretamente como contexto (sem JSON).

### `UserPromptSubmit` → decisão

```json
{
  "decision": "block",
  "reason": "Explicação para o usuário",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Contexto adicional para Claude",
    "sessionTitle": "Título da sessão",
    "suppressOriginalPrompt": false
  }
}
```

### `PreToolUse` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow | deny | ask | defer",
    "permissionDecisionReason": "Motivo",
    "updatedInput": { "field": "new value" },
    "additionalContext": "Contexto sobre o ambiente atual"
  }
}
```

> Precedência quando múltiplos hooks: `deny` > `defer` > `ask` > `allow`
> `"defer"` só funciona em modo não-interativo (`-p`) e com chamada única de ferramenta.

### `PostToolUse` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Este arquivo é gerado. Edite src/schema.ts.",
    "updatedToolOutput": {
      "stdout": "[redacted]",
      "stderr": "",
      "interrupted": false,
      "isImage": false
    },
    "updatedMCPToolOutput": "texto alternativo para MCP"
  }
}
```

> Também aceita top-level: `{ "decision": "block", "reason": "..." }`

### `PostToolUseFailure` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUseFailure",
    "additionalContext": "Informações sobre a falha para Claude"
  }
}
```

### `PostToolBatch` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolBatch",
    "additionalContext": "Estes arquivos são do módulo ledger. Execute pytest antes de concluir."
  }
}
```

> Também aceita: `{ "decision": "block", "reason": "..." }` ou `{ "continue": false }`

### `Stop` / `SubagentStop` → decisão

```json
{
  "decision": "block",
  "reason": "Todos os testes devem passar antes de parar"
}
```

### `PermissionRequest` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow | deny",
      "message": "Motivo (para deny)",
      "interrupt": false,
      "updatedInput": { "command": "npm run lint" },
      "updatedPermissions": [
        {
          "type": "addRules | replaceRules | removeRules | setMode | addDirectories | removeDirectories",
          "rules": [{ "toolName": "Bash", "ruleContent": "npm *" }],
          "behavior": "allow",
          "destination": "session | localSettings | projectSettings | userSettings"
        }
      ]
    }
  }
}
```

### `PermissionDenied` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionDenied",
    "retry": true
  }
}
```

### `SubagentStart` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "Siga as diretrizes de segurança para esta tarefa"
  }
}
```

### `ConfigChange` → decisão

```json
{
  "decision": "block",
  "reason": "Mudanças em project settings requerem aprovação"
}
```

> `policy_settings` nunca pode ser bloqueado.

### `CwdChanged` / `FileChanged` → watchPaths

```json
{
  "watchPaths": ["/absolute/path/to/file1", "/absolute/path/to/file2"]
}
```

### `WorktreeCreate` → path

```bash
# Command hook: imprimir path no stdout
echo "/absolute/path/to/new/worktree"
```

```json
// HTTP hook
{
  "hookSpecificOutput": {
    "hookEventName": "WorktreeCreate",
    "worktreePath": "/absolute/path/to/new/worktree"
  }
}
```

### `Elicitation` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Elicitation",
    "action": "accept | decline | cancel",
    "content": { "username": "alice" }
  }
}
```

### `ElicitationResult` → hookSpecificOutput

```json
{
  "hookSpecificOutput": {
    "hookEventName": "ElicitationResult",
    "action": "accept | decline | cancel",
    "content": { "username": "alice-override" }
  }
}
```

---

## Exit Codes para Command Hooks

| Exit code | Comportamento padrão                               | Quando bloqueia                 |
| --------- | -------------------------------------------------- | ------------------------------- |
| `0`       | Sucesso. stdout parseado como JSON                 | —                               |
| `2`       | Erro bloqueante                                    | Ver tabela abaixo               |
| Outros    | Erro não-bloqueante. Execução continua (fail-open) | Nunca (exceto `WorktreeCreate`) |

### Comportamento de exit code 2 por evento

| Evento                | Bloqueia? | Efeito                                           |
| --------------------- | :-------: | ------------------------------------------------ |
| `PreToolUse`          |    ✅     | Bloqueia a chamada da ferramenta                 |
| `PermissionRequest`   |    ✅     | Nega a permissão                                 |
| `UserPromptSubmit`    |    ✅     | Bloqueia processamento e apaga o prompt          |
| `UserPromptExpansion` |    ✅     | Bloqueia a expansão                              |
| `Stop`                |    ✅     | Impede Claude de parar, continua a conversa      |
| `SubagentStop`        |    ✅     | Impede o subagente de parar                      |
| `TeammateIdle`        |    ✅     | Teammate continua trabalhando                    |
| `TaskCreated`         |    ✅     | Desfaz a criação da tarefa                       |
| `TaskCompleted`       |    ✅     | Impede tarefa de ser marcada como concluída      |
| `ConfigChange`        |    ✅     | Bloqueia mudança de configuração                 |
| `PostToolBatch`       |    ✅     | Para o loop agentivo antes do próximo model call |
| `PreCompact`          |    ✅     | Bloqueia compactação                             |
| `Elicitation`         |    ✅     | Nega a elicitação                                |
| `ElicitationResult`   |    ✅     | Bloqueia resposta (vira `decline`)               |
| `WorktreeCreate`      |    ✅     | Qualquer exit non-zero falha a criação           |
| `PostToolUse`         |    ❌     | Mostra stderr ao Claude                          |
| `PostToolUseFailure`  |    ❌     | Mostra stderr ao Claude                          |
| `PermissionDenied`    |    ❌     | Ignorado (negação já ocorreu)                    |
| `Notification`        |    ❌     | Mostra stderr ao usuário apenas                  |
| `SubagentStart`       |    ❌     | Mostra stderr ao usuário apenas                  |
| `SessionStart`        |    ❌     | Mostra stderr ao usuário apenas                  |
| `Setup`               |    ❌     | Mostra stderr ao usuário apenas                  |
| `SessionEnd`          |    ❌     | Mostra stderr ao usuário apenas                  |
| `StopFailure`         |    ❌     | Ignorado                                         |
| `PostCompact`         |    ❌     | Mostra stderr ao usuário apenas                  |
| `InstructionsLoaded`  |    ❌     | Exit code ignorado                               |
| `WorktreeRemove`      |    ❌     | Falhas logadas apenas em debug mode              |

---

## Matcher Patterns

| Matcher                       | Comportamento                                           |
| ----------------------------- | ------------------------------------------------------- |
| `"*"`, `""`, ou omitido       | Dispara em toda ocorrência                              |
| Só letras, dígitos, `_`, `\|` | String exata ou lista separada por `\|` (`Edit\|Write`) |
| Contém outros caracteres      | Regex JavaScript (`^Notebook`, `mcp__memory__.*`)       |

### Ferramenta MCP: padrão `mcp__<server>__<tool>`

- `mcp__memory__.*` → todas as ferramentas do servidor `memory`
- `mcp__.*__write.*` → qualquer ferramenta começando com `write` de qualquer servidor

### Filtro `if` (tool events apenas)

```json
{
  "if": "Bash(git *)",
  "command": "/path/to/git-hook.sh"
}
```

Usa sintaxe de permission rules. Só avaliado em: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`.

---

## Campos comuns dos hook handlers

| Campo           | Obrigatório | Descrição                                                                                              |
| --------------- | :---------: | ------------------------------------------------------------------------------------------------------ |
| `type`          |     Sim     | `command`, `http`, `mcp_tool`, `prompt`, `agent`                                                       |
| `if`            |     Não     | Filtro adicional (permission rule syntax)                                                              |
| `timeout`       |     Não     | Segundos. Padrão: 600 (command/http/mcp_tool), 30 (prompt), 60 (agent). `UserPromptSubmit` limita a 30 |
| `statusMessage` |     Não     | Mensagem no spinner enquanto o hook roda                                                               |
| `once`          |     Não     | Se `true`, roda uma vez por sessão (apenas frontmatter de skills)                                      |

### Campos de command hook

| Campo         | Obrigatório | Descrição                                         |
| ------------- | :---------: | ------------------------------------------------- |
| `command`     |     Sim     | Comando ou executável                             |
| `args`        |     Não     | Array de argumentos (exec form — sem shell)       |
| `async`       |     Não     | Se `true`, roda em background sem bloquear        |
| `asyncRewake` |     Não     | Se `true`, exit code 2 desperta Claude mesmo idle |
| `shell`       |     Não     | `"bash"` (padrão) ou `"powershell"`               |

### Campos de HTTP hook

| Campo            | Obrigatório | Descrição                                              |
| ---------------- | :---------: | ------------------------------------------------------ |
| `url`            |     Sim     | URL do endpoint                                        |
| `headers`        |     Não     | Headers adicionais (suporta `$VAR_NAME`)               |
| `allowedEnvVars` |     Não     | Vars de ambiente permitidas na interpolação de headers |

### Campos de MCP tool hook

| Campo    | Obrigatório | Descrição                                         |
| -------- | :---------: | ------------------------------------------------- |
| `server` |     Sim     | Nome do servidor MCP conectado                    |
| `tool`   |     Sim     | Nome da ferramenta                                |
| `input`  |     Não     | Argumentos (suporta `${path}` do JSON de entrada) |

### Campos de prompt/agent hook

| Campo             | Obrigatório | Descrição                                                        |
| ----------------- | :---------: | ---------------------------------------------------------------- |
| `prompt`          |     Sim     | Texto do prompt. Use `$ARGUMENTS` para injetar o JSON de entrada |
| `model`           |     Não     | Modelo a usar (padrão: modelo rápido)                            |
| `continueOnBlock` |     Não     | Se `true`, feed reason de volta ao Claude em vez de parar        |

---

## Suporte por tipo de hook

| Tipo                          | Eventos suportados                                                                                                                                                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `command`, `http`, `mcp_tool` | Todos                                                                                                                                                                                                                          |
| `prompt`, `agent`             | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Stop`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle`, `UserPromptSubmit`, `UserPromptExpansion`, `PermissionRequest`, `PermissionDenied` |
| `command`, `mcp_tool` apenas  | `SessionStart`, `Setup` (não suportam `http`, `prompt`, `agent`)                                                                                                                                                               |

---

## Hooks assíncronos (`async: true`)

Apenas `type: "command"`. O hook roda em background enquanto Claude continua.

- **Não pode** bloquear ou retornar `decision`, `permissionDecision`, `continue`
- `additionalContext` é entregue no próximo turno da conversa
- `asyncRewake: true` + exit code 2 desperta Claude imediatamente mesmo idle
- Cada execução cria processo separado (sem deduplicação)

---

## Variáveis de ambiente especiais

| Variável             | Disponível em                                        | Conteúdo                                                   |
| -------------------- | ---------------------------------------------------- | ---------------------------------------------------------- |
| `CLAUDE_ENV_FILE`    | `SessionStart`, `Setup`, `CwdChanged`, `FileChanged` | Arquivo para persistir vars de ambiente para comandos Bash |
| `CLAUDE_PROJECT_DIR` | Todos command hooks                                  | Raiz do projeto                                            |
| `CLAUDE_PLUGIN_ROOT` | Plugin hooks                                         | Diretório de instalação do plugin                          |
| `CLAUDE_PLUGIN_DATA` | Plugin hooks                                         | Diretório de dados persistentes do plugin                  |
| `CLAUDE_CODE_REMOTE` | Todos                                                | `"true"` em ambientes web remotos                          |
| `CLAUDE_EFFORT`      | Eventos com `effort` field                           | Nível de esforço atual                                     |

---

## Path placeholders

```json
{
  "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-style.sh",
  "args": []
}
```

> Use **exec form** (`args` presente) para paths com placeholders — evita problemas de quoting.

---

## Hooks em Skills e Agentes (frontmatter YAML)

```yaml
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

> Para subagentes, hooks `Stop` são automaticamente convertidos para `SubagentStop`.

---

## Desabilitar hooks

```json
{
  "disableAllHooks": true,
  "hooks": {}
}
```

- Em arquivo `.github/hooks/*.json` → apenas aquele arquivo é ignorado
- Em `settings.json` → todos os hooks de todas as fontes ignorados (respeita hierarquia de managed settings)

---

## Depuração

```bash
claude --debug-file /path/to/debug.log
# ou
claude --debug
# log em ~/.claude/debug/<session-id>.txt
```

```
[DEBUG] Executing hooks for PostToolUse:Write
[DEBUG] Found 1 hook commands to execute
[DEBUG] Executing hook command: <command> with timeout 600000ms
[DEBUG] Hook command completed with status 0: <stdout>
```

Para logs mais detalhados: `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose`

---

## Menu `/hooks`

Digite `/hooks` no Claude Code para navegar por todos os hooks configurados. Mostra evento, matcher, tipo, fonte (User/Project/Local/Plugin/Session/Built-in) e detalhes completos. Read-only.
