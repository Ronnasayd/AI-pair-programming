# Stack Hints — Guia por Linguagem e Framework

Use este arquivo para saber onde procurar rotas, modelos e serviços conforme a stack identificada.

---

## Node.js / TypeScript

### Express

- Rotas: arquivos com `Router()`, `app.get/post/put/delete/patch`
- Convenção de pastas: `routes/`, `controllers/`, `middlewares/`
- Modelos: se usar Prisma → `prisma/schema.prisma`; Mongoose → `models/*.ts`
- Entry point: `src/index.ts`, `src/app.ts`, `server.ts`

### NestJS

- Módulos: `*.module.ts`
- Controllers (rotas): `*.controller.ts` — decoradores `@Get()`, `@Post()`, `@Put()`, `@Delete()`
- Serviços: `*.service.ts`
- Entidades/modelos: `*.entity.ts` ou `*.schema.ts`
- Guards (auth/roles): `*.guard.ts`
- Busca de rotas: `grep -r "@Get\|@Post\|@Put\|@Delete\|@Patch" src/ --include="*.ts"`

### Fastify

- Rotas: `fastify.route()`, `fastify.get/post/put/delete`
- Plugins: `fastify.register()`
- Convenção: `routes/`, `plugins/`

---

## Python

### FastAPI

- Rotas: decoradores `@app.get`, `@app.post`, `@router.get`, etc.
- Modelos Pydantic: `class ... (BaseModel):`
- Dependências: `Depends()`
- Busca: `grep -r "@app\.\|@router\." . --include="*.py"`

### Django

- Rotas: `urls.py` (em cada app e no `project/urls.py`)
- Models: `models.py` em cada app
- Views: `views.py`
- Serializers (DRF): `serializers.py`
- Busca de apps: `find . -name "urls.py"`

### Flask

- Rotas: `@app.route()`, `@blueprint.route()`
- Blueprints: `Blueprint()`
- Busca: `grep -r "@app.route\|@.*\.route" . --include="*.py"`

---

## Go

### Gin

- Rotas: `r.GET`, `r.POST`, `r.PUT`, `r.DELETE`, `r.Group`
- Handlers: funções com `*gin.Context`
- Busca: `grep -r "\.GET\|\.POST\|\.PUT\|\.DELETE" . --include="*.go"`

### Chi / Echo / Fiber

- Rotas: `r.Get`, `r.Post`, `e.GET`, `app.Get`
- Busca: `grep -r "\.Get\|\.Post\|\.Put\|\.Delete\|Handle" . --include="*.go"`

### Modelos Go

- Structs com tags `json:`, `db:`, `bson:` são entidades de dados
- `grep -r "type .* struct" . --include="*.go" | head -30`

---

## Ruby on Rails

- Rotas: `config/routes.rb` — leia este arquivo completamente
- Controllers: `app/controllers/`
- Models: `app/models/`
- Serializers: `app/serializers/`
- Jobs: `app/jobs/`
- Mailers: `app/mailers/`

---

## PHP / Laravel

- Rotas: `routes/web.php`, `routes/api.php`
- Controllers: `app/Http/Controllers/`
- Models: `app/Models/`
- Middleware: `app/Http/Middleware/`
- Jobs/Queues: `app/Jobs/`
- Busca de rotas: `grep -r "Route::" routes/ --include="*.php"`

---

## Java / Spring Boot

- Rotas: `@RestController`, `@GetMapping`, `@PostMapping`, `@RequestMapping`
- Entidades: `@Entity`
- Repositórios: `@Repository`, `extends JpaRepository`
- Serviços: `@Service`
- Busca: `grep -r "@GetMapping\|@PostMapping\|@PutMapping\|@DeleteMapping\|@RequestMapping" src/ --include="*.java"`

---

## .NET / C# (ASP.NET Core)

- Controllers: arquivos que herdam de `ControllerBase` ou `Controller`
- Rotas: atributos `[HttpGet]`, `[HttpPost]`, `[Route]`
- Models: `Models/`, `Entities/`, `DTOs/`
- Services: `Services/`
- Busca: `grep -r "HttpGet\|HttpPost\|HttpPut\|HttpDelete" . --include="*.cs"`

---

## Rust (Actix / Axum)

- Rotas Actix: `.service()`, `web::get()`, `web::post()`
- Rotas Axum: `Router::new().route()`
- Handlers: funções async com `HttpRequest` ou `Extension`

---

## Monorepos e Projetos Full-Stack

### Next.js (App Router)

- Rotas de página: `app/**/page.tsx`
- API Routes: `app/api/**/route.ts`
- Server Actions: arquivos com `"use server"`
- Busca: `find . -name "route.ts" -path "*/api/*"`

### Next.js (Pages Router)

- Páginas: `pages/*.tsx`
- API Routes: `pages/api/*.ts`

### Nx / Turborepo

- Projetos: `apps/`, `packages/`
- Cada subprojeto tem seu próprio package.json e estrutura
- Analise cada `app` individualmente

---

## Bancos de Dados e ORMs

| ORM / ODM    | Onde estão os schemas/modelos                     |
| ------------ | ------------------------------------------------- |
| Prisma       | `prisma/schema.prisma`                            |
| TypeORM      | arquivos `*.entity.ts` ou decorador `@Entity()`   |
| Sequelize    | `models/*.js` ou `models/*.ts`                    |
| Mongoose     | `models/*.js`, schema com `new Schema({})`        |
| Drizzle      | arquivos `db/schema.ts` ou `drizzle/*.ts`         |
| SQLAlchemy   | classes que herdam de `Base` ou `DeclarativeBase` |
| Django ORM   | `models.py` em cada app                           |
| ActiveRecord | `app/models/*.rb`                                 |

---

## Filas e Workers

| Ferramenta    | Como identificar                             |
| ------------- | -------------------------------------------- |
| BullMQ / Bull | `import { Queue, Worker } from 'bullmq'`     |
| Celery        | `@app.task`, `task.delay()`                  |
| Sidekiq       | `include Sidekiq::Worker`                    |
| RabbitMQ      | `amqplib`, `pika`, `aio-pika`                |
| AWS SQS       | `@aws-sdk/client-sqs`, `boto3.client('sqs')` |
| Kafka         | `kafkajs`, `confluent-kafka-python`          |

---

## Autenticação e Autorização

Busque por estes padrões para mapear roles e permissões:

```bash
# Geral
grep -r "role\|permission\|scope\|policy\|guard\|middleware\|auth" . \
  --include="*.ts" --include="*.js" --include="*.py" --include="*.rb" \
  -l | head -20

# JWT
grep -r "jwt\|JsonWebToken\|decode\|verify" . \
  --include="*.ts" --include="*.js" --include="*.py" -l | head -10

# OAuth
grep -r "oauth\|passport\|strategy\|provider" . \
  --include="*.ts" --include="*.js" -l | head -10
```
