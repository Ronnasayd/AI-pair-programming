Let's create inside instructions/folder-structure.instructions.md the rules for folder structure
for this project. This project follows a Modular Monolith architecture with Clean Architecture
inside each module.

The top-level structure under src/ must have these directories:

- modules/ — one subdirectory per bounded context, each following Clean Architecture internally
- integrations/ — Anti-Corruption Layer for external systems (one subdirectory per provider)
- shared/ — code shared across modules: kernel base classes, event bus, error types, and shared value types
- main/ — bootstrap, HTTP route aggregation, cron jobs, async workers, and DI container

Each module under modules/<module-name>/ must have exactly these layers:

- domain/ — entities, repository interfaces (ports), domain services, and value objects. No external dependencies allowed.
- application/ — use-cases (one subdirectory per use case), DTOs, and mappers. Depends only on domain.
- infrastructure/ — concrete implementations of repository interfaces and external service adapters. Depends on domain and application.
- presentation/ — controllers, routes, and Zod validators. Depends only on application. Never imports from another module's internals.
- index.ts — the module's public facade. The only file other modules are allowed to import.

Each use-case directory under application/use-cases/<action-name>/ must contain:

- ActionNameUseCase.ts — the use-case implementation
- **tests**/ActionNameUseCase.spec.ts — unit test with all dependencies mocked

Each controller under presentation/controllers/ must have a sibling **tests**/ directory containing:

- MyController.integration.spec.ts — integration test using supertest against the HTTP layer

Add the full directory structure in notation form, and define the purpose of each directory
beside it as a comment. Also define the cross-module communication rule: a module may only
import from another module's index.ts, never from its internal layers.

Remember to bind this rule (folder-structure.instructions.md) to the AGENTS.md file.
