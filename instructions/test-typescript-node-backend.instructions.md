---
description: TS/Node backend testing — integration-first with real SQLite (Prisma), mock only external services (email/storage/3rd-party APIs/logger/clock), controller tests via supertest, error-path coverage, cleanup in beforeEach/afterEach, no mocked Prisma. Apply to *.test.ts/js in backend projects. Do NOT use for frontend/generic test style (see test.instructions.md).
applyTo: "**/*.test.ts,**/*.test.js"
---

# Testing Instructions

Backend tests are **integration-first with real SQLite** (Prisma), not mock-heavy. Production-ready, maintainable.

## Core rule: integration over mocks

**Always prefer real SQLite operations over mocked Prisma:**

```typescript
// ✅ GOOD — real database
describe("UserService - Integração com SQLite", () => {
  beforeEach(async () => {
    await prisma.user.deleteMany();
  });
  it("cria um usuário com sucesso", async () => {
    const user = await UserService.create({
      username: "joao@teste.com",
      password: "123456",
      name: "João"
    });
    const found = await prisma.user.findUnique({ where: { id: user.id } });
    expect(found?.username).toBe("joao@teste.com");
  });
});

// ❌ BAD — unnecessary mocking when integration is possible
jest.mock("@/src/lib/prisma");
```

Mock **only**: external services (email/storage/3rd-party APIs), non-critical side effects (logger, fs when not critical), time-dependent ops (`Date.now`, `setTimeout`). Never mock Prisma/DB — see [[references/test-typescript-node-backend-templates.md]] for mock-management patterns (external client, logger, fs).

## Test database setup

SQLite is configured in `jest.env-setup.ts` + `schema.test.prisma`. Clean state in `beforeAll`/`beforeEach`, disconnect in `afterAll`:

```typescript
beforeEach(async () => {
  jest.clearAllMocks();
  await prisma.resource.deleteMany();
  await prisma.user.deleteMany();
});
afterAll(async () => {
  await prisma.$disconnect();
});
```

Never hard-delete in production code; `deleteMany()` is test-cleanup only.

## File organization & naming

Service tests in `tests/`, isolated unit tests in `__tests__/` — see [[references/test-typescript-node-backend-templates.md]] for the layout. Test names descriptive, in **Portuguese**: `it("cria um usuário com sucesso")`, not `it("works")`.

## AAA pattern

```typescript
it("deve criar um recurso com sucesso", async () => {
  // ARRANGE
  const data: CreateResourceRequestDTO = {
    name: "Test Resource",
    user_id: 1,
    created_by: userId
  };
  externalApiClientMock.createResource.mockResolvedValue(100); // mock only external dep
  // ACT
  const result = await ResourceService.create(
    data,
    externalApiClientMock as any
  );
  // ASSERT
  expect(result.external_id).toBe(100);
  const found = await prisma.resource.findUnique({ where: { id: result.id } });
  expect(found).not.toBeNull();
});
```

## Controller / service / CSV / auth test templates

Full working examples (supertest integration, request/response mock fallback, service SQLite pattern, CSV import, protected-route 401/403) live in [[references/test-typescript-node-backend-templates.md]] — copy and adapt rather than writing from scratch.

## Error testing

Always test error scenarios, not just success paths:

```typescript
await expect(
  UserService.create({
    username: "duplicado@teste.com",
    password: "123456",
    name: "João"
  })
).rejects.toThrow(APIError);
```

## Common pitfalls

| Pitfall                        | ❌ Bad                                              | ✅ Good                                      |
| ------------------------------ | --------------------------------------------------- | -------------------------------------------- |
| Mocking DB operations          | `jest.mock("@/src/lib/prisma")`                     | real `prisma.user.findUnique(...)`           |
| Hard-coded dates that expire   | `new Date("2025-01-01")`                            | `date.setDate(date.getDate() + 7)` — dynamic |
| Leaving DB state between tests | create data, no cleanup                             | `beforeEach(() => prisma.user.deleteMany())` |
| Testing implementation details | `expect(service.internalHelper).toHaveBeenCalled()` | `expect(result.status).toBe("success")`      |
| Order-dependent tests          | `userId` set in test 1, used in test 2              | create fresh fixture in `beforeEach`         |
| Deleting all tables broadly    | `` prisma.$executeRaw`DELETE FROM *` ``             | delete only the tables the test touches      |

## Coverage targets

Service layer 80%+, controller layer covers success + error paths, utility functions 100%, mappers test all transformations. `yarn test --coverage`.

## Performance

SQLite tests run sequentially: `jest --runInBand` (see `package.json` scripts `test`/`test:watch`).

## Summary checklist

- [ ] Integration tests with SQLite instead of mocks whenever possible
- [ ] Mocking only external services (email, storage, external APIs, logger)
- [ ] Clean DB state in `beforeEach`/`afterEach`
- [ ] Descriptive test names in Portuguese
- [ ] AAA pattern
- [ ] Error scenarios covered, not just success paths
- [ ] Dynamic dates, not hard-coded
- [ ] Tests independent, no execution-order dependency
- [ ] Helper functions for complex setups
- [ ] DB state verified after operations
- [ ] No unnecessary mocks of Prisma or internal services

## Reference files

- [references/test-typescript-node-backend-templates.md](references/test-typescript-node-backend-templates.md) — full copy-paste templates: file layout, controller (supertest + req/res mock), service, mock management, helpers, CSV import, auth routes, running-tests commands.
