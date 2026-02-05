---
description: Comprehensive testing guidelines for TypeScript/Node.js backend projects
applyTo: "**/*.test.ts"
---

# Testing Instructions

## Overview

This document defines the testing standards and best practices for backend projects. Tests should be **production-ready**, **maintainable**, and follow the **integration-first approach** with SQLite database.

## Core Principles

### 1. Integration Tests Over Unit Tests

**ALWAYS prefer integration tests with real SQLite database operations over mocked tests.**

```typescript
// ✅ GOOD - Integration test with real database
describe("UserService - Integração com SQLite", () => {
  beforeEach(async () => {
    await prisma.user.deleteMany();
  });

  it("cria um usuário com sucesso", async () => {
    const user = await UserService.create({
      username: "joao@teste.com",
      password: "123456",
      name: "João",
    });

    const found = await prisma.user.findUnique({ where: { id: user.id } });
    expect(found).not.toBeNull();
    expect(found?.username).toBe("joao@teste.com");
  });
});

// ❌ BAD - Unnecessary mocking when integration is possible
jest.mock("@/src/lib/prisma");
const mockPrisma = prisma as jest.Mocked<typeof prisma>;
mockPrisma.user.create.mockResolvedValue({ ... });
```

### 2. Use Mocks Only When Necessary

Mocks should be used **exclusively** for:

- **External services** (email providers, cloud storage, external APIs)
- **Side effects** that cannot be tested in isolation (loggers, file system when not critical)
- **Third-party APIs** that require network calls
- **Time-dependent operations** (Date.now(), setTimeout)

```typescript
// ✅ GOOD - Mock external service
jest.mock("@/src/lib/mail");
jest.mock("@/src/utils/logger");

// Mock email provider (external dependency)
mockSendEmail = jest
  .spyOn(EmailProvider, "sendEmail")
  .mockResolvedValue(undefined);

// ✅ GOOD - Mock external API client
externalApiClientMock.createResource.mockResolvedValue(100);
```

### 3. Test Database Setup

**ALWAYS use SQLite for tests** (configured in `jest.env-setup.ts` and `schema.test.prisma`).

```typescript
// ✅ GOOD - Clean database state before tests
beforeAll(async () => {
  await prisma.resource.deleteMany();
  await prisma.user.deleteMany();
});

beforeEach(async () => {
  jest.clearAllMocks();
  await prisma.resource.deleteMany();
  await prisma.user.deleteMany();
});

afterAll(async () => {
  await prisma.$disconnect();
});
```

**NEVER** hard-delete records in production code; tests can use `deleteMany()` for cleanup.

## Test Structure Standards

### File Organization

```
src/modules/<feature>/
├── tests/                          # For service/business logic tests
│   ├── <feature>.service.test.ts
│   ├── <feature>.controller.test.ts
│   ├── <feature>.mappers.test.ts
│   └── utils.test.ts
└── __tests__/                      # For isolated unit tests (utilities)
    └── <feature>-utils.test.ts
```

### Naming Conventions

```typescript
// ✅ GOOD - Descriptive test names in Portuguese
describe("UserService - Integração com SQLite", () => {
  it("cria um usuário com sucesso", async () => { ... });
  it("impede criação de usuário duplicado", async () => { ... });
  it("retorna erro quando usuário não é encontrado", async () => { ... });
});

// ❌ BAD - Generic or unclear names
describe("UserService", () => {
  it("works", () => { ... });
  it("test1", () => { ... });
});
```

### Test Structure Pattern

Follow the **Arrange-Act-Assert (AAA)** pattern:

```typescript
it("deve criar um recurso com sucesso", async () => {
  // ARRANGE - Setup test data
  const data: CreateResourceRequestDTO = {
    name: "Test Resource",
    description: "Description",
    type: "user",
    start_date: new Date(),
    duration: 60,
    visible: true,
    user_id: 1,
    created_by: userId,
  };

  // Mock only external dependencies
  externalApiClientMock.createResource.mockResolvedValue(100);

  // ACT - Execute the function
  const result = await ResourceService.create(
    data,
    externalApiClientMock as any,
  );

  // ASSERT - Verify results
  expect(result).toBeDefined();
  expect(result.id).toBeDefined();
  expect(result.name).toBe(data.name);
  expect(result.external_id).toBe(100);

  // Verify database state
  const found = await prisma.resource.findUnique({ where: { id: result.id } });
  expect(found).not.toBeNull();
});
```

