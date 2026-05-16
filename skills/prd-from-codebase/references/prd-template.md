# PRD — {Nome do Produto}

> **Versão:** 1.0
> **Gerado em:** {data atual}
> **Fonte:** Análise automatizada da base de código
> **Status:** Rascunho — validar com o time de produto

---

## 1. Visão Geral do Produto

**O que é:**
{2-4 frases descrevendo o propósito central da aplicação, o problema que resolve e para quem}

**Tipo de sistema:**
{ex: API REST, Aplicação Web Full-Stack, Microserviço, CLI, Worker de processamento, etc.}

**Público-alvo / Usuários:**
{quem usa o sistema — inferido dos modelos de usuário, roles e fluxos de autenticação encontrados}

---

## 2. Stack Tecnológica

| Camada              | Tecnologia                                             |
| ------------------- | ------------------------------------------------------ |
| Linguagem           | {ex: TypeScript 5.x, Python 3.11, Go 1.21}             |
| Runtime / Framework | {ex: Node.js 20, FastAPI, Gin}                         |
| Banco de dados      | {ex: PostgreSQL via Prisma, MongoDB via Mongoose}      |
| Cache               | {ex: Redis, Memcached — ou "não identificado"}         |
| Fila / Mensageria   | {ex: BullMQ, RabbitMQ, SQS — ou "não identificado"}    |
| Autenticação        | {ex: JWT, OAuth2, Passport.js — ou "não identificado"} |
| Infraestrutura      | {ex: Docker, Docker Compose, Kubernetes}               |
| Serviços externos   | {ex: Stripe, SendGrid, OpenAI, S3}                     |

---

## 3. Arquitetura e Módulos

### Estrutura principal

```
{reproduza a estrutura de diretórios relevante, omitindo node_modules, dist, etc.}
```

### Módulos e responsabilidades

| Módulo / Pasta | Responsabilidade        |
| -------------- | ----------------------- |
| `{módulo}`     | {o que esse módulo faz} |
| `{módulo}`     | {o que esse módulo faz} |

---

## 4. Funcionalidades Mapeadas

{Para cada domínio/feature encontrado, um bloco como abaixo:}

### 4.1 {Nome da Funcionalidade}

**Descrição:** {o que faz, em 1-2 frases}
**Localização no código:** `{arquivo ou pasta principal}`

**Comportamentos identificados:**

- {comportamento 1}
- {comportamento 2}
- {comportamento 3}

---

### 4.2 {Nome da Funcionalidade}

**Descrição:** {o que faz, em 1-2 frases}
**Localização no código:** `{arquivo ou pasta principal}`

**Comportamentos identificados:**

- {comportamento 1}
- {comportamento 2}

---

## 5. Agentes e Papéis do Sistema

{Descreva os perfis de usuário, agentes automatizados, workers e serviços internos identificados}

### Papéis de usuário

| Papel    | Permissões / Capacidades |
| -------- | ------------------------ |
| `{role}` | {o que pode fazer}       |
| `{role}` | {o que pode fazer}       |

### Agentes / Processos automatizados

| Agente / Worker | Função      | Gatilho              |
| --------------- | ----------- | -------------------- |
| `{nome}`        | {o que faz} | {evento, cron, fila} |

---

## 6. Endpoints e APIs

{Liste os endpoints encontrados, agrupados por domínio/recurso}

### {Domínio / Recurso}

| Método   | Rota           | Descrição inferida            |
| -------- | -------------- | ----------------------------- |
| `GET`    | `/recurso`     | Lista ou recupera recursos    |
| `POST`   | `/recurso`     | Cria um novo recurso          |
| `PUT`    | `/recurso/:id` | Atualiza um recurso existente |
| `DELETE` | `/recurso/:id` | Remove um recurso             |

---

## 7. Fluxos de Dados e Integrações

### Integrações externas identificadas

| Serviço     | Finalidade   | Como é usado                |
| ----------- | ------------ | --------------------------- |
| `{serviço}` | {finalidade} | {SDK, HTTP direto, webhook} |

### Fluxos principais

**{Nome do fluxo}:**

```
{Usuário / Sistema} → {passo 1} → {passo 2} → {resultado}
```

---

## 8. Configurações e Variáveis de Ambiente

| Variável     | Finalidade       | Obrigatória |
| ------------ | ---------------- | ----------- |
| `{VAR_NAME}` | {para que serve} | Sim / Não   |

---

## 9. Pontos de Atenção para o Time de Produto

{Liste aqui inconsistências, código comentado, TODOs relevantes, ou decisões de arquitetura que merecem atenção — inferidos do código}

- {ponto 1}
- {ponto 2}

---

## ⚠️ Limitações da Análise

{Inclua esta seção apenas se houver limitações}

- {ex: "Pasta `legacy/` não analisada por conter código sem estrutura clara"}
- {ex: "Endpoints de terceiros não mapeados — encontrado apenas client HTTP genérico"}
- {ex: "Lógica de permissões parcialmente inferida — validar com o time de engenharia"}

---

_Documento gerado automaticamente por análise de código. Recomenda-se validação com o time de engenharia antes de uso em decisões de produto._
