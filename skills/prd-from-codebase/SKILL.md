---
name: prd-from-codebase
description: >
  Gera um PRD (Product Requirements Document) completo em Markdown a partir de uma base de código existente.
  Use esta skill sempre que o usuário quiser documentar um software sem documentação, entender o que um projeto faz,
  gerar um documento de produto a partir de código, mapear funcionalidades de uma aplicação, identificar agentes/papéis
  de um sistema, ou quando mencionar termos como "PRD", "documentar o projeto", "gerar documentação do produto",
  "o que esse código faz", "mapear funcionalidades", "entender a base de código", "reverse PRD" ou similares.
  A skill usa as ferramentas disponíveis (bash, view, etc.) para explorar autonomamente a base de código
  antes de gerar o documento — o usuário não precisa colar código manualmente.
---

# PRD from Codebase

Gera um PRD estruturado e profissional a partir da análise autônoma de uma base de código, usando as ferramentas disponíveis para explorar arquivos, dependências, rotas e estrutura do projeto.

---

## Fluxo de execução

### FASE 1 — Descoberta do projeto

Antes de escrever qualquer linha do PRD, execute as etapas de descoberta abaixo em ordem. **Não pule etapas.** Use `bash_tool` e `view` para cada uma.

#### 1.1 Localizar o projeto

Se o usuário informou um caminho, use-o. Caso contrário, procure em ordem:

```bash
ls /mnt/user-data/uploads/        # arquivos enviados via upload
ls /home/claude/                   # diretório de trabalho
find / -name "package.json" -o -name "requirements.txt" -o -name "go.mod" 2>/dev/null | head -20
```

#### 1.2 Mapear a estrutura de alto nível

```bash
find <ROOT> -type f \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/dist/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/build/*" \
  ! -path "*/.next/*" \
  | head -120
```

Depois use `view <ROOT>` para ter a visão em árvore de 2 níveis.

#### 1.3 Identificar a stack tecnológica

Leia os arquivos de manifesto/dependências relevantes. Leia **todos** que existirem:

| Arquivo                                            | Stack                         |
| -------------------------------------------------- | ----------------------------- |
| `package.json`                                     | Node / JS / TS                |
| `requirements.txt` / `pyproject.toml` / `setup.py` | Python                        |
| `go.mod`                                           | Go                            |
| `Cargo.toml`                                       | Rust                          |
| `pom.xml` / `build.gradle`                         | Java / Kotlin                 |
| `Gemfile`                                          | Ruby                          |
| `composer.json`                                    | PHP                           |
| `*.csproj` / `*.sln`                               | .NET / C#                     |
| `Dockerfile` / `docker-compose.yml`                | Infraestrutura                |
| `.env.example` / `.env.sample`                     | Variáveis e serviços externos |

#### 1.4 Ler arquivos de entrada do projeto

Leia nesta ordem de prioridade:

1. `README.md` ou `README.rst` (visão geral existente)
2. Arquivos de configuração principal (`config.js`, `settings.py`, `appsettings.json`, etc.)
3. Ponto de entrada da aplicação (`main.py`, `index.js`, `app.py`, `server.ts`, `Program.cs`, `main.go`, etc.)

#### 1.5 Mapear módulos e domínios

Identifique as pastas de domínio/módulo (ex: `src/`, `app/`, `modules/`, `services/`, `controllers/`, `features/`).
Para cada módulo principal, leia seu arquivo de índice ou o arquivo mais representativo:

```bash
# Exemplo para projetos Node/TS:
find <ROOT>/src -name "index.*" | head -30
# Exemplo para projetos Python:
find <ROOT> -name "__init__.py" | head -30
```

#### 1.6 Descobrir rotas e endpoints

Busque padrões de roteamento conforme a stack:

```bash
# Express / Fastify / Koa (JS)
grep -r "router\.\|app\.get\|app\.post\|app\.put\|app\.delete\|app\.patch" <ROOT>/src --include="*.js" --include="*.ts" -l

# FastAPI / Flask / Django (Python)
grep -r "@app\.\|@router\.\|path(" <ROOT> --include="*.py" -l

# Go (gin/chi/echo)
grep -r "\.GET\|\.POST\|\.PUT\|\.DELETE\|Handle\|HandleFunc" <ROOT> --include="*.go" -l

# Rails
find <ROOT> -name "routes.rb"
```

Depois leia os arquivos encontrados para extrair os endpoints.

#### 1.7 Identificar agentes, papéis e entidades

Busque por:

- Modelos de dados / entidades (`models/`, `entities/`, `schemas/`)
- Serviços de negócio (`services/`, `usecases/`, `handlers/`)
- Integrações externas (`integrations/`, `adapters/`, `clients/`, `providers/`)
- Autenticação e papéis de usuário (busque por "role", "permission", "auth", "guard", "middleware")
- Workers / jobs / agendadores (busque por "queue", "worker", "cron", "scheduler", "job")

```bash
grep -r "role\|permission\|admin\|user\|auth" <ROOT>/src --include="*.ts" --include="*.js" --include="*.py" -l | head -15
```

#### 1.8 Mapear integrações e fluxos de dados

Identifique serviços externos e fluxos:

```bash
# Buscar imports de SDKs, clients HTTP e filas
grep -r "import\|require\|from" <ROOT>/src --include="*.ts" --include="*.js" --include="*.py" | \
  grep -iE "stripe|sendgrid|twilio|s3|sqs|redis|rabbitmq|kafka|openai|anthropic|firebase|supabase|prisma|mongoose|sequelize|typeorm|axios|fetch|httpx|requests" | \
  head -40
```

---

### FASE 2 — Síntese e geração do PRD

Com todas as informações coletadas, gere o PRD seguindo **exatamente** o template em `references/prd-template.md`.

**Regras de geração:**

- Escreva em linguagem clara e orientada a produto — não técnica demais, não vaga demais
- Cada seção deve ter conteúdo real extraído do código — **nunca deixe seções genéricas ou com placeholder**
- Se uma seção não se aplicar (ex: sem workers), omita-a completamente
- Infira nomes de produto/sistema a partir do `package.json` (campo `name`), `README`, ou nome da pasta raiz
- Ao listar endpoints, use o formato `MÉTODO /caminho — descrição inferida`
- Ao descrever funcionalidades, use bullets curtos e diretos ao ponto
- Adicione uma seção `⚠️ Limitações da Análise` ao final caso alguma parte do código não tenha sido possível analisar

### FASE 3 — Salvar o arquivo

Salve o PRD gerado em:

```
/mnt/user-data/outputs/<nome-do-projeto>-prd.md
```

Depois use `present_files` para entregar ao usuário.

---

## Boas práticas de análise

- **Não assuma** — se não encontrou algo, diga que não encontrou
- **Priorize código sobre comentários** — o código é a fonte de verdade
- **Leia no mínimo 5-10 arquivos centrais** antes de escrever qualquer coisa
- **Busque por testes** (`__tests__/`, `tests/`, `spec/`) — eles revelam comportamentos esperados
- **Verifique variáveis de ambiente** — revelam serviços externos e configurações críticas
- Se o projeto for muito grande (>500 arquivos), foque nos módulos com mais conexões (mais importados)

---

## Leia antes de gerar

→ `references/prd-template.md` — Template obrigatório do PRD
→ `references/stack-hints.md` — Dicas por linguagem/framework para localizar rotas, modelos e serviços