## Controller Tests

### Integration Pattern with Supertest

```typescript
import request from "supertest";
import app from "@/src/app";
import { PATHS } from "@/src/common/paths";
import prisma from "@/src/lib/prisma";
import { UserService } from "../user/user.service";
import { AuthService } from "../auth/auth.service";

describe("Team Controller - Integração com DB real", () => {
  let adminAccessToken: string;

  beforeEach(async () => {
    await prisma.team.deleteMany();
    await prisma.refreshToken.deleteMany();
    await prisma.user.deleteMany();

    const adminUser = await UserService.create({
      username: "admin@example.com",
      password: "password123",
      name: "Admin User",
    });

    const tokenResult = await AuthService.login({
      username: adminUser.username,
      password: "password123",
    });
    adminAccessToken = tokenResult.accessToken;
  });

  it("deve criar um time com sucesso", async () => {
    const res = await request(app)
      .post(PATHS.TEAMS.CREATE.path)
      .set("Authorization", `Bearer ${adminAccessToken}`)
      .send({ name: "Tech Team" });

    expect(res.statusCode).toBe(201);
    expect(res.body).toHaveProperty("id");
    expect(res.body.name).toBe("Tech Team");
  });
});
```

### Request/Response Mock Pattern (When Necessary)

```typescript
import { Request, Response } from "express";
import { jest } from "@jest/globals";

describe("ResourceController", () => {
  let req: Partial<Request>;
  let res: Partial<Response>;
  let json: jest.Mock;
  let status: jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();

    json = jest.fn();
    status = jest.fn().mockReturnValue({ json });

    req = {
      body: {},
      params: {},
      query: {},
      user: { userId: "test-user-id" } as any,
    };

    res = {
      json: json as any,
      status: status as any,
    };
  });

  it("deve criar um recurso", async () => {
    req.body = { name: "Test Resource", ... };

    await ResourceController.create(req as Request, res as Response);

    expect(status).toHaveBeenCalledWith(201);
    expect(json).toHaveBeenCalledWith(
      expect.objectContaining({ name: "Test Resource" })
    );
  });
});
```

## Service Tests

**ALWAYS test services with real database operations:**

```typescript
describe("ResourceService - Integração com SQLite", () => {
  let userId: string;

  beforeEach(async () => {
    await prisma.resource.deleteMany();
    await prisma.user.deleteMany();

    const user = await prisma.user.create({
      data: {
        username: "testuser",
        password: "password123",
        name: "Test User",
      },
    });
    userId = user.id;
  });

  it("deve criar um recurso com sucesso", async () => {
    const data: CreateResourceRequestDTO = { ... };

    // Mock only external services
    externalApiClientMock.createResource.mockResolvedValue(100);

    const result = await ResourceService.create(
      data,
      externalApiClientMock as any
    );

    expect(result).toBeDefined();
    expect(result.name).toBe(data.name);

    // Verify database persistence
    const found = await prisma.resource.findUnique({ where: { id: result.id } });
    expect(found).not.toBeNull();
  });
});
```

## Mock Management

### External Services Pattern

```typescript
// ✅ GOOD - Centralized mock files
// src/lib/external-api.client.mock.ts
export const externalApiClientMock = {
  createResource: jest.fn(),
  updateResource: jest.fn(),
  deleteResource: jest.fn(),
};

// In test file
import { externalApiClientMock } from "@/src/lib/external-api.client.mock";

beforeEach(() => {
  jest.clearAllMocks();
  externalApiClientMock.createResource.mockResolvedValue(100);
});
```

### Logger and Non-Critical Side Effects

```typescript
// ✅ GOOD - Mock logger to reduce console noise
jest.mock("@/src/utils/logger");

beforeEach(() => {
  jest.spyOn(logger, "info").mockImplementation();
  jest.spyOn(logger, "warn").mockImplementation();
  jest.spyOn(logger, "error").mockImplementation();
});

afterEach(() => {
  jest.restoreAllMocks();
});
```

### File System and Uploads

```typescript
// ✅ GOOD - Mock file system operations when necessary
jest.mock("fs");
import fs from "fs";

beforeEach(() => {
  (fs.readFileSync as jest.Mock).mockReturnValue("mock CSV content");
  (fs.existsSync as jest.Mock).mockReturnValue(true);
});
```

## Error Testing

**ALWAYS test error scenarios:**

```typescript
it("deve retornar erro ao criar usuário duplicado", async () => {
  await UserService.create({
    username: "duplicado@teste.com",
    password: "123456",
    name: "João",
  });

  await expect(
    UserService.create({
      username: "duplicado@teste.com",
      password: "123456",
      name: "João",
    }),
  ).rejects.toThrow(APIError);
});

it("deve retornar erro 404 quando recurso não existe", async () => {
  await expect(ResourceService.findById("non-existent-id")).rejects.toThrow(
    new APIError("Recurso não encontrado", 404),
  );
});
```

## Helper Functions and Utilities

Create helper functions to improve test maintainability:

```typescript
/**
 * Helper function to generate test dates dynamically
 * Prevents tests from breaking when hardcoded dates become outdated
 */
function generateTestDateSequence(
  startDaysFromNow: number,
  intervalDays: number,
  count: number,
): Date[] {
  const baseDate = new Date();
  baseDate.setDate(baseDate.getDate() + startDaysFromNow);
  baseDate.setHours(10, 0, 0, 0);

  return Array.from({ length: count }, (_, i) => {
    const date = new Date(baseDate);
    date.setDate(date.getDate() + i * intervalDays);
    return date;
  });
}

/**
 * Helper function to mock external utility
 */
function mockExtractExternalId(externalId: number | null): void {
  const mock = require("../utils").extractExternalIdFromUrl as jest.Mock;
  mock.mockClear();
  mock.mockReturnValue(externalId);
}
```

## CSV and Bulk Operations

```typescript
describe("Resource CSV Import", () => {
  beforeEach(async () => {
    await prisma.importJobLine.deleteMany();
    await prisma.importJob.deleteMany();
    await prisma.resource.deleteMany();

    jest.clearAllMocks();
  });

  it("deve importar recursos via CSV com sucesso", async () => {
    const mockCSVContent = `Name,Description,Type,StartDate,Duration
Resource 1,Desc 1,user,2026-02-10T10:00:00,60`;

    (fs.readFileSync as jest.Mock).mockReturnValue(mockCSVContent);

    const result = await ResourceService.importFromCSV({
      filePath: "test.csv",
      userId,
    });

    expect(result.importedCount).toBe(1);
    expect(result.errors).toHaveLength(0);

    const resources = await prisma.resource.findMany();
    expect(resources).toHaveLength(1);
    expect(resources[0].name).toBe("Resource 1");
  });
});
```

## Authentication and Authorization Tests

```typescript
describe("Protected Routes", () => {
  it("deve retornar 401 sem token", async () => {
    const res = await request(app).get(PATHS.TEAMS.LIST.path);

    expect(res.statusCode).toBe(401);
  });

  it("deve retornar 403 sem permissão", async () => {
    const normalUser = await UserService.create({
      username: "normal@example.com",
      password: "password123",
      name: "Normal User",
    });

    const tokenResult = await AuthService.login({
      username: normalUser.username,
      password: "password123",
    });

    const res = await request(app)
      .post(PATHS.TEAMS.CREATE.path)
      .set("Authorization", `Bearer ${tokenResult.accessToken}`)
      .send({ name: "New Team" });

    expect(res.statusCode).toBe(403);
  });
});
```

## Test Coverage

- **Service layer**: Aim for **80%+ coverage** of business logic
- **Controller layer**: Cover main success paths and error scenarios
- **Utility functions**: **100% coverage** for pure functions
- **Mappers**: Test all transformations with real data

```bash
# Run tests with coverage
yarn test --coverage

# View coverage report
open coverage/lcov-report/index.html
```

## Common Pitfalls to Avoid

### ❌ DON'T Mock Database Operations

```typescript
// ❌ BAD - Mocking Prisma when integration test is possible
jest.mock("@/src/lib/prisma");
const mockPrisma = prisma as jest.Mocked<typeof prisma>;
mockPrisma.user.findUnique.mockResolvedValue({ ... });
```

### ❌ DON'T Use Hard-Coded Dates

```typescript
// ❌ BAD - Hard-coded dates that will expire
const date = new Date("2025-01-01");

// ✅ GOOD - Dynamic dates
const date = new Date();
date.setDate(date.getDate() + 7); // 7 days from now
```

### ❌ DON'T Leave Database State Between Tests

```typescript
// ❌ BAD - Not cleaning up
it("test 1", async () => {
  await prisma.user.create({ ... });
  // No cleanup
});

// ✅ GOOD - Clean state in beforeEach/afterEach
beforeEach(async () => {
  await prisma.user.deleteMany();
});
```

### ❌ DON'T Test Implementation Details

```typescript
// ❌ BAD - Testing internal implementation
expect(service.internalHelperFunction).toHaveBeenCalled();

// ✅ GOOD - Test observable behavior
expect(result.status).toBe("success");
expect(await prisma.resource.count()).toBe(1);
```

### ❌ DON'T Write Dependent Tests

```typescript
// ❌ BAD - Tests depending on execution order
it("creates user", async () => {
  userId = (await UserService.create({ ... })).id;
});

it("updates user", async () => {
  await UserService.update(userId, { ... }); // Depends on previous test
});

// ✅ GOOD - Independent tests
beforeEach(async () => {
  const user = await UserService.create({ ... });
  userId = user.id;
});

it("updates user", async () => {
  await UserService.update(userId, { ... });
});
```

## Performance Considerations

### Run Tests in Band

SQLite tests run sequentially (`--runInBand`) to avoid concurrency issues:

```json
// package.json
{
  "scripts": {
    "test": "jest --runInBand",
    "test:watch": "jest --watch --runInBand"
  }
}
```

### Optimize Cleanup

```typescript
// ✅ GOOD - Delete only what's necessary
beforeEach(async () => {
  await prisma.resource.deleteMany();
  await prisma.user.deleteMany();
});

// ❌ BAD - Deleting all tables unnecessarily
beforeEach(async () => {
  await prisma.$executeRaw`DELETE FROM *`;
});
```

## Documentation in Tests

Add JSDoc comments for complex test helpers:

```typescript
/**
 * Creates a test user with admin privileges
 * @param overrides - Optional fields to override default user data
 * @returns User object with generated access token
 */
async function createAdminUser(overrides = {}) {
  const user = await UserService.create({
    username: "admin@test.com",
    password: "password123",
    name: "Admin",
    ...overrides,
  });

  const role = await RoleService.create({ name: "SYSTEM_ADMIN" });
  await AccessControlService.create({
    user_id: user.id,
    role_id: role.id,
    team_id: null,
  });

  return user;
}
```

## Running Tests

```bash
# Prepare test database (generates schema.test.prisma)
yarn test:prepare

# Run all tests
yarn test

# Run tests in watch mode
yarn test:watch

# Run specific test file
yarn test src/modules/user/user.service.test.ts

# Run tests with coverage
yarn test --coverage
```

## Summary Checklist

Before submitting tests, ensure:

- [ ] Using **integration tests with SQLite** instead of mocks whenever possible
- [ ] Mocking **only external services** (email, cloud storage, external APIs, logger)
- [ ] **Clean database state** in `beforeEach`/`afterEach`
- [ ] Descriptive test names in **Portuguese**
- [ ] Following **AAA pattern** (Arrange-Act-Assert)
- [ ] Testing **error scenarios** in addition to success paths
- [ ] Using **dynamic dates** instead of hard-coded values
- [ ] Tests are **independent** and don't rely on execution order
- [ ] Added **helper functions** for complex setups
- [ ] Verified **database state** after operations
- [ ] No unnecessary mocks of Prisma or internal services

---

**Remember**: Integration tests provide more confidence than unit tests. Test real behavior, not mocked implementations.
